"""Replanning Models - Data structures for dynamic replanning."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class DriftType(str, Enum):
    """Types of plan drift."""
    SCHEDULE_DRIFT = "schedule_drift"
    RISK_DRIFT = "risk_drift"
    RESOURCE_DRIFT = "resource_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    OPPORTUNITY_SHIFT = "opportunity_shift"
    GOAL_SHIFT = "goal_shift"


class AdjustmentType(str, Enum):
    """Types of plan adjustments."""
    REORDER_STEPS = "reorder_steps"
    DEFER_STEP = "defer_step"
    ACCELERATE_STEP = "accelerate_step"
    REPLACE_STEP = "replace_step"
    REMOVE_STEP = "remove_step"
    SPLIT_STEP = "split_step"
    REGENERATE_PLAN = "regenerate_plan"
    SWITCH_PLAN = "switch_plan"


class ReplanningAction(str, Enum):
    """Actions to take on replanning."""
    CONTINUE = "continue"
    ADJUST_CURRENT_PLAN = "adjust_current_plan"
    REGENERATE_CURRENT_PLAN = "regenerate_current_plan"
    SWITCH_TO_ALTERNATE_PLAN = "switch_to_alternate_plan"
    ESCALATE_FOR_REVIEW = "escalate_for_review"


class TriggerSeverity(str, Enum):
    """Severity of replanning triggers."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PlanDriftSignal(BaseModel):
    """Signal indicating plan drift."""
    id: str
    execution_program_id: str
    plan_id: str
    
    drift_type: DriftType
    severity: TriggerSeverity
    
    description: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    
    impacted_tasks: List[str] = Field(default_factory=list)
    impacted_milestones: List[str] = Field(default_factory=list)
    
    # Metrics
    expected_value: float = 0.0
    actual_value: float = 0.0
    deviation_percent: float = 0.0


class ReplanningTrigger(BaseModel):
    """Trigger for replanning."""
    id: str
    execution_program_id: str
    
    trigger_type: str  # minor_adjustment, moderate_replanning, major_replacement, critical
    severity: TriggerSeverity
    
    reason: str
    
    drift_signals: List[str] = Field(default_factory=list)  # Signal IDs
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    resolved: bool = False
    action_taken: Optional[ReplanningAction] = None


class PlanAdjustment(BaseModel):
    """A tactical adjustment to a plan."""
    id: str
    plan_id: str
    
    adjustment_type: AdjustmentType
    
    description: str
    
    affected_steps: List[str] = Field(default_factory=list)
    
    recommended_action: str
    
    # Changes
    priority_change: Dict[str, int] = Field(default_factory=dict)
    timeline_change: Dict[str, int] = Field(default_factory=dict)  # days
    risk_delta: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReplanningDecision(BaseModel):
    """Record of a replanning decision."""
    id: str
    execution_program_id: str
    
    original_plan_id: str
    
    action_taken: ReplanningAction
    
    new_plan_id: Optional[str] = None
    
    adjustments_applied: List[str] = Field(default_factory=list)  # Adjustment IDs
    
    reasoning: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Outcome tracking
    successful: Optional[bool] = None


class DriftSummary(BaseModel):
    """Summary of drift for a program."""
    execution_program_id: str
    
    total_signals: int = 0
    critical_signals: int = 0
    high_severity_signals: int = 0
    
    drift_by_type: Dict[str, int] = Field(default_factory=dict)
    
    overall_health: str = "healthy"  # healthy, concerning, degraded, critical
    
    recommendation: str = ""
