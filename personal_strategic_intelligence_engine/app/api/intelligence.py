"""Intelligence API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.intelligence import (
    ForecastResponse,
    ScenarioCreate,
    ScenarioResponse,
    RiskProjectionResponse,
    GoalProbabilityResponse,
    TrendsSummaryResponse,
    IntelligenceDashboardResponse,
)
from app.services.governance_service import GovernanceService
from app.intelligence.intelligence_service import IntelligenceService
from app.intelligence.forecasting_engine import ForecastingEngine
from app.intelligence.risk_projection_engine import RiskProjector as RiskProjectionEngine
from app.intelligence.goal_probability_model import GoalProbabilityEngine as GoalProbabilityModel
from app.intelligence.trend_analyzer import TrendAnalyzer
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


# ========== Trends ==========

@router.get("/trends", response_model=TrendsSummaryResponse)
async def get_trends(
    days: int = Query(default=30, ge=1, le=365),
    session: AsyncSession = Depends(get_db),
):
    """Get trend analysis."""
    analyzer = TrendAnalyzer(session)
    trends = await analyzer.get_comprehensive_trends(days=days)
    return trends


# ========== Forecasts ==========

@router.get("/forecasts", response_model=list[ForecastResponse])
async def list_forecasts(
    forecast_type: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """List forecasts."""
    from sqlalchemy import select
    from app.models.forecast_model import ForecastModel
    
    query = select(ForecastModel).order_by(ForecastModel.created_at.desc())
    if forecast_type:
        query = query.where(ForecastModel.forecast_type == forecast_type)
    
    result = await session.execute(query)
    return list(result.scalars().all())


@router.post("/forecasts/generate")
async def generate_forecasts(
    days_ahead: int = Query(default=30, ge=1, le=365),
    session: AsyncSession = Depends(get_db),
):
    """Generate new forecasts."""
    engine = ForecastingEngine(session)
    forecasts = await engine.generate_all_forecasts(days_ahead)
    return {"generated": len(forecasts), "forecasts": forecasts}


# ========== Risks ==========

@router.get("/risks", response_model=list[RiskProjectionResponse])
async def list_risks(
    category: Optional[str] = None,
    min_probability: float = Query(default=0.0, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_db),
):
    """List risk projections."""
    from sqlalchemy import select
    from app.models.risk_projection import RiskProjection
    
    query = select(RiskProjection).order_by(RiskProjection.risk_probability.desc())
    if category:
        query = query.where(RiskProjection.risk_category == category)
    query = query.where(RiskProjection.risk_probability >= min_probability)
    
    result = await session.execute(query)
    return list(result.scalars().all())


@router.post("/risks/project")
async def project_risks(
    session: AsyncSession = Depends(get_db),
):
    """Generate new risk projections."""
    engine = RiskProjectionEngine(session)
    risks = await engine.project_all_risks()
    return {"projected": len(risks), "risks": risks}


# ========== Goal Probability ==========

@router.get("/goals/probability", response_model=list[GoalProbabilityResponse])
async def list_goal_probabilities(
    session: AsyncSession = Depends(get_db),
):
    """List goal probabilities."""
    from sqlalchemy import select
    from app.models.goal_probability import GoalProbability
    
    result = await session.execute(
        select(GoalProbability).order_by(GoalProbability.probability_of_success)
    )
    return list(result.scalars().all())


@router.get("/goals/{goal_id}/probability")
async def get_goal_probability(
    goal_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get probability for a specific goal."""
    import uuid
    from app.intelligence.goal_probability_model import GoalProbabilityEngine as GoalProbabilityModel
    
    model = GoalProbabilityModel(session)
    try:
        prob = await model.calculate_goal_probability(uuid.UUID(goal_id))
        return prob
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/goals/probability/calculate")
async def calculate_goal_probabilities(
    session: AsyncSession = Depends(get_db),
):
    """Calculate probabilities for all active goals."""
    model = GoalProbabilityModel(session)
    probabilities = await model.calculate_all_goal_probabilities()
    return {"calculated": len(probabilities)}


# ========== Scenarios ==========

@router.post("/scenario/run", response_model=ScenarioResponse)
async def run_scenario(
    scenario: ScenarioCreate,
    session: AsyncSession = Depends(get_db),
):
    """Run a scenario simulation."""
    from app.intelligence.scenario_simulator import ScenarioSimulator
    
    simulator = ScenarioSimulator(session)
    
    if scenario.scenario_type == "savings_increase":
        result = await simulator.simulate_savings_increase(
            scenario.parameters.get("increase_percentage", 20) if scenario.parameters else 20
        )
    elif scenario.scenario_type == "expense_reduction":
        result = await simulator.simulate_expense_reduction(
            scenario.parameters.get("reduction_percentage", 15) if scenario.parameters else 15
        )
    elif scenario.scenario_type == "workload_change":
        result = await simulator.simulate_workload_change(
            scenario.parameters.get("change_percentage", -20) if scenario.parameters else -20
        )
    elif scenario.scenario_type == "health_activity":
        result = await simulator.simulate_health_activity_change(
            scenario.parameters.get("activity_change", "increase") if scenario.parameters else "increase",
            scenario.parameters.get("percentage", 25) if scenario.parameters else 25,
        )
    else:
        result = await simulator.run_custom_scenario(
            scenario.scenario_type,
            scenario.parameters or {},
            {},
        )
    
    return result


# ========== Dashboard ==========

@router.get("/dashboard", response_model=IntelligenceDashboardResponse)
async def get_dashboard(
    session: AsyncSession = Depends(get_db),
):
    """Get intelligence dashboard."""
    service = IntelligenceService(session)
    return await service.get_intelligence_dashboard()
