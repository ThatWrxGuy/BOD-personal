"""Decision schemas for API validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DecisionCreate(BaseModel):
    """Schema for creating a decision record."""

    meeting_id: Optional[int] = Field(default=None, description="Optional link to meeting")
    decision_summary: str = Field(..., description="Summary of the decision")
    chosen_action: str = Field(..., description="The action taken")
    rationale: Optional[str] = Field(default=None, description="Rationale for the decision")
    status: str = Field(default="pending", description="Status: pending, decided, reviewed")
    review_due_at: Optional[datetime] = Field(default=None, description="When to review this decision")


class DecisionUpdate(BaseModel):
    """Schema for updating a decision record."""

    decision_summary: Optional[str] = None
    chosen_action: Optional[str] = None
    rationale: Optional[str] = None
    status: Optional[str] = None
    review_due_at: Optional[datetime] = None


class DecisionResponse(BaseModel):
    """Schema for decision response."""

    id: int
    meeting_id: Optional[int] = None
    decision_summary: str
    chosen_action: str
    rationale: Optional[str] = None
    status: str
    review_due_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DecisionListResponse(BaseModel):
    """Schema for listing decisions."""

    decisions: list[DecisionResponse]
    total: int
