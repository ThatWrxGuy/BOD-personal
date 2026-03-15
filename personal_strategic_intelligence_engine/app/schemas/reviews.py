"""Review schemas for API validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OutcomeReviewCreate(BaseModel):
    """Schema for creating an outcome review."""

    decision_id: int = Field(..., description="ID of the decision being reviewed")
    actual_result: str = Field(..., description="Actual outcome of the decision")
    success_score: Optional[float] = Field(default=None, description="Success score 0-10")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    reviewed_at: Optional[datetime] = Field(default=None, description="When the review was conducted")


class OutcomeReviewUpdate(BaseModel):
    """Schema for updating an outcome review."""

    actual_result: Optional[str] = None
    success_score: Optional[float] = None
    notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class OutcomeReviewResponse(BaseModel):
    """Schema for outcome review response."""

    id: int
    decision_id: int
    actual_result: str
    success_score: Optional[float] = None
    notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OutcomeReviewListResponse(BaseModel):
    """Schema for listing outcome reviews."""

    reviews: list[OutcomeReviewResponse]
    total: int
