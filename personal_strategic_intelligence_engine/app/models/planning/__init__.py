"""Planning data models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class PlanType(str, Enum):
    """Strategic plan types."""
    FINANCIAL = "financial"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    CROSS_DOMAIN = "cross_domain"
    QUARTERLY = "quarterly"


class TimeHorizon(str, Enum):
    """Plan time horizons."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlanStatus(str, Enum):
    """Plan status."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionStatus(str, Enum):
    """Plan action status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class StrategicPlan(Base, TimestampMixin):
    """Strategic plan record."""

    __tablename__ = "strategic_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    plan_type: Mapped[str] = mapped_column(String(50), nullable=False)
    time_horizon: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PlanStatus.DRAFT.value)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domains_involved: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    insights_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tradeoff_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    risk_assessment: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    governance_decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    correlation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


class PlanAction(Base, TimestampMixin):
    """Action within a strategic plan."""

    __tablename__ = "plan_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default=ActionStatus.PENDING.value)
    
    domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effort_estimate: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class PlanOutcome(Base, TimestampMixin):
    """Outcome tracking for strategic plans."""

    __tablename__ = "plan_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    action_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    outcome_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    success_metric: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
