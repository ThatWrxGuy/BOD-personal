"""Market Intelligence Data Models - BB-FIN-014"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RegimeType(str, Enum):
    """Primary regime states for market classification."""
    RISK_ON_TREND = "RISK_ON_TREND"
    RISK_ON_MOMENTUM = "RISK_ON_MOMENTUM"
    NEUTRAL_MIXED = "NEUTRAL_MIXED"
    ROTATION_TRANSITION = "ROTATION_TRANSITION"
    RISK_OFF_DEFENSIVE = "RISK_OFF_DEFENSIVE"
    VOLATILITY_STRESS = "VOLATILITY_STRESS"
    LIQUIDITY_DISLOCATION = "LIQUIDITY_DISLOCATION"
    RANGE_COMPRESSION = "RANGE_COMPRESSION"
    MEAN_REVERSION = "MEAN_REVERSION"
    MACRO_EVENT_UNCERTAINTY = "MACRO_EVENT_UNCERTAINTY"


class ConfidenceLevel(str, Enum):
    """Regime classification confidence."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class RiskPosture(str, Enum):
    """Recommended risk posture based on regime."""
    AGGRESSIVE = "aggressive"
    GROWTH = "growth"
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"
    CRISIS = "crisis"


class TrendDirection(str, Enum):
    """Trend direction classification."""
    STRONG_UP = "strong_up"
    MODERATE_UP = "moderate_up"
    SIDEWAYS = "sideways"
    MODERATE_DOWN = "moderate_down"
    STRONG_DOWN = "strong_down"


class VolatilityState(str, Enum):
    """Volatility regime state."""
    COMPRESSED = "compressed"
    NORMAL = "normal"
    EXPANDING = "expanding"
    STRESSED = "stressed"


class BreadthState(str, Enum):
    """Market breadth state."""
    STRONG_BREADTH = "strong_breadth"
    MODERATE_BREADTH = "moderate_breadth"
    NARROW_LEAD = "narrow_lead"
    WEAK_BREADTH = "weak_breadth"


class LiquidityState(str, Enum):
    """Liquidity condition state."""
    ABUNDANT = "abundant"
    NORMAL = "normal"
    TIGHT = "tight"
    STRESSED = "stressed"


class MacroPressureState(str, Enum):
    """Macro pressure environment."""
    STIMULUS = "stimulus"
    NEUTRAL = "neutral"
    TIGHTENING = "tightening"
    STRESS = "stress"


class AssetSignal(BaseModel):
    """Signal data for a single asset or asset class."""
    symbol: str
    name: str
    asset_class: str
    price: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None
    trend: Optional[TrendDirection] = None
    momentum: Optional[float] = None
    volatility: Optional[float] = None
    relative_strength: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CrossAssetSnapshot(BaseModel):
    """Snapshot of cross-asset market conditions."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Equity indices
    equities: List[AssetSignal] = Field(default_factory=list)
    
    # Sector ETFs
    sectors: List[AssetSignal] = Field(default_factory=list)
    
    # Bonds/Rates
    bonds: List[AssetSignal] = Field(default_factory=list)
    yields: Dict[str, float] = Field(default_factory=dict)
    yield_curve_state: Optional[str] = None
    
    # Volatility
    vix: Optional[float] = None
    vix_state: Optional[VolatilityState] = None
    
    # Commodities
    commodities: List[AssetSignal] = Field(default_factory=list)
    
    # FX
    dollar: Optional[AssetSignal] = None
    
    # Crypto
    crypto: List[AssetSignal] = Field(default_factory=list)
    
    # Credit
    credit_spreads: Dict[str, float] = Field(default_factory=dict)


class SignalScore(BaseModel):
    """Normalized score for a signal family."""
    family: str
    score: float = Field(ge=-1.0, le=1.0)
    direction: str
    confidence: ConfidenceLevel
    contributing_factors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RegimeScorecard(BaseModel):
    """Complete scorecard of all signal families."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Individual signal scores
    trend_score: SignalScore
    breadth_score: SignalScore
    volatility_score: SignalScore
    correlation_score: SignalScore
    liquidity_score: SignalScore
    macro_pressure_score: SignalScore
    credit_stress_score: SignalScore
    cross_asset_confirmation: SignalScore
    risk_appetite_score: SignalScore
    
    # Aggregated scores
    overall_risk_score: float = Field(ge=-1.0, le=1.0)
    environment_support: float = Field(ge=0.0, le=1.0)


class RegimeState(BaseModel):
    """Current regime classification."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Primary classification
    primary_regime: RegimeType
    confidence: ConfidenceLevel
    
    # Secondary attributes
    is_transitioning: bool = False
    transition_probability: float = Field(ge=0.0, le=1.0, default=0.0)
    prior_regime: Optional[RegimeType] = None
    
    # Risk posture
    risk_posture: RiskPosture
    
    # State indicators
    volatility_state: VolatilityState
    breadth_state: BreadthState
    liquidity_state: LiquidityState
    macro_pressure_state: MacroPressureState
    
    # Cross-asset confirmation
    cross_asset_confirmation: bool
    
    # Supporting and risk factors
    top_supporting_factors: List[str] = Field(default_factory=list)
    top_risk_factors: List[str] = Field(default_factory=list)
    
    # Flags
    flags: List[str] = Field(default_factory=list)
    
    # Reasoning trace
    classification_reasoning: List[str] = Field(default_factory=list)


class MacroPressureProfile(BaseModel):
    """Macro economic pressure profile."""
    rate_pressure: float = Field(ge=-1.0, le=1.0)
    dollar_pressure: float = Field(ge=-1.0, le=1.0)
    commodity_pressure: float = Field(ge=-1.0, le=1.0)
    growth_inference: str  # "growth", "neutral", "slowdown"
    overall_macro_state: MacroPressureState
    
    # Contributing signals
    rate_signals: List[str] = Field(default_factory=list)
    dollar_signals: List[str] = Field(default_factory=list)
    commodity_signals: List[str] = Field(default_factory=list)


class BreadthProfile(BaseModel):
    """Market breadth profile."""
    state: BreadthState
    advance_decline_ratio: Optional[float] = None
    new_highs_new_lows: Optional[Dict[str, int]] = None
    sector_participation: Dict[str, float] = Field(default_factory=dict)
    leadership_concentration: float = Field(ge=0.0, le=1.0)
    
    # Contributing signals
    advancing_stocks: Optional[int] = None
    declining_stocks: Optional[int] = None
    total_stocks: Optional[int] = None


class VolatilityProfile(BaseModel):
    """Volatility profile."""
    state: VolatilityState
    vix_level: Optional[float] = None
    vix_percentile: Optional[float] = None
    realized_vol: Optional[float] = None
    implied_vs_realized: Optional[float] = None
    term_structure: Optional[str] = None  # "normal", "inverted", "flat"
    
    # Contributing signals
    vol_signals: List[str] = Field(default_factory=list)


class CorrelationProfile(BaseModel):
    """Cross-asset correlation profile."""
    equity_bond_correlation: Optional[float] = None
    sector_correlation_avg: Optional[float] = None
    is_high_correlation_env: bool = False
    correlation_trend: str  # "increasing", "stable", "decreasing"
    
    # Contributing signals
    correlation_signals: List[str] = Field(default_factory=list)


class LiquidityProfile(BaseModel):
    """Liquidity condition profile."""
    state: LiquidityState
    liquidity_score: float = Field(ge=-1.0, le=1.0)
    
    # Contributing signals
    liquidity_signals: List[str] = Field(default_factory=list)


class RegimeTransitionAlert(BaseModel):
    """Alert for potential regime transition."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_regime: RegimeType
    potential_regimes: List[RegimeType]
    transition_probability: float = Field(ge=0.0, le=1.0)
    warning_signals: List[str] = Field(default_factory=list)
    expected_timeline: Optional[str] = None
    severity: str  # "low", "moderate", "high"


class RegimePolicy(BaseModel):
    """Policy recommendations based on regime."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    regime: RegimeType
    risk_posture: RiskPosture = RiskPosture.NEUTRAL
    
    # Exposure limits
    max_gross_exposure: float = Field(ge=0.0, le=2.0, default=1.0)
    max_single_position_risk: float = Field(ge=0.0, le=1.0, default=0.02)
    recommended_net_exposure: float = Field(ge=-1.0, le=1.0, default=0.0)
    cash_preference: float = Field(ge=0.0, le=1.0, default=0.1)
    
    # Hedging
    hedging_bias: str  # "none", "partial", "full"
    hedging_method: Optional[str] = None
    
    # Tactical
    aggression_level: str  # "conservative", "moderate", "aggressive"
    position_sizing_multiplier: float = Field(ge=0.0, le=2.0, default=1.0)
    
    # Strategy permissions
    approved_strategy_classes: List[str] = Field(default_factory=list)
    restricted_strategy_classes: List[str] = Field(default_factory=list)
    
    # Risk controls
    stop_discipline: str  # "tight", "normal", "relaxed"
    risk_compression_enabled: bool = False
    
    # Governance notes
    governance_notes: List[str] = Field(default_factory=list)


class RegimeHistoryEntry(BaseModel):
    """Historical regime entry."""
    timestamp: datetime
    regime: RegimeType
    confidence: ConfidenceLevel
    key_factors: List[str] = Field(default_factory=list)


class MarketIntelligenceReport(BaseModel):
    """Complete market intelligence report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Executive summary
    executive_summary: str
    
    # Current state
    regime: RegimeState
    scorecard: RegimeScorecard
    policy: RegimePolicy
    
    # Cross-asset details
    cross_asset_snapshot: CrossAssetSnapshot
    
    # Transition alerts
    transition_alert: Optional[RegimeTransitionAlert] = None
    
    # Detailed profiles
    macro_profile: Optional[MacroPressureProfile] = None
    breadth_profile: Optional[BreadthProfile] = None
    volatility_profile: Optional[VolatilityProfile] = None
    correlation_profile: Optional[CorrelationProfile] = None
    liquidity_profile: Optional[LiquidityProfile] = None
    
    # Historical context
    regime_history: List[RegimeHistoryEntry] = Field(default_factory=list)
    
    # Metadata
    data_freshness: Dict[str, str] = Field(default_factory=dict)
    model_version: str = "1.0.0"
    ruleset_version: str = "1.0.0"
