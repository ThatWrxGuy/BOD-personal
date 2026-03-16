"""Council Data Models - BB-CORE-022

Data models for the Executive Council Intelligence Engine.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Domain(str, Enum):
    """Life domains for strategic coordination."""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    LIFESTYLE = "lifestyle"
    INTELLIGENCE = "intelligence"
    RELATIONSHIPS = "relationships"


class ChiefOfficer(str, Enum):
    """Chief Officer positions."""
    CFO = "Chief Financial Officer"
    CHO = "Chief Health Officer"
    CCO = "Chief Career Officer"
    CLA = "Chief Life Architect"
    CIO = "Chief Intelligence Officer"
    CRO = "Chief Relationship Officer"


class PriorityLevel(str, Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, Enum):
    """Status of a recommendation."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    IMPLEMENTED = "implemented"


class AlignmentScore(BaseModel):
    """Strategic alignment score for a domain."""
    domain: Domain
    score: float = Field(ge=0.0, le=1.0)
    contributing_factors: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)


class RecommendationSignal(BaseModel):
    """A supporting signal for a recommendation."""
    source: str
    signal_type: str
    description: str
    strength: float = Field(ge=0.0, le=1.0)


class DomainRecommendation(BaseModel):
    """Recommendation from a Chief Officer."""
    recommendation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Domain information
    domain: Domain
    chief_officer: ChiefOfficer
    
    # Recommendation content
    title: str
    description: str
    action_items: List[str] = Field(default_factory=list)
    
    # Priority and confidence
    priority: PriorityLevel = PriorityLevel.MEDIUM
    confidence: float = Field(ge=0.0, le=1.0)
    importance_score: float = Field(ge=0.0, le=1.0)
    
    # Supporting signals
    signals: List[RecommendationSignal] = Field(default_factory=list)
    
    # Status
    status: RecommendationStatus = RecommendationStatus.PENDING
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RankedRecommendation(BaseModel):
    """Recommendation with priority ranking."""
    rank: int
    recommendation: DomainRecommendation
    priority_score: float
    reasoning: str


class Conflict(BaseModel):
    """Conflict between domain recommendations."""
    conflict_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Domains in conflict
    domain_a: Domain
    domain_b: Domain
    
    # Recommendations involved
    recommendation_a: str  # title
    recommendation_b: str  # title
    
    # Conflict description
    description: str
    
    # Resolution
    resolved: bool = False
    resolution: Optional[str] = None
    resolution_reason: Optional[str] = None


class CouncilCycleResult(BaseModel):
    """Result of one council decision cycle."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Input recommendations
    recommendations: List[DomainRecommendation] = Field(default_factory=list)
    
    # Processed outputs
    ranked_recommendations: List[RankedRecommendation] = Field(default_factory=list)
    conflicts: List[Conflict] = Field(default_factory=list)
    alignment_scores: List[AlignmentScore] = Field(default_factory=list)
    
    # Executive brief content
    top_priority_title: str = ""
    brief_summary: str = ""
    action_items: List[str] = Field(default_factory=list)
    alerts: List[str] = Field(default_factory=list)
    
    # Metadata
    cycle_duration_ms: float = 0.0
    domains_represented: List[Domain] = Field(default_factory=list)


class StrategicGoal(BaseModel):
    """Long-term strategic goal."""
    goal_id: str
    title: str
    description: str
    domain: Domain
    target_date: Optional[datetime] = None
    progress: float = Field(ge=0.0, le=1.0, default=0.0)
    status: str = "active"


class CouncilState(BaseModel):
    """Current state of the Executive Council."""
    is_active: bool = False
    last_cycle: Optional[datetime] = None
    
    # Active recommendations by domain
    pending_recommendations: Dict[Domain, List[DomainRecommendation]] = Field(default_factory=dict)
    approved_recommendations: Dict[Domain, List[DomainRecommendation]] = Field(default_factory=dict)
    
    # Strategic goals
    goals: List[StrategicGoal] = Field(default_factory=list)
    
    # Recent conflicts
    recent_conflicts: List[Conflict] = Field(default_factory=list)


# Default Chief Officer mapping
DOMAIN_TO_OFFICER: Dict[Domain, ChiefOfficer] = {
    Domain.FINANCE: ChiefOfficer.CFO,
    Domain.HEALTH: ChiefOfficer.CHO,
    Domain.CAREER: ChiefOfficer.CCO,
    Domain.LIFESTYLE: ChiefOfficer.CLA,
    Domain.INTELLIGENCE: ChiefOfficer.CIO,
    Domain.RELATIONSHIPS: ChiefOfficer.CRO,
}

OFFICER_TO_DOMAIN: Dict[ChiefOfficer, Domain] = {v: k for k, v in DOMAIN_TO_OFFICER.items()}
