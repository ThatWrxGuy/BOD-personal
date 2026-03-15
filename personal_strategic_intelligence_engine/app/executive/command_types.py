"""Executive Command Center - command types and models."""
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


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


# Re-export ORM classes for backward compatibility
from app.models.executive import ExecutiveCommandLog, OverrideLog, AutonomyOverride

__all__ = [
    "CommandCategory",
    "OverrideType",
    "ReportPeriod",
    "ExecutiveCommand",
    "OverrideCommand",
    "SystemOverview",
    "DashboardData",
    "ExecutiveReport",
    "ExecutiveCommandLog",
    "OverrideLog",
    "AutonomyOverride",
]
