"""Planning Models - Core data structures for strategic planning."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class TimeHorizon(str, Enum):
    """Planning time horizons."""
    IMMEDIATE = "immediate"  # 0-7 days
    SHORT_TERM = "short_term"  # 7-30 days
    MEDIUM_TERM = "medium_term"  # 30-90 days
    LONG_TERM = "long_term"  # 90-365 days
    STRATEGIC = "strategic"  # 365+ days


class PlanType(str, Enum):
    """Types of strategic plans."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    RESILIENCE = "resilience"


class PlanStatus(str, Enum):
    """Status of a plan."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PriorityLevel(str, Enum):
    """Priority levels for goals."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StrategicGoal(BaseModel):
    """A strategic goal to achieve."""
    id: str
    title: str
    description: str
    
    # Priority and timing
    priority: PriorityLevel = PriorityLevel.MEDIUM
    time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM
    
    # Target metrics
    target_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Context
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = None
    
    # Status
    achieved: bool = False
    progress: float = Field(ge=0, le=1, default=0.0)


class GoalDecomposition(BaseModel):
    """Decomposition of a goal into components."""
    goal_id: str
    
    # Milestones
    milestones: List[str] = Field(default_factory=list)
    
    # Dependencies
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Time estimates
    estimated_duration_days: int = 0
    
    # Resources
    required_resources: Dict[str, Any] = Field(default_factory=dict)


class PlanStep(BaseModel):
    """A single step in a strategic plan."""
    step_id: str
    sequence: int
    
    action: str
    description: str
    
    # Resources
    required_resources: Dict[str, Any] = Field(default_factory=dict)
    
    # Expected results
    expected_result: str
    expected_impact: float = Field(ge=0, le=10)
    
    # Timing
    estimated_duration_days: int = 7
    deadline: Optional[datetime] = None
    
    # Status
    completed: bool = False
    completion_date: Optional[datetime] = None


class StrategicPlan(BaseModel):
    """A strategic plan for achieving a goal."""
    id: str
    goal_id: str
    
    # Plan type
    plan_type: PlanType
    title: str
    description: str
    
    # Expected outcome
    expected_outcome: str
    
    # Scores
    reward_score: float = Field(ge=0, le=10)
    risk_score: float = Field(ge=0, le=10)
    confidence: float = Field(ge=0, le=1)
    
    # Time
    time_horizon: TimeHorizon
    estimated_duration_days: int = 30
    
    # Steps
    steps: List[PlanStep] = Field(default_factory=list)
    
    # Status
    status: PlanStatus = PlanStatus.DRAFT
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None


class PlanEvaluation(BaseModel):
    """Evaluation of a strategic plan."""
    plan_id: str
    
    # Evaluation metrics
    expected_return: float = Field(ge=0, le=10)
    probability_of_success: float = Field(ge=0, le=1)
    resilience_score: float = Field(ge=0, le=1)
    risk_score: float = Field(ge=0, le=10)
    
    # Combined score
    overall_score: float = Field(ge=0, le=10)
    
    # Simulation results
    simulation_details: Dict[str, Any] = Field(default_factory=dict)
    
    # Comparison
    rank: int = 0
    
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class PlanAdjustmentSignal(BaseModel):
    """Signal indicating a plan needs adjustment."""
    signal_id: str
    plan_id: str
    
    # Trigger
    trigger_type: str  # market_change, risk_spike, goal_failure, opportunity
    description: str
    
    # Severity
    severity: PriorityLevel = PriorityLevel.MEDIUM
    
    # Recommendation
    recommended_action: str  # continue, pause, replan, abort
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StrategicPlanPortfolio(BaseModel):
    """Complete portfolio of strategic plans."""
    portfolio_id: str
    
    # Goals
    goals: List[StrategicGoal] = Field(default_factory=list)
    
    # Generated plans
    generated_plans: List[StrategicPlan] = Field(default_factory=list)
    
    # Evaluated plans
    plan_evaluations: List[PlanEvaluation] = Field(default_factory=list)
    
    # Prioritized
    prioritized_plans: List[str] = Field(default_factory=list)  # Plan IDs
    
    # Selected
    selected_plan_id: Optional[str] = None
    
    # Active plans
    active_plans: List[str] = Field(default_factory=list)  # Plan IDs
    
    # Monitoring
    adjustment_signals: List[PlanAdjustmentSignal] = Field(default_factory=list)
    
    # Summary
    evaluation_summary: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
