"""Enhanced Simulation Types - Comprehensive models for strategic scenario simulation."""
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StrategyType(str, Enum):
    """Types of strategic decisions."""
    FOCUS_SHIFT = "focus_shift"
    RESOURCE_REALLOCATION = "resource_reallocation"
    INTERVENTION = "intervention"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    RISK_MITIGATION = "risk_mitigation"


class StrategyDecision(BaseModel):
    """A strategic decision to simulate."""
    decision_id: str
    name: str
    description: str
    strategy_type: StrategyType
    affected_domains: List[str] = Field(default_factory=list)
    resource_changes: Dict[str, float] = Field(default_factory=dict)  # domain -> change
    expected_outcome: str = ""
    priority: float = 0.5


class SimulatedOutcome(BaseModel):
    """Outcome of a simulated strategy."""
    strategy_id: str
    time_horizon_days: int
    
    # Projected domain states
    projected_domains: Dict[str, float] = Field(default_factory=dict)  # domain -> performance
    
    # Risk projections
    projected_risk: Dict[str, float] = Field(default_factory=dict)
    
    # Goal impact
    goal_probability_change: Dict[str, float] = Field(default_factory=dict)
    
    # Metrics
    expected_performance_gain: float = 0.0
    risk_exposure_change: float = 0.0
    overall_score: float = 0.0


class StrategyComparison(BaseModel):
    """Comparison of multiple strategies."""
    comparison_id: str
    baseline_outcome: SimulatedOutcome
    strategy_outcomes: List[SimulatedOutcome] = Field(default_factory=list)
    
    # Rankings
    best_strategy: Optional[str] = None
    worst_strategy: Optional[str] = None
    
    # Recommendation
    recommended_strategy: Optional[str] = None
    recommendation_reason: str = ""


class EnvironmentScenario(BaseModel):
    """Environmental scenario for simulation."""
    scenario_id: str
    name: str
    description: str
    
    # External factors
    economic_conditions: float = 0.5  # 0 = recession, 1 = boom
    market_volatility: float = 0.5
    health_factors: float = 0.5
    opportunity_availability: float = 0.5
    
    probability: float = 0.5


class SimulationCycle(BaseModel):
    """Results of a simulation cycle."""
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Current state
    current_domains: Dict[str, float] = Field(default_factory=dict)
    
    # Strategies evaluated
    strategies: List[StrategyDecision] = Field(default_factory=list)
    
    # Outcomes
    outcomes: List[SimulatedOutcome] = Field(default_factory=list)
    
    # Comparison
    comparison: Optional[StrategyComparison] = None
    
    # Summary
    best_strategy: Optional[str] = None
    execution_recommended: bool = False


class SimulationPolicy(BaseModel):
    """Policy for simulation."""
    time_horizons: List[int] = Field(default_factory=lambda: [30, 90, 180])
    max_strategies_to_compare: int = 5
    scenarios_to_test: int = 3
    confidence_threshold: float = 0.6


class SimulationStatistics(BaseModel):
    """Statistics about simulations."""
    total_cycles: int = 0
    strategies_evaluated: int = 0
    best_strategy_count: Dict[str, int] = Field(default_factory=dict)


# ==== Additional Models for V5-002 Enhanced Features ====

class SimulationStatus(str, Enum):
    """Status of simulation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScenarioType(str, Enum):
    """Types of scenario environments."""
    BASELINE_ENVIRONMENT = "baseline_environment"
    ECONOMIC_STRESS = "economic_stress"
    UNEXPECTED_OPPORTUNITY = "unexpected_opportunity"
    HEALTH_DISRUPTION = "health_disruption"
    EXECUTION_OVERLOAD = "execution_overload"
    STRATEGIC_CONFLICT = "strategic_conflict"


class CandidateStrategy(BaseModel):
    """A complete candidate strategy (may contain multiple decisions)."""
    strategy_id: str
    strategy_name: str
    description: str
    strategy_type: StrategyType
    affected_domains: List[str] = Field(default_factory=list)
    decisions: List[StrategyDecision] = Field(default_factory=list)
    total_resource_changes: Dict[str, float] = Field(default_factory=dict)
    expected_outcome: str = ""
    priority: float = 0.5


class DomainImpact(BaseModel):
    """Impact on a single domain."""
    domain: str
    performance_change: float = 0.0
    risk_change: float = 0.0
    opportunity_change: float = 0.0
    resource_allocation_change: float = 0.0


class RiskImpact(BaseModel):
    """Risk impact projection."""
    risk_type: str
    probability_change: float = 0.0
    severity_change: float = 0.0


class GoalImpact(BaseModel):
    """Goal impact projection."""
    goal_id: str
    probability_change: float = 0.0
    timeline_change_days: int = 0


class DecisionEffect(BaseModel):
    """Complete effect of a decision."""
    domain_impacts: List[DomainImpact] = Field(default_factory=list)
    risk_impacts: List[RiskImpact] = Field(default_factory=list)
    goal_impacts: List[GoalImpact] = Field(default_factory=list)


class StrategyScore(BaseModel):
    """Detailed score for a strategy."""
    strategy_id: str
    
    # Primary scores
    expected_value: float = 0.0
    risk_score: float = 0.0
    resilience_score: float = 0.0
    balance_score: float = 0.0
    
    # Detailed metrics
    average_outcome_score: float = 0.0
    downside_risk_score: float = 0.0
    best_case_outcome: float = 0.0
    worst_case_outcome: float = 0.0
    collapse_avoidance_score: float = 0.0
    domain_balance_preservation: float = 0.0
    
    # Goal impact
    goal_probability_improvement: float = 0.0
    
    # Intervention burden
    expected_interventions: int = 0


class ScenarioEnvironment(BaseModel):
    """Enhanced environmental scenario for simulation."""
    scenario_id: str
    scenario_type: ScenarioType = ScenarioType.BASELINE_ENVIRONMENT
    name: str
    description: str
    
    # External factors (0-1 scale)
    external_pressure_level: float = 0.5
    opportunity_density: float = 0.5
    disruption_frequency: float = 0.5
    volatility_level: float = 0.5
    
    # Domain-specific modifiers
    domain_modifiers: Dict[str, float] = Field(default_factory=dict)
    
    probability: float = 0.5


class SimulatedOutcome(BaseModel):
    """Enhanced outcome of a simulated strategy."""
    strategy_id: str
    time_horizon_days: int
    scenario_type: ScenarioType = ScenarioType.BASELINE_ENVIRONMENT
    
    # Projected domain states
    projected_domains: Dict[str, float] = Field(default_factory=dict)
    
    # Risk projections
    projected_risk: Dict[str, float] = Field(default_factory=dict)
    
    # Goal impact
    goal_probability_change: Dict[str, float] = Field(default_factory=list)
    
    # Detailed effects
    effects: Optional[DecisionEffect] = None
    
    # Metrics
    expected_performance_gain: float = 0.0
    risk_exposure_change: float = 0.0
    overall_score: float = 0.0


class StrategyComparison(BaseModel):
    """Enhanced comparison of multiple strategies."""
    comparison_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    baseline_outcome: Optional[SimulatedOutcome] = None
    strategy_outcomes: List[SimulatedOutcome] = Field(default_factory=list)
    strategy_scores: List[StrategyScore] = Field(default_factory=list)
    
    # Rankings
    best_strategy: Optional[str] = None
    worst_strategy: Optional[str] = None
    most_resilient_strategy: Optional[str] = None
    
    # Recommendation
    recommended_strategy: Optional[str] = None
    alternative_strategy: Optional[str] = None
    recommendation_reason: str = ""


class SimulationRecommendation(BaseModel):
    """Final strategy recommendation."""
    recommended_strategy_id: str
    strategy_name: str
    reasoning: str
    
    expected_benefits: List[str] = Field(default_factory=list)
    expected_risks: List[str] = Field(default_factory=list)
    
    # Projected effects
    projected_effects: Dict[str, float] = Field(default_factory=dict)
    
    # Alternative if conditions worsen
    alternative_strategy_id: Optional[str] = None
    alternative_reason: str = ""
    
    # Key assumptions
    key_assumptions: List[str] = Field(default_factory=list)


class SimulationCycle(BaseModel):
    """Enhanced results of a simulation cycle."""
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: SimulationStatus = SimulationStatus.PENDING
    
    # Input state
    current_domains: Dict[str, float] = Field(default_factory=dict)
    current_risks: Dict[str, float] = Field(default_factory=dict)
    
    # Strategies evaluated
    candidate_strategies: List[CandidateStrategy] = Field(default_factory=list)
    
    # Scenario environments
    scenarios: List[ScenarioEnvironment] = Field(default_factory=list)
    
    # Outcomes
    outcomes: List[SimulatedOutcome] = Field(default_factory=list)
    scores: List[StrategyScore] = Field(default_factory=list)
    
    # Comparison
    comparison: Optional[StrategyComparison] = None
    
    # Recommendation
    recommendation: Optional[SimulationRecommendation] = None
    
    # Summary
    best_strategy: Optional[str] = None
    execution_recommended: bool = False
    confidence_level: float = 0.0


class SimulationPolicy(BaseModel):
    """Enhanced policy for simulation."""
    max_candidate_strategies: int = 8
    max_scenarios_per_strategy: int = 6
    time_horizons: List[int] = Field(default_factory=lambda: [30, 90, 365])
    min_confidence_threshold: float = 0.6
    
    # Fallback behavior
    fallback_to_baseline: bool = True
    safe_mode: bool = True
    
    # Scoring weights
    expected_value_weight: float = 0.35
    risk_weight: float = 0.25
    resilience_weight: float = 0.25
    balance_weight: float = 0.15
