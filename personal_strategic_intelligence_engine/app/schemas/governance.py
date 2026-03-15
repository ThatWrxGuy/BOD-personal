"""Governance schemas for API validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Goal Schemas
class GoalCreate(BaseModel):
    """Schema for creating a goal."""

    title: str = Field(..., description="Goal title")
    description: Optional[str] = Field(None, description="Goal description")
    category: str = Field(..., description="Goal category")
    priority: int = Field(default=5, ge=1, le=10)
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    target_date: Optional[datetime] = None


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None


class GoalResponse(BaseModel):
    """Schema for goal response."""

    id: UUID
    title: str
    description: Optional[str]
    category: str
    priority: int
    target_value: Optional[float]
    current_value: Optional[float]
    unit: Optional[str]
    target_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoalProgressCreate(BaseModel):
    """Schema for recording goal progress."""

    goal_id: UUID
    value: float
    notes: Optional[str] = None


class GoalProgressResponse(BaseModel):
    """Schema for goal progress response."""

    id: UUID
    goal_id: UUID
    recorded_value: Optional[float]
    recorded_at: datetime
    notes: Optional[str]

    model_config = {"from_attributes": True}


# Plan Schemas
class PlanCreate(BaseModel):
    """Schema for creating a plan."""

    title: str = Field(..., description="Plan title")
    description: Optional[str] = None
    goal_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Optional[dict] = None


class PlanUpdate(BaseModel):
    """Schema for updating a plan."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PlanResponse(BaseModel):
    """Schema for plan response."""

    id: UUID
    title: str
    description: Optional[str]
    goal_id: Optional[UUID]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: str
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Schedule Schemas
class ScheduleResponse(BaseModel):
    """Schema for schedule response."""

    id: UUID
    meeting_type: str
    scheduled_time: Optional[datetime]
    frequency: str
    is_active: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Trigger Event Schemas
class TriggerEventResponse(BaseModel):
    """Schema for trigger event response."""

    id: UUID
    signal_id: Optional[UUID]
    trigger_type: str
    trigger_reason: str
    severity: str
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# Review Schemas
class ReviewResponse(BaseModel):
    """Schema for review report response."""

    review_type: str
    summary: str
    findings: list
    recommendations: list
    metrics: dict
    generated_at: str


class DashboardResponse(BaseModel):
    """Schema for governance dashboard."""

    active_goals: int
    active_plans: int
    goals_at_risk: int
    pending_triggers: int
    due_schedules: int
    goals: list
