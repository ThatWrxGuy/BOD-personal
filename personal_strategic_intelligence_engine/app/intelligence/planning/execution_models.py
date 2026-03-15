"""Execution Models - Data structures for plan execution."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Status of execution."""
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionType(str, Enum):
    """Type of execution."""
    MANUAL = "manual"
    ASSISTED = "assisted"
    AUTOMATED = "automated"


class TaskPriority(str, Enum):
    """Priority of execution tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Severity of execution alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionProgram(BaseModel):
    """A program for executing a strategic plan."""
    id: str
    plan_id: str
    goal_id: str
    goal_title: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Progress tracking
    total_steps: int = 0
    completed_steps: int = 0
    blocked_steps: int = 0
    overdue_steps: int = 0
    progress_percent: float = Field(ge=0, le=100, default=0.0)
    
    # Metadata
    execution_mode: ExecutionType = ExecutionType.MANUAL
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ExecutionTask(BaseModel):
    """A single execution task."""
    id: str
    execution_program_id: str
    step_id: str
    
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Dependencies
    dependency_ids: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    
    # Resources
    required_resources: Dict[str, Any] = Field(default_factory=dict)
    execution_type: ExecutionType = ExecutionType.MANUAL
    
    # Tracking
    is_critical_path: bool = False
    retry_count: int = 0


class ExecutionMilestone(BaseModel):
    """A milestone in the execution program."""
    id: str
    execution_program_id: str
    
    name: str
    description: str
    
    target_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    success_criteria: Dict[str, Any] = Field(default_factory=dict)
    
    # Progress
    tasks_total: int = 0
    tasks_completed: int = 0


class ExecutionAlert(BaseModel):
    """An alert during execution."""
    id: str
    execution_program_id: str
    
    alert_type: str  # blocked, overdue, failed, milestone_missed
    severity: AlertSeverity
    
    message: str
    description: str = ""
    
    recommended_action: str  # continue, pause, replan, abort
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Related
    task_id: Optional[str] = None
    milestone_id: Optional[str] = None
    
    resolved: bool = False


class ExecutionPolicy(BaseModel):
    """Policy for execution automation."""
    # Automation thresholds
    auto_approve_threshold: float = 100.0  # Dollar amount
    auto_execute_low_risk: bool = True
    
    # Risk levels
    high_risk_actions: List[str] = Field(default_factory=list)
    manual_only_actions: List[str] = Field(default_factory=list)
    
    # Timing
    task_timeout_hours: int = 24
    escalation_delay_hours: int = 4
    
    # Approval requirements
    requires_approval_above: float = 1000.0


class ExecutionSummary(BaseModel):
    """Summary of execution status."""
    program_id: str
    
    overall_health: str  # healthy, degraded, blocked, failed
    
    progress_percent: float
    tasks_total: int
    tasks_completed: int
    tasks_blocked: int
    tasks_overdue: int
    
    active_alerts: int
    critical_alerts: int
    
    next_deadline: Optional[datetime] = None
    
    recommendation: str = ""
