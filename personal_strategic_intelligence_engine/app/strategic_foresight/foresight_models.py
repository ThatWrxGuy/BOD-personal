"""Foresight Models.

Defines predictive intelligence data structures.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ForecastHorizon(str, Enum):
    """Time horizons for forecasts."""
    DAYS_7 = "7_days"
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    DAYS_365 = "365_days"


class Domain(str, Enum):
    """Strategic domains."""
    HEALTH = "health"
    FINANCE = "finance"
    PRODUCTIVITY = "productivity"
    SCHEDULE = "schedule"
    RISK = "risk"


class RiskType(str, Enum):
    """Types of strategic risks."""
    BURNOUT = "burnout"
    FINANCIAL_STRESS = "financial_stress"
    PRODUCTIVITY_COLLAPSE = "productivity_collapse"
    LIQUIDITY_SHORTAGE = "liquidity_shortage"
    SCHEDULE_OVERLOAD = "schedule_overload"


class OpportunityType(str, Enum):
    """Types of strategic opportunities."""
    FINANCIAL_SURPLUS = "financial_surplus"
    SCHEDULE_RECOVERY = "schedule_recovery"
    HIGH_PRODUCTIVITY = "high_productivity"
    HEALTH_RECOVERY = "health_recovery"


class ScenarioType(str, Enum):
    """Types of forecast scenarios."""
    BASELINE = "baseline"
    ESCALATION = "escalation"
    RECOVERY = "recovery"
    CROSS_DOMAIN = "cross_domain"


class FutureTrajectory(BaseModel):
    """A projected future trajectory."""
    trajectory_id: str
    domain: Domain
    
    # Time horizon
    horizon: ForecastHorizon
    
    # Projection
    start_value: float
    projected_value: float
    trend: str  # "increasing", "decreasing", "stable"
    
    # Signals
    contributing_signals: Dict[str, float] = Field(default_factory=dict)
    
    # Timing
    projected_date: datetime
    
    # Confidence
    confidence: float = 0.5


class StrategicRiskProjection(BaseModel):
    """A projected strategic risk."""
    risk_id: str
    risk_type: RiskType
    domain: Domain
    
    # Probability
    probability: float = 0.0  # 0.0 to 1.0
    
    # Time horizon
    horizon: ForecastHorizon
    projected_days: int
    
    # Contributing signals
    contributing_signals: Dict[str, float] = Field(default_factory=dict)
    
    # Severity
    severity: str = "low"  # low, medium, high, critical
    
    # Confidence
    confidence: float = 0.5
    
    # Recommendations
    preventive_recommendations: List[str] = Field(default_factory=list)


class StrategicOpportunityProjection(BaseModel):
    """A projected strategic opportunity."""
    opportunity_id: str
    opportunity_type: OpportunityType
    domain: Domain
    
    # Probability
    probability: float = 0.0
    
    # Time horizon
    horizon: ForecastHorizon
    projected_days: int
    
    # Supporting signals
    supporting_signals: Dict[str, float] = Field(default_factory=dict)
    
    # Potential value
    potential_value: float = 0.0
    
    # Confidence
    confidence: float = 0.5
    
    # Recommendations
    capitalizing_recommendations: List[str] = Field(default_factory=list)


class ScenarioProjection(BaseModel):
    """An alternative future scenario."""
    scenario_id: str
    scenario_type: ScenarioType
    description: str
    
    # Domain
    domains: List[Domain] = Field(default_factory=list)
    
    # Time
    horizon: ForecastHorizon
    
    # Projections
    projected_changes: Dict[str, float] = Field(default_factory=dict)
    
    # Probability
    probability: float = 0.5
    
    # Confidence
    confidence: float = 0.5


class ForecastProbability(BaseModel):
    """Probability estimate for an outcome."""
    outcome: str
    domain: Domain
    
    # Probability
    probability: float = 0.0
    
    # Time horizon
    horizon: ForecastHorizon
    
    # Confidence interval
    confidence_lower: float = 0.0
    confidence_upper: float = 1.0
    
    # Confidence score
    confidence: float = 0.5
    
    # Evidence
    evidence_count: int = 0


class StrategicForecastReport(BaseModel):
    """Complete strategic forecast report."""
    report_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Context
    current_signals: Dict[str, float] = Field(default_factory=dict)
    
    # Trajectories
    trajectories: List[FutureTrajectory] = Field(default_factory=list)
    
    # Risks
    risks: List[StrategicRiskProjection] = Field(default_factory=list)
    
    # Opportunities
    opportunities: List[StrategicOpportunityProjection] = Field(default_factory=list)
    
    # Scenarios
    scenarios: List[ScenarioProjection] = Field(default_factory=list)
    
    # Probabilities
    probabilities: List[ForecastProbability] = Field(default_factory=list)
    
    # Summary
    high_priority_risks: int = 0
    high_value_opportunities: int = 0
    
    # Metadata
    forecast_horizons: List[ForecastHorizon] = Field(default_factory=list)


class ForesightSummary(BaseModel):
    """Summary of foresight state."""
    total_risks: int = 0
    total_opportunities: int = 0
    total_scenarios: int = 0
    
    # Coverage
    domains_covered: List[str] = Field(default_factory=list)
    horizons_covered: List[str] = Field(default_factory=list)
    
    # Assessment
    overall_risk_level: str = "low"
    overall_opportunity_level: str = "moderate"
    
    # Generated
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants
LIVE_EXECUTION_ENABLED = False
FORESIGHT_MODE = "advisory"
