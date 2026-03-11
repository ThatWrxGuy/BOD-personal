"""Chat and conversation data models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class IntentType(str, Enum):
    """Chat intent types."""
    QUERY_RISKS = "query_risks"
    QUERY_OPPORTUNITIES = "query_opportunities"
    RUN_SIMULATION = "run_simulation"
    START_RESEARCH = "start_research"
    GENERATE_PLAN = "generate_plan"
    RUN_REVIEW = "run_review"
    CHECK_FINANCES = "check_finances"
    QUERY_GOALS = "query_goals"
    SYSTEM_STATUS = "system_status"
    QUERY_INSIGHTS = "query_insights"
    LIST_BILLS = "list_bills"
    CHECK_LIQUIDITY = "check_liquidity"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


class ChatSessionStatus(str, Enum):
    """Chat session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


class ChatMessageStatus(str, Enum):
    """Chat message status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatSession(Base, TimestampMixin):
    """Chat session."""

    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # User info
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=ChatSessionStatus.ACTIVE)
    
    # Context
    context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Metadata
    message_count: Mapped[int] = mapped_column(default=0)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ChatMessage(Base, TimestampMixin):
    """Chat message."""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Content
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Intent
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    intent_confidence: Mapped[Optional[float]] = mapped_column(default=0.0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=ChatMessageStatus.PROCESSING)
    
    # Execution
    command_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    command_result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timing
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_message_session", "session_id"),
    )
