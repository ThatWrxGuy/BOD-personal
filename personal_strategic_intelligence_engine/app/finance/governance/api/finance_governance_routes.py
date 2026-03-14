"""Finance Governance API routes."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.finance.services.finance_state_service import FinanceStateService
from app.finance.intelligence.services.finance_intelligence_service import FinanceIntelligenceService
from app.finance.simulation.services.finance_simulation_service import FinanceSimulationService
from app.finance.governance.services.finance_governance_service import FinanceGovernanceService
from app.finance.governance.models.financial_decision_request import DecisionClass, DecisionStatus
from app.finance.governance.models.financial_decision_result import DecisionOutcome
from app.finance.governance.models.financial_audit_event import AuditEventType


router = APIRouter(prefix="/finance/governance", tags=["finance-governance"])


# Request models
class SubmitDecisionRequest(BaseModel):
    """Request to submit a recommendation for decision."""
    recommendation_id: str


class ResolveDecisionRequest(BaseModel):
    """Request to resolve a decision."""
    outcome: DecisionOutcome
    reviewer: str = "system"
    review_notes: str = ""


def get_governance_service(session: AsyncSession = Depends(get_db)) -> FinanceGovernanceService:
    """Get finance governance service."""
    finance_service = FinanceStateService(session)
    intelligence_service = FinanceIntelligenceService(finance_service)
    simulation_service = FinanceSimulationService(finance_service)
    return FinanceGovernanceService(finance_service, intelligence_service, simulation_service)


@router.get("/board-brief")
async def get_board_brief(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Generate and retrieve a board-ready financial intelligence brief.
    """
    service = get_governance_service(session)
    brief = await service.generate_board_brief(profile_id)
    
    return {
        "brief": brief.to_dict(),
    }


@router.get("/decisions")
async def get_decisions(
    profile_id: int = Query(..., description="Profile ID"),
    decision_class: Optional[str] = Query(None, description="Filter by decision class"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get pending financial decisions for a profile.
    """
    service = get_governance_service(session)
    
    decision_class_filter = None
    if decision_class:
        try:
            decision_class_filter = DecisionClass(decision_class)
        except ValueError:
            pass
    
    decisions = await service.get_pending_financial_decisions(
        profile_id, 
        decision_class_filter
    )
    
    return {
        "decisions": [d.to_dict() for d in decisions],
        "count": len(decisions),
    }


@router.post("/decisions/submit")
async def submit_decision(
    request: SubmitDecisionRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Submit a recommendation for governance decision.
    """
    service = get_governance_service(session)
    decision = await service.submit_recommendation_for_decision(
        recommendation_id=request.recommendation_id
    )
    
    if not decision:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendation not found: {request.recommendation_id}"
        )
    
    return {
        "decision": decision.to_dict(),
    }


@router.post("/decisions/{decision_id}/resolve")
async def resolve_decision(
    decision_id: str,
    request: ResolveDecisionRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Resolve a governance decision.
    """
    service = get_governance_service(session)
    result = await service.resolve_decision(
        decision_id=decision_id,
        outcome=request.outcome,
        reviewer=request.reviewer,
        review_notes=request.review_notes,
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Decision not found: {decision_id}"
        )
    
    return {
        "result": result.to_dict(),
    }


@router.get("/audit-log")
async def get_audit_log(
    profile_id: int = Query(..., description="Profile ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum events to return"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get financial audit log for a profile.
    """
    service = get_governance_service(session)
    
    event_type_filter = None
    if event_type:
        try:
            event_type_filter = AuditEventType(event_type)
        except ValueError:
            pass
    
    events = await service.get_financial_audit_log(
        profile_id, 
        event_type_filter,
        limit
    )
    
    return {
        "events": [e.to_dict() for e in events],
        "count": len(events),
    }
