"""Audit Models.

Defines structures for strategic audit.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TimeHorizon(str, Enum):
    """Time horizon for decisions."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SignalObservation(BaseModel):
    """A signal observed during a cycle."""
    signal_id: str
    signal_type: str
    domain: str
    value: float
    timestamp: datetime
    
    # Calibration
    calibrated_value: float = 0.0
    weight: float = 1.0
    is_usable: bool = True
    
    # Source
    source: str = "connector"


class DecisionRecord(BaseModel):
    """A decision made by the system."""
    decision_id: str
    timestamp: datetime
    
    # Decision details
    decision_type: str
    action_type: str
    description: str
    
    # Context
    time_horizon: TimeHorizon
    domains: List[str] = Field(default_factory=list)
    
    # Signals
    triggered_by: List[str] = Field(default_factory=list)
    
    # Governance
    governance_outcome: str = "approved"  # approved, rejected, requires_manual
    
    # Execution
    execution_intent: Optional[str] = None
    simulated_execution: bool = False
    
    # Learning
    confidence: float = 0.5
    outcome: Optional[str] = None


class GovernanceOutcome(BaseModel):
    """Outcome of governance review."""
    decision_id: str
    approved: bool
    requires_manual: bool = False
    rejection_reason: Optional[str] = None
    
    # Approval level
    approval_level: str = "auto"  # auto, manager, executive
    
    # Policy check
    policy_passed: bool = True
    policy_details: Dict[str, Any] = Field(default_factory=dict)


class LearningUpdate(BaseModel):
    """Learning update from a cycle."""
    timestamp: datetime
    update_type: str
    
    # What was learned
    entity_type: str
    entity_id: str
    adjustment: float = 0.0
    new_confidence: float = 0.5


class PatternInsight(BaseModel):
    """Pattern insight from pattern learning."""
    timestamp: datetime
    
    # Insight details
    insight_type: str
    description: str
    
    # Evidence
    context_cluster: Optional[str] = None
    strategy_family: Optional[str] = None
    success_rate: float = 0.0
    sample_size: int = 0


class MemoryRelationship(BaseModel):
    """Memory relationship formed during audit."""
    timestamp: datetime
    
    # Relationship
    source_node: str
    target_node: str
    relationship_type: str
    
    # Evidence
    evidence_count: int = 1
    confidence: float = 0.5


class CycleAuditRecord(BaseModel):
    """Complete audit record for a single cycle."""
    cycle_id: str
    cycle_number: int
    timestamp: datetime
    
    # Time context
    time_horizon: TimeHorizon
    day_number: int
    
    # Signals
    signals_observed: List[SignalObservation] = Field(default_factory=list)
    signals_calibrated: int = 0
    
    # Decisions
    decisions: List[DecisionRecord] = Field(default_factory=list)
    
    # Governance
    governance_outcomes: List[GovernanceOutcome] = Field(default_factory=list)
    
    # Learning
    learning_updates: List[LearningUpdate] = Field(default_factory=list)
    
    # Pattern learning
    pattern_insights: List[PatternInsight] = Field(default_factory=list)
    
    # Memory
    memory_relationships: List[MemoryRelationship] = Field(default_factory=list)
    
    # State
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)


class StrategicIntelligenceMetrics(BaseModel):
    """Strategic intelligence metrics computed during audit."""
    
    # SSAR - Signal to Action Ratio
    ssar: float = 0.0  # meaningful decisions / total signals
    ssar_rating: str = "unknown"  # low, optimal, high
    
    # SCS - Strategic Consistency Score
    scs: float = 0.0  # alignment across time horizons
    scs_rating: str = "unknown"  # low, moderate, high
    
    # SISR - Strategic Intervention Success Rate
    sisr: float = 0.0  # successful interventions / total
    sisr_rating: str = "unknown"  # low, moderate, high
    
    # Decision quality
    strategic_coherence_score: float = 0.0
    signal_justification_score: float = 0.0
    proportional_response_score: float = 0.0
    domain_balance_score: float = 0.0
    execution_discipline_score: float = 0.0
    
    # Decision load
    avg_decisions_per_day: float = 0.0
    weekly_decision_load: float = 0.0
    recommendation_saturation_events: int = 0
    decision_load_classification: str = "unknown"  # low, moderate, high
    
    # Strategic drift
    drift_events: int = 0
    drift_severity: str = "none"  # none, low, moderate, high


class StrategicBehaviorScore(BaseModel):
    """Composite strategic behavior score."""
    
    # Overall score (0-100)
    overall_score: float = 0.0
    score_grade: str = "F"  # A, B, C, D, F
    
    # Component scores
    signal_interpretation_quality: float = 0.0
    decision_coherence: float = 0.0
    intervention_success: float = 0.0
    governance_discipline: float = 0.0
    learning_adaptation: float = 0.0
    
    # Summary
    assessment: str = ""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class AuditSummary(BaseModel):
    """Summary of the complete audit."""
    # Cycle counts
    total_cycles: int = 0
    daily_cycles: int = 0
    weekly_cycles: int = 0
    monthly_cycles: int = 0
    quarterly_cycles: int = 0
    yearly_cycles: int = 0
    
    # Signal counts
    total_signals_observed: int = 0
    signals_calibrated: int = 0
    
    # Decision counts
    total_decisions: int = 0
    daily_decisions: int = 0
    weekly_decisions: int = 0
    monthly_decisions: int = 0
    quarterly_decisions: int = 0
    yearly_decisions: int = 0
    
    # Governance
    approved_decisions: int = 0
    rejected_decisions: int = 0
    manual_required: int = 0
    
    # Execution
    execution_intents: int = 0
    simulated_executions: int = 0
    
    # Learning
    learning_updates: int = 0
    pattern_insights: int = 0
    memory_relationships: int = 0
    
    # Metrics
    intelligence_metrics: StrategicIntelligenceMetrics = Field(
        default_factory=StrategicIntelligenceMetrics
    )
    behavior_score: StrategicBehaviorScore = Field(
        default_factory=StrategicBehaviorScore
    )
    
    # Alignment
    alignment_assessment: str = ""
    
    # Generated
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants
LIVE_EXECUTION_ENABLED = False
AUDIT_MODE = "simulation_only"
