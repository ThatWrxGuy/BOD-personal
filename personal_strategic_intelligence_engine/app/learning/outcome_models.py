"""Outcome tracking and learning models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LifecycleStatus(str, Enum):
    """Status of a recommendation over time."""
    ISSUED = "issued"
    OBSERVED = "observed"
    FOLLOWED = "followed"
    IGNORED = "ignored"
    BLOCKED = "blocked"
    UNRESOLVED = "unresolved"
    EXPIRED = "expired"


class OutcomeQuality(str, Enum):
    """Quality of the observed outcome."""
    IMPROVEMENT = "improvement"
    NO_CHANGE = "no_change"
    DETERIORATION = "deterioration"
    MIXED = "mixed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ObservationWindow(BaseModel):
    """Time window for observing outcomes."""
    window_type: str = "standard"  # standard, extended, short
    duration_hours: int = 168  # 7 days default
    start_time: datetime
    end_time: Optional[datetime] = None


class RecommendationOutcomeRecord(BaseModel):
    """Record of a recommendation and its observed outcome."""
    recommendation_id: str
    cycle_id: str
    target_domain: str
    action: str
    issued_timestamp: datetime
    baseline_state: Dict[str, Any] = Field(default_factory=dict)
    observation_window: Optional[ObservationWindow] = None
    followup_signals: List[Dict[str, Any]] = Field(default_factory=list)
    followup_state: Dict[str, Any] = Field(default_factory=dict)
    lifecycle_status: LifecycleStatus = LifecycleStatus.ISSUED
    outcome_quality: Optional[OutcomeQuality] = None
    effectiveness_score: Optional[float] = None
    confidence_adjustment: float = 0.0
    evaluation_rationale: str = ""
    evaluated_at: Optional[datetime] = None


class OutcomeEvaluationResult(BaseModel):
    """Result of evaluating a recommendation outcome."""
    recommendation_id: str
    cycle_id: str
    outcome_quality: OutcomeQuality
    evidence_summary: Dict[str, Any] = Field(default_factory=dict)
    magnitude_of_change: float = 0.0
    direction: str = "neutral"  # positive, negative, neutral
    confidence_in_evaluation: float = 0.5
    evaluation_rationale: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class RecommendationEffectivenessScore(BaseModel):
    """Aggregated effectiveness score for recommendations."""
    recommendation_id: str
    total_evaluations: int = 0
    positive_outcomes: int = 0
    negative_outcomes: int = 0
    neutral_outcomes: int = 0
    average_effectiveness: float = 0.0
    confidence_impact: float = 0.0
    pattern_flags: List[str] = Field(default_factory=list)


class ConfidenceCalibrationResult(BaseModel):
    """Result of confidence calibration based on outcomes."""
    domain: str
    baseline_confidence: float
    adjusted_confidence: float
    calibration_factor: float
    evidence_count: int
    rationale: str
    calibrated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningCycleSummary(BaseModel):
    """Summary of learning from a batch of recommendations."""
    cycle_id: str
    timestamp: datetime
    recommendations_evaluated: int
    positive_outcomes: int
    negative_outcomes: int
    neutral_outcomes: int
    avg_effectiveness_score: float
    confidence_adjustments: Dict[str, float] = Field(default_factory=dict)
    learning_insights: List[str] = Field(default_factory=list)


class LearningEvent(BaseModel):
    """Structured log event for learning operations."""
    event_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    event_type: str
    recommendation_id: Optional[str] = None
    cycle_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    lifecycle_status: Optional[str] = None
    outcome_quality: Optional[str] = None
    effectiveness_score: Optional[float] = None
    confidence_adjustment: float = 0.0
    processing_latency_ms: float = 0.0
    error_message: Optional[str] = None


# Constants for safety
LIVE_EXECUTION_ENABLED = False  # No real execution
LEARNING_MODE = True  # Learning is observational only
