"""Finance Simulation API routes."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.finance.services.finance_state_service import FinanceStateService
from app.finance.simulation.services.finance_simulation_service import FinanceSimulationService
from app.finance.simulation.models.scenario_definition import ScenarioType


router = APIRouter(prefix="/finance/simulation", tags=["finance-simulation"])


# Request/Response models
class RunScenarioRequest(BaseModel):
    """Request to run a simulation scenario."""
    profile_id: int
    scenario_type: str
    parameters: Optional[dict] = None


class CompareScenariosRequest(BaseModel):
    """Request to compare two scenarios."""
    base_scenario_id: str
    comparison_scenario_id: str


def get_simulation_service(session: AsyncSession = Depends(get_db)) -> FinanceSimulationService:
    """Get finance simulation service."""
    finance_service = FinanceStateService(session)
    return FinanceSimulationService(finance_service)


@router.post("/run")
async def run_simulation(
    request: RunScenarioRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Run a financial simulation scenario.
    
    Available scenario types:
    - debt_payoff: Evaluate accelerated debt payoff strategies
    - income_shock: Model effects of reduced income
    - expense_shock: Model unexpected financial obligations
    - liquidity_stress: Evaluate resilience to financial disruption
    - investment_allocation: Project asset growth under different allocations
    """
    try:
        scenario_type = ScenarioType(request.scenario_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario type: {request.scenario_type}"
        )
    
    service = get_simulation_service(session)
    result = await service.run_scenario(
        profile_id=request.profile_id,
        scenario_type=scenario_type,
        parameters=request.parameters,
    )
    
    return {
        "result": result.to_dict(),
    }


@router.get("/results")
async def get_simulation_results(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get all simulation results for a profile.
    """
    service = get_simulation_service(session)
    results = await service.get_scenario_results(profile_id)
    
    return {
        "results": [r.to_dict() for r in results],
        "count": len(results),
    }


@router.get("/results/{scenario_id}")
async def get_simulation_result(
    scenario_id: str,
    session: AsyncSession = Depends(get_db),
):
    """
    Get a specific simulation result by ID.
    """
    service = get_simulation_service(session)
    result = await service.get_scenario_by_id(scenario_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario result not found: {scenario_id}"
        )
    
    return {
        "result": result.to_dict(),
    }


@router.post("/compare")
async def compare_scenarios(
    request: CompareScenariosRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Compare two scenario results.
    """
    service = get_simulation_service(session)
    comparison = await service.compare_scenarios(
        base_scenario_id=request.base_scenario_id,
        comparison_scenario_id=request.comparison_scenario_id,
    )
    
    if not comparison:
        raise HTTPException(
            status_code=404,
            detail="One or both scenario results not found"
        )
    
    return {
        "comparison": comparison.to_dict(),
    }
