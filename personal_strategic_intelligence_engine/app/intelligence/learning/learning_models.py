"""Learning Models - Data models for meta-cognitive learning layer."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StrategyType(str, Enum):
    """Types of strategic actions."""
    RISK_MITIGATION = "risk_mitigation"
    OPPORTUNITY_SEIZING = "opportunity_seizing"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RESOURCE_REALLOCATION = "resource_reallocation"
    BALANCE_ADJUSTMENT = "balance_adjustment"
    FOCUS_SHIFT = "focus_shift"


class DecisionStatus(str, Enum):
    """Status of a tracked decision."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    EVALUATED = "evaluated"
    EXPIRED = "expired"


class OutcomeStatus(str, Enum):
    """Status of outcome evaluation."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    INCONCLUSIVE = "inconclusive"


class DecisionRecord(BaseModel):
    """Record of a strategic decision."""
    decision_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Source
    insight_id: Optional[str] = None
    recommendation_id: str
    
    # Decision details
    strategy_type: StrategyType
    action: str
    expected_outcome: str
    
    # Context
    confidence: float = Field(ge=0, le=1)
    priority_score: float = Field(ge=0, le=10)
    
    # State snapshot
    domain_state: Dict[str, float] = Field(default_factory=dict)
    risk_state: Dict[str, float] = Field(default_factory=dict)
    
    # Status
    status: DecisionStatus = DecisionStatus.PENDING
    evaluation_id: Optional[str] = None
    
    # Metadata
    source_engine: str = "synthesizer"


class OutcomeEvaluation(BaseModel):
    """Evaluation of a decision's outcome."""
    evaluation_id: str
    decision_id: str
    
    # Timing
    decision_timestamp: datetime
    evaluation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    time_elapsed_days: int = 0
    
    # Outcome assessment
    outcome_status: OutcomeStatus
    success_score: float = Field(ge=0, le=1)  # 0 = failure, 1 = success
    
    # Metrics
    expected_vs_actual: Dict[str, float] = Field(default_factory=dict)
    goal_progress_change: float = 0.0
    risk_change: float = 0.0
    performance_change: float = 0.0
    
    # Deviations
    deviation_from_expected: float = 0.0
    deviation_description: str = ""
    
    # Notes
    notes: str = ""


class StrategyEffectiveness(BaseModel):
    """Effectiveness metrics for a strategy type."""
    strategy_type: StrategyType
    
    # Counts
    total_decisions: int = 0
    successful_decisions: int = 0
    failed_decisions: int = 0
    
    # Rates
    success_rate: float = 0.0
    
    # Impact metrics
    average_impact: float = 0.0
    average_confidence: float = 0.0
    average_risk_change: float = 0.0
    
    # Accuracy
    confidence_accuracy: float = 0.0  # How often confidence matched outcome
    
    # Historical data
    historical_samples: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class DoctrineUpdate(BaseModel):
    """Record of a doctrine update."""
    update_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # What changed
    parameter_name: str
    old_value: float
    new_value: float
    change_reason: str
    
    # Impact
    affected_strategies: List[str] = Field(default_factory=list)
    
    # Verification
    verified: bool = False


class LearningReport(BaseModel):
    """Complete learning report."""
    report_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Evaluation summary
    decisions_evaluated: int = 0
    successful_decisions: int = 0
    failed_decisions: int = 0
    
    # Strategy effectiveness
    strategy_effectiveness: Dict[str, StrategyEffectiveness] = Field(default_factory=dict)
    
    # Doctrine updates
    doctrine_updates: List[DoctrineUpdate] = Field(default_factory=list)
    
    # Patterns detected
    successful_strategies: List[str] = Field(default_factory=list)
    failing_strategies: List[str] = Field(default_factory=list)
    emerging_patterns: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommended_doctrine_changes: List[str] = Field(default_factory=list)
    
    # Metadata
    evaluation_period_days: int = 0
    confidence: float = 0.0


class LearningPolicy(BaseModel):
    """Policy for learning behavior."""
    # Evaluation timing
    evaluation_delay_days: int = 7  # Wait before evaluating
    minimum_samples_for_update: int = 5
    
    # Update constraints
    max_weight_change_per_update: float = 0.1  # Max 10% change
    learning_rate: float = 0.05
    
    # Thresholds
    success_rate_threshold: float = 0.7
    failure_rate_threshold: float = 0.4
    
    # Confidence calibration
    confidence_tolerance: float = 0.2  # How far off before adjustment
