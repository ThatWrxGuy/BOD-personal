"""Doctrine data models for strategic alignment."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AlignmentLevel(str, Enum):
    """Level of alignment with doctrine."""
    ALIGNED = "aligned"
    MISALIGNED = "misaligned"
    REQUIRES_REVIEW = "requires_review"
    NEUTRAL = "neutral"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyRuleType(str, Enum):
    """Categories of policy rules."""
    RISK_MANAGEMENT = "risk_management"
    CAPITAL_ALLOCATION = "capital_allocation"
    SIGNAL_RELIABILITY = "signal_reliability"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    STRATEGIC_ALIGNMENT = "strategic_alignment"
    ETHICAL_CONSTRAINTS = "ethical_constraints"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PRIORITY_BALANCE = "priority_balance"


class PolicyRule(BaseModel):
    """A doctrine policy rule."""
    rule_id: str
    rule_type: PolicyRuleType
    name: str
    description: str
    enabled: bool = True
    weight: float = 1.0  # How much this rule influences alignment
    threshold: float = 0.5  # Threshold for triggering
    priority: int = 1  # Higher = more important


class AlignmentScore(BaseModel):
    """Score representing doctrine alignment."""
    level: AlignmentLevel
    score: float = Field(ge=-1.0, le=1.0)  # -1 to 1 scale
    confidence: float = Field(ge=0.0, le=1.0)
    factors: Dict[str, float] = Field(default_factory=dict)


class DoctrineConflict(BaseModel):
    """Conflict detected between rules or with state."""
    conflict_type: str
    rules_involved: List[str]
    severity: float = Field(ge=0.0, le=1.0)
    description: str
    resolution_suggestion: Optional[str] = None


class DoctrineRecommendation(BaseModel):
    """Recommendation from doctrine evaluation."""
    adjustment_type: str  # priority_adjustment, policy_adjustment, flag
    target: str  # domain or recommendation_id
    adjustment: float
    rationale: str
    priority: int


class DecisionContext(BaseModel):
    """Context for doctrine evaluation."""
    cycle_id: str
    timestamp: datetime
    signals: List[Dict[str, Any]] = Field(default_factory=list)
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    optimization_output: Dict[str, Any] = Field(default_factory=dict)
    candidate_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    learning_feedback: Dict[str, Any] = Field(default_factory=dict)
    journal_history: List[Dict[str, Any]] = Field(default_factory=list)


class DoctrineAssessment(BaseModel):
    """Complete doctrine evaluation result."""
    cycle_id: str
    timestamp: datetime
    doctrine_version: str = "1.0.0"
    
    # Core assessment
    alignment_score: AlignmentScore
    
    # Conflicts and risks
    doctrine_conflicts: List[DoctrineConflict] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommended_adjustments: List[DoctrineRecommendation] = Field(default_factory=list)
    
    # Audit trail
    policy_rules_applied: List[str] = Field(default_factory=list)
    signals_considered: List[str] = Field(default_factory=list)
    journal_events_referenced: List[str] = Field(default_factory=list)
    learning_feedback_used: List[str] = Field(default_factory=list)
    
    # Confidence
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Explanation
    evaluation_summary: str = ""


class DoctrineEvent(BaseModel):
    """Structured log event for doctrine operations."""
    event_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    event_type: str
    cycle_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    doctrine_version: str = "1.0.0"
    alignment_level: Optional[str] = None
    rules_evaluated: int = 0
    processing_latency_ms: float = 0.0
    error_message: Optional[str] = None


# Safety constants
LIVE_EXECUTION_ENABLED = False  # Doctrine never executes
DOCTRINE_VERSION = "1.0.0"
