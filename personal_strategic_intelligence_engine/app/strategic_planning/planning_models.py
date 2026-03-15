"""Strategic Planning Models.

Defines structures for strategic planning across time horizons.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TimeHorizon(str, Enum):
    """Time horizon for strategic planning."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlanStatus(str, Enum):
    """Status of a strategic plan."""
    ACTIVE = "active"
    ACHIEVED = "achieved"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class StrategicPriority(BaseModel):
    """A strategic priority at a specific time horizon."""
    priority_id: str
    title: str
    description: str
    
    # Time horizon
    time_horizon: TimeHorizon
    
    # Hierarchy
    parent_priority_id: Optional[str] = None
    child_priority_ids: List[str] = Field(default_factory=list)
    
    # Status
    status: PlanStatus = PlanStatus.ACTIVE
    
    # Content
    focus_area: str  # e.g., "health", "finance", "productivity"
    target_outcome: str
    success_metrics: List[str] = Field(default_factory=list)
    
    # Relationships
    signal_dependencies: List[str] = Field(default_factory=list)
    recommendation_types: List[str] = Field(default_factory=list)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = None
    
    # Progress
    progress: float = 0.0  # 0.0 to 1.0
    
    # Alignment
    alignment_score: float = 1.0


class StrategicPlan(BaseModel):
    """A complete strategic plan spanning multiple horizons."""
    plan_id: str
    name: str
    description: str
    
    # Time horizons
    yearly_priority: Optional[StrategicPriority] = None
    quarterly_priorities: List[StrategicPriority] = Field(default_factory=list)
    monthly_priorities: List[StrategicPriority] = Field(default_factory=list)
    weekly_priorities: List[StrategicPriority] = Field(default_factory=list)
    daily_focus: List[StrategicPriority] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    
    # Alignment
    overall_alignment_score: float = 1.0


class AlignmentScore(BaseModel):
    """Score for alignment between time horizons."""
    horizon: TimeHorizon
    
    # Alignment with next level up
    parent_alignment: float = 1.0
    
    # Alignment with next level down
    child_alignment: float = 1.0
    
    # Combined score
    overall_score: float = 1.0
    
    # Details
    aligned_priorities: List[str] = Field(default_factory=list)
    misaligned_priorities: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)


class PlanGenerationContext(BaseModel):
    """Context for generating strategic plans."""
    # Current signals
    active_signals: Dict[str, float] = Field(default_factory=dict)
    
    # Current state
    current_goals: List[str] = Field(default_factory=list)
    current_concerns: List[str] = Field(default_factory=list)
    
    # Historical patterns
    pattern_context: Optional[str] = None
    
    # Time
    current_horizon: TimeHorizon = TimeHorizon.DAILY


class PlanEvaluation(BaseModel):
    """Evaluation of a plan or recommendation against strategic priorities."""
    recommendation_id: str
    recommendation_type: str
    
    # Alignment scores
    yearly_alignment: float = 0.0
    quarterly_alignment: float = 0.0
    monthly_alignment: float = 0.0
    weekly_alignment: float = 0.0
    daily_alignment: float = 0.0
    
    # Overall
    overall_alignment_score: float = 0.0
    
    # Details
    supports_priorities: List[str] = Field(default_factory=list)
    conflicts_with_priorities: List[str] = Field(default_factory=list)
    neutral: List[str] = Field(default_factory=list)
    
    # Recommendation
    alignment_verdict: str = "neutral"  # supports, conflicts, neutral
    adjusted_score: float = 0.5


class PlanningSummary(BaseModel):
    """Summary of strategic planning state."""
    total_plans: int = 0
    active_priorities: int = 0
    achieved_priorities: int = 0
    
    # Coverage
    horizons_covered: List[str] = Field(default_factory=list)
    
    # Alignment
    average_alignment: float = 1.0
    
    # Recent changes
    last_updated: Optional[datetime] = None


# Safety constants
LIVE_EXECUTION_ENABLED = False
PLANNING_MODE = "advisory"
