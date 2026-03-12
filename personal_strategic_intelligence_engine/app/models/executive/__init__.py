"""Executive Command Center data models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ExecutiveCommandLog(Base, TimestampMixin):
    """Log of executive commands."""

    __tablename__ = "executive_command_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    command_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    command_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    target: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    issued_by: Mapped[str] = mapped_column(String(50), default="operator")
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")


class OverrideLog(Base, TimestampMixin):
    """Log of override commands."""

    __tablename__ = "executive_override_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    override_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    override_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    issued_by: Mapped[str] = mapped_column(String(50), default="operator")
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="applied")


class AutonomyOverride(Base, TimestampMixin):
    """Autonomy override state."""

    __tablename__ = "executive_autonomy_overrides"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    override_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    issued_by: Mapped[str] = mapped_column(String(50), default="operator")
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
