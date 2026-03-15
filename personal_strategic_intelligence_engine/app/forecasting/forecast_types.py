"""Forecasting Types - Core models for probabilistic forecasting."""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    """Direction of trend."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    UNCERTAIN = "uncertain"


class RiskLevel(str, Enum):
    """Risk severity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ForecastHorizon(str, Enum):
    """Forecast time horizon."""
    SHORT = "short"  # 30 days
    MEDIUM = "medium"  # 90 days
    LONG = "long"  # 365 days


class DomainTrend(BaseModel):
    """Trend for a domain."""
    domain: str
    current_performance: float
    projected_performance_30d: float
    projected_performance_90d: float
    projected_performance_365d: float
    trend_direction: TrendDirection
    trend_confidence: float = Field(ge=0, le=1)
    acceleration: float = 0.0  # Positive = improving faster


class RiskProjection(BaseModel):
    """Projection of future risk."""
    domain: str
    risk_type: str
    current_risk: float
    projected_risk_30d: float
    projected_risk_90d: float
    probability_of_event: float = Field(ge=0, le=1)
    estimated_time_to_event_days: Optional[int] = None
    severity: RiskLevel = RiskLevel.LOW


class GoalProbability(BaseModel):
    """Probability of achieving a goal."""
    goal_id: str
    goal_name: str
    current_progress: float = Field(ge=0, le=1)
    probability_of_success: float = Field(ge=0, le=1)
    expected_completion_date: Optional[date] = None
    expected_months_to_completion: Optional[float] = None
    confidence: float = Field(ge=0, le=1)
    risk_factors: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None


class FutureScenario(BaseModel):
    """A potential future scenario."""
    scenario_id: str
    scenario_name: str
    probability: float = Field(ge=0, le=1)
    domain_states: Dict[str, float]  # domain -> projected performance
    key_events: List[str] = Field(default_factory=list)
    overall_risk: float = 0.0
    description: str


class ForecastCycle(BaseModel):
    """Results of a forecast cycle."""
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Domain trends
    domain_trends: List[DomainTrend] = Field(default_factory=list)
    
    # Risk projections
    risk_projections: List[RiskProjection] = Field(default_factory=list)
    
    # Goal probabilities
    goal_probabilities: List[GoalProbability] = Field(default_factory=list)
    
    # Scenarios
    scenarios: List[FutureScenario] = Field(default_factory=list)
    
    # Summary
    highest_risk_domains: List[str] = Field(default_factory=list)
    declining_domains: List[str] = Field(default_factory=list)
    at_risk_goals: List[str] = Field(default_factory=list)
    opportunities_identified: List[str] = Field(default_factory=list)


class ForecastPolicy(BaseModel):
    """Policy for forecasting."""
    short_horizon_days: int = 30
    medium_horizon_days: int = 90
    long_horizon_days: int = 365
    min_confidence_threshold: float = 0.5
    scenarios_to_generate: int = 4


class ForecastStatistics(BaseModel):
    """Statistics about forecasting."""
    total_cycles: int = 0
    last_forecast_time: Optional[datetime] = None
    average_confidence: float = 0.0
    predictions_accurate: float = 0.0
