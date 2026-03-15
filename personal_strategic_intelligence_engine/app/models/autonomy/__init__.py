"""Autonomy data models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StrategyLoopCycle(Base, TimestampMixin):
    """Strategy loop cycle record."""

    __tablename__ = "autonomy_strategy_loop_cycles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Cycle metadata
    trigger_type: Mapped[str] = mapped_column(String(20), default="scheduled")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    runtime_ms: Mapped[int] = mapped_column(default=0)
    
    # Observation
    observed_domains: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    overall_health: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Changes
    changes_detected: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    changes_count: Mapped[int] = mapped_column(default=0)
    
    # Adjustments
    adjustments: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    adjustments_count: Mapped[int] = mapped_column(default=0)
    
    # Actions
    actions_executed: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Outcome
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class LoopPolicy(Base, TimestampMixin):
    """Loop policy configuration."""

    __tablename__ = "autonomy_loop_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Thresholds
    max_priority_shifts: Mapped[int] = mapped_column(default=3)
    cooldown_minutes: Mapped[int] = mapped_column(default=60)
    max_plan_regenerations: Mapped[int] = mapped_column(default=2)
    emergency_threshold: Mapped[str] = mapped_column(String(20), default="critical")
    
    # Flags
    weak_signal_suppression: Mapped[bool] = mapped_column(Boolean, default=True)
    require_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
