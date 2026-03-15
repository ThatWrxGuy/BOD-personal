"""Signal schemas for API validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SignalBase(BaseModel):
    """Base signal schema."""

    category: str = Field(..., description="Signal category")
    source: str = Field(..., description="Signal source")
    title: str = Field(..., description="Signal title")
    description: str = Field(..., description="Signal description")


class SignalCreate(SignalBase):
    """Schema for creating a signal."""

    signal_strength: float = Field(default=5.0, description="Signal strength 0-10")
    urgency: int = Field(default=5, description="Urgency 1-10")
    confidence: float = Field(default=0.5, description="Confidence 0-1")
    metadata: Optional[dict] = Field(default=None, description="Raw signal data")


class SignalResponse(SignalBase):
    """Schema for signal response."""

    id: UUID
    timestamp: datetime
    signal_strength: float
    urgency: int
    confidence: float
    metadata: Optional[dict] = None
    processed_at: Optional[datetime] = None
    meeting_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SignalListResponse(BaseModel):
    """Schema for listing signals."""

    signals: list[SignalResponse]
    total: int


class SignalSummaryResponse(BaseModel):
    """Schema for signal summary."""

    total: int
    by_category: dict[str, int]
    avg_urgency: float
    avg_strength: float
    high_urgency_count: int
    high_strength_count: int
