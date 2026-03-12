"""Executive Command Center - command types and models."""
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, String, ForeignKey, Text, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CommandCategory(str, Enum):
    """Command categories."""
    STRATEGIC = "strategic"
    GOAL = "goal"
    RISK = "risk"
    FINANCIAL = "financial"
    AUTONOMY = "autonomy"
    HABIT = "habit"
    SYSTEM = "system"


class OverrideType(str, Enum):
    """Override types."""
    PAUSE_AUTONOMY = "pause_autonomy"
    RESUME_AUTONOMY = "resume_autonomy"
    FORCE_CYCLE = "force_cycle"
    DISABLE_ADJUSTMENT = "disable_adjustment"
    ENABLE_ADJUSTMENT = "enable_adjustment"


class ReportPeriod(str, Enum):
    """Report periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Pydantic Models
class ExecutiveCommand(BaseModel):
    """Executive command model."""
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    command_type: str
    category: CommandCategory
    target: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    issued_by: str = "operator"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OverrideCommand(BaseModel):
    """Override command model."""
    override_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    override_type: OverrideType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    issued_by: str = "operator"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemOverview(BaseModel):
    """System overview response."""
    strategic_focus: str
    goal_progress: Dict[str, Any]
    risk_level: str
    habit_adherence: float
    autonomy_status: str
    recent_strategy_changes: int


class DashboardData(BaseModel):
    """Dashboard data response."""
    strategic_overview: Dict[str, Any]
    goals: Dict[str, Any]
    risks: Dict[str, Any]
    opportunities: Dict[str, Any]
    financial: Dict[str, Any]
    habits: Dict[str, Any]
    autonomy: Dict[str, Any]


class ExecutiveReport(BaseModel):
    """Executive report model."""
    report_id: str
    period: ReportPeriod
    generated_at: datetime
    summary: Dict[str, Any]
    highlights: List[str]
    recommendations: List[str]


# Database Models
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
