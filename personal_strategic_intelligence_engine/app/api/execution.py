"""Execution API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.execution.execution_engine import ExecutionEngine
from app.execution.action_types import ActionType
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/execution", tags=["execution"])


@router.get("/pending")
async def list_pending(
    session: AsyncSession = Depends(get_db),
):
    """List pending executions."""
    engine = ExecutionEngine(session)
    pending = await engine.list_pending()
    
    return {
        "executions": [
            {
                "id": str(e.id),
                "action_type": e.action_type,
                "status": e.status,
                "risk_score": e.risk_score,
                "payload": e.payload,
                "created_at": e.created_at.isoformat(),
            }
            for e in pending
        ]
    }


@router.get("/executing")
async def list_executing(
    session: AsyncSession = Depends(get_db),
):
    """List currently executing actions."""
    engine = ExecutionEngine(session)
    executing = await engine.list_executing()
    
    return {
        "executions": [
            {
                "id": str(e.id),
                "action_type": e.action_type,
                "status": e.status,
                "execution_start": e.execution_start.isoformat() if e.execution_start else None,
            }
            for e in executing
        ]
    }


@router.get("/history")
async def get_history(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """Get execution history."""
    engine = ExecutionEngine(session)
    history = await engine.get_history(limit)
    
    return {
        "history": [
            {
                "id": str(h.id),
                "execution_id": str(h.execution_id),
                "action_type": h.action_type,
                "status": h.status,
                "timestamp": h.timestamp.isoformat(),
                "details": h.details,
            }
            for h in history
        ]
    }


@router.post("/create")
async def create_execution(
    action_type: str,
    payload: dict,
    decision_id: Optional[str] = None,
    approval_type: str = "MANUAL_APPROVAL_REQUIRED",
    session: AsyncSession = Depends(get_db),
):
    """Create a new execution."""
    # Validate action type
    try:
        ActionType(action_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action type: {action_type}"
        )
    
    engine = ExecutionEngine(session)
    
    execution = await engine.create_execution(
        action_type=action_type,
        payload=payload,
        decision_id=uuid.UUID(decision_id) if decision_id else None,
        approval_type=approval_type,
    )
    
    return {
        "id": str(execution.id),
        "action_type": execution.action_type,
        "status": execution.status,
        "risk_score": execution.risk_score,
    }


@router.post("/{execution_id}/validate")
async def validate_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Validate an execution."""
    engine = ExecutionEngine(session)
    
    try:
        is_valid, error = await engine.validate_execution(uuid.UUID(execution_id))
        
        return {
            "valid": is_valid,
            "error": error,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{execution_id}/approve")
async def approve_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Approve an execution."""
    engine = ExecutionEngine(session)
    
    try:
        execution = await engine.approve_execution(uuid.UUID(execution_id))
        
        return {
            "id": str(execution.id),
            "status": execution.status,
            "message": "Execution approved",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{execution_id}/reject")
async def reject_execution(
    execution_id: str,
    reason: str = "Rejected by user",
    session: AsyncSession = Depends(get_db),
):
    """Reject an execution."""
    engine = ExecutionEngine(session)
    
    try:
        execution = await engine.reject_execution(uuid.UUID(execution_id), reason)
        
        return {
            "id": str(execution.id),
            "status": execution.status,
            "message": "Execution rejected",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{execution_id}/run")
async def run_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Run an approved execution."""
    engine = ExecutionEngine(session)
    
    try:
        execution = await engine.execute(uuid.UUID(execution_id))
        
        return {
            "id": str(execution.id),
            "status": execution.status,
            "result": execution.result,
            "error_message": execution.error_message,
            "execution_duration": execution.execution_duration,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{execution_id}")
async def get_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get execution details."""
    engine = ExecutionEngine(session)
    
    try:
        execution = await engine.get_execution(uuid.UUID(execution_id))
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "id": str(execution.id),
            "decision_id": str(execution.decision_id) if execution.decision_id else None,
            "action_type": execution.action_type,
            "status": execution.status,
            "approval_type": execution.approval_type,
            "risk_score": execution.risk_score,
            "validated": execution.validated,
            "validation_message": execution.validation_message,
            "payload": execution.payload,
            "result": execution.result,
            "error_message": execution.error_message,
            "retry_count": execution.retry_count,
            "execution_start": execution.execution_start.isoformat() if execution.execution_start else None,
            "execution_end": execution.execution_end.isoformat() if execution.execution_end else None,
            "execution_duration": execution.execution_duration,
            "created_at": execution.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


@router.get("/connectors/status")
async def get_connector_status(
    session: AsyncSession = Depends(get_db),
):
    """Get connector status."""
    from sqlalchemy import select
    from app.models.execution_record import ConnectorStatus
    
    result = await session.execute(select(ConnectorStatus))
    connectors = list(result.scalars().all())
    
    return {
        "connectors": [
            {
                "name": c.connector_name,
                "is_connected": c.is_connected,
                "last_check": c.last_check.isoformat() if c.last_check else None,
                "last_error": c.last_error,
            }
            for c in connectors
        ]
    }
