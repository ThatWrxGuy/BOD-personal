"""Evaluation Types - Core models for intervention effectiveness evaluation."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EvaluationStatus(str, Enum):
    """Status of an evaluation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InterventionOutcome(BaseModel):
    """Outcome of a single intervention."""
    intervention_id: str
    protocol_name: str
    protocol_id: str
    target_domain: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Initial state
    initial_performance: float
    initial_risk: float
    initial_momentum: float
    
    # Post-intervention state
    post_performance: float = 0.0
    post_risk: float = 0.0
    post_momentum: float = 0.0
    
    # Measurements
    performance_change: float = 0.0
    risk_change: float = 0.0
    momentum_change: float = 0.0
    
    # Recovery tracking
    time_to_recovery_days: Optional[int] = None
    recovered: bool = False
    
    # Confidence
    confidence_score: float = 0.0
    
    # Outcome classification
    outcome: str = "unknown"  # success, partial, failure, harmful
    

class ProtocolEffectiveness(BaseModel):
    """Effectiveness scores for a protocol."""
    protocol_id: str
    protocol_name: str
    
    # Count metrics
    total_interventions: int = 0
    successful_interventions: int = 0
    failed_interventions: int = 0
    partial_interventions: int = 0
    
    # Performance metrics
    average_performance_improvement: float = 0.0
    average_risk_reduction: float = 0.0
    average_momentum_change: float = 0.0
    
    # Derived scores
    success_rate: float = 0.0
    effectiveness_score: float = 0.0
    consistency_score: float = 0.0
    
    # Recovery metrics
    average_recovery_time_days: float = 0.0
    recovery_rate: float = 0.0
    
    # Flag for review
    requires_review: bool = False
    review_reason: Optional[str] = None


class ThresholdAnalysis(BaseModel):
    """Analysis of trigger thresholds."""
    trigger_type: str
    
    # Threshold metrics
    threshold_value: float
    times_triggered: int = 0
    
    # Outcome metrics
    useful_triggers: int = 0
    useless_triggers: int = 0
    success_rate: float = 0.0
    
    # Recommendations
    recommended_adjustment: Optional[str] = None
    confidence: float = 0.0


class EvaluationCycle(BaseModel):
    """Results of an evaluation cycle."""
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: EvaluationStatus = EvaluationStatus.PENDING
    
    # Metrics
    total_interventions_evaluated: int = 0
    total_protocols_evaluated: int = 0
    protocols_requiring_review: List[str] = Field(default_factory=list)
    
    # Aggregated metrics
    overall_success_rate: float = 0.0
    average_performance_improvement: float = 0.0
    average_risk_reduction: float = 0.0
    average_recovery_time: float = 0.0
    
    # Threshold recommendations
    threshold_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Protocol rankings
    top_protocols: List[Dict[str, Any]] = Field(default_factory=list)
    bottom_protocols: List[Dict[str, Any]] = Field(default_factory=list)


class EvaluationPolicy(BaseModel):
    """Policy for evaluation."""
    min_interventions_for_review: int = 5
    success_rate_threshold: float = 0.5
    review_confidence_threshold: float = 0.7
    enable_auto_threshold_adjustment: bool = False


class EvaluationStatistics(BaseModel):
    """Statistics about all evaluations."""
    total_cycles: int = 0
    total_interventions_tracked: int = 0
    total_protocols_evaluated: int = 0
    overall_success_rate: float = 0.0
    
    # Protocol breakdown
    protocol_stats: Dict[str, ProtocolEffectiveness] = Field(default_factory=dict)
    
    # Historical trends
    recent_trends: Dict[str, Any] = Field(default_factory=dict)
