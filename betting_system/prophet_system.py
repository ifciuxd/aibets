"""
PROPHET-70 System - Główny moduł analizy zakładów
Łączy model Poissona, kryterium Kelly'ego i filtry value betting
"""

from typing import List, Optional, Dict
import pandas as pd
from .data_models import Match, BettingDecision, TeamStats
from .poisson_model import PoissonFootballModel
from .kelly_criterion import KellyCriterion


class ProphetSystem:
    """
    Główny system analizy kuponów bukmacherskich PROPHET-70

    Algorytm:
    1. Oblicz prawdopodobieństwa z modelu Poissona
    2. Porównaj z kursami bukmachera (znajdź value)
    3. Zastosuj filtry bezpieczeństwa
    4. Oblicz optymalny stake z Kelly Criterion
    5. Zwróć ranking najlepszych zakładów
    """

    def __init__(
        self,
        bankroll: float,
        kelly_fraction: float = 0.25,
        min_edge: float = 0.05,
        min_probability: float = 0.35,
        max_probability: float = 0.75,
        league_avg_goals: float = 2.7
    ):
        """
        Args:
            bankroll: Kapitał do zarządzania (PLN/EUR/USD)
            kelly_fraction: Ułamek Kelly (0.25 = Quarter Kelly, zalecane)
            min_edge: Minimalna przewaga do postawienia (5% = 0.05)
            min_probability: Min prawdopodobieństwo (unikaj longshots)
            max_probability: Max prawdopodobieństwo (unikaj niskich kursów)
            league_avg_goals: Średnia bramek w lidze (2.7 dla top 5 lig)
        """
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.min_edge = min_edge
        self.min_probability = min_probability
        self.max_probability = max_probability
        self.league_avg_goals = league_avg_goals

        # Inicjalizuj komponenty
        self.poisson_model = PoissonFootballModel(max_goals=6)
        self.kelly = KellyCriterion(fraction=kelly_fraction)

        # Historia decyzji
        self.history: List[BettingDecision] = []

    def analyze_match(self, match: Match) -> BettingDecision:
        """
        Analizuje pojedynczy mecz i zwraca decyzję zakładową

        Args:
            match: Obiekt Match z danymi

        Returns:
            BettingDecision: Rekomendacja zakładu
        """
        # 1. Oblicz prawdopodobieństwa z modelu Poissona
        if match.home_xg is not None and match.away_xg is not None:
            # Jeśli mamy xG, użyj ich bezpośrednio
            p_home, p_draw, p_away = self.poisson_model.calculate_from_expected_goals(
                match.home_xg, match.away_xg
            )
        else:
            # Użyj statystyk drużyn
            p_home, p_draw, p_away = self.poisson_model.calculate_match_probabilities(
                home_attack=match.home_team.goals_scored_avg,
                away_attack=match.away_team.goals_scored_avg,
                home_defense=match.home_team.goals_conceded_avg,
                away_defense=match.away_team.goals_conceded_avg,
                league_avg_goals=self.league_avg_goals
            )

        # 2. Sprawdź każdy możliwy zakład (Home, Draw, Away)
        bets = [
            ("Home Win", p_home, match.odds_home),
            ("Draw", p_draw, match.odds_draw),
            ("Away Win", p_away, match.odds_away)
        ]

        best_bet = None
        best_ev = 0

        for bet_type, prob, odds in bets:
            # Oblicz implied probability
            implied_prob = 1 / odds

            # Oblicz edge
            edge = prob - implied_prob

            # Zastosuj filtry
            if not self._passes_filters(prob, edge):
                continue

            # Oblicz Kelly stake
            kelly_result = self.kelly.calculate_stake(prob, odds, self.bankroll)

            # Oblicz EV
            ev = kelly_result['expected_value']

            # Wybierz najlepszy zakład (największy EV)
            if ev > best_ev and kelly_result['recommendation'] == 'BET':
                best_ev = ev
                best_bet = {
                    'type': bet_type,
                    'prob': prob,
                    'odds': odds,
                    'kelly': kelly_result
                }

        # 3. Utwórz decyzję
        if best_bet is None:
            return BettingDecision(
                match_name=match.match_name,
                recommended_bet="NO BET",
                model_probability=max(p_home, p_draw, p_away),
                implied_probability=1 / min(match.odds_home, match.odds_draw, match.odds_away),
                edge_percentage=0.0,
                expected_value=1.0,
                bookmaker_odds=0.0,
                recommended_stake_pct=0.0,
                recommended_stake_amount=0.0,
                confidence_level="LOW",
                reason="Brak value lub nie spełniono filtrów"
            )

        # Określ poziom pewności
        confidence = self._calculate_confidence(
            best_bet['kelly']['edge_percentage'],
            best_bet['prob']
        )

        decision = BettingDecision(
            match_name=match.match_name,
            recommended_bet=best_bet['type'],
            model_probability=best_bet['prob'],
            implied_probability=1 / best_bet['odds'],
            edge_percentage=best_bet['kelly']['edge_percentage'],
            expected_value=best_bet['kelly']['expected_value'],
            bookmaker_odds=best_bet['odds'],
            recommended_stake_pct=best_bet['kelly']['kelly_percentage'],
            recommended_stake_amount=best_bet['kelly'].get('stake_amount', 0.0),
            confidence_level=confidence,
            reason=f"Value bet z {best_bet['kelly']['edge_percentage']:.1f}% przewagą"
        )

        self.history.append(decision)
        return decision

    def analyze_matches(self, matches: List[Match]) -> pd.DataFrame:
        """
        Analizuje wiele meczów i zwraca ranking najlepszych zakładów

        Args:
            matches: Lista obiektów Match

        Returns:
            DataFrame: Posortowane rekomendacje
        """
        decisions = [self.analyze_match(match) for match in matches]

        # Filtruj tylko zakłady do postawienia
        valid_bets = [d for d in decisions if d.recommended_bet != "NO BET"]

        if not valid_bets:
            return pd.DataFrame()

        # Konwertuj do DataFrame
        df = pd.DataFrame([d.model_dump() for d in valid_bets])

        # Posortuj po Expected Value (malejąco)
        df = df.sort_values('expected_value', ascending=False)

        # Dodaj ranking
        df.insert(0, 'rank', range(1, len(df) + 1))

        return df

    def _passes_filters(self, probability: float, edge: float) -> bool:
        """
        Sprawdza czy zakład przechodzi filtry bezpieczeństwa

        Args:
            probability: Prawdopodobieństwo z modelu
            edge: Przewaga (model_prob - implied_prob)

        Returns:
            bool: True jeśli zakład jest akceptowalny
        """
        # Filtr 1: Minimalna przewaga
        if edge < self.min_edge:
            return False

        # Filtr 2: Prawdopodobieństwo w rozsądnym zakresie
        if probability < self.min_probability or probability > self.max_probability:
            return False

        # Filtr 3: Edge nie może być zbyt duży (podejrzane)
        if edge > 0.30:  # >30% edge jest nierealne
            return False

        return True

    def _calculate_confidence(self, edge: float, probability: float) -> str:
        """
        Oblicza poziom pewności zakładu

        Args:
            edge: Przewaga w %
            probability: Prawdopodobieństwo

        Returns:
            str: "LOW", "MEDIUM", "HIGH", "VERY HIGH"
        """
        score = 0

        # Punkty za edge
        if edge > 15:
            score += 3
        elif edge > 10:
            score += 2
        elif edge > 5:
            score += 1

        # Punkty za prawdopodobieństwo w sweet spot (45-65%)
        if 0.45 <= probability <= 0.65:
            score += 2
        elif 0.40 <= probability <= 0.70:
            score += 1

        # Mapowanie
        if score >= 4:
            return "VERY HIGH"
        elif score >= 3:
            return "HIGH"
        elif score >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    def get_portfolio_summary(self) -> Dict:
        """
        Podsumowanie portfela zakładów

        Returns:
            dict: Statystyki
        """
        if not self.history:
            return {"message": "Brak zakładów w historii"}

        valid_bets = [b for b in self.history if b.recommended_bet != "NO BET"]

        if not valid_bets:
            return {"message": "Brak rekomendowanych zakładów"}

        total_stake = sum(b.recommended_stake_amount or 0 for b in valid_bets)
        avg_odds = sum(b.bookmaker_odds for b in valid_bets) / len(valid_bets)
        avg_edge = sum(b.edge_percentage for b in valid_bets) / len(valid_bets)
        avg_ev = sum(b.expected_value for b in valid_bets) / len(valid_bets)

        return {
            "total_bets": len(valid_bets),
            "total_stake_amount": round(total_stake, 2),
            "percentage_of_bankroll": round((total_stake / self.bankroll) * 100, 2),
            "average_odds": round(avg_odds, 2),
            "average_edge": round(avg_edge, 2),
            "average_expected_value": round(avg_ev, 4),
            "confidence_distribution": {
                level: len([b for b in valid_bets if b.confidence_level == level])
                for level in ["LOW", "MEDIUM", "HIGH", "VERY HIGH"]
            }
        }

    def update_bankroll(self, new_bankroll: float):
        """Aktualizuje bankroll (np. po wygranej/przegranej)"""
        self.bankroll = new_bankroll

    def reset_history(self):
        """Czyści historię decyzji"""
        self.history = []
