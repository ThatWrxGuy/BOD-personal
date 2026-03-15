"""Profile schemas for API validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    """Base profile schema."""

    mission_statement: str = Field(..., description="User's mission statement")
    values: list[str] = Field(..., description="List of core values")
    priorities: list[str] = Field(..., description="Current priorities")
    non_negotiables: list[str] = Field(..., description="Non-negotiable boundaries")
    active_goals: list[str] = Field(..., description="Active goals")
    constraints: Optional[list[str]] = Field(default=None, description="Current constraints")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance level")
    name: Optional[str] = Field(default=None, description="User's name")
    email: Optional[str] = Field(default=None, description="User's email")


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""

    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""

    mission_statement: Optional[str] = None
    values: Optional[list[str]] = None
    priorities: Optional[list[str]] = None
    non_negotiables: Optional[list[str]] = None
    active_goals: Optional[list[str]] = None
    constraints: Optional[list[str]] = None
    risk_tolerance: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class ProfileResponse(ProfileBase):
    """Schema for profile response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileSummary(BaseModel):
    """Summary profile for context building."""

    mission_statement: str
    values: list[str]
    priorities: list[str]
    non_negotiables: list[str]
    active_goals: list[str]
    risk_tolerance: str

    @classmethod
    def from_profile(cls, profile: "ProfileResponse") -> "ProfileSummary":
        """Create summary from full profile."""
        return cls(
            mission_statement=profile.mission_statement,
            values=profile.values,
            priorities=profile.priorities,
            non_negotiables=profile.non_negotiables,
            active_goals=profile.active_goals,
            risk_tolerance=profile.risk_tolerance,
        )
