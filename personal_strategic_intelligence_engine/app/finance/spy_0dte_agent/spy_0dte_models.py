"""SPY 0DTE Intelligence Agent Models - BB-FIN-019"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class TradeDirection(str, Enum):
    """Trade direction for 0DTE."""
    CALL = "call"
    PUT = "put"
    AVOID = "avoid"


class OpportunityConfidence(str, Enum):
    """Confidence level for opportunity."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    """Risk classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class SignalType(str, Enum):
    """Delta velocity signal types."""
    MOMENTUM_BURST = "momentum_burst"
    BREAKOUT_DISPLACEMENT = "breakout_displacement"
    GAMMA_WALL_BREACH = "gamma_wall_breach"
    REVERSAL_SWEEP = "reversal_sweep"
    TREND_CONTINUATION = "trend_continuation"


class IntradayPhase(str, Enum):
    """Intraday market phase."""
    OPENING_RANGE = "opening_range"
    TRENDING = "trending"
    CONSOLIDATION = "consolidation"
    REVERSAL = "reversal"
    CLOSING = "closing"


# Models

class GammaLevelMap(BaseModel):
    """Gamma levels and dealer positioning."""
    symbol: str = "SPY"
    
    # Gamma levels
    gamma_support: float
    gamma_resistance: float
    gamma_flip: float
    
    # Dealer positioning
    net_gamma: float
    gamma_zone: str  # "acceleration", "deceleration", "neutral"
    
    # Pinning
    pin_level: Optional[float] = None
    pinning_probability: float = Field(ge=0.0, le=1.0)
    
    # Additional levels
    call_wall: Optional[float] = None
    put_wall: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeltaVelocitySignal(BaseModel):
    """Delta velocity signal - rapid delta expansion detection."""
    symbol: str = "SPY"
    
    # Signal type
    signal_type: SignalType
    
    # Direction
    direction: TradeDirection
    
    # Velocity metrics
    velocity_score: float = Field(ge=0.0, le=1.0)
    acceleration: float
    
    # Confidence (derived from velocity and follow-through)
    confidence: OpportunityConfidence = OpportunityConfidence.MEDIUM
    
    # Confirmation
    confirmed: bool = False
    follow_through_probability: float = Field(ge=0.0, le=1.0)
    
    # Context
    structure_context: str = ""
    volume_surge: bool = False
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StrikeRecommendation(BaseModel):
    """Strike selection recommendation."""
    symbol: str = "SPY"
    
    # Strike info
    strike: float
    direction: TradeDirection
    
    # Metrics
    delta: float
    gamma: float
    theta: float
    
    # Liquidity
    open_interest: int
    volume: int
    spread: float
    
    # Distance from spot
    distance_from_spot_pct: float
    
    # Recommendation
    confidence: OpportunityConfidence
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IntradayVolatilityState(BaseModel):
    """Intraday volatility analysis."""
    symbol: str = "SPY"
    
    # Phase
    phase: IntradayPhase
    
    # Volatility metrics
    current_iv: Optional[float] = None
    iv_percentile: float = Field(ge=0.0, le=1.0)
    
    # Range
    session_high: float
    session_low: float
    range_pct: float
    
    # Compression
    compression_ratio: Optional[float] = None
    expansion_probability: float = Field(ge=0.0, le=1.0)
    
    # VWAP context
    vwap: Optional[float] = None
    vwap_distance_pct: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SPY0DTEOpportunity(BaseModel):
    """SPY 0DTE trading opportunity."""
    # Identification
    opportunity_id: str
    
    # Direction
    direction: TradeDirection
    confidence: OpportunityConfidence
    
    # Strike
    recommended_strike: float
    strike_distance_pct: float
    
    # Entry
    entry_window: str  # "now", "wait_for_breakout", "wait_for_pullback"
    entry_trigger_price: Optional[float] = None
    
    # Risk
    risk_level: RiskLevel
    max_loss_pct: float
    
    # Reward
    reward_risk_ratio: Optional[float] = None
    target_profit_pct: Optional[float] = None
    
    # Components
    delta_signal: Optional[DeltaVelocitySignal] = None
    gamma_levels: Optional[GammaLevelMap] = None
    strike_recommendation: Optional[StrikeRecommendation] = None
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    warning: Optional[str] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SPY0DTEReport(BaseModel):
    """Complete SPY 0DTE intelligence report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Symbol
    symbol: str = "SPY"
    current_price: float
    
    # Market context (from other modules)
    market_regime: Optional[str] = None
    options_environment: Optional[str] = None
    
    # Intraday analysis
    intraday: IntradayVolatilityState
    
    # Gamma analysis
    gamma_levels: GammaLevelMap
    
    # Delta velocity
    delta_signal: Optional[DeltaVelocitySignal] = None
    
    # Opportunity
    opportunity: SPY0DTEOpportunity
    
    # Strike recommendations
    recommended_strikes: List[StrikeRecommendation] = Field(default_factory=list)
    
    # Overall assessment
    suitable_for_0dte: bool
    primary_risk: Optional[str] = None
    
    # Governance note
    governance_note: str = "RECOMMENDATION ONLY - Requires Risk Governor & CEO approval"
    
    # Version
    model_version: str = "1.0.0"
