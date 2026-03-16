"""Sector Intelligence Data Models - BB-FIN-015"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class MomentumPhase(str, Enum):
    """Momentum phase classification."""
    ACCELERATING = "accelerating"
    PERSISTENT = "persistent"
    DECELERATING = "decelerating"
    EXHAUSTED = "exhausted"
    REVERSING = "reversing"


class RotationPhase(str, Enum):
    """Phase of sector rotation."""
    NONE = "none"
    EARLY = "early"
    ACTIVE = "active"
    COMPLETED = "completed"


class CapitalFlowDirection(str, Enum):
    """Direction of capital flow."""
    INFLOW = "inflow"
    OUTFLOW = "outflow"
    NEUTRAL = "neutral"


class SectorProfile(BaseModel):
    """Profile for a single sector."""
    symbol: str  # e.g., "XLK"
    name: str    # e.g., "Technology"
    
    # Price data
    price: Optional[float] = None
    change_1d: Optional[float] = None
    change_1w: Optional[float] = None
    change_1m: Optional[float] = None
    change_3m: Optional[float] = None
    change_ytd: Optional[float] = None
    
    # Relative strength
    rs_vs_spy: Optional[float] = None  # Relative strength vs SPY
    rs_rank: Optional[int] = None     # Ranking position
    
    # Momentum
    momentum_phase: Optional[MomentumPhase] = None
    momentum_score: Optional[float] = None
    
    # Breadth
    advancing_stocks: Optional[int] = None
    declining_stocks: Optional[int] = None
    participation_pct: Optional[float] = None
    
    # Volume
    volume: Optional[float] = None
    volume_change: Optional[float] = None
    
    # Volatility
    volatility: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RelativeStrengthScore(BaseModel):
    """Relative strength score between two assets."""
    base_symbol: str
    target_symbol: str
    
    # Ratio data
    current_ratio: Optional[float] = None
    ratio_change_1m: Optional[float] = None
    ratio_change_3m: Optional[float] = None
    
    # Scores
    strength_score: float = Field(ge=-1.0, le=1.0)
    momentum_score: float = Field(ge=-1.0, le=1.0)
    overall_score: float = Field(ge=-1.0, le=1.0)
    
    # Metadata
    confidence: str = "moderate"  # low, moderate, high
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SectorLeadershipRanking(BaseModel):
    """Ranked list of sector leadership."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Rankings by timeframe
    short_term: List[SectorProfile] = Field(default_factory=list)  # 1W-1M
    medium_term: List[SectorProfile] = Field(default_factory=list)  # 1M-3M
    long_term: List[SectorProfile] = Field(default_factory=list)   # 3M-YTD
    
    # Composite ranking
    composite: List[SectorProfile] = Field(default_factory=list)
    
    # Metadata
    total_sectors: int = 0
    benchmark_symbol: str = "SPY"


class RotationEvent(BaseModel):
    """Detected sector rotation event."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Rotation details
    phase: RotationPhase
    
    # From sector (weakening)
    from_sector: Optional[str] = None
    from_momentum: Optional[float] = None
    
    # To sector (strengthening)
    to_sector: Optional[str] = None
    to_momentum: Optional[float] = None
    
    # Severity
    strength: float = Field(ge=0.0, le=1.0)
    
    # Description
    description: str
    
    # Alert level
    alert_level: str = "moderate"  # low, moderate, high


class SectorBreadthProfile(BaseModel):
    """Breadth analysis for a sector."""
    symbol: str
    
    # Participation metrics
    advancing_stocks: int = 0
    declining_stocks: int = 0
    total_stocks: int = 0
    
    # Calculated
    advance_decline_ratio: float = 0.0
    participation_pct: float = 0.0
    
    # Quality
    is_concentrated: bool = False
    concentration_risk: str = "low"  # low, medium, high
    
    # Moving average participation
    above_50ma_pct: Optional[float] = None
    above_200ma_pct: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MomentumProfile(BaseModel):
    """Momentum analysis for a sector."""
    symbol: str
    
    # Phase
    phase: MomentumPhase
    
    # Scores
    acceleration_score: float = 0.0  # positive = accelerating
    persistence_score: float = 0.0  # how long momentum lasted
    exhaustion_score: float = 0.0    # risk of reversal
    
    # Divergence
    has_positive_divergence: bool = False
    has_negative_divergence: bool = False
    
    # Trend
    trend_slope: float = 0.0
    momentum_continuation_pct: float = 0.0
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CapitalFlowSignal(BaseModel):
    """Institutional capital flow signal."""
    symbol: str
    
    # Direction
    direction: CapitalFlowDirection
    
    # Strength
    strength: float = Field(ge=0.0, le=1.0)
    
    # Proxies used
    volume_signal: Optional[float] = None
    momentum_signal: Optional[float] = None
    volatility_signal: Optional[float] = None
    
    # Confidence
    confidence: str = "moderate"
    
    # Description
    description: str
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SectorPolicyRecommendation(BaseModel):
    """Portfolio recommendation for a sector."""
    symbol: str
    name: str
    
    # Allocation guidance
    weight: float = Field(ge=0.0, le=1.0)  # 0 = no exposure, 1 = full
    adjustment: str = "none"  # increase, decrease, maintain, avoid
    
    # Rationale
    rationale: List[str] = Field(default_factory=list)
    
    # Risk
    risk_level: str = "moderate"  # low, moderate, high
    
    # Priority
    priority: int = 0  # 1 = top priority
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SectorIntelligenceReport(BaseModel):
    """Complete sector intelligence report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Leadership
    leadership: SectorLeadershipRanking
    
    # Rotation
    rotation: Optional[RotationEvent] = None
    rotation_detected: bool = False
    
    # Breadth
    breadth_profiles: List[SectorBreadthProfile] = Field(default_factory=list)
    
    # Flows
    capital_flows: List[CapitalFlowSignal] = Field(default_factory=list)
    
    # Policy
    recommendations: List[SectorPolicyRecommendation] = Field(default_factory=list)
    
    # Summary
    summary: str
    
    # Integration context (from BB-FIN-014)
    market_regime: Optional[str] = None
    regime_risk_posture: Optional[str] = None
    
    # Metadata
    data_freshness: Dict[str, str] = Field(default_factory=dict)
    model_version: str = "1.0.0"
