"""Market Structure Models for PSIE Finance Module.

Defines structured models for intraday market structure intelligence.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class VWAPState(str, Enum):
    """VWAP state classification."""
    ABOVE_VWAP_ACCEPTANCE = "above_vwap_acceptance"
    BELOW_VWAP_ACCEPTANCE = "below_vwap_acceptance"
    VWAP_RECLAIM_BULLISH = "vwap_reclaim_bullish"
    VWAP_REJECT_BEARISH = "vwap_reject_bearish"
    VWAP_CHOP_NEUTRAL = "vwap_chop_neutral"
    OVEREXTENDED_FROM_VWAP = "overextended_from_vwap"


class DayType(str, Enum):
    """Day type classification."""
    TREND_DAY_UP = "trend_day_up"
    TREND_DAY_DOWN = "trend_day_down"
    OPEN_DRIVE_UP = "open_drive_up"
    OPEN_DRIVE_DOWN = "open_drive_down"
    RANGE_DAY = "range_day"
    CHOP_DAY = "chop_day"
    REVERSAL_DAY = "reversal_day"
    DOUBLE_DISTRIBUTION_DAY = "double_distribution_day"
    VOLATILITY_EXPANSION_DAY = "volatility_expansion_day"
    LOW_PARTICIPATION_DAY = "low_participation_day"


class TrendState(str, Enum):
    """Trend state classification."""
    STRONG_UPTREND = "strong_uptrend"
    WEAK_UPTREND = "weak_uptrend"
    STRONG_DOWNTREND = "strong_downtrend"
    WEAK_DOWNTREND = "weak_downtrend"
    NEUTRAL = "neutral"
    UNCERTAIN = "uncertain"


class SweepType(str, Enum):
    """Liquidity sweep type."""
    SWEEP_ABOVE_HIGH = "sweep_above_high"
    SWEEP_BELOW_LOW = "sweep_below_low"
    OPENING_RANGE_SWEEP = "opening_range_sweep"
    SESSION_HL_SWEEP = "session_hl_sweep"
    FALSE_BREAKOUT = "false_breakout"
    FALSE_BREAKDOWN = "false_breakdown"


class SweepDirection(str, Enum):
    """Sweep direction."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SweepOutcome(str, Enum):
    """Outcome of sweep event."""
    BULLISH_TRAP = "bullish_trap"
    BEARISH_TRAP = "bearish_trap"
    CONFIRMED_CONTINUATION = "confirmed_continuation"
    FAILED_AUCTION = "failed_auction"
    REVERSAL_SETUP = "reversal_setup"
    RECLAIM_AFTER_SWEEP = "reclaim_after_sweep"


class VolatilityState(str, Enum):
    """Volatility state classification."""
    COMPRESSION_BUILDING = "compression_building"
    HEALTHY_EXPANSION = "healthy_expansion"
    UNSTABLE_EXPANSION = "unstable_expansion"
    EXHAUSTION_EXPANSION = "exhaustion_expansion"
    LOW_ENERGY_CHOP = "low_energy_chop"


class LevelType(str, Enum):
    """Price level type."""
    SESSION_HIGH = "session_high"
    SESSION_LOW = "session_low"
    OR_HIGH = "or_high"
    OR_LOW = "or_low"
    PREMARKET_HIGH = "premarket_high"
    PREMARKET_LOW = "premarket_low"
    PRIOR_CLOSE = "prior_close"
    PIVOT = "pivot"
    SUPPORT = "support"
    RESISTANCE = "resistance"
    LOCAL_CLUSTER = "local_cluster"


class LevelStatus(str, Enum):
    """Level interaction status."""
    INTACT = "intact"
    BROKEN = "broken"
    REJECTED = "rejected"
    TESTING = "testing"


@dataclass
class VWAPContext:
    """VWAP calculation and context."""
    vwap: float
    price: float
    distance_from_vwap: float
    distance_pct: float
    vwap_slope: float
    state: VWAPState
    volume_at_vwap: float
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "vwap": self.vwap,
            "price": self.price,
            "distance_from_vwap": self.distance_from_vwap,
            "distance_pct": self.distance_pct,
            "vwap_slope": self.vwap_slope,
            "state": self.state.value,
            "volume_at_vwap": self.volume_at_vwap,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class IntradayLevel:
    """Intraday price level."""
    price: float
    level_type: LevelType
    relevance_score: float
    last_touch: datetime
    touch_count: int
    status: LevelStatus
    distance_from_price: float
    
    def to_dict(self) -> dict:
        return {
            "price": self.price,
            "level_type": self.level_type.value,
            "relevance_score": self.relevance_score,
            "last_touch": self.last_touch.isoformat(),
            "touch_count": self.touch_count,
            "status": self.status.value,
            "distance_from_price": self.distance_from_price,
        }


@dataclass
class IntradayLevelMap:
    """Map of all intraday levels."""
    levels: List[IntradayLevel] = field(default_factory=list)
    session_high: Optional[IntradayLevel] = None
    session_low: Optional[IntradayLevel] = None
    nearest_support: Optional[IntradayLevel] = None
    nearest_resistance: Optional[IntradayLevel] = None
    
    def to_dict(self) -> dict:
        return {
            "levels": [l.to_dict() for l in self.levels],
            "session_high": self.session_high.to_dict() if self.session_high else None,
            "session_low": self.session_low.to_dict() if self.session_low else None,
            "nearest_support": self.nearest_support.to_dict() if self.nearest_support else None,
            "nearest_resistance": self.nearest_resistance.to_dict() if self.nearest_resistance else None,
        }


@dataclass
class LiquiditySweepEvent:
    """Liquidity sweep event."""
    id: str
    timestamp: datetime
    sweep_type: SweepType
    direction: SweepDirection
    price: float
    target_level: float
    outcome: Optional[SweepOutcome]
    rejection_price: Optional[float]
    volume: int
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "sweep_type": self.sweep_type.value,
            "direction": self.direction.value,
            "price": self.price,
            "target_level": self.target_level,
            "outcome": self.outcome.value if self.outcome else None,
            "rejection_price": self.rejection_price,
            "volume": self.volume,
        }


@dataclass
class VolatilityStructureState:
    """Volatility structure state."""
    state: VolatilityState
    realized_volatility: float
    volatility_percentile: float
    bar_range_avg: float
    bar_range_current: float
    expansion_ratio: float
    momentum_ignition: bool
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "realized_volatility": self.realized_volatility,
            "volatility_percentile": self.volatility_percentile,
            "bar_range_avg": self.bar_range_avg,
            "bar_range_current": self.bar_range_current,
            "expansion_ratio": self.expansion_ratio,
            "momentum_ignition": self.momentum_ignition,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DayTypeClassification:
    """Day type classification."""
    day_type: DayType
    confidence: float
    is_provisional: bool
    trend_strength: float
    open_direction: str
    open_range_size: float
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "day_type": self.day_type.value,
            "confidence": self.confidence,
            "is_provisional": self.is_provisional,
            "trend_strength": self.trend_strength,
            "open_direction": self.open_direction,
            "open_range_size": self.open_range_size,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MarketStructureSignal:
    """Market structure tactical signal."""
    timestamp: datetime
    price: float
    session_open: float
    session_high: float
    session_low: float
    vwap_context: VWAPContext
    level_map: IntradayLevelMap
    volatility_state: VolatilityStructureState
    day_type: DayTypeClassification
    
    # Derived metrics
    directional_bias: str
    continuation_probability: float
    reversal_probability: float
    chop_probability: float
    structure_quality_score: float
    tactical_suitability_score: float
    
    # Suppression
    suppression_flags: List[str] = field(default_factory=list)
    suppression_reasons: List[str] = field(default_factory=list)
    
    # Sweep events
    recent_sweeps: List[LiquiditySweepEvent] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "session_open": self.session_open,
            "session_high": self.session_high,
            "session_low": self.session_low,
            "vwap_context": self.vwap_context.to_dict(),
            "level_map": self.level_map.to_dict(),
            "volatility_state": self.volatility_state.to_dict(),
            "day_type": self.day_type.to_dict(),
            "directional_bias": self.directional_bias,
            "continuation_probability": self.continuation_probability,
            "reversal_probability": self.reversal_probability,
            "chop_probability": self.chop_probability,
            "structure_quality_score": self.structure_quality_score,
            "tactical_suitability_score": self.tactical_suitability_score,
            "suppression_flags": self.suppression_flags,
            "suppression_reasons": self.suppression_reasons,
            "recent_sweeps": [s.to_dict() for s in self.recent_sweeps],
        }


@dataclass
class StructureConfidenceProfile:
    """Structure-adjusted confidence profile."""
    base_confidence: float
    vwap_adjustment: float
    level_adjustment: float
    sweep_adjustment: float
    volatility_adjustment: float
    day_type_adjustment: float
    final_confidence: float
    adjustment_reasons: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "base_confidence": self.base_confidence,
            "vwap_adjustment": self.vwap_adjustment,
            "level_adjustment": self.level_adjustment,
            "sweep_adjustment": self.sweep_adjustment,
            "volatility_adjustment": self.volatility_adjustment,
            "day_type_adjustment": self.day_type_adjustment,
            "final_confidence": self.final_confidence,
            "adjustment_reasons": self.adjustment_reasons,
        }
