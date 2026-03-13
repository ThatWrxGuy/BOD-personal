"""Governance simulation data models for stress testing."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """Types of governance stress scenarios."""
    STEADY_STATE = "steady_state"
    NOISY_SIGNAL = "noisy_signal"
    HIGH_VOLATILITY = "high_volatility"
    CONFLICTING_DOMAIN = "conflicting_domain"
    SIGNAL_RELIABILITY_DEGRADATION = "signal_reliability_degradation"
    CONFIDENCE_SHOCK = "confidence_shock"
    RECOVERY = "recovery"
    ADVERSARIAL_POLICY_PRESSURE = "adversarial_policy_pressure"


class SimulationCyclePhase(str, Enum):
    """Phases in a governance simulation cycle."""
    SIGNAL_INGESTION = "signal_ingestion"
    STATE_UPDATE = "state_update"
    FORECASTING = "forecasting"
    DOCTRINE_EVALUATION = "doctrine_evaluation"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    EXECUTION_INTENT = "execution_intent"
    GOVERNANCE_GATES = "governance_gates"
    EXECUTION_OUTCOME = "execution_outcome"
    LEARNING_UPDATE = "learning_update"
    APPROVAL_REASSESSMENT = "approval_reassessment"


class OscillationType(str, Enum):
    """Types of oscillation detected."""
    RECOMMENDATION_REVERSAL = "recommendation_reversal"
    PRIORITY_FLAPPING = "priority_flapping"
    CONFIDENCE_SWING = "confidence_swing"
    POLICY_STATE_ALTERNATION = "policy_state_alternation"


class ConflictSeverity(str, Enum):
    """Severity of doctrine conflicts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GovernanceSimulationScenario(BaseModel):
    """Configuration for a governance simulation scenario."""
    scenario_id: str = Field(default_factory=lambda: f"scenario_{datetime.utcnow().timestamp()}")
    scenario_type: ScenarioType
    name: str
    description: str
    
    # Simulation parameters
    cycle_count: int = 100
    random_seed: Optional[int] = None
    
    # Signal parameters
    signal_count_per_cycle: int = 5
    signal_noise_level: float = 0.0  # 0.0 = no noise, 1.0 = maximum noise
    signal_volatility: float = 0.0   # 0.0 = stable, 1.0 = highly volatile
    signal_conflict_rate: float = 0.0  # Rate of conflicting signals
    
    # Domain parameters
    domain_count: int = 3
    conflicting_domain_weight: float = 0.0
    
    # Stress parameters
    confidence_shock_magnitude: float = 0.0
    reliability_degradation_rate: float = 0.0
    
    # Execution parameters
    execution_intent_rate: float = 0.3  # Probability of generating execution intent
    auto_approval_enabled: bool = False
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SignalPattern(BaseModel):
    """Recorded signal pattern for simulation."""
    pattern_id: str
    domain: str
    category: str
    magnitude: float
    reliability: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GovernanceSimulationCycle(BaseModel):
    """Single cycle in a governance simulation."""
    cycle_id: str
    scenario_id: str
    cycle_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Input signals
    signals: List[SignalPattern] = Field(default_factory=list)
    
    # State
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing outputs
    optimization_output: Dict[str, Any] = Field(default_factory=dict)
    doctrine_assessment: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    execution_intents: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Governance gates
    governance_gate_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution outcome (simulated)
    execution_outcome: Optional[Dict[str, Any]] = None
    
    # Learning feedback
    learning_update: Dict[str, Any] = Field(default_factory=dict)
    
    # Approval tier
    current_tier: Optional[str] = None
    
    # Metrics
    cycle_duration_ms: float = 0.0
    phase_durations_ms: Dict[str, float] = Field(default_factory=dict)


class OscillationEvent(BaseModel):
    """Event detected as oscillation."""
    event_id: str = Field(default_factory=lambda: f"oscillation_{datetime.utcnow().timestamp()}")
    oscillation_type: OscillationType
    cycle_range: tuple[int, int]  # (start_cycle, end_cycle)
    
    # Details
    description: str
    affected_elements: List[str] = Field(default_factory=list)
    reversal_count: int = 0
    
    # Severity
    severity: str = "low"  # low, medium, high, critical
    amplitude: float = 0.0  # How extreme the oscillation is
    
    # Timing
    first_detected_at: datetime = Field(default_factory=datetime.utcnow)
    last_detected_at: datetime = Field(default_factory=datetime.utcnow)


class TierTransitionEvent(BaseModel):
    """Event for approval tier transitions."""
    event_id: str = Field(default_factory=lambda: f"tier_trans_{datetime.utcnow().timestamp()}")
    cycle_number: int
    
    # Transition details
    from_tier: str
    to_tier: str
    transition_type: str  # upgrade, downgrade, no_change
    
    # Trigger
    trigger: str
    details: str
    
    # Timing
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class DoctrineConflictEvent(BaseModel):
    """Event for doctrine conflicts detected."""
    event_id: str = Field(default_factory=lambda: f"doctrine_conf_{datetime.utcnow().timestamp()}")
    cycle_number: int
    
    # Conflict details
    conflict_type: str
    rules_involved: List[str] = Field(default_factory=list)
    severity: ConflictSeverity
    
    # Context
    context_hash: str  # Hash of the input context for comparison
    previous_result_hash: Optional[str] = None  # Hash of previous doctrine result
    
    # Description
    description: str
    
    # Timing
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class SaturationEvent(BaseModel):
    """Event for governance saturation detection."""
    event_id: str = Field(default_factory=lambda: f"saturation_{datetime.utcnow().timestamp()}")
    cycle_number: int
    
    # Saturation type
    saturation_type: str  # recommendation_overload, approval_queue, doctrine_flag_excess
    
    # Metrics
    current_load: float = 0.0
    capacity: float = 0.0
    overload_ratio: float = 0.0
    
    # Details
    affected_count: int = 0
    description: str
    
    # Timing
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class StabilityMetric(BaseModel):
    """Metric for governance stability."""
    metric_name: str
    value: float  # 0.0 to 1.0, where 1.0 is most stable
    details: Dict[str, Any] = Field(default_factory=dict)
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class GovernanceSimulationResult(BaseModel):
    """Complete result of a governance simulation."""
    result_id: str = Field(default_factory=lambda: f"sim_result_{datetime.utcnow().timestamp()}")
    scenario_id: str
    scenario_type: ScenarioType
    
    # Simulation parameters
    cycle_count: int
    random_seed: Optional[int]
    
    # Counts
    signals_processed: int = 0
    recommendations_generated: int = 0
    execution_intents_generated: int = 0
    doctrine_conflicts_detected: int = 0
    tier_transitions_detected: int = 0
    
    # Events detected
    oscillation_events: List[OscillationEvent] = Field(default_factory=list)
    doctrine_conflict_events: List[DoctrineConflictEvent] = Field(default_factory=list)
    tier_transition_events: List[TierTransitionEvent] = Field(default_factory=list)
    saturation_events: List[SaturationEvent] = Field(default_factory=list)
    
    # Stability metrics
    recommendation_stability_score: float = 1.0
    doctrine_consistency_score: float = 1.0
    tier_stability_score: float = 1.0
    confidence_stability_score: float = 1.0
    execution_pressure_score: float = 0.0
    governance_load_score: float = 0.0
    overall_stability_score: float = 1.0
    
    # Additional metrics
    stability_metrics: List[StabilityMetric] = Field(default_factory=list)
    
    # Risk findings
    risk_findings: List[str] = Field(default_factory=list)
    
    # Cycles
    cycles: List[GovernanceSimulationCycle] = Field(default_factory=list)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0


class GovernanceStressReport(BaseModel):
    """Comprehensive report of governance stress testing."""
    report_id: str = Field(default_factory=lambda: f"stress_report_{datetime.utcnow().timestamp()}")
    
    # Summary
    scenario_summary: str
    total_simulations: int = 0
    
    # Results
    results: List[GovernanceSimulationResult] = Field(default_factory=list)
    
    # Aggregate metrics
    avg_recommendation_stability: float = 1.0
    avg_doctrine_consistency: float = 1.0
    avg_tier_stability: float = 1.0
    avg_confidence_stability: float = 1.0
    avg_execution_pressure: float = 0.0
    avg_governance_load: float = 0.0
    avg_overall_stability: float = 1.0
    
    # Summary of findings
    total_oscillation_events: int = 0
    total_doctrine_conflicts: int = 0
    total_tier_transitions: int = 0
    total_saturation_events: int = 0
    
    # Notable findings
    critical_findings: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    info_findings: List[str] = Field(default_factory=list)
    
    # Remediation recommendations
    remediation_actions: List[str] = Field(default_factory=list)
    
    # Safety verification
    replay_mode_verified: bool = True
    no_live_execution: bool = True
    
    # Timing
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants
REPLAY_MODE = True  # Always in replay mode for simulations
LIVE_EXECUTION_ENABLED = False  # Never enable live execution in simulations
AUTO_EXECUTION_ENABLED = False  # Never enable auto-execution in simulations
EXECUTION_MODE = "disabled"  # Disabled execution mode
