"""
Testy jednostkowe dla komponentów matematycznych systemu PROPHET-70
Weryfikacja poprawności obliczeń Poissona i Kelly Criterion
"""

import pytest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from betting_system.poisson_model import PoissonFootballModel
from betting_system.kelly_criterion import KellyCriterion


class TestPoissonModel:
    """Testy modelu Poissona - weryfikacja matematyczna"""

    def test_probabilities_sum_to_one(self):
        """Suma wszystkich prawdopodobieństw powinna być ~1"""
        model = PoissonFootballModel()
        p_home, p_draw, p_away = model.calculate_from_expected_goals(2.0, 1.5)

        total = p_home + p_draw + p_away
        assert math.isclose(total, 1.0, rel_tol=0.01), f"Suma prawdopodobieństw: {total}"

    def test_known_scenario_equal_xg(self):
        """Test znanego scenariusza: 1.0 xG vs 1.0 xG"""
        model = PoissonFootballModel()
        p_home, p_draw, p_away = model.calculate_from_expected_goals(1.0, 1.0)

        # Przy równych xG, prawdopodobieństwa powinny być symetryczne
        assert math.isclose(p_home, p_away, rel_tol=0.01), \
            f"Home: {p_home}, Away: {p_away} - powinny być równe"

        # P(Draw) dla 1.0 vs 1.0 powinno być ~0.27 (znane z teorii)
        assert 0.25 <= p_draw <= 0.30, \
            f"P(Draw) = {p_draw}, oczekiwano ~0.27"

    def test_strong_favorite_scenario(self):
        """Test silnego faworyta: 3.0 xG vs 0.5 xG"""
        model = PoissonFootballModel()
        p_home, p_draw, p_away = model.calculate_from_expected_goals(3.0, 0.5)

        # Gospodarze powinni być zdecydowanym faworytem
        assert p_home > 0.70, f"P(Home) = {p_home}, oczekiwano >70%"
        assert p_away < 0.10, f"P(Away) = {p_away}, oczekiwano <10%"
        assert p_home > p_draw > p_away, "Nieprawidłowa kolejność prawdopodobieństw"

    def test_defensive_match(self):
        """Test defensywnego meczu: 0.5 xG vs 0.5 xG"""
        model = PoissonFootballModel()
        p_home, p_draw, p_away = model.calculate_from_expected_goals(0.5, 0.5)

        # Przy niskich xG, remis powinien być bardziej prawdopodobny
        assert p_draw > p_home and p_draw > p_away, \
            f"P(Draw)={p_draw} powinno być największe w defensywnym meczu"

    def test_score_probabilities(self):
        """Test prawdopodobieństw konkretnych wyników"""
        model = PoissonFootballModel()
        scores = model.get_score_probabilities(2.0, 1.0, top_n=5)

        # Sprawdź, czy zwraca 5 najczęstszych wyników
        assert len(scores) == 5, f"Oczekiwano 5 wyników, otrzymano {len(scores)}"

        # Wszystkie prawdopodobieństwa > 0
        assert all(prob > 0 for prob in scores.values()), \
            "Wszystkie prawdopodobieństwa powinny być > 0"

        # Suma prawdopodobieństw top 5 powinna być znacząca (>30%)
        total_prob = sum(scores.values())
        assert total_prob > 0.30, \
            f"Suma top 5 wyników: {total_prob}, oczekiwano >30%"

    def test_over_under_probability(self):
        """Test prawdopodobieństw Over/Under"""
        model = PoissonFootballModel()
        p_over, p_under = model.calculate_over_under_probability(2.0, 1.0, threshold=2.5)

        # Suma powinna być ~1
        assert math.isclose(p_over + p_under, 1.0, rel_tol=0.01), \
            f"P(Over) + P(Under) = {p_over + p_under}, oczekiwano 1.0"

        # Przy total xG = 3.0, Over 2.5 powinno być bardziej prawdopodobne
        assert p_over > p_under, \
            f"P(Over)={p_over} powinno być > P(Under)={p_under} dla total xG=3.0"

    def test_boundary_conditions(self):
        """Test warunków brzegowych"""
        model = PoissonFootballModel()

        # Bardzo niskie xG
        p_home, p_draw, p_away = model.calculate_from_expected_goals(0.1, 0.1)
        assert 0 <= p_home <= 1 and 0 <= p_draw <= 1 and 0 <= p_away <= 1

        # Bardzo wysokie xG
        p_home, p_draw, p_away = model.calculate_from_expected_goals(5.0, 5.0)
        assert 0 <= p_home <= 1 and 0 <= p_draw <= 1 and 0 <= p_away <= 1


class TestKellyCriterion:
    """Testy kryterium Kelly'ego - weryfikacja zarządzania kapitałem"""

    def test_positive_edge_should_bet(self):
        """Test: Przy pozytywnym edge powinno być BET"""
        kelly = KellyCriterion(fraction=0.25)
        result = kelly.calculate_stake(
            true_probability=0.60,
            bookmaker_odds=2.0,
            bankroll=10000
        )

        assert result['recommendation'] == 'BET', \
            "Przy pozytywnym edge powinna być rekomendacja BET"
        assert result['stake_amount'] > 0, \
            "Stake powinien być > 0"
        assert result['kelly_percentage'] > 0, \
            "Kelly percentage powinien być > 0"

    def test_negative_edge_no_bet(self):
        """Test: Przy negatywnym edge nie powinno być zakładu"""
        kelly = KellyCriterion(fraction=0.25)
        result = kelly.calculate_stake(
            true_probability=0.40,
            bookmaker_odds=2.0,
            bankroll=10000
        )

        assert result['recommendation'] == 'NO BET', \
            "Przy negatywnym edge powinna być rekomendacja NO BET"
        assert result['stake_amount'] == 0, \
            "Stake powinien być 0"

    def test_no_edge_no_bet(self):
        """Test: Przy zerowym edge (fair odds) nie powinno być zakładu"""
        kelly = KellyCriterion(fraction=0.25)

        # P = 0.5, Odds = 2.0 -> Fair odds (0% edge)
        result = kelly.calculate_stake(
            true_probability=0.50,
            bookmaker_odds=2.0,
            bankroll=10000
        )

        assert result['kelly_percentage'] == 0, \
            "Przy zerowym edge Kelly powinien być 0"

    def test_kelly_percentage_reasonable(self):
        """Test: Kelly percentage powinien być w rozsądnych granicach"""
        kelly = KellyCriterion(fraction=0.25)

        # Duża przewaga
        result = kelly.calculate_stake(
            true_probability=0.70,
            bookmaker_odds=2.0,
            bankroll=10000
        )

        # Quarter Kelly + safety cap (10%) powinien ograniczyć stake
        assert result['kelly_percentage'] <= 0.10, \
            f"Kelly powinien być ograniczony do 10%, otrzymano {result['kelly_percentage']}"

    def test_expected_value_calculation(self):
        """Test: Weryfikacja obliczeń Expected Value"""
        kelly = KellyCriterion()

        # EV = probability * odds
        # Jeśli P=0.55, Odds=2.0 -> EV = 1.10 (10% expected return)
        ev = kelly._calculate_ev(0.55, 2.0)
        assert math.isclose(ev, 1.10, rel_tol=0.01), \
            f"EV = {ev}, oczekiwano 1.10"

        # Przy P=0.50, Odds=2.0 -> EV = 1.00 (break-even)
        ev = kelly._calculate_ev(0.50, 2.0)
        assert math.isclose(ev, 1.00, rel_tol=0.01), \
            f"EV = {ev}, oczekiwano 1.00"

    def test_fractional_kelly_reduces_stake(self):
        """Test: Fractional Kelly powinien redukować stake"""
        full_kelly = KellyCriterion(fraction=1.0)
        quarter_kelly = KellyCriterion(fraction=0.25)

        probability = 0.60
        odds = 2.0
        bankroll = 10000

        full_result = full_kelly.calculate_stake(probability, odds, bankroll)
        quarter_result = quarter_kelly.calculate_stake(probability, odds, bankroll)

        # Quarter Kelly powinien być ~4x mniejszy
        assert quarter_result['stake_amount'] < full_result['stake_amount'], \
            "Quarter Kelly powinien dać mniejszy stake niż Full Kelly"

        ratio = full_result['stake_amount'] / quarter_result['stake_amount']
        assert 3.5 <= ratio <= 4.5, \
            f"Stosunek Full/Quarter powinien być ~4, otrzymano {ratio}"

    def test_edge_calculation(self):
        """Test: Weryfikacja obliczeń edge (przewagi)"""
        kelly = KellyCriterion()

        # P=0.60, Odds=2.0 -> Implied=0.50 -> Edge=10%
        result = kelly.calculate_stake(0.60, 2.0)
        expected_edge = (0.60 - 0.50) * 100

        assert math.isclose(result['edge_percentage'], expected_edge, rel_tol=0.01), \
            f"Edge = {result['edge_percentage']}, oczekiwano {expected_edge}"

    def test_different_fractions(self):
        """Test różnych wartości fractional Kelly"""
        fractions = [0.10, 0.25, 0.50, 1.0]
        probability = 0.60
        odds = 2.0
        bankroll = 10000

        stakes = []
        for frac in fractions:
            kelly = KellyCriterion(fraction=frac)
            result = kelly.calculate_stake(probability, odds, bankroll)
            stakes.append(result['stake_amount'])

        # Stakes powinny rosnąć wraz z fraction
        assert stakes == sorted(stakes), \
            "Stakes powinny rosnąć wraz ze wzrostem fraction"

    def test_bankroll_scaling(self):
        """Test: Stake powinien skalować się z bankrollem"""
        kelly = KellyCriterion(fraction=0.25)

        result_10k = kelly.calculate_stake(0.60, 2.0, bankroll=10000)
        result_20k = kelly.calculate_stake(0.60, 2.0, bankroll=20000)

        # Przy 2x bankroll, stake powinien być ~2x większy
        ratio = result_20k['stake_amount'] / result_10k['stake_amount']
        assert math.isclose(ratio, 2.0, rel_tol=0.01), \
            f"Stake powinien skalować liniowo z bankrollem, otrzymano ratio={ratio}"

    def test_validation_errors(self):
        """Test: Walidacja błędnych danych wejściowych"""
        kelly = KellyCriterion()

        # Prawdopodobieństwo poza zakresem
        with pytest.raises(ValueError):
            kelly.calculate_stake(1.5, 2.0)  # >1

        with pytest.raises(ValueError):
            kelly.calculate_stake(-0.1, 2.0)  # <0

        # Kurs niepoprawny
        with pytest.raises(ValueError):
            kelly.calculate_stake(0.50, 0.5)  # <1


class TestIntegration:
    """Testy integracyjne - pełny przepływ"""

    def test_realistic_scenario(self):
        """Test realistycznego scenariusza zakładu"""
        # Scenariusz: Manchester City (silny) vs słabszy zespół
        poisson = PoissonFootballModel()
        kelly = KellyCriterion(fraction=0.25)

        # xG sugeruje City jako faworyta
        p_home, p_draw, p_away = poisson.calculate_from_expected_goals(2.5, 1.0)

        # Bukmacher daje kurs 1.80 (implied prob ~55.6%)
        bookmaker_odds = 1.80
        bankroll = 10000

        # Nasz model pokazuje wyższe prawdopodobieństwo
        # Powinno być value bet
        kelly_result = kelly.calculate_stake(p_home, bookmaker_odds, bankroll)

        assert kelly_result['recommendation'] == 'BET', \
            "W tym scenariuszu powinien być value bet"
        assert kelly_result['edge_percentage'] > 0, \
            "Powinno być positive edge"
        assert 0 < kelly_result['stake_amount'] < bankroll * 0.10, \
            "Stake powinien być rozsądny (0-10% bankrolla)"

    def test_no_value_scenario(self):
        """Test scenariusza bez value"""
        poisson = PoissonFootballModel()
        kelly = KellyCriterion(fraction=0.25)

        # Wyrównany mecz
        p_home, _, _ = poisson.calculate_from_expected_goals(1.5, 1.5)

        # Bukmacher oferuje zbyt niski kurs (przepłacony)
        bookmaker_odds = 1.50  # Implied prob ~66.7%
        bankroll = 10000

        kelly_result = kelly.calculate_stake(p_home, bookmaker_odds, bankroll)

        # Nie powinno być value
        assert kelly_result['recommendation'] == 'NO BET', \
            "Przy przepłaconym kursie nie powinno być zakładu"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
