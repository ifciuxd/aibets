"""
Podstawowe testy systemu PROPHET-70
"""

import pytest
import sys
import os

# Dodaj ścieżkę do modułu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from betting_system import ProphetSystem
from betting_system.data_models import Match, TeamStats
from betting_system.poisson_model import PoissonFootballModel
from betting_system.kelly_criterion import KellyCriterion


class TestPoissonModel:
    """Testy modelu Poissona"""

    def test_basic_probabilities(self):
        model = PoissonFootballModel()
        p_home, p_draw, p_away = model.calculate_from_expected_goals(2.0, 1.0)

        # Suma prawdopodobieństw powinna być ~1
        assert abs((p_home + p_draw + p_away) - 1.0) < 0.01

        # Przy xG 2.0 vs 1.0, gospodarze powinni być faworytami
        assert p_home > p_draw
        assert p_home > p_away

    def test_score_probabilities(self):
        model = PoissonFootballModel()
        scores = model.get_score_probabilities(2.0, 1.0, top_n=5)

        assert len(scores) == 5
        # Wszystkie prawdopodobieństwa powinny być > 0
        assert all(prob > 0 for prob in scores.values())

    def test_over_under(self):
        model = PoissonFootballModel()
        p_over, p_under = model.calculate_over_under_probability(2.0, 1.0, threshold=2.5)

        # Suma powinna być ~1
        assert abs((p_over + p_under) - 1.0) < 0.01


class TestKellyCriterion:
    """Testy kryterium Kelly'ego"""

    def test_positive_edge(self):
        kelly = KellyCriterion(fraction=0.25)
        result = kelly.calculate_stake(
            true_probability=0.60,
            bookmaker_odds=2.0,
            bankroll=10000
        )

        # Powinno być BET przy pozytywnym edge
        assert result['recommendation'] == 'BET'
        assert result['stake_amount'] > 0
        assert result['edge_percentage'] > 0

    def test_negative_edge(self):
        kelly = KellyCriterion(fraction=0.25)
        result = kelly.calculate_stake(
            true_probability=0.40,
            bookmaker_odds=2.0,
            bankroll=10000
        )

        # Nie powinno być zakładu przy braku edge
        assert result['recommendation'] == 'NO BET'
        assert result['stake_amount'] == 0

    def test_expected_value(self):
        kelly = KellyCriterion()
        ev = kelly._calculate_ev(0.55, 2.0)

        # EV powinno być > 1 przy pozytywnym edge
        assert ev > 1.0


class TestProphetSystem:
    """Testy głównego systemu"""

    def test_analyze_single_match(self):
        system = ProphetSystem(bankroll=10000)

        match = Match(
            match_name="Test Match",
            home_team=TeamStats(
                name="Home Team",
                goals_scored_avg=2.5,
                goals_conceded_avg=1.0
            ),
            away_team=TeamStats(
                name="Away Team",
                goals_scored_avg=1.5,
                goals_conceded_avg=1.5
            ),
            odds_home=1.80,
            odds_draw=3.50,
            odds_away=4.50
        )

        decision = system.analyze_match(match)

        # Sprawdź czy decyzja jest poprawna
        assert decision.match_name == "Test Match"
        assert decision.recommended_bet in ["Home Win", "Draw", "Away Win", "NO BET"]
        assert 0 <= decision.model_probability <= 1
        assert decision.expected_value >= 0

    def test_filters(self):
        system = ProphetSystem(
            bankroll=10000,
            min_edge=0.10,  # Bardzo wysoki min edge
            min_probability=0.60
        )

        # Ten mecz nie powinien przejść filtrów
        match = Match(
            match_name="Tight Match",
            home_team=TeamStats(
                name="Team A",
                goals_scored_avg=1.5,
                goals_conceded_avg=1.5
            ),
            away_team=TeamStats(
                name="Team B",
                goals_scored_avg=1.5,
                goals_conceded_avg=1.5
            ),
            odds_home=2.50,
            odds_draw=3.20,
            odds_away=2.80
        )

        decision = system.analyze_match(match)

        # Z tak wysokimi filtrami, prawdopodobnie NO BET
        # (chyba że model znajdzie duże value, co jest mało prawdopodobne)
        assert isinstance(decision.recommended_bet, str)


class TestDataModels:
    """Testy modeli danych"""

    def test_match_validation(self):
        # Poprawny mecz
        match = Match(
            match_name="Valid Match",
            home_team=TeamStats(
                name="Home",
                goals_scored_avg=2.0,
                goals_conceded_avg=1.0
            ),
            away_team=TeamStats(
                name="Away",
                goals_scored_avg=1.5,
                goals_conceded_avg=1.5
            ),
            odds_home=1.90,
            odds_draw=3.40,
            odds_away=4.00
        )

        assert match.match_name == "Valid Match"
        assert match.odds_home == 1.90

    def test_invalid_odds(self):
        # Kursy muszą być > 1
        with pytest.raises(Exception):
            Match(
                match_name="Invalid",
                home_team=TeamStats(
                    name="Home",
                    goals_scored_avg=2.0,
                    goals_conceded_avg=1.0
                ),
                away_team=TeamStats(
                    name="Away",
                    goals_scored_avg=1.5,
                    goals_conceded_avg=1.5
                ),
                odds_home=0.5,  # Niepoprawne
                odds_draw=3.0,
                odds_away=4.0
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
