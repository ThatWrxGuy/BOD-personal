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
from app.core.response_wrapper import (
    wrap_response,
    error_response,
    success_response,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["executive-dashboard"])


# ============ Overview Endpoints ============

@router.get("/overview")
async def get_overview():
    """Get complete dashboard overview."""
    service = get_dashboard_service()
    return success_response(service.get_full_overview())


@router.get("/system")
async def get_system_overview():
    """Get system overview."""
    service = get_dashboard_service()
    overview = service.get_system_overview()
    return success_response(overview.dict())


# ============ Strategy Endpoints ============

@router.get("/strategies")
async def get_strategy_overview():
    """Get strategy pipeline overview."""
    service = get_dashboard_service()
    overview = service.get_strategy_overview()
    return success_response(overview.dict())


# ============ Execution Endpoints ============

@router.get("/executions")
async def get_execution_overview():
    """Get execution overview."""
    service = get_dashboard_service()
    overview = service.get_execution_overview()
    return success_response(overview.dict())


# ============ Agent Endpoints ============

@router.get("/agents")
async def get_agent_overview():
    """Get agent overview."""
    service = get_dashboard_service()
    overview = service.get_agent_overview()
    return success_response(overview.dict())


# ============ Learning Endpoints ============

@router.get("/learning")
async def get_learning_overview():
    """Get learning overview."""
    service = get_dashboard_service()
    overview = service.get_learning_overview()
    return success_response(overview.dict())


# ============ Graph Endpoints ============

@router.get("/graph")
async def get_graph_overview():
    """Get knowledge graph overview."""
    service = get_dashboard_service()
    overview = service.get_graph_overview()
    return success_response(overview.dict())


# ============ Command Endpoints ============

@router.post("/command", response_model=dict)
async def execute_command(request: CommandRequest):
    """Execute a dashboard command."""
    router_instance = get_command_router()
    result = await router_instance.execute_command(request)
    return success_response(result.dict())


@router.post("/approve")
async def approve_proposal(request: ApprovalRequest):
    """Approve or reject a strategy proposal."""
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
        return error_response("Invalid decision. Use 'approve' or 'reject'.")
    
    result = await router_instance.execute_command(cmd_request)
    
    return success_response({
        "proposal_id": request.proposal_id,
        "decision": request.decision,
        "status": result.status.value,
        "message": result.message,
    })


# ============ Statistics Endpoint ============

@router.get("/statistics")
async def get_dashboard_statistics():
    """Get dashboard statistics."""
    service = get_dashboard_service()
    stats = service.get_statistics()
    return success_response(stats.dict())


# ============ Command History ============

@router.get("/commands/history")
async def get_command_history(limit: int = 50):
    """Get command execution history."""
    router_instance = get_command_router()
    return success_response(router_instance.get_command_history(limit))


# ============ Utility Endpoints ============

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return success_response({"status": "healthy", "service": "executive-dashboard"})


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return success_response({"status": "ready", "service": "executive-dashboard"})
