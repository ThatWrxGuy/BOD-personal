"""Security Selection Data Models - BB-FIN-016"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SecurityClassification(str, Enum):
    """Security use case classification."""
    TREND_CONTINUATION = "trend_continuation"
    BREAKOUT_CANDIDATE = "breakout_candidate"
    PULLBACK_CANDIDATE = "pullback_candidate"
    MEAN_REVERSION = "mean_reversion"
    DEFENSIVE_LEADER = "defensive_leader"
    HIGH_BETA_MOMENTUM = "high_beta_momentum"
    WATCHLIST_ONLY = "watchlist_only"
    AVOID = "avoid"


class OpportunityTier(str, Enum):
    """Opportunity score tier."""
    ELITE = "elite"
    STRONG = "strong"
    QUALIFIED = "qualified"
    WATCHLIST = "watchlist"
    WEAK_AVOID = "weak_avoid"


class TrendDirection(str, Enum):
    """Trend direction."""
    STRONG_UP = "strong_up"
    MODERATE_UP = "moderate_up"
    SIDEWAYS = "sideways"
    MODERATE_DOWN = "moderate_down"
    STRONG_DOWN = "strong_down"


class StructureType(str, Enum):
    """Chart structure type."""
    BASELINE = "base"
    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    RECLAIM = "reclaim"
    CONTINUATION = "continuation"
    FAILED_TREND = "failed_trend"
    UNSTABLE = "unstable"


class VolatilityRegime(str, Enum):
    """Volatility regime."""
    COMPRESSED = "compressed"
    NORMAL = "normal"
    EXPANDING = "expanding"
    STRESSED = "stressed"


class WatchlistBucket(str, Enum):
    """Watchlist bucket type."""
    TOP_ACTIVE = "top_active"
    TREND_LEADERS = "trend_leaders"
    BREAKOUT_WATCH = "breakout_watch"
    PULLBACK_WATCH = "pullback_watch"
    DEFENSIVE_LEADERS = "defensive_leaders"
    AVOID_DEGRADED = "avoid_degraded"


class ActionStatus(str, Enum):
    """Portfolio action recommendation."""
    APPROVED = "approved"
    REDUCED_SIZE = "reduced_size"
    WATCH_ONLY = "watch_only"
    AVOID = "avoid"


class SecurityProfile(BaseModel):
    """Profile for a single security."""
    symbol: str
    name: str
    
    # Sector info
    sector: str
    sector_etf: Optional[str] = None
    
    # Price data
    price: Optional[float] = None
    change_1d: Optional[float] = None
    change_1w: Optional[float] = None
    change_1m: Optional[float] = None
    change_3m: Optional[float] = None
    
    # Technical
    trend: Optional[TrendDirection] = None
    structure: Optional[StructureType] = None
    
    # Volume
    avg_volume: Optional[float] = None
    volume_ratio: Optional[float] = None
    
    # Volatility
    volatility: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OpportunityScore(BaseModel):
    """Composite opportunity score."""
    overall: float = Field(ge=0.0, le=1.0)
    tier: OpportunityTier
    
    # Component scores
    trend_quality: float = Field(ge=0.0, le=1.0)
    relative_strength: float = Field(ge=0.0, le=1.0)
    momentum_quality: float = Field(ge=0.0, le=1.0)
    volatility_suitability: float = Field(ge=0.0, le=1.0)
    liquidity_quality: float = Field(ge=0.0, le=1.0)
    risk_reward: float = Field(ge=0.0, le=1.0)
    structural_quality: float = Field(ge=0.0, le=1.0)
    regime_alignment: float = Field(ge=0.0, le=1.0)
    sector_alignment: float = Field(ge=0.0, le=1.0)


class TechnicalQualityProfile(BaseModel):
    """Technical quality analysis."""
    trend_direction: TrendDirection
    trend_strength: float = Field(ge=0.0, le=1.0)
    trend_persistence: float = Field(ge=0.0, le=1.0)
    slope_consistency: float = Field(ge=0.0, le=1.0)
    pullback_quality: float = Field(ge=0.0, le=1.0)
    degradation_risk: float = Field(ge=0.0, le=1.0)
    ma_structure: str = ""  # e.g., "above_50_200ma"


class RelativeStrengthProfile(BaseModel):
    """Relative strength analysis."""
    vs_spy: float = 0.0
    vs_sector: float = 0.0
    vs_peers: float = 0.0
    percentile_rank: float = Field(ge=0.0, le=1.0)
    leadership_confirmation: bool = False


class VolatilitySuitabilityProfile(BaseModel):
    """Volatility suitability analysis."""
    realized_vol: Optional[float] = None
    volatility_regime: VolatilityRegime
    compression_score: float = Field(ge=0.0, le=1.0)
    suitability_score: float = Field(ge=0.0, le=1.0)
    tactical_suitable: bool = True
    swing_suitable: bool = True


class LiquidityProfile(BaseModel):
    """Liquidity quality analysis."""
    avg_dollar_volume: Optional[float] = None
    turnover_quality: float = Field(ge=0.0, le=1.0)
    slippage_risk: str = "low"  # low, medium, high
    tradability_score: float = Field(ge=0.0, le=1.0)
    institutional_participation: bool = False


class RiskRewardProfile(BaseModel):
    """Risk/reward profile."""
    upside_potential: Optional[float] = None
    downside_risk: Optional[float] = None
    reward_risk_ratio: Optional[float] = None
    stop_distance: Optional[float] = None
    target_distance: Optional[float] = None
    asymmetry_score: float = Field(ge=0.0, le=1.0)
    invalidation_zone: Optional[float] = None


class CandidateRecommendation(BaseModel):
    """Complete candidate recommendation."""
    symbol: str
    name: str
    
    # Classification
    classification: SecurityClassification
    opportunity_score: OpportunityScore
    action_status: ActionStatus
    
    # Alignment
    regime_alignment: str  # aligned, neutral, opposed
    sector_alignment: str  # leading, neutral, lagging
    
    # Profile
    sector: str
    price: Optional[float] = None
    
    # Setup
    setup_type: str  # trend_continuation, breakout, etc.
    
    # Quality
    liquidity_quality: str  # high, medium, low
    risk_reward_estimate: str  # favorable, neutral, unfavorable
    
    # Reasoning
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    reasoning_trace: str = ""
    
    # Policy
    recommended_weight: Optional[float] = None
    max_weight: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SecuritySelectionReport(BaseModel):
    """Complete security selection report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Rankings
    ranked_candidates: List[CandidateRecommendation] = Field(default_factory=list)
    
    # Watchlists
    watchlists: Dict[WatchlistBucket, List[CandidateRecommendation]] = Field(default_factory=dict)
    
    # Summary
    summary: str
    total_candidates: int = 0
    elite_count: int = 0
    strong_count: int = 0
    watchlist_count: int = 0
    avoid_count: int = 0
    
    # Context
    market_regime: Optional[str] = None
    regime_risk_posture: Optional[str] = None
    sector_context: Optional[str] = None
    
    # Metadata
    universe_size: int = 0
    model_version: str = "1.0.0"
    ruleset_version: str = "1.0.0"


class OpportunityReasonTrace(BaseModel):
    """Reasoning trace for a security."""
    symbol: str
    
    # Why selected
    positive_factors: List[str] = Field(default_factory=list)
    
    # Why penalized
    negative_factors: List[str] = Field(default_factory=list)
    
    # Context
    regime_notes: List[str] = Field(default_factory=list)
    sector_notes: List[str] = Field(default_factory=list)
    
    # Invalidation
    invalidation_conditions: List[str] = Field(default_factory=list)
    
    # Plain language
    summary: str = ""


class UniverseDefinition(BaseModel):
    """Universe definition."""
    name: str
    symbols: List[str]
    min_volume: Optional[float] = None
    min_price: Optional[float] = None
    max_volatility: Optional[float] = None
    excluded_symbols: List[str] = Field(default_factory=list)
