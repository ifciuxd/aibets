"""
Advanced Risk Analysis Module
Calculates Risk of Ruin (ROR) and Confidence Scores
"""

import math
from typing import Tuple, Dict
from datetime import datetime, timedelta


class RiskAnalyzer:
    """
    Advanced risk metrics calculator

    Calculates:
    1. Risk of Ruin (ROR) - probability of losing 50% of bankroll
    2. Confidence Score (CS) - data quality metric (0-100)
    3. Sharpe Ratio - risk-adjusted return
    """

    @staticmethod
    def calculate_risk_of_ruin(
        win_probability: float,
        avg_odds: float,
        kelly_fraction: float,
        bankroll: float,
        ruin_threshold: float = 0.50
    ) -> float:
        """
        Calculate Risk of Ruin using actuarial formula

        ROR = ((1-p)/(p*b))^(K/(1-K))

        gdzie:
        - p = średnie prawdopodobieństwo wygranej
        - b = średnie net odds (odds - 1)
        - K = Kelly fraction
        - ruin_threshold = % kapitału do utraty (default 50% = 0.50)

        Args:
            win_probability: Average win probability across portfolio
            avg_odds: Average odds across portfolio
            kelly_fraction: Kelly fraction used (0.0-1.0)
            bankroll: Current bankroll
            ruin_threshold: Threshold for ruin (0.5 = 50% loss)

        Returns:
            float: Risk of Ruin percentage (0-100)
        """
        if win_probability <= 0 or win_probability >= 1:
            return 100.0  # Invalid probability

        if avg_odds <= 1.0:
            return 100.0  # Invalid odds

        if kelly_fraction <= 0:
            return 0.0  # No risk if not betting

        # Net odds (what you win per unit bet)
        net_odds = avg_odds - 1

        # Expected value (should be > 1 for value bets)
        ev = win_probability * avg_odds

        if ev <= 1.0:
            return 100.0  # No edge = certain ruin

        # Lose probability
        q = 1 - win_probability

        # Calculate ROR using the formula
        # ROR = ((q/p) / net_odds)^(K/(1-K) * ruin_threshold)
        try:
            loss_to_win_ratio = q / win_probability
            edge_ratio = loss_to_win_ratio / net_odds

            # Adjust for ruin threshold and Kelly fraction
            # Higher Kelly = higher ROR
            # More aggressive ruin threshold (e.g., 75% = 0.75) = lower ROR
            exponent = (kelly_fraction / (1 - kelly_fraction)) * ruin_threshold

            ror = math.pow(edge_ratio, exponent)

            # Convert to percentage and cap at 100%
            ror_percent = min(ror * 100, 100.0)

            # Additional penalty for high Kelly fractions (>0.5)
            if kelly_fraction > 0.5:
                penalty = (kelly_fraction - 0.5) * 100
                ror_percent = min(ror_percent + penalty, 100.0)

            return round(ror_percent, 2)

        except (ValueError, ZeroDivisionError, OverflowError):
            return 100.0

    @staticmethod
    def calculate_confidence_score(
        has_xg: bool,
        xg_age_hours: float = 0,
        has_form: bool = False,
        has_h2h: bool = False,
        data_completeness: float = 1.0,
        odds_age_hours: float = 0
    ) -> Tuple[int, str]:
        """
        Calculate Confidence Score (CS) based on data quality

        Scoring system (0-100):
        - xG data present: +40 points
        - xG data fresh (<24h): +10 points
        - Form data: +15 points
        - H2H data: +15 points
        - Data completeness (0-1): +20 points
        - Odds fresh (<1h): +10 points

        Args:
            has_xg: Whether xG data is available
            xg_age_hours: Age of xG data in hours
            has_form: Whether form data (WWDLW) is available
            has_h2h: Whether head-to-head history is available
            data_completeness: Overall data completeness (0.0-1.0)
            odds_age_hours: Age of odds data in hours

        Returns:
            Tuple[int, str]: (confidence_score, reason)
        """
        score = 0
        reasons = []

        # xG data (40 points max)
        if has_xg:
            score += 40
            reasons.append("xG available")

            # Freshness bonus
            if xg_age_hours < 24:
                score += 10
                reasons.append("xG fresh (<24h)")
            elif xg_age_hours < 72:
                score += 5
                reasons.append("xG recent (<72h)")
        else:
            reasons.append("No xG (estimated)")

        # Form data (15 points)
        if has_form:
            score += 15
            reasons.append("Form data")

        # H2H data (15 points)
        if has_h2h:
            score += 15
            reasons.append("H2H history")

        # Data completeness (20 points)
        completeness_score = int(data_completeness * 20)
        score += completeness_score
        if completeness_score >= 15:
            reasons.append("Complete data")
        else:
            reasons.append("Partial data")

        # Odds freshness (10 points)
        if odds_age_hours < 1:
            score += 10
            reasons.append("Live odds")
        elif odds_age_hours < 6:
            score += 5
            reasons.append("Recent odds")

        # Cap at 100
        score = min(score, 100)

        # Generate reason string
        reason_str = ", ".join(reasons[:3])  # Top 3 reasons

        return score, reason_str

    @staticmethod
    def get_risk_category(ror: float) -> Dict[str, str]:
        """
        Categorize Risk of Ruin into user-friendly categories

        Args:
            ror: Risk of Ruin percentage

        Returns:
            Dict with 'level', 'color', 'message'
        """
        if ror < 1.0:
            return {
                'level': 'VERY LOW',
                'color': 'success',
                'message': 'Bardzo bezpieczne ustawienia'
            }
        elif ror < 5.0:
            return {
                'level': 'LOW',
                'color': 'success',
                'message': 'Bezpieczne ustawienia'
            }
        elif ror < 15.0:
            return {
                'level': 'MODERATE',
                'color': 'warning',
                'message': 'Umiarkowane ryzyko - zalecane dla doświadczonych'
            }
        elif ror < 30.0:
            return {
                'level': 'HIGH',
                'color': 'error',
                'message': 'Wysokie ryzyko - zmniejsz Kelly Fraction'
            }
        else:
            return {
                'level': 'EXTREME',
                'color': 'error',
                'message': 'NIEBEZPIECZNIE! Natychmiast zmniejsz stawki'
            }

    @staticmethod
    def calculate_sharpe_ratio(
        expected_return: float,
        std_deviation: float,
        risk_free_rate: float = 0.05
    ) -> float:
        """
        Calculate Sharpe Ratio (risk-adjusted return)

        Sharpe = (Expected Return - Risk Free Rate) / Standard Deviation

        Args:
            expected_return: Expected return (%)
            std_deviation: Standard deviation of returns (%)
            risk_free_rate: Risk-free rate (default 5% = 0.05)

        Returns:
            float: Sharpe Ratio
        """
        if std_deviation == 0:
            return 0.0

        sharpe = (expected_return - risk_free_rate) / std_deviation
        return round(sharpe, 2)

    @staticmethod
    def suggest_optimal_kelly_fraction(
        current_ror: float,
        target_ror: float = 5.0,
        current_kelly: float = 0.25
    ) -> float:
        """
        Suggest optimal Kelly fraction based on target ROR

        Args:
            current_ror: Current Risk of Ruin (%)
            target_ror: Target Risk of Ruin (%)
            current_kelly: Current Kelly fraction

        Returns:
            float: Suggested Kelly fraction
        """
        if current_ror <= target_ror:
            return current_kelly  # Already safe

        # Simple adjustment: reduce Kelly proportionally
        adjustment_factor = math.sqrt(target_ror / current_ror)
        suggested_kelly = current_kelly * adjustment_factor

        # Cap between 0.05 and 0.50
        suggested_kelly = max(0.05, min(suggested_kelly, 0.50))

        return round(suggested_kelly, 2)
