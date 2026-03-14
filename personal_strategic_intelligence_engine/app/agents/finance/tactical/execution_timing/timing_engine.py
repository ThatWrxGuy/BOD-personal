"""Core Timing Engine for Execution Timing.

Orchestrates momentum, pullback, breakout, overextension, and microstructure analysis.
"""

from datetime import datetime
from typing import Optional, List

from app.agents.finance.tactical.execution_timing.timing_models import (
    ExecutionTimingDecision,
    TimingDecision,
    TimingConfidenceProfile,
    EntryRecommendation,
)
from app.agents.finance.tactical.execution_timing.momentum_analyzer import MomentumAnalyzer, create_momentum_analyzer
from app.agents.finance.tactical.execution_timing.pullback_detector import PullbackDetector, create_pullback_detector
from app.agents.finance.tactical.execution_timing.breakout_confirmation import BreakoutConfirmationEngine, create_breakout_confirmation
from app.agents.finance.tactical.execution_timing.overextension_detector import OverextensionDetector, create_overextension_detector
from app.agents.finance.tactical.execution_timing.microstructure_analyzer import MicrostructureAnalyzer, create_microstructure_analyzer


class TimingEngine:
    """Core execution timing engine."""
    
    def __init__(self):
        self.momentum = create_momentum_analyzer()
        self.pullback = create_pullback_detector()
        self.breakout = create_breakout_confirmation()
        self.overextension = create_overextension_detector()
        self.microstructure = create_microstructure_analyzer()
    
    def update(self, timestamp: datetime, open_price: float, high: float, low: float, close: float, volume: int) -> None:
        """Update all components with new bar."""
        self.momentum.add_bar(timestamp, close, high, low, volume)
        self.pullback.add_bar(timestamp, high, low, close)
        self.breakout.add_bar(timestamp, high, low, close)
        self.overextension.add_bar(timestamp, high, low, close)
        self.microstructure.add_bar(timestamp, open_price, high, low, close)
    
    def evaluate(
        self,
        signal_id: str,
        current_price: float,
        direction: str,
        vwap: Optional[float] = None,
        support_level: Optional[float] = None,
        resistance_level: Optional[float] = None,
        base_confidence: float = 50.0,
    ) -> ExecutionTimingDecision:
        """Evaluate execution timing."""
        
        # Get component analyses
        momentum = self.momentum.analyze(current_price)
        pullback = self.pullback.analyze(current_price, direction, vwap, support_level)
        breakout_conf = self.breakout.analyze(current_price, resistance_level)
        overext = self.overextension.analyze(current_price, vwap)
        micro = self.microstructure.analyze(current_price)
        
        # Determine timing decision
        timing_decision, reasoning = self._determine_decision(
            momentum, pullback, breakout_conf, overext, micro, direction
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            momentum, pullback, breakout_conf, overext, micro, base_confidence
        )
        
        # Calculate entry recommendation
        entry = self._calculate_entry(
            current_price, direction, timing_decision, pullback, momentum
        )
        
        # Determine suppression flags
        flags = self._get_suppression_flags(momentum, breakout_conf, overext)
        
        return ExecutionTimingDecision(
            timestamp=datetime.now(),
            signal_id=signal_id,
            price=current_price,
            momentum=momentum,
            pullback=pullback,
            breakout=breakout_conf,
            overextension=overext,
            microstructure=micro,
            timing_decision=timing_decision,
            timing_confidence=confidence,
            entry_recommendation=entry,
            reasoning_summary=reasoning,
            suppression_flags=flags,
        )
    
    def _determine_decision(self, momentum, pullback, breakout_conf, overext, micro, direction) -> tuple:
        """Determine timing decision."""
        
        # Check for avoidance
        if overext.condition.value == "overextended_move":
            return TimingDecision.AVOID_ENTRY, "Price overextended - avoid chasing"
        
        if overext.condition.value == "exhaustion_risk":
            return TimingDecision.AVOID_ENTRY, "Exhaustion detected - high reversal risk"
        
        if momentum.state.value == "momentum_exhaustion":
            return TimingDecision.AVOID_ENTRY, "Momentum exhaustion - waiting for reversal"
        
        if breakout_conf.state.value == "failed_breakout":
            return TimingDecision.AVOID_ENTRY, "Failed breakout detected"
        
        # Check for pullback entry
        if pullback.state.value == "healthy_pullback":
            return TimingDecision.ENTER_NOW, "Healthy pullback - enter at support"
        
        # Check for breakout confirmation
        if breakout_conf.state.value == "confirmed_breakout":
            return TimingDecision.ENTER_NOW, "Confirmed breakout - enter on continuation"
        
        # Check for weak momentum
        if momentum.state.value == "weak_momentum":
            return TimingDecision.WAIT_FOR_CONFIRMATION, "Weak momentum - wait for confirmation"
        
        # Check for strong acceleration
        if momentum.state.value == "strong_acceleration":
            return TimingDecision.ENTER_NOW, "Strong momentum acceleration"
        
        # Default
        return TimingDecision.WAIT_FOR_PULLBACK, "No clear entry - wait for pullback"
    
    def _calculate_confidence(self, momentum, pullback, breakout_conf, overext, micro, base_confidence: float) -> float:
        """Calculate timing-adjusted confidence."""
        
        adjustment = 0.0
        
        # Momentum adjustment
        if momentum.state.value == "strong_acceleration":
            adjustment += 15
        elif momentum.state.value == "healthy_continuation":
            adjustment += 10
        elif momentum.state.value == "weak_momentum":
            adjustment -= 15
        elif momentum.state.value == "momentum_exhaustion":
            adjustment -= 25
        
        # Pullback adjustment
        if pullback.state.value == "healthy_pullback":
            adjustment += 10
        elif pullback.state.value == "deep_pullback":
            adjustment -= 10
        
        # Breakout adjustment
        if breakout_conf.state.value == "confirmed_breakout":
            adjustment += 15
        elif breakout_conf.state.value == "failed_breakout":
            adjustment -= 20
        
        # Overextension adjustment
        if overext.condition.value in ["overextended_move", "exhaustion_risk"]:
            adjustment -= 25
        elif overext.condition.value == "extended_move":
            adjustment -= 10
        
        # Microstructure adjustment
        if micro.pattern.value == "momentum_ignition":
            adjustment += 10
        elif micro.pattern.value == "coil_breakout":
            adjustment += 5
        
        final = base_confidence + adjustment
        return max(10, min(90, final))
    
    def _calculate_entry(self, current_price: float, direction: str, decision: TimingDecision, pullback, momentum) -> EntryRecommendation:
        """Calculate entry recommendation."""
        
        if decision == TimingDecision.AVOID_ENTRY:
            return EntryRecommendation(
                decision=decision,
                entry_zone_low=current_price,
                entry_zone_high=current_price,
                stop_level=current_price,
                invalidation_conditions=["overextension", "exhaustion"],
                reasoning="Avoid entry due to poor timing conditions",
            )
        
        zone_size = 0.2
        
        if direction == "bullish":
            entry_low = current_price
            entry_high = current_price + zone_size
            stop = current_price - zone_size
        else:
            entry_low = current_price - zone_size
            entry_high = current_price
            stop = current_price + zone_size
        
        return EntryRecommendation(
            decision=decision,
            entry_zone_low=entry_low,
            entry_zone_high=entry_high,
            stop_level=stop,
            invalidation_conditions=["price_below_stop", "momentum_reversal"],
            reasoning=f"Entry zone: {entry_low:.2f}-{entry_high:.2f}",
        )
    
    def _get_suppression_flags(self, momentum, breakout_conf, overext) -> List[str]:
        """Get suppression flags."""
        flags = []
        
        if overext.condition.value in ["overextended_move", "exhaustion_risk"]:
            flags.append("overextension")
        
        if momentum.state.value == "momentum_exhaustion":
            flags.append("momentum_exhaustion")
        
        if breakout_conf.state.value == "failed_breakout":
            flags.append("failed_breakout")
        
        return flags


def create_timing_engine() -> TimingEngine:
    return TimingEngine()
