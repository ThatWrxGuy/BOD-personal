"""Orchestration API Routes - BB-CORE-021"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.core.orchestration.strategic_intelligence_orchestrator import (
    get_strategic_orchestrator,
)
from app.core.orchestration.orchestration_models import (
    OrchestrationCycleResult,
    SystemStateSnapshot,
    ActivationDecision,
    FusedDecision,
    CapitalPosture,
    ExecutiveBrief,
    RoutedPriorityItem,
    PriorityLevel,
)

router = APIRouter(prefix="/core/orchestration", tags=["Strategic Orchestration"])


@router.get("/status", response_model=SystemStateSnapshot)
async def get_system_status():
    """Get current system state snapshot."""
    orchestrator = get_strategic_orchestrator()
    
    # Run a cycle to get current state
    result = orchestrator.run_cycle()
    
    return result.state_snapshot


@router.post("/cycle", response_model=OrchestrationCycleResult)
async def run_orchestration_cycle(
    regime: Optional[dict] = Query(None, description="Market regime data"),
    portfolio: Optional[dict] = Query(None, description="Portfolio state data"),
    strategies: Optional[List[dict]] = Query(None, description="Strategy data"),
    tactical_opportunities: Optional[List[dict]] = Query(None, description="Tactical opportunities"),
    governance_state: Optional[dict] = Query(None, description="Governance state"),
):
    """Run a complete orchestration cycle."""
    orchestrator = get_strategic_orchestrator()
    
    return orchestrator.run_cycle(
        regime=regime,
        portfolio=portfolio,
        strategies=strategies,
        tactical_opportunities=tactical_opportunities,
        governance_state=governance_state,
    )


@router.get("/decision", response_model=FusedDecision)
async def get_current_decision():
    """Get the current fused decision."""
    orchestrator = get_strategic_orchestrator()
    
    result = orchestrator.run_cycle()
    
    return result.decision


@router.get("/capital-posture", response_model=CapitalPosture)
async def get_capital_posture():
    """Get current capital deployment posture."""
    orchestrator = get_strategic_orchestrator()
    
    result = orchestrator.run_cycle()
    
    return result.capital.posture


@router.get("/brief", response_model=ExecutiveBrief)
async def get_executive_brief():
    """Get executive brief with prioritized items."""
    orchestrator = get_strategic_orchestrator()
    
    result = orchestrator.run_cycle()
    
    return result.executive_brief


@router.get("/alerts", response_model=List[RoutedPriorityItem])
async def get_alerts(
    priority: Optional[str] = Query(None, description="Filter by priority: critical, high, medium, low"),
):
    """Get priority alerts."""
    orchestrator = get_strategic_orchestrator()
    
    if priority:
        try:
            p = PriorityLevel(priority)
            result = orchestrator.run_cycle()
            return [item for item in result.executive_brief.priority_items if item.priority == p]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
    
    result = orchestrator.run_cycle()
    return result.executive_brief.priority_items


@router.get("/activation", response_model=ActivationDecision)
async def get_activation_decision():
    """Get current engine activation decisions."""
    orchestrator = get_strategic_orchestrator()
    
    result = orchestrator.run_cycle()
    
    return result.activation


@router.get("/critical-alerts", response_model=List[RoutedPriorityItem])
async def get_critical_alerts():
    """Get critical priority alerts requiring immediate attention."""
    orchestrator = get_strategic_orchestrator()
    
    orchestrator.run_cycle()
    
    return orchestrator.get_critical_alerts()
