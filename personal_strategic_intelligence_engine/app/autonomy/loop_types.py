"""Autonomous strategy loop data models and types.

Note: ORM models have been moved to app/models/autonomy/
This file contains only Pydantic schemas and enums.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class ChangeSeverity(str, Enum):
    """Change severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class ChangeCategory(str, Enum):
    """Categories of detectable changes."""
    RISK_INCREASE = "risk_increase"
    RISK_DECREASE = "risk_decrease"
    OPPORTUNITY_EMERGE = "opportunity_emerge"
    OPPORTUNITY_DECAY = "opportunity_decay"
    GOAL_PROGRESS_ACCELERATE = "goal_progress_accelerate"
    GOAL_PROGRESS_STALL = "goal_progress_stall"
    HABIT_IMPROVE = "habit_improve"
    HABIT_DECLINE = "habit_decline"
    FOCUS_MISALIGN = "focus_misalign"
    EXECUTION_OVERLOAD = "execution_overload"
    PRIORITY_CONFLICT = "priority_conflict"
    DATA_STALE = "data_stale"


class AdjustmentType(str, Enum):
    """Types of strategic adjustments."""
    ELEVATE_PRIORITY = "elevate_priority"
    REDUCE_PRIORITY = "reduce_priority"
    DEFER_INITIATIVE = "defer_initiative"
    ACCELERATE_INITIATIVE = "accelerate_initiative"
    INTRODUCE_FOCUS_BLOCK = "introduce_focus_block"
    REMOVE_FOCUS_BLOCK = "remove_focus_block"
    INCREASE_RECOVERY = "increase_recovery"
    INCREASE_OPPORTUNITY_RESPONSE = "increase_opportunity_response"
    INCREASE_RISK_MITIGATION = "increase_risk_mitigation"
    REBALANCE_WEEKLY_THEME = "rebalance_weekly_theme"
    REGENERATE_DAILY_PLAN = "regenerate_daily_plan"
    REGENERATE_WEEKLY_PLAN = "regenerate_weekly_plan"
    NO_ACTION = "no_action"


class CycleTriggerType(str, Enum):
    """What triggered the cycle."""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    EVENT_DRIVEN = "event_driven"
    EMERGENCY = "emergency"


class CycleStatus(str, Enum):
    """Cycle execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# Pydantic Models for API
class DomainState(BaseModel):
    """State of a single domain."""
    domain: str
    state: Dict[str, Any]
    freshness: datetime
    confidence: float = 1.0


class StateObservation(BaseModel):
    """Complete system state observation."""
    observation_id: str
    timestamp: datetime
    domains: List[DomainState]
    overall_health: float = 1.0


class ChangeEvent(BaseModel):
    """Detected change event."""
    change_id: str
    category: ChangeCategory
    domain: str
    prior_value: Any
    current_value: Any
    severity: ChangeSeverity
    confidence: float = 1.0
    explanation: str
    recommended_response: Optional[AdjustmentType] = None


class StrategicAdjustment(BaseModel):
    """Strategic adjustment recommendation."""
    adjustment_id: str
    adjustment_type: AdjustmentType
    reason: str
    domain: str
    target: Optional[str] = None
    parameters: Dict[str, Any] = {}


class LoopPolicyConfig(BaseModel):
    """Policy configuration for the loop."""
    max_priority_shifts: int = 3
    cooldown_minutes: int = 60
    max_plan_regenerations: int = 2
    emergency_threshold: ChangeSeverity = ChangeSeverity.CRITICAL
    weak_signal_suppression: bool = True
    require_approval: bool = False


class CycleOutcome(BaseModel):
    """Result of a strategy loop cycle."""
    cycle_id: str
    status: CycleStatus
    trigger_type: CycleTriggerType
    observation: Optional[StateObservation] = None
    changes: List[ChangeEvent] = []
    adjustments: List[StrategicAdjustment] = []
    actions_executed: List[str] = []
    runtime_ms: int = 0
    error_message: Optional[str] = None


# Re-export ORM classes for backward compatibility
# TODO: Remove these re-exports and update imports to use app.models.autonomy
from app.models.autonomy import StrategyLoopCycle, LoopPolicy

__all__ = [
    # Enums
    "ChangeSeverity",
    "ChangeCategory", 
    "AdjustmentType",
    "CycleTriggerType",
    "CycleStatus",
    # Pydantic models
    "DomainState",
    "StateObservation",
    "ChangeEvent",
    "StrategicAdjustment",
    "LoopPolicyConfig",
    "CycleOutcome",
    # Re-exported ORM classes
    "StrategyLoopCycle",  # Re-exported from app.models.autonomy
    "LoopPolicy",  # Re-exported from app.models.autonomy
]
