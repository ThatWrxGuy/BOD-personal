"""Monte Carlo Types - Models for Monte Carlo stress testing."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MonteCarloStatus(str, Enum):
    """Status of Monte Carlo run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationRandomizationConfig(BaseModel):
    """Configuration for randomization in Monte Carlo runs."""
    seed: int = 42
    num_runs: int = 100
    time_horizons: List[int] = Field(default_factory=lambda: [30, 90, 365])
    
    # Randomization factors
    economic_volatility: float = 0.3
    opportunity_frequency: float = 0.2
    disruption_probability: float = 0.15
    intervention_success_variance: float = 0.2


class MonteCarloRun(BaseModel):
    """A single Monte Carlo simulation run."""
    run_id: str
    batch_id: str
    strategy_id: str
    run_number: int
    
    # Randomization
    seed: int
    random_state: Dict[str, float] = Field(default_factory=dict)
    
    # Outcomes
    domain_outcomes: Dict[str, float] = Field(default_factory=dict)
    risk_outcomes: Dict[str, float] = Field(default_factory=dict)
    
    # Events
    collapse_events: List[str] = Field(default_factory=list)
    intervention_events: int = 0
    
    # Metrics
    final_score: float = 0.0
    performance_gain: float = 0.0
    risk_exposure: float = 0.0
    stability_score: float = 0.0
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StrategyDistribution(BaseModel):
    """Distribution of outcomes for a strategy."""
    strategy_id: str
    
    # Basic stats
    num_runs: int = 0
    mean_score: float = 0.0
    median_score: float = 0.0
    std_deviation: float = 0.0
    
    # Extreme values
    min_score: float = 0.0
    max_score: float = 0.0
    percentile_5: float = 0.0
    percentile_25: float = 0.0
    percentile_75: float = 0.0
    percentile_95: float = 0.0
    
    # Failure metrics
    collapse_count: int = 0
    collapse_probability: float = 0.0
    
    # Domain-specific
    domain_collapse_frequency: Dict[str, float] = Field(default_factory=dict)


class FailureEvent(BaseModel):
    """A detected failure event."""
    event_id: str
    event_type: str
    domain: str
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: float = 0.0
    description: str = ""


class ResilienceMetrics(BaseModel):
    """Resilience metrics for a strategy."""
    strategy_id: str
    
    # Primary scores
    resilience_score: float = 0.0
    collapse_resistance: float = 0.0
    recovery_rate: float = 0.0
    intervention_success_rate: float = 0.0
    domain_balance_stability: float = 0.0
    
    # Detailed metrics
    stability_variance: float = 0.0
    worst_case_score: float = 0.0
    recovery_probability: float = 0.0
    
    # Fragility detection
    is_fragile: bool = False
    fragility_reasons: List[str] = Field(default_factory=list)


class MonteCarloBatch(BaseModel):
    """A batch of Monte Carlo runs."""
    batch_id: str
    status: MonteCarloStatus = MonteCarloStatus.PENDING
    
    # Configuration
    config: SimulationRandomizationConfig
    strategy_ids: List[str] = Field(default_factory=list)
    
    # Results
    runs: List[MonteCarloRun] = Field(default_factory=list)
    distributions: List[StrategyDistribution] = Field(default_factory=list)
    resilience_metrics: List[ResilienceMetrics] = Field(default_factory=list)
    failure_events: List[FailureEvent] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Summary
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0


class StressTestReport(BaseModel):
    """Complete stress test report."""
    report_id: str
    batch_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Strategy results
    strategy_results: List[StrategyDistribution] = Field(default_factory=list)
    resilience_results: List[ResilienceMetrics] = Field(default_factory=list)
    
    # Rankings
    best_average_strategy: Optional[str] = None
    most_resilient_strategy: Optional[str] = None
    most_fragile_strategy: Optional[str] = None
    highest_risk_strategy: Optional[str] = None
    
    # Failure analysis
    failure_events: List[FailureEvent] = Field(default_factory=list)
    common_failure_modes: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommended_strategy: Optional[str] = None
    strategy_adjustments: Dict[str, str] = Field(default_factory=dict)
    
    # Summary metrics
    total_runs: int = 0
    overall_collapse_probability: float = 0.0
    average_resilience_score: float = 0.0


class StressTestPolicy(BaseModel):
    """Policy for Monte Carlo stress testing."""
    default_num_runs: int = 100
    max_num_runs: int = 10000
    min_num_runs: int = 10
    
    # Time horizons
    time_horizons: List[int] = Field(default_factory=lambda: [30, 90, 365])
    
    # Parallel execution
    enable_parallel: bool = True
    max_workers: int = 4
    
    # Timeouts
    run_timeout_seconds: int = 300
    batch_timeout_seconds: int = 3600
    
    # Quality thresholds
    min_resilience_threshold: float = 0.5
    collapse_probability_threshold: float = 0.3
    
    # Fragility detection
    fragility_variance_threshold: float = 0.4
    fragility_collapse_threshold: float = 0.2
