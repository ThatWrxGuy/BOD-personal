"""Execution Record database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ExecutionRecord(Base, TimestampMixin):
    """Execution record for tracking action execution."""

    __tablename__ = "execution_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )  # PENDING, APPROVED, REJECTED, EXECUTING, COMPLETED, FAILED
    approval_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="MANUAL_APPROVAL_REQUIRED",
    )  # AUTO_APPROVED, MANUAL_APPROVAL_REQUIRED, MULTI_AGENT_APPROVAL
    
    # Timing
    execution_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    execution_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    execution_duration: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )  # seconds
    
    # Payload and results
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Risk and validation
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    validated: Mapped[bool] = mapped_column(default=False)
    validation_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Retry tracking
    retry_count: Mapped[int] = mapped_column(default=0)
    max_retries: Mapped[int] = mapped_column(default=3)


class ExecutionHistory(Base, TimestampMixin):
    """Historical execution log for audit."""

    __tablename__ = "execution_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class ConnectorStatus(Base, TimestampMixin):
    """Connector health status tracking."""

    __tablename__ = "connector_status"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    connector_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_connected: Mapped[bool] = mapped_column(default=False)
    last_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
