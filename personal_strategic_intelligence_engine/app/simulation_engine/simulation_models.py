"""Simulation Models - Unified models for all simulation types."""
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SimulationType(str, Enum):
    """Types of simulation."""
    STRATEGY = "strategy"
    MONTE_CARLO = "monte_carlo"
    VALIDATION = "validation"
    SCENARIO = "scenario"


class SimulationStatus(str, Enum):
    """Status of simulation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationConfig(BaseModel):
    """Configuration for simulation run."""
    simulation_type: SimulationType
    num_iterations: int = 1000
    time_horizon_days: int = 365
    random_seed: Optional[int] = None
    parallel: bool = True
    confidence_level: float = 0.95


class DomainState(BaseModel):
    """State of a life domain."""
    domain: str
    current_score: float = 5.0
    target_score: float = 7.0
    risk_level: float = 3.0
    momentum: float = 0.0
    resource_allocation: float = 1.0


class SimulationResult(BaseModel):
    """Result of a simulation run."""
    simulation_id: str
    simulation_type: SimulationType
    status: SimulationStatus
    
    # Timing
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Domain results
    initial_domains: Dict[str, DomainState] = Field(default_factory=dict)
    projected_domains: Dict[str, DomainState] = Field(default_factory=dict)
    
    # Metrics
    expected_performance: float = 0.0
    risk_exposure: float = 0.0
    goal_achievement_probability: float = 0.0
    
    # Statistical results (for Monte Carlo)
    confidence_interval_low: Optional[float] = None
    confidence_interval_high: Optional[float] = None
    percentile_results: Dict[str, float] = Field(default_factory=dict)
    
    # Validation results (for validation)
    baseline_score: Optional[float] = None
    system_score: Optional[float] = None
    improvement_delta: Optional[float] = None
    
    # Errors
    errors: List[str] = Field(default_factory=list)


class StrategyOutcome(BaseModel):
    """Outcome of a strategy simulation."""
    strategy_id: str
    strategy_name: str
    
    # Projected impacts
    domain_impacts: Dict[str, float] = Field(default_factory=dict)
    risk_changes: Dict[str, float] = Field(default_factory=dict)
    
    # Overall metrics
    expected_value: float = 0.0
    probability_of_success: float = 0.5
    risk_adjusted_score: float = 0.0
    
    # Comparison
    vs_baseline: float = 0.0
    rank: int = 0
