"""Operations Domain Data Models.

Canonical models for operations domain data including:
- Standard operating procedures
- Procedural documentation
- Workflow records
- Task records
- Operational metrics
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ProcedureDocument(BaseModel):
    """Standard operating procedure document."""
    document_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Procedure title")
    content: str = Field(..., description="Procedure content")
    
    # Classification
    category: str = Field(..., description="Procedure category")
    subcategory: Optional[str] = Field(None, description="Procedure subcategory")
    version: str = Field(..., description="Version number")
    
    # Metadata
    owner: Optional[str] = Field(None, description="Procedure owner")
    approver: Optional[str] = Field(None, description="Approver")
    approved_date: Optional[datetime] = Field(None, description="Approval date")
    effective_date: datetime = Field(..., description="Effective date")
    review_frequency_days: int = Field(90, description="Review frequency in days")
    next_review_date: Optional[datetime] = Field(None, description="Next review date")
    
    # Content
    prerequisites: Optional[List[str]] = Field(None, description="Prerequisites")
    steps: List[dict] = Field(default_factory=list, description="Procedure steps")
    checkpoints: Optional[List[dict]] = Field(None, description="Quality checkpoints")
    references: Optional[List[str]] = Field(None, description="Reference documents")
    
    source_id: str = Field("ops_sops", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowRecord(BaseModel):
    """Workflow definition record."""
    record_id: UUID = Field(default_factory=uuid4)
    workflow_name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    
    # Classification
    workflow_type: str = Field(..., description="Workflow type")
    department: str = Field(..., description="Department")
    status: str = Field(..., description="Workflow status")
    
    # Structure
    steps: List[dict] = Field(default_factory=list, description="Workflow steps")
    transitions: List[dict] = Field(default_factory=list, description="State transitions")
    roles: List[dict] = Field(default_factory=list, description="Required roles")
    
    # Metadata
    owner: Optional[str] = Field(None, description="Workflow owner")
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    
    source_id: str = Field("ops_workflows", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskRecord(BaseModel):
    """Task record from task management."""
    record_id: UUID = Field(default_factory=uuid4)
    task_name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    
    # Classification
    task_type: str = Field(..., description="Task type")
    priority: str = Field(..., description="Priority (high, medium, low)")
    status: str = Field(..., description="Status")
    
    # Timing
    due_date: Optional[datetime] = Field(None, description="Due date")
    completed_date: Optional[datetime] = Field(None, description="Completion date")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours")
    actual_hours: Optional[float] = Field(None, description="Actual hours")
    
    # Relationships
    parent_workflow_id: Optional[str] = Field(None, description="Parent workflow ID")
    assignee: Optional[str] = Field(None, description="Assignee")
    
    # Tags
    tags: List[str] = Field(default_factory=list, description="Task tags")
    
    source_id: str = Field("ops_tasks", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OperationalMetricRecord(BaseModel):
    """Operational metric data point."""
    record_id: UUID = Field(default_factory=uuid4)
    metric_name: str = Field(..., description="Metric name")
    
    # Value
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    
    # Classification
    metric_type: str = Field(..., description="Metric type (count, rate, percentage, etc.)")
    department: str = Field(..., description="Department")
    
    # Timing
    period_start: datetime = Field(..., description="Period start")
    period_end: datetime = Field(..., description="Period end")
    timestamp: datetime = Field(..., description="Recording timestamp")
    
    # Context
    tags: List[str] = Field(default_factory=list, description="Metric tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    
    source_id: str = Field("ops_metrics", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
