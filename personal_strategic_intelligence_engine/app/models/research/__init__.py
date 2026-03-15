"""Research data models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ResearchTask(Base, TimestampMixin):
    """Research task record."""

    __tablename__ = "research_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    scope: Mapped[str] = mapped_column(String(20), default="standard")
    trigger_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    trigger_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sources_queried: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    data_collected: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ResearchReport(Base, TimestampMixin):
    """Research report."""

    __tablename__ = "research_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_tasks.id"),
        nullable=False,
    )
    
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_findings: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    supporting_evidence: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    risk_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recommended_actions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    sources_count: Mapped[int] = mapped_column(default=0)
    linked_entities: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    linked_goals: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    research_scope: Mapped[str] = mapped_column(String(20), default="standard")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ResearchSourceResult(Base, TimestampMixin):
    """Result from a research source."""

    __tablename__ = "research_source_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_tasks.id"),
        nullable=False,
    )
    
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(default=True)
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
