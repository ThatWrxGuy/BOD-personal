"""Execution Engine API routes.

API endpoints for the Execution Engine subsystem.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.execution_engine.execution_models import (
    ActionType,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from app.execution_engine.execution_engine import (
    ExecutionEngine,
    get_execution_engine,
    reset_execution_engine,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/execution-engine", tags=["execution-engine"])


# ============ Request/Response Models ============

class CreateExecutionRequest(BaseModel):
    """Request to create an execution."""
    proposal_id: str
    action_type: str
    parameters: dict = {}
    risk_level: str = "medium"
    governance_decision_id: Optional[str] = None
    approved_by: str = "governance"


class ExecutionResponse(BaseModel):
    """Response for execution details."""
    id: str
    proposal_id: str
    action_type: str
    status: str
    risk_level: str
    approved_by: str
    result: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: str
    executed_at: Optional[str] = None
    completed_at: Optional[str] = None


class ExecutionListResponse(BaseModel):
    """Response for execution list."""
    executions: list
    total: int


class ExecutionStatisticsResponse(BaseModel):
    """Response for execution statistics."""
    total: int
    completed: int
    failed: int
    pending: int
    executing: int
    success_rate: float


# ============ Execution Endpoints ============

@router.get("", response_model=ExecutionListResponse)
async def list_executions(
    status_filter: Optional[str] = None,
    limit: int = 50,
):
    """
    List executions.
    
    Returns a list of all executions, optionally filtered by status.
    """
    engine = get_execution_engine()
    
    if status_filter:
        try:
            status_enum = ExecutionStatus(status_filter)
            executions = engine.get_executions_by_status(status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    else:
        # Get all executions
        executions = list(engine._executions.values())
    
    return {
        "executions": [
            {
                "id": e.id,
                "proposal_id": e.proposal_id,
                "action_type": e.action_type,
                "status": e.status,
                "risk_level": e.risk_level,
                "approved_by": e.approved_by,
                "result": e.result,
                "error_message": e.error_message,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "executed_at": e.executed_at.isoformat() if e.executed_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            }
            for e in executions[:limit]
        ],
        "total": len(executions),
    }


@router.get("/history", response_model=ExecutionListResponse)
async def get_execution_history(
    limit: int = 100,
    offset: int = 0,
):
    """
    Get execution history.
    
    Returns paginated execution history.
    """
    logger = get_execution_logger()
    records = logger.get_history(limit=limit, offset=offset)
    
    return {
        "executions": [r.to_dict() for r in records],
        "total": len(logger._records),
    }


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution_details(
    execution_id: str,
):
    """
    Retrieve execution details.
    
    Returns detailed information about a specific execution.
    """
    engine = get_execution_engine()
    execution = engine.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    return {
        "id": execution.id,
        "proposal_id": execution.proposal_id,
        "action_type": execution.action_type,
        "status": execution.status,
        "risk_level": execution.risk_level,
        "approved_by": execution.approved_by,
        "result": execution.result,
        "error_message": execution.error_message,
        "created_at": execution.created_at.isoformat() if execution.created_at else None,
        "executed_at": execution.executed_at.isoformat() if execution.executed_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
    }


@router.post("/execute", response_model=ExecutionResponse)
async def execute_action(
    request: CreateExecutionRequest,
):
    """
    Execute an approved action.
    
    Creates and executes an action from an approved strategy proposal.
    """
    engine = get_execution_engine()
    
    # Validate action type
    try:
        action_type = ActionType(request.action_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action type: {request.action_type}"
        )
    
    # Create execution request
    execution_request = await engine.create_execution_request(
        proposal_id=request.proposal_id,
        action_type=action_type,
        parameters=request.parameters,
        risk_level=request.risk_level,
        governance_decision_id=request.governance_decision_id,
        approved_by=request.approved_by,
    )
    
    # Execute the action
    result = await engine.execute(execution_request)
    
    # Convert to response
    response = {
        "id": execution_request.id,
        "proposal_id": execution_request.proposal_id,
        "action_type": execution_request.action_type,
        "status": execution_request.status,
        "risk_level": execution_request.risk_level,
        "approved_by": execution_request.approved_by,
        "result": result.result_data if result.success else None,
        "error_message": result.error if not result.success else None,
        "created_at": execution_request.created_at.isoformat() if execution_request.created_at else None,
        "executed_at": execution_request.executed_at.isoformat() if execution_request.executed_at else None,
        "completed_at": execution_request.completed_at.isoformat() if execution_request.completed_at else None,
    }
    
    return response


@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
):
    """
    Cancel an execution.
    
    Cancels a pending or executing action.
    """
    engine = get_execution_engine()
    
    success = engine.cancel_execution(execution_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel execution - not found or already completed"
        )
    
    return {
        "id": execution_id,
        "status": "cancelled",
        "message": "Execution cancelled successfully"
    }


@router.get("/statistics/summary", response_model=ExecutionStatisticsResponse)
async def get_execution_statistics():
    """
    Get execution statistics.
    
    Returns aggregate statistics about execution activity.
    """
    engine = get_execution_engine()
    stats = engine.get_statistics()
    
    return stats


# ============ Proposal Integration Endpoints ============

@router.get("/proposal/{proposal_id}/executions")
async def get_proposal_executions(
    proposal_id: str,
):
    """
    Get all executions for a proposal.
    
    Returns all execution attempts for a specific proposal.
    """
    engine = get_execution_engine()
    executions = engine.get_executions_by_proposal(proposal_id)
    
    return {
        "proposal_id": proposal_id,
        "executions": [
            {
                "id": e.id,
                "action_type": e.action_type,
                "status": e.status,
                "result": e.result,
                "error_message": e.error_message,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            }
            for e in executions
        ],
        "total": len(executions),
    }


# ============ Utility Endpoints ============

@router.post("/reset")
async def reset_execution_engine():
    """
    Reset the execution engine.
    
    WARNING: This clears all in-memory execution state.
    """
    reset_execution_engine()
    logger.info("Execution engine reset")
    
    return {
        "message": "Execution engine reset successfully"
    }


@router.get("/supported-actions")
async def list_supported_actions():
    """
    List all supported action types.
    
    Returns all action types that can be executed.
    """
    router_instance = get_action_router()
    actions = router_instance.list_supported_actions()
    
    return {
        "supported_actions": actions
    }


# Import required functions
from app.execution_engine.action_router import get_action_router
from app.execution_engine.execution_logger import get_execution_logger
