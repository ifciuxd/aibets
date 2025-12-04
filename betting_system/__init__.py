"""
Betting System - Prophet-70
System analizy kuponów bukmacherskich oparty na modelu Poissona i kryterium Kelly'ego
"""

__version__ = "1.0.0"
__author__ = "AI Betting System"

from .prophet_system import ProphetSystem
from .data_models import Match, BettingDecision, TeamStats

__all__ = [
    'ProphetSystem',
    'Match',
    'BettingDecision',
    'TeamStats',
]
