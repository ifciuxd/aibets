"""
Kryterium Kelly'ego - Optymalne zarządzanie kapitałem
Oblicza optymalny procent bankrolla do postawienia
"""

from typing import Optional
import numpy as np


class KellyCriterion:
    """
    Implementacja kryterium Kelly'ego dla zakładów sportowych.

    Wzór: f* = (bp - q) / b
    gdzie:
        f* = optymalny ułamek kapitału do postawienia
        b = odds - 1 (net odds)
        p = prawdopodobieństwo wygranej (nasze)
        q = prawdopodobieństwo przegranej = 1 - p
    """

    def __init__(self, fraction: float = 0.25):
        """
        Args:
            fraction: Fractional Kelly (0.25 = Quarter Kelly, bezpieczniejsze)
                     1.0 = Full Kelly (agresywne)
                     0.5 = Half Kelly (zbalansowane)
        """
        if not 0 < fraction <= 1:
            raise ValueError("Fraction musi być w przedziale (0, 1]")

        self.fraction = fraction

    def calculate_stake(
        self,
        true_probability: float,
        bookmaker_odds: float,
        bankroll: Optional[float] = None
    ) -> dict:
        """
        Oblicza optymalny stake według kryterium Kelly'ego

        Args:
            true_probability: Nasze prawdopodobieństwo wygranej (0-1)
            bookmaker_odds: Kurs bukmachera (np. 2.5)
            bankroll: Kapitał (opcjonalnie, do obliczenia kwoty)

        Returns:
            dict: {
                'kelly_percentage': % kapitału do postawienia,
                'stake_amount': kwota (jeśli podano bankroll),
                'expected_value': EV zakładu,
                'recommendation': 'BET' lub 'NO BET'
            }
        """
        if not 0 < true_probability < 1:
            raise ValueError("Prawdopodobieństwo musi być w przedziale (0, 1)")
        if bookmaker_odds <= 1:
            raise ValueError("Kurs musi być > 1")

        # Oblicz zmienne
        p = true_probability
        q = 1 - p
        b = bookmaker_odds - 1  # Net odds

        # Kryterium Kelly'ego
        kelly_fraction = (b * p - q) / b

        # Zastosuj fractional Kelly dla bezpieczeństwa
        adjusted_kelly = kelly_fraction * self.fraction

        # Nie stawiamy jeśli kelly < 0 (brak value)
        if adjusted_kelly <= 0:
            return {
                'kelly_percentage': 0.0,
                'stake_amount': 0.0 if bankroll else None,
                'expected_value': self._calculate_ev(p, bookmaker_odds),
                'edge_percentage': (p - (1 / bookmaker_odds)) * 100,
                'recommendation': 'NO BET',
                'reason': 'Brak przewagi (EV < 1)'
            }

        # Ogranicz do maksymalnie 10% bankrolla (safety cap)
        capped_kelly = min(adjusted_kelly, 0.10)

        # Oblicz Expected Value
        ev = self._calculate_ev(p, bookmaker_odds)

        # Oblicz edge
        implied_prob = 1 / bookmaker_odds
        edge = (p - implied_prob) * 100

        result = {
            'kelly_percentage': round(capped_kelly, 4),
            'expected_value': round(ev, 4),
            'edge_percentage': round(edge, 2),
            'recommendation': 'BET' if capped_kelly > 0 else 'NO BET'
        }

        if bankroll:
            result['stake_amount'] = round(bankroll * capped_kelly, 2)

        # Dodaj ostrzeżenia
        if kelly_fraction > 0.15:
            result['warning'] = 'Bardzo wysoki Kelly (>15%) - rozważ ostrożność'

        return result

    def _calculate_ev(self, probability: float, odds: float) -> float:
        """
        Oblicza Expected Value (wartość oczekiwaną)

        EV = (probability * profit) - (1 - probability) * stake
        Przy stake = 1:
        EV = probability * odds - 1

        Returns:
            float: EV (np. 1.15 = +15% expected return)
        """
        return probability * odds

    def optimal_kelly_for_edge(self, edge: float, odds: float) -> float:
        """
        Oblicza Kelly dla zadanej przewagi (edge)

        Args:
            edge: Przewaga w % (np. 5 = 5% edge)
            odds: Kurs bukmachera

        Returns:
            float: Optymalny % kapitału
        """
        edge_decimal = edge / 100
        implied_prob = 1 / odds
        true_prob = implied_prob + edge_decimal

        result = self.calculate_stake(true_prob, odds)
        return result['kelly_percentage']

    def simulate_kelly_growth(
        self,
        initial_bankroll: float,
        win_rate: float,
        avg_odds: float,
        num_bets: int = 100,
        use_kelly: bool = True
    ) -> dict:
        """
        Symulacja Monte Carlo wzrostu kapitału z Kelly vs flat staking

        Args:
            initial_bankroll: Kapitał początkowy
            win_rate: Procent wygranych zakładów (0-1)
            avg_odds: Średni kurs
            num_bets: Liczba zakładów do zasymulowania
            use_kelly: Czy używać Kelly (False = flat 2% staking)

        Returns:
            dict: Wyniki symulacji
        """
        bankroll = initial_bankroll
        stake_pct = 0.02 if not use_kelly else None

        history = [bankroll]

        for _ in range(num_bets):
            # Losuj wynik
            won = np.random.random() < win_rate

            if use_kelly:
                # Oblicz Kelly stake
                kelly_result = self.calculate_stake(win_rate, avg_odds, bankroll)
                stake = kelly_result.get('stake_amount', 0)
            else:
                # Flat staking
                stake = bankroll * stake_pct

            if stake <= 0:
                continue

            if won:
                profit = stake * (avg_odds - 1)
                bankroll += profit
            else:
                bankroll -= stake

            history.append(bankroll)

        return {
            'final_bankroll': round(bankroll, 2),
            'roi': round(((bankroll / initial_bankroll) - 1) * 100, 2),
            'max_bankroll': round(max(history), 2),
            'min_bankroll': round(min(history), 2),
            'history': history
        }
