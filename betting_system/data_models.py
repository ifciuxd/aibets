"""
Modele danych dla systemu bukmacherskiego
Używamy Pydantic do walidacji i type safety
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TeamStats(BaseModel):
    """Statystyki drużyny"""
    name: str
    goals_scored_avg: float = Field(
        ...,
        description="Średnia strzelonych bramek (ostatnie 5-10 meczów)",
        ge=0.0
    )
    goals_conceded_avg: float = Field(
        ...,
        description="Średnia straconych bramek (ostatnie 5-10 meczów)",
        ge=0.0
    )
    form: Optional[str] = Field(
        None,
        description="Forma drużyny, np. 'WWDLW'",
        max_length=10
    )

    @validator('goals_scored_avg', 'goals_conceded_avg')
    def validate_reasonable_goals(cls, v):
        if v > 10.0:
            raise ValueError("Średnia bramek wygląda podejrzanie wysoka (>10)")
        return v


class Match(BaseModel):
    """Reprezentacja meczu z danymi do analizy"""
    match_id: Optional[str] = None
    match_name: str = Field(..., description="Nazwa meczu, np. 'Real Madrid vs Barcelona'")
    date: Optional[datetime] = None
    league: Optional[str] = None

    # Statystyki drużyn
    home_team: TeamStats
    away_team: TeamStats

    # Kursy bukmacherskie
    odds_home: float = Field(..., description="Kurs na wygraną gospodarzy", gt=1.0)
    odds_draw: float = Field(..., description="Kurs na remis", gt=1.0)
    odds_away: float = Field(..., description="Kurs na wygraną gości", gt=1.0)

    # Opcjonalne: oczekiwane bramki (xG) z zaawansowanych modeli
    home_xg: Optional[float] = Field(None, description="Expected Goals gospodarzy", ge=0.0)
    away_xg: Optional[float] = Field(None, description="Expected Goals gości", ge=0.0)

    @validator('odds_home', 'odds_draw', 'odds_away')
    def validate_odds(cls, v):
        if v > 100.0:
            raise ValueError("Kurs wydaje się nierealistyczny (>100)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "match_name": "Manchester City vs Arsenal",
                "home_team": {
                    "name": "Manchester City",
                    "goals_scored_avg": 2.5,
                    "goals_conceded_avg": 0.8
                },
                "away_team": {
                    "name": "Arsenal",
                    "goals_scored_avg": 1.8,
                    "goals_conceded_avg": 1.2
                },
                "odds_home": 1.65,
                "odds_draw": 4.20,
                "odds_away": 5.50
            }
        }


class BettingDecision(BaseModel):
    """Decyzja zakładowa wygenerowana przez system"""
    match_name: str
    recommended_bet: Literal["Home Win", "Draw", "Away Win", "NO BET"]

    # Prawdopodobieństwa
    model_probability: float = Field(..., description="Prawdopodobieństwo wg modelu", ge=0.0, le=1.0)
    implied_probability: float = Field(..., description="Prawdopodobieństwo z kursu", ge=0.0, le=1.0)

    # Value
    edge_percentage: float = Field(..., description="Przewaga w %")
    expected_value: float = Field(..., description="Expected Value (EV)")

    # Stake
    bookmaker_odds: float
    recommended_stake_pct: float = Field(..., description="% bankrolla do postawienia", ge=0.0, le=1.0)
    recommended_stake_amount: Optional[float] = Field(None, description="Kwota do postawienia")

    # Metadata
    confidence_level: Literal["LOW", "MEDIUM", "HIGH", "VERY HIGH"] = "MEDIUM"
    reason: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "match_name": "Real Madrid vs Barcelona",
                "recommended_bet": "Home Win",
                "model_probability": 0.58,
                "implied_probability": 0.51,
                "edge_percentage": 7.0,
                "expected_value": 1.14,
                "bookmaker_odds": 1.95,
                "recommended_stake_pct": 0.035,
                "recommended_stake_amount": 350.0,
                "confidence_level": "HIGH"
            }
        }
