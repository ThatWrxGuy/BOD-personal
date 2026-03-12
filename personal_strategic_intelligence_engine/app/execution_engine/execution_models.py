"""Execution engine data models."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.execution_engine.execution_types import (
    ExecutionStatus,
    ExecutionPriority,
    PermissionLevel,
    FailureSeverity,
    TaskType,
)


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
