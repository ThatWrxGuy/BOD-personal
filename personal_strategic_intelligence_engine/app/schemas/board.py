"""Board meeting schemas for API validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentResponseBase(BaseModel):
    """Base agent response schema."""

    agent_id: int
    summary_judgment: str
    main_recommendation: str
    supporting_reasons: list[str]
    main_risks: list[str]
    tradeoffs: list[str]
    requested_followups: Optional[list[str]] = None
    confidence_score: Optional[float] = None
    version_id: str = "1.0.0"


class AgentResponseCreate(AgentResponseBase):
    """Schema for creating an agent response."""

    meeting_id: int


class AgentResponseResponse(AgentResponseBase):
    """Schema for agent response response."""

    id: int
    meeting_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CritiqueResponseBase(BaseModel):
    """Base critique response schema."""

    source_agent_id: int
    target_agent_id: int
    critique_text: str
    severity: str = "medium"


class CritiqueResponseCreate(CritiqueResponseBase):
    """Schema for creating a critique response."""

    meeting_id: int


class CritiqueResponseResponse(CritiqueResponseBase):
    """Schema for critique response response."""

    id: int
    meeting_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BoardMeetingCreate(BaseModel):
    """Schema for creating a board meeting."""

    meeting_type: str = Field(default="strategic", description="Type: strategic, weekly, monthly")
    trigger_type: str = Field(default="manual", description="Trigger: manual, scheduled")
    question: str = Field(..., description="The strategic question to address")


class BoardMeetingUpdate(BaseModel):
    """Schema for updating a board meeting."""

    executive_summary: Optional[str] = None
    consensus_recommendation: Optional[str] = None
    alternatives: Optional[list[str]] = None
    risks: Optional[list[str]] = None
    tradeoffs: Optional[list[str]] = None
    confidence_score: Optional[float] = None
    data_gaps: Optional[list[str]] = None
    status: Optional[str] = None


class BoardMeetingResponse(BaseModel):
    """Schema for board meeting response."""

    id: int
    meeting_type: str
    trigger_type: str
    question: str
    context_snapshot: Optional[str] = None
    executive_summary: Optional[str] = None
    consensus_recommendation: Optional[str] = None
    alternatives: Optional[list[str]] = None
    risks: Optional[list[str]] = None
    tradeoffs: Optional[list[str]] = None
    confidence_score: Optional[float] = None
    data_gaps: Optional[list[str]] = None
    status: str
    created_at: datetime
    updated_at: datetime
    agent_responses: list[AgentResponseResponse] = []
    critique_responses: list[CritiqueResponseResponse] = []

    model_config = {"from_attributes": True}


class BoardMeetingListResponse(BaseModel):
    """Schema for listing board meetings."""

    meetings: list[BoardMeetingResponse]
    total: int
