"""Volatility Structure Analysis for Market Structure.

Analyzes intraday volatility conditions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from collections import deque

from app.agents.finance.tactical.market_structure.structure_models import (
    VolatilityStructureState,
    VolatilityState,
)


@dataclass
class VolBar:
    """Volatility bar data."""
    timestamp: datetime
    high: float
    low: float
    close: float
    range_percent: float


class VolatilityStructureEngine:
    """
    Analyzes intraday volatility structure.
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.bars: List[VolBar] = deque(maxlen=lookback * 2)
        self.expansion_bars: int = 0
        self.contraction_bars: int = 0
        self.ignition_detected: bool = False
    
    def add_bar(
        self,
        timestamp: datetime,
        high: float,
        low: float,
        close: float,
    ) -> None:
        """Add a bar for volatility analysis."""
        range_pct = ((high - low) / low * 100) if low > 0 else 0
        
        vol_bar = VolBar(
            timestamp=timestamp,
            high=high,
            low=low,
            close=close,
            range_percent=range_pct,
        )
        
        self.bars.append(vol_bar)
        
        # Check for expansion/contraction
        if len(self.bars) > 1:
            avg_range = self._get_avg_range()
            if range_pct > avg_range * 1.5:
                self.expansion_bars += 1
                self.contraction_bars = 0
            elif range_pct < avg_range * 0.5:
                self.contraction_bars += 1
                self.expansion_bars = 0
        
        # Check for momentum ignition
        self._check_ignition()
    
    def _get_avg_range(self) -> float:
        """Get average bar range."""
        if not self.bars:
            return 0.0
        return sum(b.range_percent for b in self.bars) / len(self.bars)
    
    def _check_ignition(self) -> None:
        """Check for momentum ignition (large range bar after consolidation)."""
        if len(self.bars) < 5:
            self.ignition_detected = False
            return
        
        recent = list(self.bars)[-5:]
        avg_range = sum(b.range_percent for b in recent) / len(recent)
        
        # Current bar significantly larger than average
        if recent[-1].range_percent > avg_range * 2:
            # Check if preceded by low-range bars (consolidation)
            if all(b.range_percent < avg_range * 1.2 for b in recent[:-1]):
                self.ignition_detected = True
    
    def get_volatility_state(
        self,
        current_price: float,
    ) -> VolatilityStructureState:
        """
        Get current volatility structure state.
        
        Args:
            current_price: Current SPY price
        
        Returns:
            VolatilityStructureState
        """
        if len(self.bars) < 5:
            return VolatilityStructureState(
                state=VolatilityState.LOW_ENERGY_CHOP,
                realized_volatility=0.0,
                volatility_percentile=0.5,
                bar_range_avg=0.0,
                bar_range_current=0.0,
                expansion_ratio=1.0,
                momentum_ignition=False,
                timestamp=datetime.now(),
            )
        
        # Calculate realized volatility
        returns = []
        for i in range(1, len(self.bars)):
            ret = (self.bars[i].close - self.bars[i-1].close) / self.bars[i-1].close
            returns.append(ret)
        
        if returns:
            import math
            mean_ret = sum(returns) / len(returns)
            variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
            std_dev = math.sqrt(variance)
            # Annualize (390 minutes per day)
            realized_vol = std_dev * (390 ** 0.5) * 100
        else:
            realized_vol = 0.0
        
        # Calculate percentiles
        avg_range = self._get_avg_range()
        current_range = self.bars[-1].range_percent if self.bars else 0
        expansion_ratio = current_range / avg_range if avg_range > 0 else 1.0
        
        # Determine state
        state = self._determine_state(expansion_ratio, realized_vol)
        
        # Calculate percentile
        percentile = self._calculate_percentile(realized_vol)
        
        return VolatilityStructureState(
            state=state,
            realized_volatility=realized_vol,
            volatility_percentile=percentile,
            bar_range_avg=avg_range,
            bar_range_current=current_range,
            expansion_ratio=expansion_ratio,
            momentum_ignition=self.ignition_detected,
            timestamp=datetime.now(),
        )
    
    def _determine_state(
        self,
        expansion_ratio: float,
        realized_vol: float,
    ) -> VolatilityState:
        """Determine volatility state."""
        
        # Check for compression building
        if self.contraction_bars >= 3:
            return VolatilityState.COMPRESSION_BUILDING
        
        # Check for healthy expansion
        if expansion_ratio > 1.5 and realized_vol < 3.0:
            return VolatilityState.HEALTHY_EXPANSION
        
        # Check for unstable expansion
        if expansion_ratio > 2.5:
            return VolatilityState.UNSTABLE_EXPANSION
        
        # Check for exhaustion
        if self.expansion_bars >= 3 and expansion_ratio > 2.0:
            return VolatilityState.EXHAUSTION_EXPANSION
        
        # Check for low energy chop
        if expansion_ratio < 0.7:
            return VolatilityState.LOW_ENERGY_CHOP
        
        # Default
        return VolatilityState.HEALTHY_EXPANSION
    
    def _calculate_percentile(self, realized_vol: float) -> float:
        """Calculate volatility percentile (simplified)."""
        # Simplified percentile based on typical SPY volatility
        if realized_vol < 0.5:
            return 0.1
        elif realized_vol < 1.0:
            return 0.25
        elif realized_vol < 1.5:
            return 0.5
        elif realized_vol < 2.5:
            return 0.75
        elif realized_vol < 3.5:
            return 0.9
        else:
            return 0.95
    
    def get_state_summary(self) -> dict:
        """Get volatility state summary."""
        return {
            "bar_count": len(self.bars),
            "expansion_bars": self.expansion_bars,
            "contraction_bars": self.contraction_bars,
            "ignition_detected": self.ignition_detected,
        }


def create_volatility_engine() -> VolatilityStructureEngine:
    """Factory function to create volatility engine."""
    return VolatilityStructureEngine()
