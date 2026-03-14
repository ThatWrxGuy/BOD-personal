"""Orchestration data models."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class EventRecord(Base, TimestampMixin):
    """Stored domain event record."""

    __tablename__ = "event_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
    )
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Event data
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Correlation
    correlation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Metadata
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    processed: Mapped[bool] = mapped_column(default=False)
    processing_error: Mapped[str] = mapped_column(Text, nullable=True)


class WorkflowInstance(Base, TimestampMixin):
    """Workflow instance record."""

    __tablename__ = "workflow_instances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    workflow_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    workflow_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # State
    current_state: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_state: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Context
    context: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, completed, failed, cancelled
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_workflow_status", "status", "created_at"),
    )


class WorkflowStateTransition(Base):
    """Workflow state transition log."""

    __tablename__ = "workflow_state_transitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    workflow_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    
    from_state: Mapped[str] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_event: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    task_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True)
