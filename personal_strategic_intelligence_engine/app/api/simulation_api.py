"""Simulation API Routes."""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.simulation.seed_manager import create_seed_manager
from app.simulation.mock_data_generator import MockDataGenerator
from app.simulation.scenario_builder import ScenarioBuilder
from app.simulation.simulation_engine_v2 import SimulationEngine
from app.simulation.simulation_runner import SimulationRunner, get_simulation_runner
from app.simulation.results_analyzer import ResultsAnalyzer, create_results_analyzer
from app.simulation.simulation_logger import get_simulation_logger
from app.simulation.simulation_types import (
    ScenarioType,
    SimulationStatus,
    SimulationResults,
    SimulationConfig,
)

router = APIRouter(prefix="/simulation", tags=["simulation"])


class RunSimulationRequest(BaseModel):
    """Request to run a simulation."""
    seed: str
    scenario_type: ScenarioType = ScenarioType.BASELINE
    duration_days: int = 30
    enable_subsystems: bool = True


class SimulationStatusResponse(BaseModel):
    """Simulation status response."""
    simulation_id: str
    status: SimulationStatus
    seed: str
    scenario_type: str
    duration_days: int


@router.post("/run")
async def run_simulation(request: RunSimulationRequest):
    """Run a seeded simulation."""
    
    try:
        # Validate inputs
        if not request.seed:
            raise HTTPException(status_code=400, detail="Seed is required")
        
        if request.duration_days < 1 or request.duration_days > 90:
            raise HTTPException(status_code=400, detail="Duration must be between 1 and 90 days")
        
        # Create runner
        runner = get_simulation_runner()
        
        # Run simulation
        results = await runner.run_simulation(
            seed=request.seed,
            scenario_type=request.scenario_type,
            duration_days=request.duration_days,
            enable_subsystems=request.enable_subsystems,
        )
        
        # Build report
        analyzer = create_results_analyzer()
        scores = analyzer.analyze(results)
        
        return {
            "simulation_id": results.metadata.simulation_id,
            "status": results.metadata.status.value,
            "seed": results.metadata.seed,
            "scenario_type": results.metadata.scenario_type.value,
            "duration_days": results.metadata.duration_days,
            "scores": scores,
            "days_simulated": len(results.daily_summaries),
            "weeks_simulated": len(results.weekly_summaries),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_simulations_status():
    """Get status of all simulations."""
    
    runner = get_simulation_runner()
    history = runner.get_history()
    
    return {
        "simulations": [
            {
                "simulation_id": r.metadata.simulation_id,
                "status": r.metadata.status.value,
                "seed": r.metadata.seed,
                "scenario_type": r.metadata.scenario_type.value,
                "duration_days": r.metadata.duration_days,
                "completed_at": r.metadata.end_time.isoformat() if r.metadata.end_time else None,
            }
            for r in history
        ],
        "total": len(history),
    }


@router.get("/history")
async def get_simulation_history(limit: int = Query(10, ge=1, le=100)):
    """Get simulation history."""
    
    runner = get_simulation_runner()
    history = runner.get_history()
    
    return {
        "simulations": [
            {
                "simulation_id": r.metadata.simulation_id,
                "seed": r.metadata.seed,
                "scenario_type": r.metadata.scenario_type.value,
                "duration_days": r.metadata.duration_days,
                "status": r.metadata.status.value,
                "scores": r.analysis_scores,
            }
            for r in history[-limit:]
        ],
        "total": len(history),
    }


@router.get("/report/{simulation_id}")
async def get_simulation_report(simulation_id: str):
    """Get a specific simulation report."""
    
    runner = get_simulation_runner()
    results = runner.get_simulation(simulation_id)
    
    if not results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Build report
    from app.simulation.report_builder_v2 import create_report_builder
    builder = create_report_builder()
    report = builder.build_report(results)
    
    return builder.export_report_dict(report)


@router.get("/scenarios")
async def get_available_scenarios():
    """Get available simulation scenarios."""
    
    return {
        "scenarios": [
            {
                "type": s.value,
                "name": s.name,
                "description": _get_scenario_description(s),
            }
            for s in ScenarioType
        ]
    }


def _get_scenario_description(scenario: ScenarioType) -> str:
    """Get description for a scenario type."""
    descriptions = {
        ScenarioType.BASELINE: "Normal functioning environment with stable conditions",
        ScenarioType.PRESSURE: "High debt, low liquidity, high stress environment",
        ScenarioType.OPPORTUNITY: "Strong upside opportunities available",
        ScenarioType.RECOVERY: "System starts in degraded state",
        ScenarioType.CONFLICT: "Multiple domains compete for priority",
        ScenarioType.VOLATILITY: "Frequent disruptions and rapid changes",
    }
    return descriptions.get(scenario, "Custom scenario")


@router.post("/run-baseline")
async def run_baseline_simulation(
    seed: str = Query("BOD-V4-SIM-BASELINE-001"),
    days: int = Query(30, ge=7, le=90),
):
    """Run a baseline simulation."""
    
    try:
        runner = get_simulation_runner()
        
        results = await runner.run_simulation(
            seed=seed,
            scenario_type=ScenarioType.BASELINE,
            duration_days=days,
        )
        
        analyzer = create_results_analyzer()
        scores = analyzer.analyze(results)
        
        return {
            "simulation_id": results.metadata.simulation_id,
            "status": "completed",
            "seed": seed,
            "scenario": "baseline",
            "duration_days": days,
            "scores": scores,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-pressure")
async def run_pressure_simulation(
    seed: str = Query("BOD-V4-SIM-PRESSURE-001"),
    days: int = Query(30, ge=7, le=90),
):
    """Run a pressure simulation."""
    
    try:
        runner = get_simulation_runner()
        
        results = await runner.run_simulation(
            seed=seed,
            scenario_type=ScenarioType.PRESSURE,
            duration_days=days,
        )
        
        analyzer = create_results_analyzer()
        scores = analyzer.analyze(results)
        
        return {
            "simulation_id": results.metadata.simulation_id,
            "status": "completed",
            "seed": seed,
            "scenario": "pressure",
            "duration_days": days,
            "scores": scores,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick-test")
async def quick_simulation_test():
    """Quick test of simulation components."""
    
    # Test seed generation
    from app.simulation.seed_manager import create_seed_manager
    
    seed = "BOD-V4-SIM-BASELINE-001"
    sm = create_seed_manager(seed)
    
    # Test data generation
    mock = MockDataGenerator(sm)
    profile = mock.generate_personal_profile()
    financial = mock.generate_financial_state(ScenarioType.BASELINE)
    goals = mock.generate_strategic_goals()
    habits = mock.generate_habits()
    domains = mock.generate_domain_states(ScenarioType.BASELINE)
    
    return {
        "status": "ok",
        "seed_hash": sm.get_seed_hash(),
        "profile": profile.model_dump(),
        "financial": {
            "monthly_income": financial.monthly_income,
            "debt_balances": financial.debt_balances,
        },
        "goals_count": len(goals),
        "habits_count": len(habits),
        "domains_count": len(domains),
    }
