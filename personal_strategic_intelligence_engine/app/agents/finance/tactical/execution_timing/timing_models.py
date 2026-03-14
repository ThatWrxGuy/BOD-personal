"""Execution Timing Models for Tactical Decision Stack.

Defines models for entry timing decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class TimingDecision(str, Enum):
    """Entry timing decision types."""
    ENTER_NOW = "enter_now"
    WAIT_FOR_PULLBACK = "wait_for_pullback"
    WAIT_FOR_CONFIRMATION = "wait_for_confirmation"
    AVOID_ENTRY = "avoid_entry"
    DEFER_SIGNAL = "defer_signal"


class MomentumState(str, Enum):
    """Momentum state classification."""
    STRONG_ACCELERATION = "strong_acceleration"
    HEALTHY_CONTINUATION = "healthy_continuation"
    WEAK_MOMENTUM = "weak_momentum"
    MOMENTUM_EXHAUSTION = "momentum_exhaustion"
    MOMENTUM_REVERSAL = "momentum_reversal"


class PullbackState(str, Enum):
    """Pullback state classification."""
    HEALTHY_PULLBACK = "healthy_pullback"
    DEEP_PULLBACK = "deep_pullback"
    FAILED_PULLBACK = "failed_pullback"
    PULLBACK_COMPLETED = "pullback_completed"
    NO_PULLBACK_PRESENT = "no_pullback_present"


class BreakoutState(str, Enum):
    """Breakout confirmation state."""
    CONFIRMED_BREAKOUT = "confirmed_breakout"
    UNCONFIRMED_BREAKOUT = "unconfirmed_breakout"
    FAILED_BREAKOUT = "failed_breakout"
    BREAKOUT_PENDING = "breakout_pending"
    RANGE_CONTAINMENT = "range_containment"


class OverextensionCondition(str, Enum):
    """Overextension condition classification."""
    EXTENDED_MOVE = "extended_move"
    OVEREXTENDED_MOVE = "overextended_move"
    NORMAL_DISTANCE = "normal_distance"
    EXHAUSTION_RISK = "exhaustion_risk"


class MicrostructurePattern(str, Enum):
    """Microstructure pattern types."""
    MICRO_CONSOLIDATION = "micro_consolidation"
    MOMENTUM_IGNITION = "momentum_ignition"
    MICRO_DOUBLE_TOP = "micro_double_top"
    MICRO_DOUBLE_BOTTOM = "micro_double_bottom"
    COIL_BREAKOUT = "coil_breakout"
    NEUTRAL = "neutral"


@dataclass
class MomentumStateOutput:
    """Momentum analysis output."""
    state: MomentumState
    slope_1min: float
    slope_3min: float
    volume_expansion: float
    acceleration: float
    confidence: float
    
    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "slope_1min": self.slope_1min,
            "slope_3min": self.slope_3min,
            "volume_expansion": self.volume_expansion,
            "acceleration": self.acceleration,
            "confidence": self.confidence,
        }


@dataclass
class PullbackStructure:
    """Pullback analysis output."""
    state: PullbackState
    depth_percent: float
    target_level: Optional[str]
    entry_zone_low: float
    entry_zone_high: float
    confidence: float
    
    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "depth_percent": self.depth_percent,
            "target_level": self.target_level,
            "entry_zone_low": self.entry_zone_low,
            "entry_zone_high": self.entry_zone_high,
            "confidence": self.confidence,
        }


@dataclass
class BreakoutConfirmation:
    """Breakout confirmation output."""
    state: BreakoutState
    breakout_level: Optional[float]
    bars_since_breakout: int
    confirmation_bars: int
    rejection_detected: bool
    confidence: float
    
    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "breakout_level": self.breakout_level,
            "bars_since_breakout": self.bars_since_breakout,
            "confirmation_bars": self.confirmation_bars,
            "rejection_detected": self.rejection_detected,
            "confidence": self.confidence,
        }


@dataclass
class OverextensionOutput:
    """Overextension analysis output."""
    condition: OverextensionCondition
    distance_from_vwap_pct: float
    bar_range_vs_avg: float
    exhaustion_candles: int
    risk_score: float
    
    def to_dict(self) -> dict:
        return {
            "condition": self.condition.value,
            "distance_from_vwap_pct": self.distance_from_vwap_pct,
            "bar_range_vs_avg": self.bar_range_vs_avg,
            "exhaustion_candles": self.exhaustion_candles,
            "risk_score": self.risk_score,
        }


@dataclass
class MicrostructureSnapshot:
    """Microstructure analysis output."""
    pattern: MicrostructurePattern
    support_level: Optional[float]
    resistance_level: Optional[float]
    consolidation_range: float
    ignition_strength: float
    
    def to_dict(self) -> dict:
        return {
            "pattern": self.pattern.value,
            "support_level": self.support_level,
            "resistance_level": self.resistance_level,
            "consolidation_range": self.consolidation_range,
            "ignition_strength": self.ignition_strength,
        }


@dataclass
class TimingConfidenceProfile:
    """Timing-adjusted confidence profile."""
    base_confidence: float
    momentum_adjustment: float
    pullback_adjustment: float
    breakout_adjustment: float
    overextension_adjustment: float
    microstructure_adjustment: float
    final_confidence: float
    adjustment_reasons: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "base_confidence": self.base_confidence,
            "momentum_adjustment": self.momentum_adjustment,
            "pullback_adjustment": self.pullback_adjustment,
            "breakout_adjustment": self.breakout_adjustment,
            "overextension_adjustment": self.overextension_adjustment,
            "microstructure_adjustment": self.microstructure_adjustment,
            "final_confidence": self.final_confidence,
            "adjustment_reasons": self.adjustment_reasons,
        }


@dataclass
class EntryRecommendation:
    """Entry recommendation details."""
    decision: TimingDecision
    entry_zone_low: float
    entry_zone_high: float
    stop_level: float
    invalidation_conditions: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    def to_dict(self) -> dict:
        return {
            "decision": self.decision.value,
            "entry_zone_low": self.entry_zone_low,
            "entry_zone_high": self.entry_zone_high,
            "stop_level": self.stop_level,
            "invalidation_conditions": self.invalidation_conditions,
            "reasoning": self.reasoning,
        }


@dataclass
class ExecutionTimingDecision:
    """Complete execution timing decision."""
    timestamp: datetime
    signal_id: str
    price: float
    
    # Component analyses
    momentum: MomentumStateOutput
    pullback: PullbackStructure
    breakout: BreakoutConfirmation
    overextension: OverextensionOutput
    microstructure: MicrostructureSnapshot
    
    # Final decision
    timing_decision: TimingDecision
    timing_confidence: float
    entry_recommendation: EntryRecommendation
    
    # Reasoning
    reasoning_summary: str = ""
    suppression_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "signal_id": self.signal_id,
            "price": self.price,
            "momentum": self.momentum.to_dict(),
            "pullback": self.pullback.to_dict(),
            "breakout": self.breakout.to_dict(),
            "overextension": self.overextension.to_dict(),
            "microstructure": self.microstructure.to_dict(),
            "timing_decision": self.timing_decision.value,
            "timing_confidence": self.timing_confidence,
            "entry_recommendation": self.entry_recommendation.to_dict(),
            "reasoning_summary": self.reasoning_summary,
            "suppression_flags": self.suppression_flags,
        }
