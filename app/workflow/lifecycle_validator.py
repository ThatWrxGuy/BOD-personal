"""
BB-APP-003: Lifecycle Validator

Validates and enforces lifecycle state transitions.
Per BB-APP-003 Section 3 & 4 - Lifecycle Governance.
"""

from typing import Optional

from app.workflow.lifecycle_models import (
    RecommendationState,
    ActionState,
    LifecycleEventType,
    TransitionResult,
)


class LifecycleValidator:
    """Validates lifecycle state transitions."""
    
    # Recommendation state transitions
    RECOMMENDATION_TRANSITIONS = {
        RecommendationState.GENERATED: [
            RecommendationState.PRESENTED,
            RecommendationState.ARCHIVED,
        ],
        RecommendationState.PRESENTED: [
            RecommendationState.APPROVED,
            RecommendationState.REJECTED,
            RecommendationState.DEFERRED,
            RecommendationState.ARCHIVED,
        ],
        RecommendationState.APPROVED: [
            RecommendationState.CONVERTED_TO_ACTION,
            RecommendationState.ARCHIVED,
        ],
        RecommendationState.REJECTED: [
            RecommendationState.ARCHIVED,
        ],
        RecommendationState.DEFERRED: [
            RecommendationState.PRESENTED,  # Can be reconsidered
            RecommendationState.REJECTED,
            RecommendationState.APPROVED,
            RecommendationState.ARCHIVED,
        ],
        RecommendationState.CONVERTED_TO_ACTION: [
            RecommendationState.ARCHIVED,
        ],
        RecommendationState.ARCHIVED: [],  # Terminal state
    }
    
    # Action state transitions
    ACTION_TRANSITIONS = {
        ActionState.CREATED: [
            ActionState.SCHEDULED,
            ActionState.IN_PROGRESS,
            ActionState.CANCELED,
        ],
        ActionState.SCHEDULED: [
            ActionState.IN_PROGRESS,
            ActionState.CANCELED,
        ],
        ActionState.IN_PROGRESS: [
            ActionState.COMPLETED,
            ActionState.BLOCKED,
            ActionState.CANCELED,
        ],
        ActionState.BLOCKED: [
            ActionState.IN_PROGRESS,
            ActionState.CANCELED,
        ],
        ActionState.COMPLETED: [],  # Terminal state
        ActionState.CANCELED: [],  # Terminal state
    }
    
    @classmethod
    def validate_recommendation_transition(
        cls,
        current_state: RecommendationState,
        target_state: RecommendationState,
    ) -> TransitionResult:
        """Validate recommendation state transition."""
        allowed = cls.RECOMMENDATION_TRANSITIONS.get(current_state, [])
        
        if target_state in allowed:
            return TransitionResult(
                success=True,
                message=f"Valid transition from {current_state.value} to {target_state.value}",
                new_state=target_state.value,
            )
        
        return TransitionResult(
            success=False,
            message=f"Invalid transition from {current_state.value} to {target_state.value}",
            error_code="INVALID_TRANSITION",
        )
    
    @classmethod
    def validate_action_transition(
        cls,
        current_state: ActionState,
        target_state: ActionState,
    ) -> TransitionResult:
        """Validate action state transition."""
        allowed = cls.ACTION_TRANSITIONS.get(current_state, [])
        
        if target_state in allowed:
            return TransitionResult(
                success=True,
                message=f"Valid transition from {current_state.value} to {target_state.value}",
                new_state=target_state.value,
            )
        
        return TransitionResult(
            success=False,
            message=f"Invalid transition from {current_state.value} to {target_state.value}",
            error_code="INVALID_TRANSITION",
        )
    
    @classmethod
    def can_approve_recommendation(cls, current_state: RecommendationState) -> bool:
        """Check if recommendation can be approved."""
        result = cls.validate_recommendation_transition(
            current_state, RecommendationState.APPROVED
        )
        return result.success
    
    @classmethod
    def can_reject_recommendation(cls, current_state: RecommendationState) -> bool:
        """Check if recommendation can be rejected."""
        result = cls.validate_recommendation_transition(
            current_state, RecommendationState.REJECTED
        )
        return result.success
    
    @classmethod
    def can_defer_recommendation(cls, current_state: RecommendationState) -> bool:
        """Check if recommendation can be deferred."""
        result = cls.validate_recommendation_transition(
            current_state, RecommendationState.DEFERRED
        )
        return result.success
    
    @classmethod
    def can_convert_to_action(cls, current_state: RecommendationState) -> bool:
        """Check if recommendation can be converted to action."""
        result = cls.validate_recommendation_transition(
            current_state, RecommendationState.CONVERTED_TO_ACTION
        )
        return result.success
    
    @classmethod
    def can_start_action(cls, current_state: ActionState) -> bool:
        """Check if action can be started."""
        result = cls.validate_action_transition(
            current_state, ActionState.IN_PROGRESS
        )
        return result.success
    
    @classmethod
    def can_complete_action(cls, current_state: ActionState) -> bool:
        """Check if action can be completed."""
        result = cls.validate_action_transition(
            current_state, ActionState.COMPLETED
        )
        return result.success
    
    @classmethod
    def is_terminal_state(cls, entity_type: str, state: str) -> bool:
        """Check if state is terminal."""
        if entity_type == "recommendation":
            return state == RecommendationState.ARCHIVED.value
        elif entity_type == "action":
            return state in [ActionState.COMPLETED.value, ActionState.CANCELED.value]
        return False


# Singleton instance
lifecycle_validator = LifecycleValidator()
