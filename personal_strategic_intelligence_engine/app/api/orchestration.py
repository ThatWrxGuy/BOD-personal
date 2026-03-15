"""Orchestration API routes."""
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.orchestration.event_bus import get_event_bus
from app.orchestration.workflow_engine import get_workflow_engine
from app.orchestration.event_types import DomainEvent, EventType, create_signal_created_event
from app.models.orchestration import EventRecord, WorkflowInstance
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


# ===================
# Event Endpoints
# ===================

@router.get("/events")
async def list_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    """List stored events."""
    
    query = select(EventRecord).order_by(desc(EventRecord.timestamp)).limit(limit)
    
    if event_type:
        query = query.where(EventRecord.event_type == event_type)
    
    result = await session.execute(query)
    events = result.scalars().all()
    
    return {
        "events": [
            {
                "id": str(e.id),
                "event_id": str(e.event_id),
                "event_type": e.event_type,
                "source": e.source,
                "timestamp": e.timestamp.isoformat(),
                "correlation_id": str(e.correlation_id) if e.correlation_id else None,
                "workflow_id": str(e.workflow_id) if e.workflow_id else None,
            }
            for e in events
        ]
    }


@router.get("/events/{event_id}")
async def get_event(
    event_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific event by ID."""
    
    result = await session.execute(
        select(EventRecord).where(EventRecord.event_id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {
        "id": str(event.id),
        "event_id": str(event.event_id),
        "event_type": event.event_type,
        "source": event.source,
        "payload": event.payload,
        "timestamp": event.timestamp.isoformat(),
        "correlation_id": str(event.correlation_id) if event.correlation_id else None,
        "workflow_id": str(event.workflow_id) if event.workflow_id else None,
        "processed": event.processed,
    }


@router.post("/events/publish")
async def publish_event(
    event_type: str,
    payload: dict,
    source_module: str = "api",
    session: AsyncSession = Depends(get_db),
):
    """Publish a custom event."""
    
    event = DomainEvent(
        event_type=event_type,
        payload=payload,
        source_module=source_module,
    )
    
    event_bus = get_event_bus(session)
    await event_bus.publish_event(event)
    
    return {
        "message": "Event published",
        "event_id": str(event.event_id),
        "event_type": event_type,
    }


# ===================
# Workflow Endpoints
# ===================

@router.get("/workflows")
async def list_workflows(
    workflow_type: Optional[str] = Query(None, description="Filter by workflow type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    """List workflow instances."""
    
    query = select(WorkflowInstance).order_by(desc(WorkflowInstance.created_at)).limit(limit)
    
    if workflow_type:
        query = query.where(WorkflowInstance.workflow_id == workflow_type)
    
    if status:
        query = query.where(WorkflowInstance.status == status)
    
    result = await session.execute(query)
    workflows = result.scalars().all()
    
    return {
        "workflows": [
            {
                "id": str(w.id),
                "workflow_id": w.workflow_id,
                "workflow_name": w.workflow_name,
                "current_state": w.current_state,
                "status": w.status,
                "started_at": w.started_at.isoformat() if w.started_at else None,
                "completed_at": w.completed_at.isoformat() if w.completed_at else None,
            }
            for w in workflows
        ]
    }


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific workflow instance."""
    
    result = await session.execute(
        select(WorkflowInstance).where(WorkflowInstance.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "id": str(workflow.id),
        "workflow_id": workflow.workflow_id,
        "workflow_name": workflow.workflow_name,
        "current_state": workflow.current_state,
        "previous_state": workflow.previous_state,
        "context": workflow.context,
        "status": workflow.status,
        "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
        "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
        "error_message": workflow.error_message,
    }


@router.post("/workflows/start")
async def start_workflow(
    workflow_name: str,
    workflow_type: str,
    initial_context: dict = {},
    session: AsyncSession = Depends(get_db),
):
    """Start a new workflow instance."""
    
    from app.orchestration.workflow_engine import WorkflowEngine
    
    event_bus = get_event_bus(session)
    engine = WorkflowEngine(session, event_bus)
    
    workflow = await engine.start_workflow(
        workflow_name=workflow_name,
        workflow_type=workflow_type,
        initial_context=initial_context,
    )
    
    return {
        "message": "Workflow started",
        "workflow_id": str(workflow.id),
        "workflow_name": workflow_name,
        "initial_state": workflow.current_state,
    }


@router.post("/workflows/{workflow_id}/transition")
async def transition_workflow(
    workflow_id: uuid.UUID,
    to_state: str,
    trigger_event: str,
    context_updates: dict = {},
    session: AsyncSession = Depends(get_db),
):
    """Transition a workflow to a new state."""
    
    event_bus = get_event_bus(session)
    from app.orchestration.workflow_engine import WorkflowEngine
    
    engine = WorkflowEngine(session, event_bus)
    
    try:
        workflow = await engine.transition_workflow(
            workflow_id=workflow_id,
            to_state=to_state,
            trigger_event=trigger_event,
            context_updates=context_updates,
        )
        
        return {
            "message": "Workflow transitioned",
            "workflow_id": str(workflow.id),
            "previous_state": workflow.previous_state,
            "current_state": workflow.current_state,
            "status": workflow.status,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}/history")
async def get_workflow_history(
    workflow_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get the state transition history for a workflow."""
    
    event_bus = get_event_bus(session)
    from app.orchestration.workflow_engine import WorkflowEngine
    
    engine = WorkflowEngine(session, event_bus)
    history = await engine.get_workflow_history(workflow_id)
    
    return {
        "transitions": [
            {
                "id": str(t.id),
                "from_state": t.from_state,
                "to_state": t.to_state,
                "trigger_event": t.trigger_event,
                "timestamp": t.timestamp.isoformat(),
                "metadata": t.metadata,
            }
            for t in history
        ]
    }
