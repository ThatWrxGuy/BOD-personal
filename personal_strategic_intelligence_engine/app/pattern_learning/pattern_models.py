"""Pattern Learning Models.

Defines core structures for decision pattern learning.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StrategyFamily(str, Enum):
    """Strategy families for grouping recommendations."""
    DEFENSIVE_STABILIZATION = "defensive_stabilization"
    PRODUCTIVITY_FOCUS = "productivity_focus"
    FINANCIAL_STABILIZATION = "financial_stabilization"
    HEALTH_RECOVERY = "health_recovery"
    FOCUS_PRIORITIZATION = "focus_prioritization"
    RISK_MITIGATION = "risk_mitigation"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    EXPLORATION = "exploration"


class OutcomeType(str, Enum):
    """Types of decision outcomes."""
    IMPROVEMENT = "improvement"
    STABILIZATION = "stabilization"
    DETERIORATION = "deterioration"
    NO_CHANGE = "no_change"
    MIXED = "mixed"


class DecisionContextProfile(BaseModel):
    """Profile of a decision context."""
    context_id: str
    
    # Signal profile
    signal_signatures: Dict[str, float] = Field(default_factory=dict)  # signal_type -> value
    
    # Domain conditions
    domains: List[str] = Field(default_factory=list)
    
    # Severity
    overall_severity: float = 0.5
    
    # Persistence
    has_persistent_signals: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sample_size: int = 0


class DecisionPattern(BaseModel):
    """A pattern of decisions and outcomes."""
    pattern_id: str
    
    # Context
    context: DecisionContextProfile
    
    # Recommendation family
    recommendation_family: StrategyFamily
    
    # Outcomes
    observed_outcomes: List[str] = Field(default_factory=list)
    outcome_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Statistics
    success_count: int = 0
    failure_count: int = 0
    total_count: int = 0
    
    # Confidence
    success_rate: float = 0.0
    failure_rate: float = 0.0
    confidence_level: float = 0.0
    
    # Evidence
    evidence_record_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    first_observed: datetime = Field(default_factory=datetime.utcnow)
    last_observed: datetime = Field(default_factory=datetime.utcnow)


class RecommendationFamily(BaseModel):
    """A family of related recommendations."""
    family_id: str
    family_name: str
    strategy_family: StrategyFamily
    
    # Recommendations in this family
    recommendation_types: List[str] = Field(default_factory=list)
    
    # Aggregate statistics
    total_attempts: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Effectiveness
    success_rate: float = 0.0
    average_impact: float = 0.0
    
    # Metadata
    domain: str = "general"
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContextCluster(BaseModel):
    """A cluster of similar decision contexts."""
    cluster_id: str
    cluster_name: str
    
    # Typical signals
    typical_signals: Dict[str, float] = Field(default_factory=dict)
    
    # Domain focus
    primary_domain: str = "general"
    
    # Member patterns
    pattern_ids: List[str] = Field(default_factory=list)
    
    # Statistics
    member_count: int = 0
    
    # Strategy rankings within this cluster
    recommended_strategies: List[str] = Field(default_factory=list)
    suppressed_strategies: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PatternOutcomeSummary(BaseModel):
    """Summary of outcomes for a pattern."""
    pattern_id: str
    
    # Counts
    total_decisions: int = 0
    improvements: int = 0
    stabilizations: int = 0
    deteriorations: int = 0
    no_changes: int = 0
    
    # Rates
    success_rate: float = 0.0
    failure_rate: float = 0.0
    
    # Average impact
    avg_impact_score: float = 0.0
    
    # Confidence
    confidence: float = 0.0
    sample_size_adequate: bool = False


class StrategyEffectivenessScore(BaseModel):
    """Score for a strategy's effectiveness in a context."""
    strategy_family: StrategyFamily
    context_cluster_id: str
    
    # Rankings
    rank: int = 0
    score: float = 0.0
    
    # Statistics
    success_rate: float = 0.0
    sample_size: int = 0
    
    # Adjustment
    contextual_adjustment: float = 0.0
    final_score: float = 0.0
    
    # Confidence
    confidence: float = 0.0
    is_reliable: bool = False


class ContextualStrategyScore(BaseModel):
    """Strategy score adjusted by contextual pattern learning."""
    recommendation_id: str
    recommendation_type: str
    strategy_family: StrategyFamily
    
    # Base score (from recommendation engine)
    base_score: float = 0.5
    
    # Pattern adjustments
    pattern_adjustment: float = 0.0
    exploration_bonus: float = 0.0
    
    # Final score
    final_score: float = 0.5
    
    # Confidence
    confidence: float = 0.5
    
    # Justification
    justification: str = ""
    
    # Metadata
    context_cluster_id: Optional[str] = None


class PatternLearningSummary(BaseModel):
    """Summary of pattern learning state."""
    total_patterns: int = 0
    total_clusters: int = 0
    total_families: int = 0
    
    # Coverage
    domains_covered: List[str] = Field(default_factory=list)
    
    # Statistics
    avg_success_rate: float = 0.0
    avg_confidence: float = 0.0
    
    # Strong strategies
    strong_strategies: Dict[str, float] = Field(default_factory=dict)
    
    # Weak strategies
    weak_strategies: Dict[str, float] = Field(default_factory=dict)
    
    # Generated at
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants
LIVE_EXECUTION_ENABLED = False
PATTERN_LEARNING_MODE = "advisory"
