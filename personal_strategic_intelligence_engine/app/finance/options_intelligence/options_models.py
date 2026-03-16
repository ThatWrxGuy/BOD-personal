"""Options Intelligence Data Models - BB-FIN-017"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class IVRegime(str, Enum):
    """Implied volatility regime classification."""
    COMPRESSED = "compressed"
    NORMAL = "normal"
    ELEVATED = "elevated"
    EXTREME = "extreme"


class TermStructureShape(str, Enum):
    """Volatility term structure shape."""
    CONTANGO = "contango"
    BACKWARDATION = "backwardation"
    FLAT = "flat"
    INVERSION = "inversion"
    STEEPENING = "steepening"
    FLATTENING = "flattening"


class SkewType(str, Enum):
    """Options skew type."""
    CALL_SKEW = "call_skew"  # Upside demand
    PUT_SKEW = "put_skew"  # Downside protection demand
    TAIL_RISK = "tail_risk"
    SYMMETRIC = "symmetric"


class OptionsSuitability(str, Enum):
    """Options suitability classification."""
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    DISCOURAGED = "discouraged"


class GammaZone(str, Enum):
    """Gamma zone type."""
    SUPPORT = "support"  # Dealer long gamma
    RESISTANCE = "resistance"  # Dealer short gamma
    ACCELERATION = "acceleration"  # High gamma change


class LiquidityRating(str, Enum):
    """Options liquidity rating."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


# Models

class OptionsEnvironmentProfile(BaseModel):
    """Complete options environment profile."""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # IV
    current_iv: Optional[float] = None
    iv_percentile: float = Field(ge=0.0, le=1.0)
    iv_rank: float = Field(ge=0.0, le=1.0)
    iv_regime: IVRegime
    
    # Realized
    realized_vol: Optional[float] = None
    iv_hv_spread: Optional[float] = None
    
    # Term structure
    term_structure: Optional[TermStructureShape] = None
    front_iv: Optional[float] = None
    back_iv: Optional[float] = None
    
    # Skew
    skew_type: Optional[SkewType] = None
    put_call_ratio: Optional[float] = None
    
    # Suitability
    suitability: OptionsSuitability
    suitability_score: float = Field(ge=0.0, le=1.0)


class VolatilityTermStructure(BaseModel):
    """Volatility across expirations."""
    symbol: str
    shape: TermStructureShape
    
    # IV by expiration (days -> IV)
    expiration_ivs: Dict[int, float] = Field(default_factory=dict)
    front_iv: Optional[float] = None
    back_iv: Optional[float] = None
    
    # Calculations
    contango_ratio: Optional[float] = None
    backwardation_ratio: Optional[float] = None
    
    # Signal
    signal: str = ""  # "volatility crush expected", "contango pain", etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SkewProfile(BaseModel):
    """Options skew analysis."""
    symbol: str
    
    # Raw values
    atm_iv: Optional[float] = None
    rr_25: Optional[float] = None  # 25-delta risk reversal
    rr_10: Optional[float] = None  # 10-delta risk reversal
    butterfly: Optional[float] = None
    
    # Interpretation
    skew_type: SkewType
    tail_premium: float = Field(ge=0.0, le=1.0)
    
    # Signals
    upside_demand: bool = False
    downside_protection: bool = False
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DealerPositionEstimate(BaseModel):
    """Dealer positioning estimate."""
    symbol: str
    
    # Gamma
    net_gamma: float = 0.0
    gamma_zone: GammaZone
    gamma_support: Optional[float] = None  # Strike
    gamma_resistance: Optional[float] = None  # Strike
    pinning_risk: float = Field(ge=0.0, le=1.0)
    
    # OI distribution
    call_oi_concentration: float = Field(ge=0.0, le=1.0)
    put_oi_concentration: float = Field(ge=0.0, le=1.0)
    
    # Signals
    gamma_squeeze_risk: float = Field(ge=0.0, le=1.0)
    hedging_pressure: str = "neutral"  # long, short, neutral
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptionsLiquidityProfile(BaseModel):
    """Options liquidity analysis."""
    symbol: str
    
    # Volume
    avg_daily_volume: Optional[float] = None
    volume_trend: str = "stable"  # increasing, stable, decreasing
    
    # Open interest
    total_oi: Optional[float] = None
    oi_stability: float = Field(ge=0.0, le=1.0)
    
    # Spreads
    avg_spread: Optional[float] = None
    spread_quality: LiquidityRating
    
    # Overall
    tradability_score: float = Field(ge=0.0, le=1.0)
    liquidity_rating: LiquidityRating
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptionsSuitabilityScore(BaseModel):
    """Options suitability for a security."""
    symbol: str
    sector: Optional[str] = None
    
    # IV component
    iv_score: float = Field(ge=0.0, le=1.0)
    iv_regime: IVRegime
    
    # Liquidity component
    liquidity_score: float = Field(ge=0.0, le=1.0)
    liquidity_rating: LiquidityRating
    
    # Structure component
    structure_score: float = Field(ge=0.0, le=1.0)
    
    # Dealer component
    dealer_score: float = Field(ge=0.0, le=1.0)
    
    # Composite
    overall_score: float = Field(ge=0.0, le=1.0)
    suitability: OptionsSuitability
    
    # Recommendation
    recommendation: str = ""
    rationale: List[str] = Field(default_factory=list)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VolatilityCompressionSignal(BaseModel):
    """Volatility compression signal."""
    symbol: str
    
    # Compression metrics
    compression_level: float = Field(ge=0.0, le=1.0)  # How compressed
    compression_duration: int = 0  # Days in compression
    
    # Signal
    signal_type: str = "compression"  # compression, expansion, normal
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Implications
    breakout_probability: float = Field(ge=0.0, le=1.0)
    implied_move: Optional[float] = None  # Expected move percentage
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GammaExposureProfile(BaseModel):
    """Gamma exposure map."""
    symbol: str
    
    # Key levels
    gamma_max_strike: Optional[float] = None  # Max dealer gamma
    gamma_support: Optional[float] = None
    gamma_resistance: Optional[float] = None
    
    # Pinning
    pin_level: Optional[float] = None
    pinning_probability: float = Field(ge=0.0, le=1.0)
    
    # Zones
    positive_gamma_zone_low: Optional[float] = None
    positive_gamma_zone_high: Optional[float] = None
    
    # Risk
    gamma_squeeze_potential: float = Field(ge=0.0, le=1.0)
    vol_acceleration_zone: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptionsIntelligenceReport(BaseModel):
    """Complete options intelligence report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Environment
    iv_regime: IVRegime
    iv_percentile: float
    iv_rank: float
    
    # Structure
    term_structure: Optional[TermStructureShape] = None
    skew: Optional[SkewType] = None
    
    # Dealer
    dealer_positioning: Optional[DealerPositionEstimate] = None
    
    # Liquidity
    liquidity: Optional[OptionsLiquidityProfile] = None
    
    # Suitability
    suitability: OptionsSuitability
    suitability_score: float
    
    # Summary
    summary: str
    
    # Context from other modules
    market_regime: Optional[str] = None
    sector_context: Optional[str] = None
    security_opportunity: Optional[str] = None  # From BB-FIN-016
    
    # Version
    model_version: str = "1.0.0"
