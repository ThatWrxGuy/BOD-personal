"""Strategic review types and models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

from sqlalchemy import DateTime, String, Text, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ReviewType(str, Enum):
    """Strategic review types."""
    
    WEEKLY_STRATEGIC = "weekly_strategic"
    MONTHLY_FINANCIAL = "monthly_financial"
    MONTHLY_HEALTH = "monthly_health"
    MONTHLY_PRODUCTIVITY = "monthly_productivity"
    QUARTERLY_LIFE_STRATEGY = "quarterly_life_strategy"
    RISK_MONITORING = "risk_monitoring"


class ReviewFrequency:
    """Review frequency constants."""
    
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


class ReviewStatus:
    """Review status constants."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DomainType(str, Enum):
    """Life domains to analyze."""
    
    FINANCIAL = "financial"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    PROJECTS = "projects"
    RISK = "risk"
    LONG_TERM_GOALS = "long_term_goals"


# Review type configuration
REVIEW_TYPE_CONFIG = {
    ReviewType.WEEKLY_STRATEGIC: {
        "name": "Weekly Strategic Review",
        "frequency": ReviewFrequency.WEEKLY,
        "domains": [DomainType.FINANCIAL, DomainType.PRODUCTIVITY, DomainType.RISK],
        "agents": ["strategy", "finance", "risk", "operations"],
        "description": "Weekly overview of strategic position",
    },
    ReviewType.MONTHLY_FINANCIAL: {
        "name": "Monthly Financial Review",
        "frequency": ReviewFrequency.MONTHLY,
        "domains": [DomainType.FINANCIAL],
        "agents": ["finance", "risk"],
        "description": "Monthly deep-dive into financial status",
    },
    ReviewType.MONTHLY_HEALTH: {
        "name": "Monthly Health Review",
        "frequency": ReviewFrequency.MONTHLY,
        "domains": [DomainType.HEALTH],
        "agents": ["health", "strategy"],
        "description": "Monthly health status assessment",
    },
    ReviewType.MONTHLY_PRODUCTIVITY: {
        "name": "Monthly Productivity Review",
        "frequency": ReviewFrequency.MONTHLY,
        "domains": [DomainType.PRODUCTIVITY, DomainType.PROJECTS],
        "agents": ["operations", "strategy"],
        "description": "Monthly productivity and project review",
    },
    ReviewType.QUARTERLY_LIFE_STRATEGY: {
        "name": "Quarterly Life Strategy Review",
        "frequency": ReviewFrequency.QUARTERLY,
        "domains": [DomainType.FINANCIAL, DomainType.HEALTH, DomainType.PRODUCTIVITY, DomainType.LONG_TERM_GOALS],
        "agents": ["strategy", "finance", "risk", "health", "operations", "legacy"],
        "description": "Quarterly comprehensive life strategy review",
    },
    ReviewType.RISK_MONITORING: {
        "name": "Risk Monitoring Review",
        "frequency": ReviewFrequency.WEEKLY,
        "domains": [DomainType.RISK, DomainType.FINANCIAL, DomainType.HEALTH],
        "agents": ["risk", "finance", "health", "strategy"],
        "description": "Continuous risk monitoring and assessment",
    },
}


class StrategicReview(Base, TimestampMixin):
    """Strategic review record."""

    __tablename__ = "strategic_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=ReviewStatus.PENDING)
    
    # Timing
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Context
    domains_analyzed: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    agents_involved: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Results
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrics_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Workflow
    correlation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    workflow_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class StrategicInsight(Base, TimestampMixin):
    """Strategic insight generated from reviews."""

    __tablename__ = "strategic_insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_reviews.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # risk, opportunity, improvement, progress
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, addressed, dismissed
    
    # Related
    related_domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class ReviewDecisionProposal(Base, TimestampMixin):
    """Decision proposals generated from reviews."""

    __tablename__ = "review_decision_proposals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_reviews.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    decision_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="proposed")  # proposed, approved, rejected, executed
    
    # Governance
    governance_decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    
    # Impact
    expected_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effort_estimate: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
