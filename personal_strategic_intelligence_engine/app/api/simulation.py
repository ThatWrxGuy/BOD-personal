"""Simulation API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.simulation_engine import SimulationCore, get_simulation_core
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run", status_code=status.HTTP_201_CREATED)
async def run_simulation(
    scenario_type: str = Query(default="mixed_life_pressure"),
    simulated_days: int = Query(default=14, ge=7, le=30),
    seed: Optional[int] = Query(default=None),
    session: AsyncSession = Depends(get_db),
):
    """Start a one-time simulation."""
    simulator = SystemSimulator(session)
    
    try:
        run = await simulator.run_simulation(
            scenario_type=scenario_type,
            simulated_days=simulated_days,
            seed=seed,
        )
        return {
            "id": str(run.id),
            "name": run.name,
            "scenario_type": run.scenario_type,
            "status": run.status,
            "simulated_days": run.simulated_days,
            "start_time": run.start_time.isoformat() if run.start_time else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs")
async def list_runs(
    session: AsyncSession = Depends(get_db),
):
    """List all simulation runs."""
    simulator = SystemSimulator(session)
    runs = await simulator.list_simulation_runs()
    return {
        "runs": [
            {
                "id": str(r.id),
                "name": r.name,
                "scenario_type": r.scenario_type,
                "status": r.status,
                "simulated_days": r.simulated_days,
                "start_time": r.start_time.isoformat() if r.start_time else None,
                "end_time": r.end_time.isoformat() if r.end_time else None,
                "summary": r.summary,
            }
            for r in runs
        ]
    }


@router.get("/runs/{run_id}")
async def get_run(
    run_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get simulation run metadata."""
    import uuid
    simulator = SystemSimulator(session)
    
    try:
        run = await simulator.get_simulation_run(uuid.UUID(run_id))
        if not run:
            raise HTTPException(status_code=404, detail="Simulation run not found")
        
        return {
            "id": str(run.id),
            "name": run.name,
            "scenario_type": run.scenario_type,
            "status": run.status,
            "simulated_days": run.simulated_days,
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None,
            "summary": run.summary,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


@router.get("/runs/{run_id}/report")
async def get_report(
    run_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get audit report for a simulation run."""
    import uuid
    simulator = SystemSimulator(session)
    
    try:
        run_uuid = uuid.UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    report = await simulator.get_audit_report(run_uuid)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": str(report.id),
        "simulation_run_id": str(report.simulation_run_id),
        "executive_summary": report.executive_summary,
        "system_readiness_score": report.system_readiness_score,
        "component_scores": report.component_scores,
        "strengths": report.strengths,
        "weaknesses": report.weaknesses,
        "failures": report.failures,
        "recommendations": report.recommendations,
    }


@router.get("/runs/{run_id}/events")
async def get_events(
    run_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get simulation events for a run."""
    import uuid
    from sqlalchemy import select
    from app.models.simulation import SimulationEvent
    
    try:
        run_uuid = uuid.UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await session.execute(
        select(SimulationEvent)
        .where(SimulationEvent.simulation_run_id == run_uuid)
        .order_by(SimulationEvent.event_day, SimulationEvent.created_at)
    )
    events = list(result.scalars().all())
    
    return {
        "events": [
            {
                "id": str(e.id),
                "event_day": e.event_day,
                "event_type": e.event_type,
                "title": e.title,
                "description": e.description,
                "component": e.component,
                "severity": e.severity,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]
    }


# Strategic Simulation Engine endpoints (V3-007)

@router.get("/strategic/runs")
async def list_strategic_simulations(
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List strategic simulation runs."""
    from app.simulation_engine import get_simulation_core as get_simulation_engine
    
    engine = await get_simulation_engine(session)
    simulations = await engine.get_simulations(status, limit)
    
    return {
        "simulations": [
            {
                "id": str(s.id),
                "decision_type": s.decision_type,
                "decision_description": s.decision_description,
                "time_horizon_days": s.time_horizon_days,
                "domain": s.domain,
                "status": s.status,
                "scenarios_generated": s.scenarios_generated,
                "recommended_scenario": s.recommended_scenario,
                "overall_risk_level": s.overall_risk_level,
            }
            for s in simulations
        ]
    }


@router.post("/strategic/run")
async def run_strategic_simulation(
    decision_type: str = Query(..., description="Decision type: investment, spending, workload, expense, goal_timeline"),
    decision_description: Optional[str] = Query(None),
    decision_params: Optional[dict] = Body(None),
    time_horizon_days: int = Query(90, ge=1, le=1825),
    domain: str = Query("financial"),
    session: AsyncSession = Depends(get_db),
):
    """Run a strategic simulation."""
    from app.simulation_engine import get_simulation_core as get_simulation_engine
    
    engine = await get_simulation_engine(session)
    
    try:
        simulation = await engine.run_simulation(
            decision_type=decision_type,
            decision_description=decision_description,
            decision_params=decision_params,
            time_horizon_days=time_horizon_days,
            domain=domain,
        )
        
        return {
            "id": str(simulation.id),
            "decision_type": simulation.decision_type,
            "status": simulation.status,
            "message": "Simulation started",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategic/runs/{simulation_id}")
async def get_strategic_simulation(
    simulation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get strategic simulation details."""
    from app.simulation_engine import get_simulation_core as get_simulation_engine
    
    engine = await get_simulation_engine(session)
    simulation = await engine.get_simulation(simulation_id)
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    scenarios = await engine.get_simulation_scenarios(simulation_id)
    
    return {
        "id": str(simulation.id),
        "decision_type": simulation.decision_type,
        "decision_description": simulation.decision_description,
        "time_horizon_days": simulation.time_horizon_days,
        "domain": simulation.domain,
        "status": simulation.status,
        "scenarios_generated": simulation.scenarios_generated,
        "recommended_scenario": simulation.recommended_scenario,
        "overall_risk_level": simulation.overall_risk_level,
        "scenarios": [
            {
                "id": str(s.id),
                "scenario_name": s.scenario_name,
                "scenario_type": s.scenario_type,
                "projected_value": s.projected_value,
                "confidence_score": s.confidence_score,
                "risk_score": s.risk_score,
            }
            for s in scenarios
        ],
    }
