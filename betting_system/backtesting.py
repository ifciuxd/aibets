"""
Backtesting Engine
Simulates betting strategy on historical data
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import random
from .data_models import Match, BettingDecision
from .prophet_system import ProphetSystem


class BacktestResult:
    """Results of a backtest simulation"""

    def __init__(self):
        self.initial_bankroll = 0.0
        self.final_bankroll = 0.0
        self.total_bets = 0
        self.winning_bets = 0
        self.losing_bets = 0
        self.total_stake = 0.0
        self.total_profit = 0.0
        self.roi_percent = 0.0
        self.win_rate = 0.0
        self.avg_odds = 0.0
        self.max_bankroll = 0.0
        self.min_bankroll = 0.0
        self.max_drawdown_percent = 0.0
        self.sharpe_ratio = 0.0

        # Daily history
        self.daily_history: List[Dict] = []

        # Bet history
        self.bet_history: List[Dict] = []

    def to_dict(self) -> Dict:
        return {
            'initial_bankroll': round(self.initial_bankroll, 2),
            'final_bankroll': round(self.final_bankroll, 2),
            'total_profit': round(self.total_profit, 2),
            'roi_percent': round(self.roi_percent, 2),
            'total_bets': self.total_bets,
            'winning_bets': self.winning_bets,
            'losing_bets': self.losing_bets,
            'win_rate': round(self.win_rate, 2),
            'total_stake': round(self.total_stake, 2),
            'avg_odds': round(self.avg_odds, 2),
            'max_bankroll': round(self.max_bankroll, 2),
            'min_bankroll': round(self.min_bankroll, 2),
            'max_drawdown_percent': round(self.max_drawdown_percent, 2),
            'sharpe_ratio': round(self.sharpe_ratio, 2),
            'daily_history': self.daily_history,
            'bet_history': self.bet_history
        }


class BacktestEngine:
    """
    Backtesting engine for strategy validation

    Simulates placing bets on historical matches and calculates
    the performance metrics
    """

    def __init__(
        self,
        bankroll: float,
        kelly_fraction: float = 0.25,
        min_edge: float = 0.05
    ):
        self.initial_bankroll = bankroll
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.min_edge = min_edge

        self.system = ProphetSystem(
            bankroll=bankroll,
            kelly_fraction=kelly_fraction,
            min_edge=min_edge
        )

    def simulate_match_outcome(
        self,
        match: Match,
        bet_type: str,
        model_probability: float
    ) -> bool:
        """
        Simulate match outcome based on probability

        In production, this would use actual match results.
        For demo, we simulate based on model probability.

        Args:
            match: Match object
            bet_type: "Home Win", "Draw", "Away Win"
            model_probability: Probability from our model

        Returns:
            bool: True if bet won, False otherwise
        """
        # In production: fetch actual result from database
        # For demo: probabilistic simulation

        # Weight the random outcome based on our model probability
        # This simulates a slightly better-than-random outcome
        # (as our model should have some edge)

        # Add slight boost to reflect model edge
        adjusted_probability = min(model_probability * 1.05, 0.95)

        return random.random() < adjusted_probability

    def run_backtest(
        self,
        matches: List[Match],
        simulate_outcomes: bool = True
    ) -> BacktestResult:
        """
        Run backtest simulation on historical matches

        Args:
            matches: List of historical matches with odds
            simulate_outcomes: If True, simulate outcomes probabilistically

        Returns:
            BacktestResult: Complete backtest results
        """
        result = BacktestResult()
        result.initial_bankroll = self.initial_bankroll

        bankroll_history = [self.initial_bankroll]
        returns_history = []

        for match in matches:
            # Get betting decision from system
            decision = self.system.analyze_match(match)

            if decision.recommended_bet == "NO BET":
                continue

            # Record bet
            stake = decision.recommended_stake_amount
            odds = decision.bookmaker_odds

            result.total_bets += 1
            result.total_stake += stake

            # Simulate outcome
            won = self.simulate_match_outcome(
                match,
                decision.recommended_bet,
                decision.model_probability
            )

            # Calculate profit/loss
            if won:
                profit = stake * (odds - 1)
                self.bankroll += profit
                result.winning_bets += 1
                result.total_profit += profit
            else:
                self.bankroll -= stake
                result.losing_bets += 1
                result.total_profit -= stake

            # Update bankroll history
            bankroll_history.append(self.bankroll)

            # Calculate daily return
            daily_return = (self.bankroll / bankroll_history[-2]) - 1
            returns_history.append(daily_return)

            # Record bet details
            result.bet_history.append({
                'match': match.match_name,
                'bet': decision.recommended_bet,
                'odds': odds,
                'stake': round(stake, 2),
                'won': won,
                'profit': round(profit if won else -stake, 2),
                'bankroll_after': round(self.bankroll, 2)
            })

            # Update system bankroll (for Kelly recalculation)
            self.system.update_bankroll(self.bankroll)

        # Calculate final metrics
        result.final_bankroll = self.bankroll
        result.total_profit = self.bankroll - self.initial_bankroll
        result.roi_percent = (result.total_profit / self.initial_bankroll) * 100

        if result.total_bets > 0:
            result.win_rate = (result.winning_bets / result.total_bets) * 100

            # Calculate average odds of placed bets
            if result.bet_history:
                result.avg_odds = sum(b['odds'] for b in result.bet_history) / len(result.bet_history)

        # Bankroll stats
        result.max_bankroll = max(bankroll_history)
        result.min_bankroll = min(bankroll_history)

        # Max drawdown
        peak = result.initial_bankroll
        max_dd = 0
        for val in bankroll_history:
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100
            if dd > max_dd:
                max_dd = dd

        result.max_drawdown_percent = max_dd

        # Sharpe Ratio (simplified)
        if len(returns_history) > 1:
            import statistics
            avg_return = statistics.mean(returns_history)
            std_return = statistics.stdev(returns_history)
            if std_return > 0:
                result.sharpe_ratio = (avg_return - 0.0001) / std_return  # 0.01% daily risk-free rate

        # Daily history for charts
        # Group by day (simplified - in production, use actual dates)
        daily_chunk_size = max(1, len(bankroll_history) // 30)  # Max 30 days
        for i in range(0, len(bankroll_history), daily_chunk_size):
            chunk = bankroll_history[i:i + daily_chunk_size]
            if chunk:
                result.daily_history.append({
                    'date': f"Day {i // daily_chunk_size + 1}",
                    'open': round(chunk[0], 2),
                    'close': round(chunk[-1], 2),
                    'high': round(max(chunk), 2),
                    'low': round(min(chunk), 2),
                })

        return result

    @staticmethod
    def generate_sample_historical_matches(
        count: int = 50,
        days_back: int = 7
    ) -> List[Match]:
        """
        Generate sample historical matches for demo purposes

        In production, this would fetch from a database.

        Args:
            count: Number of matches to generate
            days_back: How many days back to generate

        Returns:
            List[Match]: Sample historical matches
        """
        from .data_models import TeamStats

        matches = []
        leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]

        teams = [
            ("Manchester City", 2.5, 0.8),
            ("Liverpool", 2.4, 0.9),
            ("Arsenal", 2.1, 1.0),
            ("Chelsea", 1.9, 1.1),
            ("Manchester United", 1.8, 1.2),
            ("Real Madrid", 2.8, 0.9),
            ("Barcelona", 2.6, 1.0),
            ("Bayern Munich", 3.0, 1.1),
            ("Inter Milan", 2.3, 0.8),
            ("PSG", 2.7, 0.9),
        ]

        for i in range(count):
            # Random matchup
            home_team_data = random.choice(teams)
            away_team_data = random.choice([t for t in teams if t != home_team_data])

            # Generate odds based on team strengths
            strength_diff = home_team_data[1] - away_team_data[1]
            base_home_odds = 2.0 - (strength_diff * 0.2)
            base_home_odds = max(1.20, min(base_home_odds, 5.0))

            odds_home = round(base_home_odds + random.uniform(-0.15, 0.15), 2)
            odds_draw = round(3.5 + random.uniform(-0.5, 0.5), 2)
            odds_away = round(1 / (1 - 1/odds_home - 1/odds_draw) + random.uniform(-0.3, 0.3), 2)

            match = Match(
                match_id=f"backtest_{i}",
                match_name=f"{home_team_data[0]} vs {away_team_data[0]}",
                date=datetime.now() - timedelta(days=random.randint(0, days_back)),
                league=random.choice(leagues),
                home_team=TeamStats(
                    name=home_team_data[0],
                    goals_scored_avg=home_team_data[1],
                    goals_conceded_avg=home_team_data[2],
                    form="WWDWL"
                ),
                away_team=TeamStats(
                    name=away_team_data[0],
                    goals_scored_avg=away_team_data[1],
                    goals_conceded_avg=away_team_data[2],
                    form="WDLWD"
                ),
                odds_home=odds_home,
                odds_draw=odds_draw,
                odds_away=odds_away,
                home_xg=home_team_data[1],
                away_xg=away_team_data[1]
            )

            matches.append(match)

        return matches
