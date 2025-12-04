"""
Model Rozkładu Poissona dla piłki nożnej
Oblicza prawdopodobieństwa wyników meczów na podstawie oczekiwanych bramek
"""

import numpy as np
from scipy.stats import poisson
from typing import Tuple, Dict


class PoissonFootballModel:
    """
    Model Poissona do przewidywania wyników meczów piłkarskich.

    Założenia:
    1. Liczba bramek strzelonych przez drużynę ma rozkład Poissona
    2. Bramki gospodarzy i gości są zdarzeniami niezależnymi
    3. Lambda (oczekiwana liczba bramek) zależy od siły ataku i obrony
    """

    def __init__(self, max_goals: int = 6):
        """
        Args:
            max_goals: Maksymalna liczba bramek do uwzględnienia w macierzy (domyślnie 6)
        """
        self.max_goals = max_goals

    def calculate_match_probabilities(
        self,
        home_attack: float,
        away_attack: float,
        home_defense: float = None,
        away_defense: float = None,
        league_avg_goals: float = 2.7
    ) -> Tuple[float, float, float]:
        """
        Oblicza prawdopodobieństwa: P(Home Win), P(Draw), P(Away Win)

        Args:
            home_attack: Siła ataku gospodarzy (bramki/mecz)
            away_attack: Siła ataku gości (bramki/mecz)
            home_defense: Siła obrony gospodarzy (stracone bramki/mecz)
            away_defense: Siła obrony gości (stracone bramki/mecz)
            league_avg_goals: Średnia bramek w lidze (domyślnie 2.7 dla top lig)

        Returns:
            Tuple: (p_home_win, p_draw, p_away_win)
        """
        # Jeśli nie podano obrony, używamy ataku jako przybliżenia
        if home_defense is None:
            home_defense = league_avg_goals - home_attack + league_avg_goals / 2
        if away_defense is None:
            away_defense = league_avg_goals - away_attack + league_avg_goals / 2

        # Oblicz oczekiwane bramki (Lambda)
        # Lambda = Atak drużyny * Obrona przeciwnika / Średnia ligowa
        home_expected_goals = (home_attack * away_defense) / (league_avg_goals / 2)
        away_expected_goals = (away_attack * home_defense) / (league_avg_goals / 2)

        # Ogranicz do rozsądnych wartości
        home_expected_goals = max(0.1, min(home_expected_goals, 5.0))
        away_expected_goals = max(0.1, min(away_expected_goals, 5.0))

        return self._calculate_from_expected_goals(home_expected_goals, away_expected_goals)

    def calculate_from_expected_goals(
        self,
        home_xg: float,
        away_xg: float
    ) -> Tuple[float, float, float]:
        """
        Uproszczona wersja - oblicza prawdopodobieństwa bezpośrednio z xG

        Args:
            home_xg: Oczekiwane bramki gospodarzy
            away_xg: Oczekiwane bramki gości

        Returns:
            Tuple: (p_home_win, p_draw, p_away_win)
        """
        return self._calculate_from_expected_goals(home_xg, away_xg)

    def _calculate_from_expected_goals(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Tuple[float, float, float]:
        """
        Wewnętrzna metoda obliczająca prawdopodobieństwa z parametrów lambda

        Buduje macierz prawdopodobieństw dla wyników od 0:0 do max_goals:max_goals
        """
        # Oblicz prawdopodobieństwa dla pojedynczych wyników
        home_probs = np.array([
            poisson.pmf(i, lambda_home) for i in range(self.max_goals + 1)
        ])
        away_probs = np.array([
            poisson.pmf(i, lambda_away) for i in range(self.max_goals + 1)
        ])

        # Utwórz macierz prawdopodobieństw (outer product)
        score_matrix = np.outer(home_probs, away_probs)

        # Sumuj prawdopodobieństwa dla każdego wyniku
        p_home_win = 0.0
        p_draw = 0.0
        p_away_win = 0.0

        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                prob = score_matrix[home_goals, away_goals]

                if home_goals > away_goals:
                    p_home_win += prob
                elif home_goals == away_goals:
                    p_draw += prob
                else:
                    p_away_win += prob

        # Normalizacja (na wypadek błędów zaokrągleń)
        total = p_home_win + p_draw + p_away_win
        return (
            p_home_win / total,
            p_draw / total,
            p_away_win / total
        )

    def get_score_probabilities(
        self,
        lambda_home: float,
        lambda_away: float,
        top_n: int = 10
    ) -> Dict[Tuple[int, int], float]:
        """
        Zwraca najczęstsze wyniki z prawdopodobieństwami

        Args:
            lambda_home: Oczekiwane bramki gospodarzy
            lambda_away: Oczekiwane bramki gości
            top_n: Liczba najczęstszych wyników do zwrócenia

        Returns:
            Dict: {(home_score, away_score): probability}
        """
        home_probs = np.array([
            poisson.pmf(i, lambda_home) for i in range(self.max_goals + 1)
        ])
        away_probs = np.array([
            poisson.pmf(i, lambda_away) for i in range(self.max_goals + 1)
        ])

        score_matrix = np.outer(home_probs, away_probs)

        # Utwórz listę (wynik, prawdopodobieństwo)
        scores = []
        for h in range(self.max_goals + 1):
            for a in range(self.max_goals + 1):
                scores.append(((h, a), score_matrix[h, a]))

        # Posortuj po prawdopodobieństwie
        scores.sort(key=lambda x: x[1], reverse=True)

        return dict(scores[:top_n])

    def calculate_over_under_probability(
        self,
        lambda_home: float,
        lambda_away: float,
        threshold: float = 2.5
    ) -> Tuple[float, float]:
        """
        Oblicza prawdopodobieństwo Over/Under dla zadanej linii

        Args:
            lambda_home: Oczekiwane bramki gospodarzy
            lambda_away: Oczekiwane bramki gości
            threshold: Linia Over/Under (np. 2.5)

        Returns:
            Tuple: (p_over, p_under)
        """
        total_lambda = lambda_home + lambda_away

        # P(X > threshold) = 1 - P(X <= threshold)
        # Dla 2.5 to oznacza P(X >= 3)
        p_under = poisson.cdf(int(threshold), total_lambda)
        p_over = 1 - p_under

        return (p_over, p_under)
