"""Execution engine data models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.execution_engine.execution_types import (
    ExecutionStatus,
    ExecutionPriority,
    PermissionLevel,
    FailureSeverity,
    TaskType,
)


class ActionType(str, Enum):
    """Types of actions that can be executed."""
    TRADE_EXECUTION = "trade_execution"
    PORTFOLIO_ADJUSTMENT = "portfolio_adjustment"
    ALERT_NOTIFICATION = "alert_notification"
    SYSTEM_ACTION = "system_action"
    REBALANCING = "rebalancing"
    HEDGING = "hedging"
    RESEARCH = "research"
    ANALYSIS = "analysis"


class ApprovalLevel(str, Enum):
    """Required approval level for execution."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    GOVERNANCE = "governance"
    CEO = "ceo"


class ExecutionRequest(BaseModel):
    """Canonical schema for execution requests."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    action_type: ActionType
    
    # Action details
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    risk_level: str = "medium"
    approved_by: str = "governance"
    approval_level: ApprovalLevel = ApprovalLevel.MANUAL
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    validated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_duration_ms: Optional[float] = None
    
    # Governance
    governance_decision_id: Optional[str] = None
    
    class Config:
        use_enum_values = True


class ActionExecutionResult(BaseModel):
    """Result of an execution (V48-004)."""
    execution_id: str
    status: ExecutionStatus
    
    # Action performed
    action_taken: str
    result_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Timing
    execution_time_ms: float = 0.0
    
    # Error handling
    success: bool = True
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionRecord(BaseModel):
    """Permanent record of an execution."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    
    # Associated proposal
    proposal_id: str
    governance_decision_id: Optional[str] = None
    
    # Action details
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Results
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Execution metadata
    risk_level: str
    approved_by: str
    execution_duration_ms: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "record_id": self.record_id,
            "execution_id": self.execution_id,
            "proposal_id": self.proposal_id,
            "governance_decision_id": self.governance_decision_id,
            "action_type": self.action_type,
            "parameters": self.parameters,
            "status": self.status,
            "result": self.result,
            "error_message": self.error_message,
            "risk_level": self.risk_level,
            "approved_by": self.approved_by,
            "execution_duration_ms": self.execution_duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class SafetyValidationResult(BaseModel):
    """Result of safety validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionStatistics(BaseModel):
    """Statistics about execution activity."""
    total_executions: int = 0
    completed: int = 0
    failed: int = 0
    pending: int = 0
    in_progress: int = 0
    
    by_action_type: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    
    average_execution_time_ms: float = 0.0
    success_rate: float = 0.0


class ExecutionTask(BaseModel):
    """An executable task derived from a council decision."""
    task_id: str
    origin_decision: str
    task_type: TaskType = TaskType.ANALYSIS
    description: str
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    permission_level: PermissionLevel = PermissionLevel.AUTONOMOUS
    status: ExecutionStatus = ExecutionStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    required_resources: Dict[str, Any] = Field(default_factory=dict)
    created_timestamp: datetime = Field(default_factory=datetime.utcnow)
    started_timestamp: Optional[datetime] = None
    completed_timestamp: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    error_message: Optional[str] = None


class ExecutionWorkflow(BaseModel):
    """A workflow containing multiple related tasks."""
    workflow_id: str
    origin_decision: str
    tasks: List[ExecutionTask] = Field(default_factory=list)
    execution_order: List[str] = Field(default_factory=list)
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_timestamp: datetime = Field(default_factory=datetime.utcnow)
    started_timestamp: Optional[datetime] = None
    completed_timestamp: Optional[datetime] = None


class ExecutionResult(BaseModel):
    """Result of task or workflow execution."""
    task_id: str
    status: ExecutionStatus
    execution_log: List[str] = Field(default_factory=list)
    error_details: Optional[Dict[str, Any]] = None
    completion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    output_data: Optional[Dict[str, Any]] = None


class WorkflowResult(BaseModel):
    """Result of workflow execution."""
    workflow_id: str
    status: ExecutionStatus
    task_results: List[ExecutionResult] = Field(default_factory=list)
    total_execution_time: float = 0.0
    failures_count: int = 0
    completions_count: int = 0
    completion_timestamp: datetime = Field(default_factory=datetime.utcnow)


class PermissionDecision(BaseModel):
    """Decision from permission manager."""
    task_id: str
    permission_level: PermissionLevel
    approved: bool
    reason: str
    requires_approval_from: Optional[str] = None


class FailureRecord(BaseModel):
    """Record of a task failure."""
    failure_id: str
    task_id: str
    severity: FailureSeverity
    error_message: str
    error_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution: Optional[str] = None


class ExecutionSummary(BaseModel):
    """Summary of execution activity."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    total_execution_time: float = 0.0
    average_task_time: float = 0.0
    active_workflows: int = 0
