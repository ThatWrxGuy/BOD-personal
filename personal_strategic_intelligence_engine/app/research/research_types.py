"""Research data models and types."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import DateTime, String, Text, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ResearchStatus(str, Enum):
    """Research task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchPriority(str, Enum):
    """Research priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResearchScope(str, Enum):
    """Research scope."""
    QUICK = "quick"  # 5-10 minutes
    STANDARD = "standard"  # 15-30 minutes
    DEEP = "deep"  # 1+ hour


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
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=ResearchStatus.PENDING)
    priority: Mapped[str] = mapped_column(String(20), default=ResearchPriority.MEDIUM)
    scope: Mapped[str] = mapped_column(String(20), default=ResearchScope.STANDARD)
    
    # Source
    trigger_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # detection, review, planning, manual
    trigger_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Progress
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Results
    sources_queried: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    data_collected: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error
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
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Content
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_findings: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    supporting_evidence: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    risk_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recommended_actions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Quality
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    sources_count: Mapped[int] = mapped_column(default=0)
    
    # Links
    linked_entities: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    linked_goals: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Metadata
    research_scope: Mapped[str] = mapped_column(String(20), default=ResearchScope.STANDARD)
    
    # Completion
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
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Data
    query: Mapped[str] = mapped_column(Text, nullable=False)
    results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Quality
    success: Mapped[bool] = mapped_column(default=True)
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


# Research source types
class ResearchSourceType:
    """Research source types."""
    FINANCIAL_API = "financial_api"
    ECONOMIC_DATA = "economic_data"
    NEWS_API = "news_api"
    LLM_SUMMARIZATION = "llm_summarization"
    KNOWLEDGE_BASE = "knowledge_base"
    MARKET_DATA = "market_data"
