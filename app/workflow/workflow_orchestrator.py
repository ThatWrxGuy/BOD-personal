"""
BB-APP-003: Workflow Orchestrator

Central workflow orchestration with lifecycle validation and event emission.
Per BB-APP-003 Section 5 - Workflow Orchestration Engine.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.workflow.lifecycle_models import (
    RecommendationState,
    ActionState,
    LifecycleEventType,
    LifecycleEvent,
    TransitionResult,
)
from app.workflow.lifecycle_validator import lifecycle_validator
from app.events.event_bus import event_bus, EventFactory, ApplicationEventType
from app.audit.audit_log_service import audit_log_service
from app.application.recommendations.service import recommendations_service
from app.application.actions.service import actions_service


class WorkflowOrchestrator:
    """
    Central workflow orchestration service.
    
    Responsibilities:
    - Manage recommendation → action transitions
    - Validate lifecycle transitions
    - Emit system events
    - Update read models
    - Ensure auditability
    """
    
    def __init__(self):
        self._recommendation_states: dict[str, RecommendationState] = {}
        self._action_states: dict[str, ActionState] = {}
    
    def _create_lifecycle_event(
        self,
        entity_type: str,
        entity_id: str,
        event_type: LifecycleEventType,
        previous_state: str,
        new_state: str,
        actor: str,
        reason: str = "",
    ) -> LifecycleEvent:
        """Create a lifecycle event."""
        return LifecycleEvent(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            previous_state=previous_state,
            new_state=new_state,
            actor=actor,
            reason=reason,
        )
    
    def _log_audit(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        actor: str,
        previous_state: Optional[str],
        new_state: Optional[str],
        reason: str = "",
    ):
        """Log to audit service."""
        audit_log_service.log_event(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
        )
    
    # ============== Recommendation Workflows ==============
    
    def approve_recommendation(
        self,
        recommendation_id: str,
        user_id: str,
        notes: str = "",
    ) -> TransitionResult:
        """Approve a recommendation."""
        # Get current state
        current_state = self._recommendation_states.get(
            recommendation_id, RecommendationState.PRESENTED
        )
        
        # Validate transition
        validation = lifecycle_validator.validate_recommendation_transition(
            current_state, RecommendationState.APPROVED
        )
        
        if not validation.success:
            return validation
        
        # Create event
        event = self._create_lifecycle_event(
            entity_type="recommendation",
            entity_id=recommendation_id,
            event_type=LifecycleEventType.RECOMMENDATION_APPROVED,
            previous_state=current_state.value,
            new_state=RecommendationState.APPROVED.value,
            actor=user_id,
            reason=notes,
        )
        
        # Update state
        self._recommendation_states[recommendation_id] = RecommendationState.APPROVED
        
        # Emit application event
        event_bus.publish(EventFactory.recommendation_approved(
            recommendation_id, user_id, notes or "approved"
        ))
        
        # Log audit
        self._log_audit(
            event_type="recommendation_approved",
            entity_type="recommendation",
            entity_id=recommendation_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=RecommendationState.APPROVED.value,
            reason=notes,
        )
        
        return TransitionResult(
            success=True,
            message="Recommendation approved",
            event=event,
            new_state=RecommendationState.APPROVED.value,
        )
    
    def reject_recommendation(
        self,
        recommendation_id: str,
        user_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """Reject a recommendation."""
        current_state = self._recommendation_states.get(
            recommendation_id, RecommendationState.PRESENTED
        )
        
        validation = lifecycle_validator.validate_recommendation_transition(
            current_state, RecommendationState.REJECTED
        )
        
        if not validation.success:
            return validation
        
        event = self._create_lifecycle_event(
            entity_type="recommendation",
            entity_id=recommendation_id,
            event_type=LifecycleEventType.RECOMMENDATION_REJECTED,
            previous_state=current_state.value,
            new_state=RecommendationState.REJECTED.value,
            actor=user_id,
            reason=reason,
        )
        
        self._recommendation_states[recommendation_id] = RecommendationState.REJECTED
        
        event_bus.publish(EventFactory.recommendation_rejected(
            recommendation_id, user_id, reason
        ))
        
        self._log_audit(
            event_type="recommendation_rejected",
            entity_type="recommendation",
            entity_id=recommendation_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=RecommendationState.REJECTED.value,
            reason=reason,
        )
        
        return TransitionResult(
            success=True,
            message="Recommendation rejected",
            event=event,
            new_state=RecommendationState.REJECTED.value,
        )
    
    def defer_recommendation(
        self,
        recommendation_id: str,
        user_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """Defer a recommendation."""
        current_state = self._recommendation_states.get(
            recommendation_id, RecommendationState.PRESENTED
        )
        
        validation = lifecycle_validator.validate_recommendation_transition(
            current_state, RecommendationState.DEFERRED
        )
        
        if not validation.success:
            return validation
        
        event = self._create_lifecycle_event(
            entity_type="recommendation",
            entity_id=recommendation_id,
            event_type=LifecycleEventType.RECOMMENDATION_DEFERRED,
            previous_state=current_state.value,
            new_state=RecommendationState.DEFERRED.value,
            actor=user_id,
            reason=reason,
        )
        
        self._recommendation_states[recommendation_id] = RecommendationState.DEFERRED
        
        event_bus.publish(EventFactory.recommendation_deferred(
            recommendation_id, user_id, reason
        ))
        
        self._log_audit(
            event_type="recommendation_deferred",
            entity_type="recommendation",
            entity_id=recommendation_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=RecommendationState.DEFERRED.value,
            reason=reason,
        )
        
        return TransitionResult(
            success=True,
            message="Recommendation deferred",
            event=event,
            new_state=RecommendationState.DEFERRED.value,
        )
    
    def convert_to_action(
        self,
        recommendation_id: str,
        user_id: str,
        action_title: str,
        action_description: str = "",
        due_date: datetime = None,
    ) -> TransitionResult:
        """Convert a recommendation to an action."""
        # Check current state allows conversion
        current_state = self._recommendation_states.get(
            recommendation_id, RecommendationState.PRESENTED
        )
        
        if current_state != RecommendationState.APPROVED:
            # Try from presented if not yet approved
            if current_state == RecommendationState.PRESENTED:
                # Auto-approve when converting
                self.approve_recommendation(recommendation_id, user_id, "Auto-approved for conversion")
                current_state = RecommendationState.APPROVED
            else:
                return TransitionResult(
                    success=False,
                    message=f"Cannot convert recommendation in {current_state.value} state. Must be approved first.",
                    error_code="INVALID_STATE_FOR_CONVERSION",
                )
        
        # Create action
        action_id = actions_service.create_action(
            user_id=user_id,
            title=action_title,
            description=action_description,
            domain="",
            due_date=due_date,
            recommendation_id=recommendation_id,
        )
        
        # Update recommendation state
        event = self._create_lifecycle_event(
            entity_type="recommendation",
            entity_id=recommendation_id,
            event_type=LifecycleEventType.RECOMMENDATION_CONVERTED,
            previous_state=current_state.value,
            new_state=RecommendationState.CONVERTED_TO_ACTION.value,
            actor=user_id,
            reason=f"Created action {action_id}",
        )
        
        self._recommendation_states[recommendation_id] = RecommendationState.CONVERTED_TO_ACTION
        self._action_states[action_id] = ActionState.CREATED
        
        # Emit events
        event_bus.publish(EventFactory.recommendation_converted(
            recommendation_id, action_id, user_id
        ))
        event_bus.publish(EventFactory.action_created(
            action_id, user_id, "", from_recommendation=True
        ))
        
        # Audit
        self._log_audit(
            event_type="recommendation_converted",
            entity_type="recommendation",
            entity_id=recommendation_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=RecommendationState.CONVERTED_TO_ACTION.value,
            reason=f"Created action {action_id}",
        )
        
        return TransitionResult(
            success=True,
            message="Recommendation converted to action",
            event=event,
            new_state=RecommendationState.CONVERTED_TO_ACTION.value,
        )
    
    # ============== Action Workflows ==============
    
    def start_action(
        self,
        action_id: str,
        user_id: str,
    ) -> TransitionResult:
        """Start an action."""
        current_state = self._action_states.get(action_id, ActionState.CREATED)
        
        validation = lifecycle_validator.validate_action_transition(
            current_state, ActionState.IN_PROGRESS
        )
        
        if not validation.success:
            return validation
        
        event = self._create_lifecycle_event(
            entity_type="action",
            entity_id=action_id,
            event_type=LifecycleEventType.ACTION_STARTED,
            previous_state=current_state.value,
            new_state=ActionState.IN_PROGRESS.value,
            actor=user_id,
        )
        
        self._action_states[action_id] = ActionState.IN_PROGRESS
        
        event_bus.publish(EventFactory.action_started(action_id, user_id))
        
        self._log_audit(
            event_type="action_started",
            entity_type="action",
            entity_id=action_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=ActionState.IN_PROGRESS.value,
        )
        
        return TransitionResult(
            success=True,
            message="Action started",
            event=event,
            new_state=ActionState.IN_PROGRESS.value,
        )
    
    def complete_action(
        self,
        action_id: str,
        user_id: str,
        success_score: float = 0.5,
    ) -> TransitionResult:
        """Complete an action."""
        current_state = self._action_states.get(action_id, ActionState.IN_PROGRESS)
        
        validation = lifecycle_validator.validate_action_transition(
            current_state, ActionState.COMPLETED
        )
        
        if not validation.success:
            return validation
        
        event = self._create_lifecycle_event(
            entity_type="action",
            entity_id=action_id,
            event_type=LifecycleEventType.ACTION_COMPLETED,
            previous_state=current_state.value,
            new_state=ActionState.COMPLETED.value,
            actor=user_id,
        )
        
        self._action_states[action_id] = ActionState.COMPLETED
        
        event_bus.publish(EventFactory.action_completed(action_id, user_id, success_score))
        
        self._log_audit(
            event_type="action_completed",
            entity_type="action",
            entity_id=action_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=ActionState.COMPLETED.value,
        )
        
        return TransitionResult(
            success=True,
            message="Action completed",
            event=event,
            new_state=ActionState.COMPLETED.value,
        )
    
    def record_outcome(
        self,
        action_id: str,
        user_id: str,
        success_score: float,
        notes: str = "",
        financial_impact: float = None,
        time_cost: int = 0,
    ) -> TransitionResult:
        """Record action outcome."""
        current_state = self._action_states.get(action_id, ActionState.IN_PROGRESS)
        
        # Ensure action is at least in progress
        if current_state not in [ActionState.IN_PROGRESS, ActionState.COMPLETED]:
            return TransitionResult(
                success=False,
                message=f"Cannot record outcome for action in {current_state.value} state",
                error_code="INVALID_STATE_FOR_OUTCOME",
            )
        
        event = self._create_lifecycle_event(
            entity_type="action",
            entity_id=action_id,
            event_type=LifecycleEventType.ACTION_OUTCOME_RECORDED,
            previous_state=current_state.value,
            new_state="outcome_recorded",
            actor=user_id,
            reason=notes,
        )
        
        event_bus.publish(EventFactory.action_outcome_recorded(
            action_id, user_id, str(uuid.uuid4())
        ))
        
        self._log_audit(
            event_type="action_outcome_recorded",
            entity_type="action",
            entity_id=action_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state="outcome_recorded",
            reason=notes,
        )
        
        return TransitionResult(
            success=True,
            message="Outcome recorded",
            event=event,
            new_state="outcome_recorded",
        )
    
    def cancel_action(
        self,
        action_id: str,
        user_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """Cancel an action."""
        current_state = self._action_states.get(action_id, ActionState.CREATED)
        
        validation = lifecycle_validator.validate_action_transition(
            current_state, ActionState.CANCELED
        )
        
        if not validation.success:
            return validation
        
        event = self._create_lifecycle_event(
            entity_type="action",
            entity_id=action_id,
            event_type=LifecycleEventType.ACTION_CANCELED,
            previous_state=current_state.value,
            new_state=ActionState.CANCELED.value,
            actor=user_id,
            reason=reason,
        )
        
        self._action_states[action_id] = ActionState.CANCELED
        
        self._log_audit(
            event_type="action_canceled",
            entity_type="action",
            entity_id=action_id,
            actor=user_id,
            previous_state=current_state.value,
            new_state=ActionState.CANCELED.value,
            reason=reason,
        )
        
        return TransitionResult(
            success=True,
            message="Action canceled",
            event=event,
            new_state=ActionState.CANCELED.value,
        )
    
    # ============== Query Methods ==============
    
    def get_recommendation_state(self, recommendation_id: str) -> RecommendationState:
        """Get current state of a recommendation."""
        return self._recommendation_states.get(
            recommendation_id, RecommendationState.GENERATED
        )
    
    def get_action_state(self, action_id: str) -> ActionState:
        """Get current state of an action."""
        return self._action_states.get(action_id, ActionState.CREATED)
    
    def get_entity_timeline(self, entity_type: str, entity_id: str) -> list:
        """Get timeline of state changes for an entity."""
        return audit_log_service.get_entity_state_timeline(entity_type, entity_id)


# Singleton instance
workflow_orchestrator = WorkflowOrchestrator()
