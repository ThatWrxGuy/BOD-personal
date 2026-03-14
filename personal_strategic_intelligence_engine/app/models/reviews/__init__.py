"""Database models for strategic reviews."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, String, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StrategicReview(Base, TimestampMixin):
    """Strategic review record."""

    __tablename__ = "strategic_reviews"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
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
    status: Mapped[str] = mapped_column(String(20), default="proposed")
    
    # Governance
    governance_decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    
    # Impact
    expected_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effort_estimate: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
