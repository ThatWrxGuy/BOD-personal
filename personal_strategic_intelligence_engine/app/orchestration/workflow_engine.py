"""Workflow Engine - Orchestrates multi-step workflows."""
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import EventBus
from app.orchestration.workflow_state_machine import (
    WorkflowStateMachine,
    WorkflowState,
    InvalidTransitionError,
)
from app.models.orchestration import WorkflowInstance, WorkflowStateTransition
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowEngine:
    """Orchestrates multi-step workflows through state transitions."""
    
    def __init__(self, session: AsyncSession, event_bus: EventBus):
        self.session = session
        self.event_bus = event_bus
        self._workflow_handlers: Dict[str, Callable] = {}
    
    async def start_workflow(
        self,
        workflow_name: str,
        workflow_type: str,
        initial_context: Dict[str, Any],
    ) -> WorkflowInstance:
        """Start a new workflow instance."""
        
        state_machine = WorkflowStateMachine(workflow_type)
        initial_state = state_machine.get_initial_state()
        
        instance = WorkflowInstance(
            workflow_id=workflow_type,
            workflow_name=workflow_name,
            current_state=initial_state,
            context=initial_context,
            status="running",
            started_at=datetime.utcnow(),
        )
        
        self.session.add(instance)
        
        # Log initial transition
        transition = WorkflowStateTransition(
            workflow_instance_id=instance.id,
            from_state=None,
            to_state=initial_state,
            trigger_event="WORKFLOW_STARTED",
            timestamp=datetime.utcnow(),
            metadata={"workflow_name": workflow_name},
        )
        self.session.add(transition)
        
        await self.session.commit()
        await self.session.refresh(instance)
        
        # Publish workflow started event
        await self.event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_STARTED,
                payload={
                    "workflow_id": str(instance.id),
                    "workflow_name": workflow_name,
                    "workflow_type": workflow_type,
                    "initial_state": initial_state,
                },
                source_module="workflow_engine",
                workflow_id=instance.id,
            )
        )
        
        logger.info(f"Started workflow {workflow_name} with id {instance.id}")
        
        return instance
    
    async def transition_workflow(
        self,
        workflow_id: uuid.UUID,
        to_state: str,
        trigger_event: str,
        context_updates: Optional[Dict[str, Any]] = None,
    ) -> WorkflowInstance:
        """Transition a workflow to a new state."""
        
        # Get workflow instance
        result = await self.session.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == workflow_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise ValueError(f"Workflow instance {workflow_id} not found")
        
        # Validate transition
        state_machine = WorkflowStateMachine(instance.workflow_id)
        state_machine.validate_transition(instance.current_state, to_state)
        
        previous_state = instance.current_state
        
        # Update instance
        instance.previous_state = previous_state
        instance.current_state = to_state
        
        if context_updates:
            instance.context = instance.context or {}
            instance.context.update(context_updates)
        
        # Log transition
        transition = WorkflowStateTransition(
            workflow_instance_id=instance.id,
            from_state=previous_state,
            to_state=to_state,
            trigger_event=trigger_event,
            timestamp=datetime.utcnow(),
            metadata=context_updates,
        )
        self.session.add(transition)
        
        # Check if terminal state
        if to_state in state_machine.get_terminal_states():
            instance.completed_at = datetime.utcnow()
            
            if to_state == WorkflowState.FAILED:
                instance.status = "failed"
            elif to_state == WorkflowState.CANCELLED:
                instance.status = "cancelled"
            else:
                instance.status = "completed"
            
            # Publish workflow completed event
            await self.event_bus.publish_event(
                DomainEvent(
                    event_type=EventType.WORKFLOW_COMPLETED,
                    payload={
                        "workflow_id": str(instance.id),
                        "final_state": to_state,
                        "status": instance.status,
                    },
                    source_module="workflow_engine",
                    workflow_id=instance.id,
                )
            )
        
        await self.session.commit()
        await self.session.refresh(instance)
        
        logger.info(f"Workflow {workflow_id} transitioned from {previous_state} to {to_state}")
        
        return instance
    
    async def fail_workflow(
        self,
        workflow_id: uuid.UUID,
        error_message: str,
    ) -> WorkflowInstance:
        """Mark a workflow as failed."""
        
        result = await self.session.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == workflow_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise ValueError(f"Workflow instance {workflow_id} not found")
        
        instance.current_state = WorkflowState.FAILED
        instance.status = "failed"
        instance.error_message = error_message
        instance.completed_at = datetime.utcnow()
        
        # Log transition
        transition = WorkflowStateTransition(
            workflow_instance_id=instance.id,
            from_state=instance.previous_state,
            to_state=WorkflowState.FAILED,
            trigger_event="WORKFLOW_FAILED",
            timestamp=datetime.utcnow(),
            metadata={"error": error_message},
        )
        self.session.add(transition)
        
        # Publish workflow failed event
        await self.event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_FAILED,
                payload={
                    "workflow_id": str(instance.id),
                    "error": error_message,
                },
                source_module="workflow_engine",
                workflow_id=instance.id,
            )
        )
        
        await self.session.commit()
        await self.session.refresh(instance)
        
        logger.error(f"Workflow {workflow_id} failed: {error_message}")
        
        return instance
    
    async def get_workflow(self, workflow_id: uuid.UUID) -> Optional[WorkflowInstance]:
        """Get a workflow instance by ID."""
        
        result = await self.session.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == workflow_id)
        )
        return result.scalar_one_or_none()
    
    async def list_workflows(
        self,
        workflow_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[WorkflowInstance]:
        """List workflow instances."""
        
        query = select(WorkflowInstance)
        
        if workflow_type:
            query = query.where(WorkflowInstance.workflow_id == workflow_type)
        
        if status:
            query = query.where(WorkflowInstance.status == status)
        
        query = query.order_by(WorkflowInstance.created_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_workflow_history(
        self,
        workflow_id: uuid.UUID,
    ) -> List[WorkflowStateTransition]:
        """Get the state transition history for a workflow."""
        
        result = await self.session.execute(
            select(WorkflowStateTransition)
            .where(WorkflowStateTransition.workflow_instance_id == workflow_id)
            .order_by(WorkflowStateTransition.timestamp)
        )
        return list(result.scalars().all())


async def get_workflow_engine(session: AsyncSession) -> WorkflowEngine:
    """Get workflow engine instance."""
    event_bus = EventBus(session)
    return WorkflowEngine(session, event_bus)
