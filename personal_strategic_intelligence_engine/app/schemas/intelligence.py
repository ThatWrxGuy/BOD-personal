"""Intelligence schemas for API validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Forecast Schemas
class ForecastResponse(BaseModel):
    """Schema for forecast response."""

    id: UUID
    forecast_type: str
    forecast_target: str
    forecast_value: Optional[float]
    confidence: float
    prediction_horizon: str
    source_data_range: Optional[str]
    methodology: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Scenario Schemas
class ScenarioCreate(BaseModel):
    """Schema for running a scenario simulation."""

    scenario_type: str = Field(..., description="Type of scenario to run")
    parameters: Optional[dict] = Field(None, description="Scenario parameters")


class ScenarioResponse(BaseModel):
    """Schema for scenario response."""

    id: UUID
    scenario_name: str
    description: Optional[str]
    predicted_outcomes: Optional[dict]
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


# Risk Schemas
class RiskProjectionResponse(BaseModel):
    """Schema for risk projection response."""

    id: UUID
    risk_category: str
    risk_probability: float
    impact_estimate: float
    time_horizon: str
    risk_description: str
    indicators: Optional[dict]
    mitigation_suggestions: Optional[list]
    created_at: datetime

    model_config = {"from_attributes": True}


# Goal Probability Schemas
class GoalProbabilityResponse(BaseModel):
    """Schema for goal probability response."""

    id: UUID
    goal_id: UUID
    probability_of_success: float
    estimated_completion_date: Optional[datetime]
    confidence: float
    calculation_method: str
    factors: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


# Trend Schemas
class TrendResponse(BaseModel):
    """Schema for trend response."""

    category: str
    direction: str
    strength: float
    confidence: float
    details: dict


class AnomalyResponse(BaseModel):
    """Schema for anomaly response."""

    type: str
    severity: str
    description: str
    details: Optional[dict]


class TrendsSummaryResponse(BaseModel):
    """Schema for trends summary."""

    signal_trends: list[TrendResponse]
    goal_trends: list[TrendResponse]
    anomalies: list[AnomalyResponse]
    analyzed_at: str


# Intelligence Dashboard
class IntelligenceDashboardResponse(BaseModel):
    """Schema for intelligence dashboard."""

    trends: dict
    forecasts: dict
    risks: dict
    goals: dict
    generated_at: str
