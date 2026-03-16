"""Entry Signal Engine - BB-FIN-018"""

from typing import Optional
import logging

from app.finance.tactical_intelligence.tactical_models import (
    MarketStructure,
    EntryType,
    EntryConfidence,
    TacticalEntrySignal,
)
from app.finance.tactical_intelligence.structure_detection_engine import get_structure_detection_engine
from app.finance.tactical_intelligence.volatility_expansion_engine import get_volatility_expansion_engine
from app.finance.tactical_intelligence.momentum_detection_engine import get_momentum_detection_engine
from app.finance.tactical_intelligence.breakout_confirmation_engine import get_breakout_confirmation_engine

logger = logging.getLogger(__name__)


class EntrySignalEngine:
    """Generates tactical entry signals by combining all analysis components."""

    def __init__(self):
        self._structure_engine = get_structure_detection_engine()
        self._volatility_engine = get_volatility_expansion_engine()
        self._momentum_engine = get_momentum_detection_engine()
        self._breakout_engine = get_breakout_confirmation_engine()

    def generate_signal(
        self,
        symbol: str,
        timeframe: str = "5m",
        candles: Optional[list] = None,
        market_regime: Optional[str] = None,
        sector_context: Optional[str] = None,
    ) -> TacticalEntrySignal:
        """Generate tactical entry signal."""
        
        # Get individual analyses
        structure = self._structure_engine.analyze_structure(symbol, timeframe, candles)
        volatility = self._volatility_engine.analyze_volatility(symbol, timeframe, candles)
        momentum = self._momentum_engine.analyze_momentum(symbol, timeframe, candles)
        breakout = self._breakout_engine.analyze_breakout(symbol, timeframe, candles)
        
        # Combine signals
        entry_type, confidence, reasoning = self._determine_entry(
            structure, volatility, momentum, breakout, market_regime
        )
        
        # Calculate price levels
        entry_price = structure.close
        stop_loss, target = self._calculate_levels(
            structure, volatility, breakout, entry_price, entry_type
        )
        
        # Risk metrics
        risk_reward = None
        win_prob = 0.5
        
        if stop_loss and target and entry_price:
            risk = abs(entry_price - stop_loss) / entry_price
            reward = abs(target - entry_price) / entry_price
            if risk > 0:
                risk_reward = reward / risk
                win_prob = min(0.9, 0.3 + risk_reward * 0.3)
        
        # Warning
        warning = self._check_warning(structure, volatility, momentum, market_regime)
        
        return TacticalEntrySignal(
            symbol=symbol,
            timeframe=timeframe,
            entry_type=entry_type,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            market_structure=structure.structure,
            breakout_confirmed=breakout.breakout_valid if breakout else False,
            momentum_confirmed=momentum.momentum_state.value in ["accelerating", "neutral"],
            liquidity_confirmed=False,
            risk_reward_ratio=risk_reward,
            win_probability=win_prob,
            reasoning=reasoning,
            warning=warning,
        )

    def _determine_entry(
        self,
        structure,
        volatility,
        momentum,
        breakout,
        market_regime: Optional[str],
    ) -> tuple:
        """Determine entry type and confidence."""
        reasoning = []
        
        # Check for avoid conditions first
        if self._is_avoid_conditions(structure, volatility, momentum, market_regime):
            return EntryType.AVOID, EntryConfidence.LOW, ["Market conditions unfavorable - avoiding entry"]
        
        # Strong breakout entry
        if breakout and breakout.breakout_valid and breakout.quality.value in ["strong", "moderate"]:
            reasoning.append(f"Breakout confirmed ({breakout.quality.value})")
            
            if breakout.follow_through_probability > 0.7:
                return EntryType.BREAKOUT_ENTRY, EntryConfidence.HIGH, reasoning
            else:
                return EntryType.BREAKOUT_ENTRY, EntryConfidence.MEDIUM, reasoning
        
        # Trend continuation
        if structure.structure in [MarketStructure.TREND_UP, MarketStructure.TREND_DOWN]:
            reasoning.append(f"Trending {structure.structure.value} (strength: {structure.trend_strength:.0%})")
            
            if momentum.momentum_state.value == "accelerating":
                return EntryType.TREND_CONTINUATION, EntryConfidence.HIGH, reasoning
            else:
                return EntryType.TREND_CONTINUATION, EntryConfidence.MEDIUM, reasoning
        
        # Pullback entry (in trend but pulling back)
        if volatility.current_state.value == "compressed" and structure.trend_strength > 0.3:
            reasoning.append("Pullback to trend with compressed volatility")
            return EntryType.PULLBACK_ENTRY, EntryConfidence.MEDIUM, reasoning
        
        # Mean reversion (reversal signal)
        if structure.structure == MarketStructure.REVERSAL:
            reasoning.append("Reversal pattern detected")
            return EntryType.MEAN_REVERSION, EntryConfidence.LOW, reasoning
        
        # No clear signal
        reasoning.append("No clear entry setup - waiting")
        return EntryType.AVOID, EntryConfidence.LOW, reasoning

    def _is_avoid_conditions(
        self,
        structure,
        volatility,
        momentum,
        market_regime: Optional[str],
    ) -> bool:
        """Check if conditions warrant avoiding entries."""
        # High volatility stress
        if market_regime and "VOLATILITY_STRESS" in market_regime:
            return True
        
        # Extreme volatility expansion without confirmation
        if volatility.current_state.value == "expanding" and not momentum.momentum_state.value == "accelerating":
            return True
        
        # Strong deceleration without reversal confirmation
        if momentum.momentum_state.value == "decelerating" and structure.structure not in [MarketStructure.REVERSAL, MarketStructure.CONSOLIDATION]:
            return True
        
        # Unknown structure
        if structure.structure == MarketStructure.UNKNOWN:
            return True
        
        return False

    def _calculate_levels(
        self,
        structure,
        volatility,
        breakout,
        entry_price: float,
        entry_type: EntryType,
    ) -> tuple:
        """Calculate entry, stop, and target levels."""
        if not entry_price or entry_price <= 0:
            return None, None
        
        # Default stops based on volatility
        if volatility.compression_ratio and volatility.compression_ratio < 0.7:
            # Tight stop in compression
            stop_pct = 0.2
        else:
            # Normal stop
            stop_pct = 0.4
        
        # Adjust for entry type
        if entry_type == EntryType.BREAKOUT_ENTRY:
            stop_pct = 0.3
        elif entry_type == EntryType.MEAN_REVERSION:
            stop_pct = 0.5
        
        # Calculate levels
        if structure.structure in [MarketStructure.TREND_UP, MarketStructure.BREAKOUT_UP]:
            stop = entry_price * (1 - stop_pct / 100)
            target = entry_price * (1 + stop_pct * 2 / 100)  # 2:1 reward
        else:
            stop = entry_price * (1 + stop_pct / 100)
            target = entry_price * (1 - stop_pct * 2 / 100)
        
        return round(stop, 2), round(target, 2)

    def _check_warning(
        self,
        structure,
        volatility,
        momentum,
        market_regime: Optional[str],
    ) -> Optional[str]:
        """Check for warning conditions."""
        warnings = []
        
        # Volatility warnings
        if volatility.current_state.value == "compressed" and volatility.expansion_probability > 0.8:
            warnings.append("High expansion probability - expect volatility spike")
        
        # Momentum warnings
        if momentum.momentum_state.value == "reversing":
            warnings.append("Momentum reversing - caution")
        
        # Market regime warnings
        if market_regime and "RISK_OFF" in market_regime:
            warnings.append("Risk-off regime - reduced position sizes recommended")
        
        if warnings:
            return " | ".join(warnings)
        
        return None


# Singleton
_entry_engine: Optional[EntrySignalEngine] = None


def get_entry_signal_engine() -> EntrySignalEngine:
    """Get the singleton EntrySignalEngine instance."""
    global _entry_engine
    if _entry_engine is None:
        _entry_engine = EntrySignalEngine()
    return _entry_engine
