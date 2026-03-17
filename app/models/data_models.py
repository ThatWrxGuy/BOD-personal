"""
BB-APP-001: Canonical Data Models

Required entities per BB-APP-001 Section 10:
- users, profiles, user_goals
- domain_state_snapshots
- raw_signals, normalized_signals, derived_signals
- recommendations, recommendation_explanations
- executive_briefs
- action_items, action_history
- memories
- review_cycles
- integrations
- system_jobs
- audit_logs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ============== Enums ==============

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class SignalSource(Enum):
    MANUAL = "manual"
    CALENDAR = "calendar"
    FINANCIAL = "financial"
    HEALTH = "health"
    TASK = "task"
    EMAIL = "email"
    API = "api"
    SYSTEM = "system"


class SignalType(str, Enum):
    EVENT = "event"
    OUTCOME = "outcome"
    METRIC = "metric"
    JOURNAL = "journal"
    CHECKIN = "checkin"
    IMPORT = "import"


class SignalStatus(str, Enum):
    RAW = "raw"
    NORMALIZED = "normalized"
    DERIVED = "derived"
    PROCESSED = "processed"
    STALE = "stale"


class RecommendationStatus(str, Enum):
    ACTIVE = "active"
    ACCEPTED = "accepted"
    DEFERRED = "deferred"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ActionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"


class ReviewType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ReviewStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ============== Helper Functions ==============

def create_user(email: str, username: str) -> "User":
    import uuid
    return User(id=str(uuid.uuid4()), email=email, username=username)


def create_signal(user_id: str, signal_type: SignalType, source: SignalSource, content: dict) -> "RawSignal":
    import uuid, json
    return RawSignal(id=str(uuid.uuid4()), user_id=user_id, signal_type=signal_type, source=source, raw_content=json.dumps(content))


def create_recommendation(user_id: str, title: str, description: str, domain: str, **kwargs) -> "Recommendation":
    import uuid
    return Recommendation(id=str(uuid.uuid4()), user_id=user_id, title=title, description=description, domain=domain, **kwargs)


# ============== Entities ==============

@dataclass
class User:
    id: str = ""
    email: str = ""
    username: str = ""
    status: UserStatus = UserStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login_at: datetime | None = None
    default_horizon: str = "weekly"
    notification_preference: str = "digest"


@dataclass
class Profile:
    id: str = ""
    user_id: str = ""
    life_stage: str = "early_career"
    finance_emphasis: int = 20
    health_emphasis: int = 20
    career_emphasis: int = 20
    relationships_emphasis: int = 20
    intelligence_emphasis: int = 10
    life_architecture_emphasis: int = 10
    operating_style: str = "balanced"
    planning_horizon_days: int = 7
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserGoal:
    id: str = ""
    user_id: str = ""
    title: str = ""
    description: str = ""
    domain: str = ""
    target_date: datetime | None = None
    progress: float = 0.0
    priority: int = 3
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RawSignal:
    id: str = ""
    user_id: str = ""
    source: SignalSource = SignalSource.MANUAL
    source_id: str | None = None
    signal_type: SignalType = SignalType.EVENT
    raw_content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    received_at: datetime = field(default_factory=datetime.now)
    status: SignalStatus = SignalStatus.RAW


@dataclass
class NormalizedSignal:
    id: str = ""
    user_id: str = ""
    raw_signal_id: str = ""
    domain: str = ""
    category: str = ""
    value: str = ""
    unit: str | None = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    status: SignalStatus = SignalStatus.NORMALIZED
    source: SignalSource = SignalSource.MANUAL


@dataclass
class DerivedSignal:
    id: str = ""
    user_id: str = ""
    source_signals: list[str] = field(default_factory=list)
    domain: str = ""
    signal_key: str = ""
    value: float = 0.0
    unit: str = "percentage"
    algorithm: str = "default"
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    status: SignalStatus = SignalStatus.DERIVED


@dataclass
class DomainStateSnapshot:
    id: str = ""
    user_id: str = ""
    domain: str = ""
    score: float = 50.0
    trend: str = "stable"
    signals_count: int = 0
    active_recommendations: int = 0
    pending_actions: int = 0
    status: str = "healthy"
    snapshot_at: datetime = field(default_factory=datetime.now)


@dataclass
class Recommendation:
    id: str = ""
    user_id: str = ""
    title: str = ""
    description: str = ""
    domain: str = ""
    recommendation_type: str = "action"
    urgency: int = 3
    confidence: float = 0.7
    status: RecommendationStatus = RecommendationStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    acknowledged_at: datetime | None = None


@dataclass
class RecommendationExplanation:
    id: str = ""
    recommendation_id: str = ""
    user_id: str = ""
    why_generated: str = ""
    influencing_signals: list[str] = field(default_factory=list)
    affected_domains: list[str] = field(default_factory=list)
    urgency_rationale: str = ""
    expected_benefit: str = ""
    likely_tradeoff: str = ""
    recommended_time_horizon: str = "this_week"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ActionItem:
    id: str = ""
    user_id: str = ""
    recommendation_id: str | None = None
    title: str = ""
    description: str = ""
    domain: str = ""
    due_date: datetime | None = None
    estimated_minutes: int = 30
    status: ActionStatus = ActionStatus.PENDING
    priority: int = 3
    is_recurring: bool = False
    recurrence_pattern: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None


@dataclass
class ActionHistory:
    id: str = ""
    action_id: str = ""
    user_id: str = ""
    previous_status: ActionStatus = ActionStatus.PENDING
    new_status: ActionStatus = ActionStatus.PENDING
    notes: str = ""
    effectiveness_score: float | None = None
    outcome_notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryEntry:
    id: str = ""
    user_id: str = ""
    title: str = ""
    content: str = ""
    memory_type: str = "note"
    tags: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    linked_signals: list[str] = field(default_factory=list)
    linked_actions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReviewCycle:
    id: str = ""
    user_id: str = ""
    review_type: ReviewType = ReviewType.WEEKLY
    status: ReviewStatus = ReviewStatus.IN_PROGRESS
    summary: str = ""
    progress_highlights: list[str] = field(default_factory=list)
    missed_priorities: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    next_week_focus: list[str] = field(default_factory=list)
    actions_completed: int = 0
    actions_missed: int = 0
    overall_score: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None


@dataclass
class ExecutiveBriefRecord:
    id: str = ""
    user_id: str = ""
    brief_data: dict[str, Any] = field(default_factory=dict)
    system_status: str = "healthy"
    strategic_posture: str = "neutral"
    readiness_score: float = 0.0
    signals_processed: int = 0
    active_recommendations: int = 0
    risk_alerts: int = 0
    generated_at: datetime = field(default_factory=datetime.now)
    valid_until: datetime | None = None


@dataclass
class Integration:
    id: str = ""
    user_id: str = ""
    integration_type: str = ""
    is_active: bool = True
    config: dict[str, Any] = field(default_factory=dict)
    last_sync_at: datetime | None = None
    sync_status: str = "idle"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SystemJob:
    id: str = ""
    job_type: str = ""
    status: str = "pending"
    progress: float = 0.0
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class AuditLog:
    id: str = ""
    user_id: str | None = None
    action: str = ""
    entity_type: str = ""
    entity_id: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
    user_agent: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


__all__ = [
    "UserStatus", "SignalSource", "SignalType", "SignalStatus",
    "RecommendationStatus", "ActionStatus", "ReviewType", "ReviewStatus",
    "User", "Profile", "UserGoal", "RawSignal", "NormalizedSignal",
    "DerivedSignal", "DomainStateSnapshot", "Recommendation",
    "RecommendationExplanation", "ActionItem", "ActionHistory",
    "MemoryEntry", "ReviewCycle", "ExecutiveBriefRecord", "Integration",
    "SystemJob", "AuditLog", "create_user", "create_signal", "create_recommendation",
]
