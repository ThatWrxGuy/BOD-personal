"""
BB-APP-003: Lifecycle Models

Defines lifecycle states and events for recommendations and actions.
Per BB-APP-003 Section 3 & 4 - Lifecycle Governance.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# ============== Recommendation Lifecycle States ==============

class RecommendationState(str, Enum):
    """Recommendation lifecycle states."""
    GENERATED = "generated"
    PRESENTED = "presented"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    CONVERTED_TO_ACTION = "converted_to_action"
    ARCHIVED = "archived"


# ============== Action Lifecycle States ==============

class ActionState(str, Enum):
    """Action lifecycle states."""
    CREATED = "created"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELED = "canceled"


# ============== Lifecycle Event Types ==============

class LifecycleEventType(str, Enum):
    """Types of lifecycle events."""
    # Recommendation events
    RECOMMENDATION_GENERATED = "recommendation_generated"
    RECOMMENDATION_PRESENTED = "recommendation_presented"
    RECOMMENDATION_APPROVED = "recommendation_approved"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    RECOMMENDATION_DEFERRED = "recommendation_deferred"
    RECOMMENDATION_CONVERTED = "recommendation_converted"
    RECOMMENDATION_ARCHIVED = "recommendation_archived"
    
    # Action events
    ACTION_CREATED = "action_created"
    ACTION_SCHEDULED = "action_scheduled"
    ACTION_STARTED = "action_started"
    ACTION_BLOCKED = "action_blocked"
    ACTION_COMPLETED = "action_completed"
    ACTION_CANCELED = "action_canceled"
    ACTION_OUTCOME_RECORDED = "action_outcome_recorded"


# ============== Lifecycle Event Model ==============

@dataclass
class LifecycleEvent:
    """Record of a lifecycle state transition."""
    id: str
    entity_type: str  # "recommendation" or "action"
    entity_id: str
    event_type: LifecycleEventType
    previous_state: str
    new_state: str
    actor: str  # "system" or user_id
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


# ============== Action Outcome Model ==============

@dataclass
class ActionOutcome:
    """Record of action completion outcome."""
    id: str
    action_id: str
    success_score: float  # 0.0 - 1.0
    impact_domains: list[str] = field(default_factory=list)
    financial_impact: Optional[float] = None
    time_cost_minutes: int = 0
    stress_level: int = 0  # 1-5
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


# ============== Audit Event Model ==============

@dataclass
class AuditEvent:
    """Central audit log record."""
    id: str
    event_type: str
    entity_type: str
    entity_id: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    actor: str = "system"
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


# ============== Transition Result ==============

@dataclass
class TransitionResult:
    """Result of a lifecycle transition attempt."""
    success: bool
    message: str
    event: Optional[LifecycleEvent] = None
    new_state: Optional[str] = None
    error_code: Optional[str] = None


__all__ = [
    "RecommendationState",
    "ActionState",
    "LifecycleEventType",
    "LifecycleEvent",
    "ActionOutcome",
    "AuditEvent",
    "TransitionResult",
]
