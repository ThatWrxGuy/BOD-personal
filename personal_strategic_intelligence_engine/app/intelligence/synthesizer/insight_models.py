"""Insight Models - Standardized intelligence data models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class InsightCategory(str, Enum):
    """Categories of strategic insights."""
    TREND = "trend"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    WEAKNESS = "weakness"
    STRENGTH = "strength"
    FORECAST = "forecast"
    SIMULATION = "simulation"
    STRESS_TEST = "stress_test"


class UrgencyLevel(str, Enum):
    """Urgency levels for insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskSeverity(str, Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StrategicInsight(BaseModel):
    """A strategic insight extracted from predictive outputs."""
    id: str
    category: InsightCategory
    title: str
    description: str
    
    # Scoring
    impact_score: float = Field(ge=0, le=10)  # How much this matters
    confidence_score: float = Field(ge=0, le=1)  # How confident we are
    priority_score: float = Field(ge=0, le=10, default=5.0)  # Combined priority
    
    # Context
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    source_engine: str  # Which engine generated this
    
    # Evidence
    supporting_evidence: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    relevant_horizon_days: int = 30
    
    # Metadata
    domains_affected: List[str] = Field(default_factory=list)
    goals_affected: List[str] = Field(default_factory=list)


class StrategicRecommendation(BaseModel):
    """A recommended strategic action."""
    id: str
    title: str
    description: str
    recommended_action: str
    
    # Expected outcome
    expected_outcome: str
    expected_impact: float = Field(ge=0, le=10)
    
    # Confidence
    confidence: float = Field(ge=0, le=1)
    
    # Risk assessment
    risk_level: RiskSeverity = RiskSeverity.MEDIUM
    
    # Related insight
    source_insight_id: Optional[str] = None
    
    # Implementation
    implementation_effort: str = "medium"  # low, medium, high
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IntelligenceConflict(BaseModel):
    """A conflict detected between predictive engines."""
    id: str
    conflict_type: str
    
    description: str
    
    # Sources of conflict
    source_a: str  # Engine A
    source_b: str  # Engine B
    
    # Details
    prediction_a: str
    prediction_b: str
    
    # Resolution
    severity: RiskSeverity = RiskSeverity.MEDIUM
    resolved: bool = False
    resolution_notes: str = ""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StrategicIntelligenceReport(BaseModel):
    """Complete strategic intelligence report."""
    report_id: str
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core outputs
    insights: List[StrategicInsight] = Field(default_factory=list)
    recommendations: List[StrategicRecommendation] = Field(default_factory=list)
    conflicts: List[IntelligenceConflict] = Field(default_factory=list)
    
    # Summary
    total_insights: int = 0
    total_recommendations: int = 0
    critical_issues: int = 0
    
    # Supporting data
    forecast_summary: Dict[str, Any] = Field(default_factory=dict)
    simulation_summary: Dict[str, Any] = Field(default_factory=dict)
    monte_carlo_summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    engines_used: List[str] = Field(default_factory=list)
    processing_time_ms: int = 0


class PredictionSnapshot(BaseModel):
    """Snapshot of prediction data from an engine."""
    engine_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Domain predictions
    domain_predictions: Dict[str, float] = Field(default_factory=dict)
    
    # Risk predictions
    risk_predictions: Dict[str, float] = Field(default_factory=dict)
    
    # Goal probabilities
    goal_probabilities: Dict[str, float] = Field(default_factory=dict)
    
    # Strategy rankings
    strategy_rankings: Dict[str, float] = Field(default_factory=dict)
    
    # Additional data
    raw_data: Dict[str, Any] = Field(default_factory=dict)
