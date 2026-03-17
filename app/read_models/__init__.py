"""
BB-APP-002: Read Models

Purpose-built, stable, page-optimized response objects.
Per BB-APP-002 Section 9 - Read Model Architecture.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from enum import Enum


# ============== Enums for Read Models ==============

class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class StrategicPosture(str, Enum):
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    NEUTRAL = "neutral"


class DomainStatus(str, Enum):
    HEALTHY = "healthy"
    CAUTION = "caution"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class RecommendationUrgency(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class RecommendationStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ARCHIVED = "archived"


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELED = "canceled"


# ============== Helper Functions ==============

def _default_datetime() -> datetime:
    return datetime.now()


def _default_timedelta() -> timedelta:
    return timedelta(days=1)


# ============== Dashboard Read Model ==============

@dataclass
class DomainHealthSummary:
    """Domain health for dashboard."""
    domain_id: str = ""
    domain_name: str = ""
    score: int = 0
    trend: TrendDirection = TrendDirection.STABLE
    status: DomainStatus = DomainStatus.HEALTHY
    active_recommendations: int = 0
    pending_actions: int = 0


@dataclass
class PriorityItem:
    """Priority item for dashboard."""
    id: str = ""
    title: str = ""
    domain: str = ""
    urgency: RecommendationUrgency = RecommendationUrgency.MEDIUM
    recommendation_id: str | None = None


@dataclass
class UrgentRecommendation:
    """Urgent recommendation for dashboard."""
    id: str = ""
    title: str = ""
    domain: str = ""
    confidence: float = 0.0
    urgency: int = 0
    status: RecommendationStatus = RecommendationStatus.PROPOSED


@dataclass
class PendingAction:
    """Pending action for dashboard."""
    id: str = ""
    title: str = ""
    domain: str = ""
    due_date: datetime | None = None
    status: ActionStatus = ActionStatus.PROPOSED


@dataclass
class SystemStatusInfo:
    """System status for dashboard."""
    status: SystemStatus = SystemStatus.HEALTHY
    posture: StrategicPosture = StrategicPosture.NEUTRAL
    readiness_score: int = 0
    risk_alerts: int = 0
    last_updated: datetime = field(default_factory=_default_datetime)


@dataclass
class BriefSummary:
    """Brief summary for dashboard."""
    id: str = ""
    title: str = ""
    generated_at: datetime = field(default_factory=_default_datetime)
    posture: StrategicPosture = StrategicPosture.NEUTRAL
    readiness_score: int = 0


@dataclass
class DashboardReadModel:
    """Complete dashboard read model."""
    system_status: SystemStatusInfo = field(default_factory=SystemStatusInfo)
    brief: BriefSummary | None = None
    domain_health: list[DomainHealthSummary] = field(default_factory=list)
    priorities: list[PriorityItem] = field(default_factory=list)
    urgent_recommendations: list[UrgentRecommendation] = field(default_factory=list)
    pending_actions: list[PendingAction] = field(default_factory=list)
    recent_changes: list[str] = field(default_factory=list)


# ============== Brief Read Models ==============

@dataclass
class BriefDomainSection:
    """Brief domain section."""
    domain_id: str = ""
    domain_name: str = ""
    summary: str = ""
    status: DomainStatus = DomainStatus.HEALTHY
    key_insight: str = ""
    recommendations_count: int = 0


@dataclass
class BriefRecommendation:
    """Brief recommendation item."""
    id: str = ""
    title: str = ""
    domain: str = ""
    priority: int = 0
    confidence: float = 0.0
    rationale: str = ""


@dataclass
class BriefRiskAlert:
    """Brief risk alert."""
    id: str = ""
    severity: str = ""
    message: str = ""
    domain: str = ""


@dataclass
class BriefDetailReadModel:
    """Complete brief detail read model."""
    id: str = ""
    title: str = ""
    generated_at: datetime = field(default_factory=_default_datetime)
    cycle_type: str = "weekly"
    status: str = "draft"
    posture: StrategicPosture = StrategicPosture.NEUTRAL
    readiness_score: int = 0
    risk_alerts: list[BriefRiskAlert] = field(default_factory=list)
    domain_sections: list[BriefDomainSection] = field(default_factory=list)
    recommendations: list[BriefRecommendation] = field(default_factory=list)
    executive_summary: str = ""
    confidence_indicators: dict[str, Any] = field(default_factory=dict)


# ============== Domain Read Models ==============

@dataclass
class DomainScoreHistory:
    """Domain score history point."""
    timestamp: datetime = field(default_factory=_default_datetime)
    score: int = 0


@dataclass
class DomainSignal:
    """Domain signal."""
    id: str = ""
    signal_type: str = ""
    description: str = ""
    timestamp: datetime = field(default_factory=_default_datetime)
    importance: int = 0


@dataclass
class DomainRecommendation:
    """Domain recommendation."""
    id: str = ""
    title: str = ""
    confidence: float = 0.0
    urgency: int = 0
    status: RecommendationStatus = RecommendationStatus.PROPOSED


@dataclass
class DomainAction:
    """Domain action."""
    id: str = ""
    title: str = ""
    status: ActionStatus = ActionStatus.PROPOSED
    due_date: datetime | None = None


@dataclass
class DomainOverviewReadModel:
    """Domain overview read model."""
    domain_id: str = ""
    domain_name: str = ""
    description: str = ""
    score: int = 0
    trend: TrendDirection = TrendDirection.STABLE
    status: DomainStatus = DomainStatus.HEALTHY
    recommendations_count: int = 0
    pending_actions_count: int = 0
    active_signals_count: int = 0


@dataclass
class DomainDetailReadModel:
    """Complete domain detail read model."""
    domain_id: str = ""
    domain_name: str = ""
    description: str = ""
    score: int = 0
    trend: TrendDirection = TrendDirection.STABLE
    status: DomainStatus = DomainStatus.HEALTHY
    
    # Score history
    score_history: list[DomainScoreHistory] = field(default_factory=list)
    
    # Signals
    active_signals: list[DomainSignal] = field(default_factory=list)
    key_issues: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    
    # Related items
    recommendations: list[DomainRecommendation] = field(default_factory=list)
    open_actions: list[DomainAction] = field(default_factory=list)
    
    # Cross-domain
    cross_domain_dependencies: list[str] = field(default_factory=list)
    
    # Recent changes
    recent_changes: list[str] = field(default_factory=list)


# ============== Recommendation Read Models ==============

@dataclass
class RecommendationDetailReadModel:
    """Complete recommendation detail read model."""
    id: str = ""
    title: str = ""
    description: str = ""
    domain: str = ""
    confidence: float = 0.0
    urgency: int = 0
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    
    # Reasoning
    rationale: str = ""
    expected_benefit: str = ""
    likely_tradeoff: str = ""
    
    # Supporting data
    supporting_signals: list[str] = field(default_factory=list)
    affected_domains: list[str] = field(default_factory=list)
    
    # Links
    source_brief_id: str | None = None
    linked_actions: list[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=_default_datetime)
    expires_at: datetime | None = None
    acknowledged_at: datetime | None = None


@dataclass
class RecommendationSummaryReadModel:
    """Recommendation summary for lists."""
    id: str = ""
    title: str = ""
    domain: str = ""
    confidence: float = 0.0
    urgency: int = 0
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    expected_impact: str = ""


# ============== Action Read Models ==============

@dataclass
class ActionOrigin:
    """Action origin tracking."""
    recommendation_id: str | None = None
    brief_id: str | None = None
    domain: str | None = None


@dataclass
class ActionDetailReadModel:
    """Complete action detail read model."""
    id: str = ""
    title: str = ""
    description: str = ""
    domain: str = ""
    status: ActionStatus = ActionStatus.PROPOSED
    
    # Timing
    due_date: datetime | None = None
    estimated_minutes: int = 30
    created_at: datetime = field(default_factory=_default_datetime)
    updated_at: datetime = field(default_factory=_default_datetime)
    completed_at: datetime | None = None
    
    # Origin
    origin: ActionOrigin = field(default_factory=ActionOrigin)
    
    # Outcome
    outcome_notes: str = ""
    effectiveness_score: float | None = None


@dataclass
class ActionSummaryReadModel:
    """Action summary for lists."""
    id: str = ""
    title: str = ""
    domain: str = ""
    status: ActionStatus = ActionStatus.PROPOSED
    due_date: datetime | None = None
    priority: int = 3


# ============== Memory Read Models ==============

@dataclass
class MemoryEntityLink:
    """Link to related entity."""
    entity_type: str = ""
    entity_id: str = ""


@dataclass
class MemoryEntryReadModel:
    """Memory entry read model."""
    id: str = ""
    title: str = ""
    content: str = ""
    memory_type: str = ""
    
    tags: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    linked_entities: list[MemoryEntityLink] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=_default_datetime)
    updated_at: datetime = field(default_factory=_default_datetime)


# ============== Review Read Models ==============

@dataclass
class ReviewActionSummary:
    """Review action summary."""
    completed: int = 0
    missed: int = 0
    total: int = 0


@dataclass
class ReviewRecommendationSummary:
    """Review recommendation summary."""
    accepted: int = 0
    rejected: int = 0
    deferred: int = 0


@dataclass
class ReviewDetailReadModel:
    """Complete review detail read model."""
    id: str = ""
    review_type: str = "weekly"
    status: str = "in_progress"
    period_start: datetime = field(default_factory=_default_datetime)
    period_end: datetime = field(default_factory=_default_datetime)
    
    # Summary data
    overall_score: float = 0.0
    actions: ReviewActionSummary = field(default_factory=ReviewActionSummary)
    recommendations: ReviewRecommendationSummary = field(default_factory=ReviewRecommendationSummary)
    
    # Content
    progress_highlights: list[str] = field(default_factory=list)
    missed_priorities: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    next_period_focus: list[str] = field(default_factory=list)
    
    # Timestamps
    started_at: datetime = field(default_factory=_default_datetime)
    completed_at: datetime | None = None


@dataclass
class ReviewSummaryReadModel:
    """Review summary for lists."""
    id: str = ""
    review_type: str = "weekly"
    status: str = "in_progress"
    period_start: datetime = field(default_factory=_default_datetime)
    period_end: datetime = field(default_factory=_default_datetime)
    overall_score: float = 0.0


# ============== Settings Read Model ==============

@dataclass
class UserPreferences:
    """User preferences."""
    default_horizon: str = "weekly"
    operating_style: str = "balanced"
    notification_preference: str = "digest"
    theme: str = "system"


@dataclass
class SettingsReadModel:
    """Settings read model."""
    user_id: str = ""
    email: str = ""
    username: str = ""
    preferences: UserPreferences = field(default_factory=UserPreferences)
    integrations: list[dict[str, Any]] = field(default_factory=list)


# ============== Command Result Models ==============

@dataclass
class CommandResult:
    """Standard command result."""
    success: bool = False
    message: str = ""
    entity_id: str | None = None
    error_code: str | None = None
    refresh_hint: str | None = None


__all__ = [
    # Enums
    "SystemStatus", "StrategicPosture", "DomainStatus", "TrendDirection",
    "RecommendationUrgency", "RecommendationStatus", "ActionStatus",
    # Dashboard
    "DashboardReadModel", "DomainHealthSummary", "PriorityItem",
    "UrgentRecommendation", "PendingAction", "SystemStatusInfo", "BriefSummary",
    # Briefs
    "BriefDetailReadModel", "BriefDomainSection", "BriefRecommendation", "BriefRiskAlert",
    # Domains
    "DomainOverviewReadModel", "DomainDetailReadModel", "DomainScoreHistory",
    "DomainSignal", "DomainRecommendation", "DomainAction",
    # Recommendations
    "RecommendationDetailReadModel", "RecommendationSummaryReadModel",
    # Actions
    "ActionDetailReadModel", "ActionSummaryReadModel", "ActionOrigin",
    # Memory
    "MemoryEntryReadModel", "MemoryEntityLink",
    # Reviews
    "ReviewDetailReadModel", "ReviewSummaryReadModel", "ReviewActionSummary", "ReviewRecommendationSummary",
    # Settings
    "SettingsReadModel", "UserPreferences",
    # Commands
    "CommandResult",
]
