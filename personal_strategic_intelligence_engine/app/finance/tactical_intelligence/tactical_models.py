"""Tactical Intelligence Data Models - BB-FIN-018"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


# Enums

class MarketStructure(str, Enum):
    """Market structure states."""
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    CONSOLIDATION = "consolidation"
    BREAKOUT_UP = "breakout_up"
    BREAKOUT_DOWN = "breakout_down"
    REVERSAL = "reversal"
    UNKNOWN = "unknown"


class LiquidityEventType(str, Enum):
    """Types of liquidity events."""
    STOP_HUNT = "stop_hunt"
    LIQUIDITY_SWEEP = "liquidity_sweep"
    FALSE_BREAKOUT = "false_breakout"
    EXHAUSTION = "exhaustion"
    ORDER_BLOCK = "order_block"


class VolatilityState(str, Enum):
    """Volatility states."""
    COMPRESSED = "compressed"
    EXPANDING = "expanding"
    CONTRACTING = "contracting"
    STABLE = "stable"


class MomentumState(str, Enum):
    """Momentum states."""
    ACCELERATING = "accelerating"
    DECELERATING = "decelerating"
    NEUTRAL = "neutral"
    REVERSING = "reversing"


class BreakoutQuality(str, Enum):
    """Breakout quality assessment."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    FALSE = "false"


class EntryType(str, Enum):
    """Tactical entry types."""
    BREAKOUT_ENTRY = "breakout_entry"
    TREND_CONTINUATION = "trend_continuation"
    PULLBACK_ENTRY = "pullback_entry"
    MEAN_REVERSION = "mean_reversion"
    AVOID = "avoid"


class EntryConfidence(str, Enum):
    """Entry confidence levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Models

class MarketStructureState(BaseModel):
    """Current market structure state."""
    symbol: str
    timeframe: str  # 1m, 5m, 15m, etc.
    structure: MarketStructure
    
    # Structure details
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    
    # Trend metrics
    trend_strength: float = Field(ge=0.0, le=1.0)
    consecutive_higher_highs: int = 0
    consecutive_lower_lows: int = 0
    
    # Consolidation details
    range_width: Optional[float] = None
    compression_ratio: Optional[float] = None
    
    # Signal
    structure_change: bool = False
    change_timestamp: Optional[datetime] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LiquiditySweepEvent(BaseModel):
    """Detected liquidity sweep event."""
    symbol: str
    event_type: LiquidityEventType
    
    # Price levels
    sweep_level: float
    stop_level: Optional[float] = None
    
    # Direction
    direction: str = "bullish"  # bullish, bearish
    
    # Evidence
    volume_surge: bool = False
    wick_penetration: bool = False
    
    # Interpretation
    interpretation: str = ""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BreakoutSignal(BaseModel):
    """Breakout signal with confirmation."""
    symbol: str
    timeframe: str
    
    # Direction
    direction: str  # bullish, bearish
    
    # Levels
    breakout_level: float
    previous_range_high: float
    previous_range_low: float
    
    # Quality
    quality: BreakoutQuality
    strength: float = Field(ge=0.0, le=1.0)
    
    # Confirmation metrics
    volume_confirmation: bool = False
    momentum_confirmation: bool = False
    follow_through_probability: float = Field(ge=0.0, le=1.0)
    false_breakout_risk: float = Field(ge=0.0, le=1.0)
    
    # Signal
    breakout_valid: bool = True
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VolatilityExpansionSignal(BaseModel):
    """Volatility expansion signal."""
    symbol: str
    timeframe: str
    
    # State
    current_state: VolatilityState
    
    # Metrics
    compression_ratio: Optional[float] = None
    range_contraction_pct: Optional[float] = None
    
    # Expansion indicators
    expansion_probability: float = Field(ge=0.0, le=1.0)
    expected_move_pct: Optional[float] = None
    
    # Direction bias (if breakout)
    expansion_direction: Optional[str] = None
    
    # Signal
    signal: str = ""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MomentumBurstSignal(BaseModel):
    """Momentum burst detection."""
    symbol: str
    timeframe: str
    
    # State
    momentum_state: MomentumState
    
    # Metrics
    acceleration: float = 0.0  # Rate of change
    impulse_strength: float = Field(ge=0.0, le=1.0)
    
    # Burst indicators
    is_burst: bool = False
    burst_magnitude: Optional[float] = None
    
    # Duration
    bursts_in_last_n_bars: int = 0
    
    # Signal
    follow_through_likely: bool = True
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TacticalEntrySignal(BaseModel):
    """Final tactical entry signal."""
    symbol: str
    timeframe: str
    
    # Entry decision
    entry_type: EntryType
    confidence: EntryConfidence
    
    # Price levels
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    
    # Structure
    market_structure: MarketStructure
    
    # Confirmation
    breakout_confirmed: bool = False
    momentum_confirmed: bool = False
    liquidity_confirmed: bool = False
    
    # Risk metrics
    risk_reward_ratio: Optional[float] = None
    win_probability: float = Field(ge=0.0, le=1.0)
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    
    # Warning
    warning: Optional[str] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TacticalAnalysisReport(BaseModel):
    """Complete tactical analysis report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Symbol & context
    symbol: str
    timeframe: str
    current_price: float
    
    # Market structure
    structure: MarketStructureState
    
    # Events
    liquidity_events: List[LiquiditySweepEvent] = Field(default_factory=list)
    
    # Volatility
    volatility: VolatilityExpansionSignal
    
    # Momentum
    momentum: MomentumBurstSignal
    
    # Breakout
    breakout: Optional[BreakoutSignal] = None
    
    # Final signal
    entry_signal: TacticalEntrySignal
    
    # Risk assessment
    risk_level: str = "moderate"  # low, moderate, high
    avoid_conditions: bool = False
    
    # Context from other modules
    market_regime: Optional[str] = None
    sector_context: Optional[str] = None
    options_environment: Optional[str] = None
    
    # Version
    model_version: str = "1.0.0"
