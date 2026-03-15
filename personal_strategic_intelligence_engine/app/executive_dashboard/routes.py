"""Executive Dashboard API routes.

API endpoints for the Executive Dashboard subsystem.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.executive_dashboard.dashboard_models import (
    CommandCategory,
    CommandRequest,
    CommandResult,
    ApprovalRequest,
    ApprovalResult,
)
from app.executive_dashboard.dashboard_service import get_dashboard_service
from app.executive_dashboard.command_router import get_command_router
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["executive-dashboard"])


# ============ Overview Endpoints ============

@router.get("/overview")
async def get_overview():
    """
    Get complete dashboard overview.
    
    Returns all dashboard views in a single response.
    """
    service = get_dashboard_service()
    return service.get_full_overview()


@router.get("/system")
async def get_system_overview():
    """
    Get system overview.
    
    Returns high-level operational metrics.
    """
    service = get_dashboard_service()
    overview = service.get_system_overview()
    return overview.dict()


# ============ Strategy Endpoints ============

@router.get("/strategies")
async def get_strategy_overview():
    """
    Get strategy pipeline overview.
    
    Returns strategy pipeline activity and metrics.
    """
    service = get_dashboard_service()
    overview = service.get_strategy_overview()
    return overview.dict()


# ============ Execution Endpoints ============

@router.get("/executions")
async def get_execution_overview():
    """
    Get execution overview.
    
    Returns execution activity and metrics.
    """
    service = get_dashboard_service()
    overview = service.get_execution_overview()
    return overview.dict()


# ============ Agent Endpoints ============

@router.get("/agents")
async def get_agent_overview():
    """
    Get agent overview.
    
    Returns agent performance and metrics.
    """
    service = get_dashboard_service()
    overview = service.get_agent_overview()
    return overview.dict()


# ============ Learning Endpoints ============

@router.get("/learning")
async def get_learning_overview():
    """
    Get learning overview.
    
    Returns learning engine metrics and insights.
    """
    service = get_dashboard_service()
    overview = service.get_learning_overview()
    return overview.dict()


# ============ Graph Endpoints ============

@router.get("/graph")
async def get_graph_overview():
    """
    Get knowledge graph overview.
    
    Returns contextual intelligence metrics.
    """
    service = get_dashboard_service()
    overview = service.get_graph_overview()
    return overview.dict()


# ============ Command Endpoints ============

@router.post("/command", response_model=CommandResult)
async def execute_command(request: CommandRequest):
    """
    Execute a dashboard command.
    
    Commands include:
    - approve_proposal: Approve a strategy proposal
    - reject_proposal: Reject a strategy proposal
    - trigger_execution: Manually trigger an execution
    - pause_agent: Pause an agent
    - resume_agent: Resume an agent
    - rebuild_graph: Rebuild the knowledge graph
    - trigger_learning_cycle: Trigger a learning cycle
    - get_system_status: Get system status
    """
    router_instance = get_command_router()
    result = await router_instance.execute_command(request)
    return result


@router.post("/approve")
async def approve_proposal(request: ApprovalRequest):
    """
    Approve or reject a strategy proposal.
    
    This is a convenience endpoint for governance overrides.
    """
    router_instance = get_command_router()
    
    if request.decision == "approve":
        cmd_request = CommandRequest(
            command="approve_proposal",
            category=CommandCategory.GOVERNANCE,
            parameters={"proposal_id": request.proposal_id, "reason": request.reason},
            requester=request.approver,
        )
    elif request.decision == "reject":
        cmd_request = CommandRequest(
            command="reject_proposal",
            category=CommandCategory.GOVERNANCE,
            parameters={"proposal_id": request.proposal_id, "reason": request.reason},
            requester=request.approver,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid decision. Use 'approve' or 'reject'."
        )
    
    result = await router_instance.execute_command(cmd_request)
    
    return ApprovalResult(
        proposal_id=request.proposal_id,
        decision=request.decision,
        status=result.status.value,
        message=result.message,
    )


# ============ Statistics Endpoint ============

@router.get("/statistics")
async def get_dashboard_statistics():
    """
    Get dashboard statistics.
    
    Returns aggregate metrics across all subsystems.
    """
    service = get_dashboard_service()
    stats = service.get_statistics()
    return stats.dict()


# ============ Command History ============

@router.get("/commands/history")
async def get_command_history(limit: int = 50):
    """
    Get command execution history.
    
    Returns recent command executions.
    """
    router_instance = get_command_router()
    return router_instance.get_command_history(limit)


# ============ Utility Endpoints ============

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "executive-dashboard"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "service": "executive-dashboard"}
