"""
AlphaBet Platform - FastAPI Backend
Production-ready API with validation, optimization, and error handling
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import os
import time

# Dodaj ścieżkę do modułu betting_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from betting_system import ProphetSystem
from betting_system.data_models import Match, TeamStats, BettingDecision
from betting_system.poisson_model import PoissonFootballModel
from betting_system.kelly_criterion import KellyCriterion
from betting_system.risk_analysis import RiskAnalyzer
from betting_system.backtesting import BacktestEngine

# Initialize FastAPI
app = FastAPI(
    title="AlphaBet API",
    description="Professional Betting Analysis Platform powered by PROPHET-70",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware - GZIP compression for optimization
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware for performance monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================================================
# REQUEST/RESPONSE MODELS with Enhanced Validation
# ============================================================================

class TeamStatsInput(BaseModel):
    """Validated team statistics input"""
    name: str = Field(..., min_length=2, max_length=100)
    goals_scored_avg: float = Field(..., ge=0.0, le=10.0, description="Average goals scored per match")
    goals_conceded_avg: float = Field(..., ge=0.0, le=10.0, description="Average goals conceded per match")
    form: Optional[str] = Field(None, regex="^[WDL]{0,10}$", description="Recent form (e.g., WWDLW)")

    @validator('goals_scored_avg', 'goals_conceded_avg')
    def validate_reasonable_goals(cls, v):
        if v > 6.0:
            raise ValueError("Goals average > 6.0 seems unrealistic")
        return v


class MatchInput(BaseModel):
    """Validated match input with strict validation"""
    match_id: Optional[str] = None
    match_name: str = Field(..., min_length=5, max_length=200)
    date: Optional[datetime] = None
    league: Optional[str] = Field(None, max_length=100)

    home_team: TeamStatsInput
    away_team: TeamStatsInput

    # Odds validation - must be > 1.0 and < 100.0 (realistic)
    odds_home: float = Field(..., gt=1.0, lt=100.0, description="Home win odds")
    odds_draw: float = Field(..., gt=1.0, lt=100.0, description="Draw odds")
    odds_away: float = Field(..., gt=1.0, lt=100.0, description="Away win odds")

    # Optional xG
    home_xg: Optional[float] = Field(None, ge=0.0, le=6.0)
    away_xg: Optional[float] = Field(None, ge=0.0, le=6.0)

    @validator('odds_home', 'odds_draw', 'odds_away')
    def validate_odds_reasonable(cls, v):
        if v > 50.0:
            raise ValueError("Odds > 50.0 seem unrealistic")
        return v

    class Config:
        schema_extra = {
            "example": {
                "match_name": "Manchester City vs Arsenal",
                "league": "Premier League",
                "home_team": {
                    "name": "Manchester City",
                    "goals_scored_avg": 2.5,
                    "goals_conceded_avg": 0.8,
                    "form": "WWWDW"
                },
                "away_team": {
                    "name": "Arsenal",
                    "goals_scored_avg": 2.1,
                    "goals_conceded_avg": 1.0,
                    "form": "WWDWL"
                },
                "odds_home": 1.65,
                "odds_draw": 4.20,
                "odds_away": 5.50,
                "home_xg": 2.3,
                "away_xg": 1.1
            }
        }


class AnalysisRequest(BaseModel):
    """Request to analyze multiple matches"""
    matches: List[MatchInput] = Field(..., min_items=1, max_items=50)
    bankroll: float = Field(10000.0, ge=100.0, le=1000000.0, description="Available bankroll")
    kelly_fraction: float = Field(0.25, gt=0.0, le=1.0, description="Kelly fraction (0.25 = Quarter Kelly)")
    min_edge: float = Field(0.05, ge=0.0, le=0.5, description="Minimum edge threshold")
    min_probability: float = Field(0.35, ge=0.1, le=0.9)
    max_probability: float = Field(0.75, ge=0.5, le=0.99)

    @validator('matches')
    def validate_not_too_many(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 matches per request")
        return v

    class Config:
        schema_extra = {
            "example": {
                "matches": [],  # Array of MatchInput
                "bankroll": 10000.0,
                "kelly_fraction": 0.25,
                "min_edge": 0.05
            }
        }


class BettingDecisionResponse(BaseModel):
    """Enhanced betting decision response"""
    match_name: str
    recommended_bet: str
    model_probability: float
    implied_probability: float
    edge_percentage: float
    expected_value: float
    bookmaker_odds: float
    recommended_stake_pct: float
    recommended_stake_amount: float
    confidence_level: str
    reason: Optional[str]

    # Additional metadata for frontend
    match_id: Optional[str] = None
    league: Optional[str] = None
    date: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    """Complete analysis response with metadata"""
    success: bool
    timestamp: datetime
    processing_time_ms: float

    # Results
    total_matches_analyzed: int
    value_bets_found: int
    recommendations: List[BettingDecisionResponse]

    # Portfolio summary
    portfolio_summary: Dict[str, Any]

    # Metadata
    settings: Dict[str, float]


class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = False
    error: str
    error_code: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    uptime_seconds: float


# ============================================================================
# GLOBAL STATE
# ============================================================================

# Track startup time for health check
_startup_time = time.time()


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "AlphaBet API - Professional Betting Analysis Platform",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        uptime_seconds=time.time() - _startup_time
    )


@app.post("/api/analyze-matches", response_model=AnalysisResponse)
async def analyze_matches(request: AnalysisRequest):
    """
    Analyze multiple matches and return value betting recommendations

    This is the main endpoint for the AlphaBet platform.
    It accepts a list of matches with odds and statistics, then:
    1. Calculates probabilities using Poisson model
    2. Identifies value bets
    3. Calculates optimal stakes using Kelly Criterion
    4. Returns ranked recommendations
    """
    start_time = time.time()

    try:
        # Initialize Prophet system with user settings
        system = ProphetSystem(
            bankroll=request.bankroll,
            kelly_fraction=request.kelly_fraction,
            min_edge=request.min_edge,
            min_probability=request.min_probability,
            max_probability=request.max_probability
        )

        # Convert input matches to internal Match objects
        matches = []
        for match_input in request.matches:
            match = Match(
                match_id=match_input.match_id,
                match_name=match_input.match_name,
                date=match_input.date,
                league=match_input.league,
                home_team=TeamStats(**match_input.home_team.dict()),
                away_team=TeamStats(**match_input.away_team.dict()),
                odds_home=match_input.odds_home,
                odds_draw=match_input.odds_draw,
                odds_away=match_input.odds_away,
                home_xg=match_input.home_xg,
                away_xg=match_input.away_xg
            )
            matches.append(match)

        # Analyze all matches
        results_df = system.analyze_matches(matches)

        # Convert to response format
        recommendations = []
        if not results_df.empty:
            for _, row in results_df.iterrows():
                # Find original match for metadata
                original_match = next(
                    (m for m in request.matches if m.match_name == row['match_name']),
                    None
                )

                rec = BettingDecisionResponse(
                    match_name=row['match_name'],
                    recommended_bet=row['recommended_bet'],
                    model_probability=row['model_probability'],
                    implied_probability=row['implied_probability'],
                    edge_percentage=row['edge_percentage'],
                    expected_value=row['expected_value'],
                    bookmaker_odds=row['bookmaker_odds'],
                    recommended_stake_pct=row['recommended_stake_pct'],
                    recommended_stake_amount=row['recommended_stake_amount'],
                    confidence_level=row['confidence_level'],
                    reason=row.get('reason'),
                    match_id=original_match.match_id if original_match else None,
                    league=original_match.league if original_match else None,
                    date=original_match.date if original_match else None
                )
                recommendations.append(rec)

        # Get portfolio summary
        portfolio = system.get_portfolio_summary()

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        return AnalysisResponse(
            success=True,
            timestamp=datetime.utcnow(),
            processing_time_ms=round(processing_time, 2),
            total_matches_analyzed=len(request.matches),
            value_bets_found=len(recommendations),
            recommendations=recommendations,
            portfolio_summary=portfolio,
            settings={
                "bankroll": request.bankroll,
                "kelly_fraction": request.kelly_fraction,
                "min_edge": request.min_edge,
                "min_probability": request.min_probability,
                "max_probability": request.max_probability
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/analyze-single", response_model=BettingDecisionResponse)
async def analyze_single_match(match_input: MatchInput,
                               bankroll: float = 10000.0,
                               kelly_fraction: float = 0.25):
    """
    Analyze a single match
    Convenience endpoint for analyzing one match at a time
    """
    try:
        system = ProphetSystem(
            bankroll=bankroll,
            kelly_fraction=kelly_fraction
        )

        match = Match(
            match_id=match_input.match_id,
            match_name=match_input.match_name,
            date=match_input.date,
            league=match_input.league,
            home_team=TeamStats(**match_input.home_team.dict()),
            away_team=TeamStats(**match_input.away_team.dict()),
            odds_home=match_input.odds_home,
            odds_draw=match_input.odds_draw,
            odds_away=match_input.odds_away,
            home_xg=match_input.home_xg,
            away_xg=match_input.away_xg
        )

        decision = system.analyze_match(match)

        return BettingDecisionResponse(
            match_name=decision.match_name,
            recommended_bet=decision.recommended_bet,
            model_probability=decision.model_probability,
            implied_probability=decision.implied_probability,
            edge_percentage=decision.edge_percentage,
            expected_value=decision.expected_value,
            bookmaker_odds=decision.bookmaker_odds,
            recommended_stake_pct=decision.recommended_stake_pct,
            recommended_stake_amount=decision.recommended_stake_amount,
            confidence_level=decision.confidence_level,
            reason=decision.reason,
            match_id=match_input.match_id,
            league=match_input.league,
            date=match_input.date
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/poisson-analysis")
async def poisson_analysis(home_xg: float, away_xg: float):
    """
    Get detailed Poisson analysis for given xG values
    Returns probabilities and most likely scores
    """
    try:
        if not (0 <= home_xg <= 6) or not (0 <= away_xg <= 6):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="xG values must be between 0 and 6"
            )

        model = PoissonFootballModel()

        # Calculate probabilities
        p_home, p_draw, p_away = model.calculate_from_expected_goals(home_xg, away_xg)

        # Get top scores
        scores = model.get_score_probabilities(home_xg, away_xg, top_n=10)

        # Over/Under
        p_over_25, p_under_25 = model.calculate_over_under_probability(
            home_xg, away_xg, threshold=2.5
        )

        return {
            "success": True,
            "input": {"home_xg": home_xg, "away_xg": away_xg},
            "probabilities": {
                "home_win": round(p_home, 4),
                "draw": round(p_draw, 4),
                "away_win": round(p_away, 4)
            },
            "top_scores": [
                {"score": f"{h}:{a}", "probability": round(prob, 4)}
                for (h, a), prob in scores.items()
            ],
            "over_under_2_5": {
                "over": round(p_over_25, 4),
                "under": round(p_under_25, 4)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/calculate-ror")
async def calculate_risk_of_ruin(
    win_probability: float,
    avg_odds: float,
    kelly_fraction: float,
    bankroll: float,
    ruin_threshold: float = 0.50
):
    """
    Calculate Risk of Ruin (ROR)

    Returns the probability of losing a percentage of your bankroll
    given your betting parameters.

    Args:
        win_probability: Average win probability (0.0-1.0)
        avg_odds: Average odds of your bets
        kelly_fraction: Kelly fraction you're using (0.0-1.0)
        bankroll: Your current bankroll
        ruin_threshold: Threshold for "ruin" (default 0.50 = 50% loss)

    Returns:
        Dict with ROR percentage, risk category, and suggested adjustments
    """
    try:
        # Validate inputs
        if not (0 < win_probability < 1):
            raise HTTPException(400, "win_probability must be between 0 and 1")
        if avg_odds <= 1.0:
            raise HTTPException(400, "avg_odds must be > 1.0")
        if not (0 < kelly_fraction <= 1):
            raise HTTPException(400, "kelly_fraction must be between 0 and 1")

        analyzer = RiskAnalyzer()

        # Calculate ROR
        ror = analyzer.calculate_risk_of_ruin(
            win_probability,
            avg_odds,
            kelly_fraction,
            bankroll,
            ruin_threshold
        )

        # Get risk category
        risk_category = analyzer.get_risk_category(ror)

        # Suggest optimal Kelly if ROR is high
        suggested_kelly = None
        if ror > 10.0:
            suggested_kelly = analyzer.suggest_optimal_kelly_fraction(
                current_ror=ror,
                target_ror=5.0,
                current_kelly=kelly_fraction
            )

        return {
            "success": True,
            "risk_of_ruin_percent": round(ror, 2),
            "ruin_threshold": ruin_threshold,
            "risk_category": risk_category,
            "suggested_kelly_fraction": suggested_kelly,
            "current_settings": {
                "win_probability": win_probability,
                "avg_odds": avg_odds,
                "kelly_fraction": kelly_fraction,
                "bankroll": bankroll
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error calculating ROR: {str(e)}")


@app.get("/api/confidence-score")
async def calculate_confidence_score(
    has_xg: bool = False,
    xg_age_hours: float = 0,
    has_form: bool = False,
    has_h2h: bool = False,
    data_completeness: float = 1.0,
    odds_age_hours: float = 0
):
    """
    Calculate Confidence Score for a prediction

    Confidence Score (0-100) indicates the quality of data used
    for a prediction. Higher scores mean more reliable data.

    Args:
        has_xg: Whether xG data is available
        xg_age_hours: Age of xG data in hours
        has_form: Whether recent form data is available
        has_h2h: Whether head-to-head history is available
        data_completeness: Overall data completeness (0.0-1.0)
        odds_age_hours: Age of odds data in hours

    Returns:
        Dict with confidence score and explanation
    """
    try:
        analyzer = RiskAnalyzer()

        score, reason = analyzer.calculate_confidence_score(
            has_xg=has_xg,
            xg_age_hours=xg_age_hours,
            has_form=has_form,
            has_h2h=has_h2h,
            data_completeness=data_completeness,
            odds_age_hours=odds_age_hours
        )

        # Determine warning level
        if score >= 80:
            level = "HIGH"
            message = "Wysokiej jakości dane - duże zaufanie"
        elif score >= 60:
            level = "MEDIUM"
            message = "Dobra jakość danych - umiarkowane zaufanie"
        elif score >= 40:
            level = "LOW"
            message = "Ograniczone dane - ostrożność zalecana"
        else:
            level = "VERY LOW"
            message = "Słabe dane - wysokie ryzyko błędu"

        # Kelly adjustment recommendation
        kelly_multiplier = 1.0
        if score < 70:
            kelly_multiplier = score / 100  # Reduce stake proportionally

        return {
            "success": True,
            "confidence_score": score,
            "confidence_level": level,
            "message": message,
            "reason": reason,
            "recommended_kelly_multiplier": round(kelly_multiplier, 2),
            "data_quality": {
                "has_xg": has_xg,
                "xg_freshness": "fresh" if xg_age_hours < 24 else "stale",
                "has_form": has_form,
                "has_h2h": has_h2h,
                "completeness_percent": round(data_completeness * 100, 1)
            }
        }

    except Exception as e:
        raise HTTPException(500, f"Error calculating confidence score: {str(e)}")


@app.post("/api/backtest-simulation")
async def run_backtest_simulation(
    bankroll: float = 10000,
    kelly_fraction: float = 0.25,
    min_edge: float = 0.05,
    num_matches: int = 50,
    days_back: int = 7
):
    """
    Run backtesting simulation

    Simulates betting strategy on historical matches to evaluate
    performance. In production, this would use real historical data.

    Args:
        bankroll: Starting bankroll
        kelly_fraction: Kelly fraction to test
        min_edge: Minimum edge threshold
        num_matches: Number of matches to simulate
        days_back: Days of history to simulate

    Returns:
        Complete backtest results with metrics and history
    """
    try:
        # Validate
        if bankroll < 100:
            raise HTTPException(400, "Bankroll must be >= 100")
        if not (0 < kelly_fraction <= 1):
            raise HTTPException(400, "Kelly fraction must be between 0 and 1")
        if num_matches > 200:
            raise HTTPException(400, "Maximum 200 matches for simulation")

        # Initialize backtest engine
        engine = BacktestEngine(
            bankroll=bankroll,
            kelly_fraction=kelly_fraction,
            min_edge=min_edge
        )

        # Generate sample historical matches (in production: fetch from DB)
        matches = BacktestEngine.generate_sample_historical_matches(
            count=num_matches,
            days_back=days_back
        )

        # Run simulation
        result = engine.run_backtest(matches, simulate_outcomes=True)

        return {
            "success": True,
            "simulation_settings": {
                "initial_bankroll": bankroll,
                "kelly_fraction": kelly_fraction,
                "min_edge": min_edge,
                "num_matches": num_matches
            },
            "results": result.to_dict(),
            "performance_summary": {
                "profitable": result.total_profit > 0,
                "roi_rating": "Excellent" if result.roi_percent > 10 else
                             "Good" if result.roi_percent > 5 else
                             "Fair" if result.roi_percent > 0 else "Poor",
                "risk_assessment": "Low" if result.max_drawdown_percent < 10 else
                                  "Moderate" if result.max_drawdown_percent < 20 else "High"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Backtest simulation error: {str(e)}")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.utcnow(),
            details={"path": str(request.url)}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            timestamp=datetime.utcnow(),
            details={"message": str(exc)}
        ).dict()
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 80)
    print("AlphaBet API - Starting up...")
    print("=" * 80)
    print(f"Docs available at: http://localhost:8000/api/docs")
    print(f"Health check at: http://localhost:8000/api/health")
    print("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("AlphaBet API - Shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
