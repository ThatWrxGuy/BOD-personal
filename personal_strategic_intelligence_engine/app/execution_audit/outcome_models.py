"""Execution audit data models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OutcomeCategory(str, Enum):
    """Category of execution outcome."""
    IMPROVEMENT = "improvement"
    NO_CHANGE = "no_change"
    DETERIORATION = "deterioration"
    MIXED = "mixed"
    ERROR = "error"
    UNKNOWN = "unknown"


class ReversibilityLevel(str, Enum):
    """Level of reversibility for an action."""
    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"
    UNKNOWN = "unknown"


class ApprovalPolicyLevel(str, Enum):
    """Level of approval required."""
    MANUAL_ONLY = "manual_only"
    REQUIRE_ADDITIONAL_REVIEW = "require_additional_review"
    ELIGIBLE_FOR_AUTO = "eligible_for_auto"
    AUTO_APPROVED = "auto_approved"


class ExecutionOutcomeSnapshot(BaseModel):
    """Snapshot of execution outcome."""
    snapshot_id: str = Field(default_factory=lambda: f"snap_{datetime.utcnow().timestamp()}")
    execution_id: str
    recommendation_id: str
    action_type: str
    domain: str
    
    # State comparison
    pre_execution_state: Dict[str, Any] = Field(default_factory=dict)
    post_execution_state: Dict[str, Any] = Field(default_factory=dict)
    
    # Observed signals
    observed_signals: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timing
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    observed_at: Optional[datetime] = None
    
    # Metadata
    confidence: float = 0.5
    error_message: Optional[str] = None


class OutcomeEvaluation(BaseModel):
    """Evaluation of an execution outcome."""
    evaluation_id: str = Field(default_factory=lambda: f"eval_{datetime.utcnow().timestamp()}")
    snapshot_id: str
    
    # Outcome category
    category: OutcomeCategory
    score: float = Field(ge=-1.0, le=1.0)  # -1 = deterioration, 1 = improvement
    
    # Details
    metrics_improved: List[str] = Field(default_factory=list)
    metrics_deteriorated: List[str] = Field(default_factory=list)
    metrics_unchanged: List[str] = Field(default_factory=list)
    
    # Confidence in evaluation
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = ""
    
    # Timing
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionReliabilityScore(BaseModel):
    """Reliability score for an action type."""
    action_type: str
    domain: str
    
    # Statistics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Success rate
    success_rate: float = Field(ge=0.0, le=1.0)
    
    # Trend
    recent_trend: str = "stable"  # improving, declining, stable
    
    # Last calculated
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Minimum data threshold
    min_samples: int = 5


class ReversibilityClassification(BaseModel):
    """Classification of action reversibility."""
    action_type: str
    domain: str
    
    reversibility: ReversibilityLevel
    reversible_conditions: List[str] = Field(default_factory=list)
    recovery_time_estimate: Optional[str] = None
    
    classified_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalPolicyRecommendation(BaseModel):
    """Recommendation for approval policy."""
    recommendation_id: str = Field(default_factory=lambda: f"policy_rec_{datetime.utcnow().timestamp()}")
    action_type: str
    domain: str
    
    # Current policy
    current_level: ApprovalPolicyLevel
    
    # Recommended policy
    recommended_level: ApprovalPolicyLevel
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Reasoning
    reasoning: str = ""
    supporting_evidence: List[str] = Field(default_factory=list)
    
    # Risk assessment
    risk_assessment: str = ""
    
    # Generated at
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants - audit subsystem doesn't modify execution
LIVE_EXECUTION_ENABLED = False  # Still enforced
EXECUTION_MODE_DISABLED = True  # Execution remains controlled
