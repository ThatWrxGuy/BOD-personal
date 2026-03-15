"""Trigger Event model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TriggerEvent(Base, TimestampMixin):
    """Trigger event model for signal-triggered governance."""

    __tablename__ = "trigger_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    signal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_signals.id"),
        nullable=True,
    )
    trigger_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # BOARD_MEETING, RISK_REVIEW, FINANCE_REVIEW, OPERATIONS_REVIEW
    trigger_reason: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )  # LOW, MEDIUM, HIGH, CRITICAL
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    signal = relationship("StrategicSignal", backref="trigger_events")


class TriggerType:
    """Trigger type constants."""

    BOARD_MEETING = "BOARD_MEETING"
    RISK_REVIEW = "RISK_REVIEW"
    FINANCE_REVIEW = "FINANCE_REVIEW"
    OPERATIONS_REVIEW = "OPERATIONS_REVIEW"
    HEALTH_REVIEW = "HEALTH_REVIEW"
    STRATEGY_REVIEW = "STRATEGY_REVIEW"

    ALL = [BOARD_MEETING, RISK_REVIEW, FINANCE_REVIEW, OPERATIONS_REVIEW, HEALTH_REVIEW, STRATEGY_REVIEW]


class TriggerSeverity:
    """Trigger severity constants."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    ALL = [LOW, MEDIUM, HIGH, CRITICAL]
