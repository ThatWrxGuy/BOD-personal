"""VWAP Intelligence Engine for Market Structure Analysis.

Computes and interprets VWAP-based market structure.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
import math

from app.agents.finance.tactical.market_structure.structure_models import (
    VWAPContext,
    VWAPState,
)


@dataclass
class VWAPBar:
    """Single bar for VWAP calculation."""
    timestamp: datetime
    high: float
    low: float
    close: float
    volume: int
    typical_price: float = 0.0
    
    def __post_init__(self):
        self.typical_price = (self.high + self.low + self.close) / 3


class VWAPEngine:
    """
    VWAP Intelligence Engine.
    
    Calculates session VWAP and interprets price behavior relative to VWAP.
    """
    
    def __init__(self):
        self.bars: List[VWAPBar] = []
        self.vwap: float = 0.0
        self.volume_profile: List[tuple] = []  # (price, volume)
    
    def add_bar(
        self,
        timestamp: datetime,
        high: float,
        low: float,
        close: float,
        volume: int,
    ) -> None:
        """Add a bar to the VWAP calculation."""
        bar = VWAPBar(
            timestamp=timestamp,
            high=high,
            low=low,
            close=close,
            volume=volume,
        )
        self.bars.append(bar)
        
        # Update volume profile
        self._update_volume_profile(high, low, volume)
        
        # Recalculate VWAP
        self._calculate_vwap()
    
    def _update_volume_profile(self, high: float, low: float, volume: int) -> None:
        """Update volume profile by price level."""
        # Simple volume profile - track high, low, close volumes
        self.volume_profile.append({
            'high': high,
            'low': low,
            'close': (high + low) / 2,
            'volume': volume,
        })
    
    def _calculate_vwap(self) -> None:
        """Calculate VWAP from accumulated bars."""
        if not self.bars:
            self.vwap = 0.0
            return
        
        total_pv = 0.0
        total_volume = 0
        
        for bar in self.bars:
            pv = bar.typical_price * bar.volume
            total_pv += pv
            total_volume += bar.volume
        
        if total_volume > 0:
            self.vwap = total_pv / total_volume
        else:
            self.vwap = self.bars[-1].typical_price if self.bars else 0.0
    
    def get_vwap_context(
        self,
        current_price: float,
        lookback_bars: int = 20,
    ) -> VWAPContext:
        """
        Get current VWAP context.
        
        Args:
            current_price: Current SPY price
            lookback_bars: Number of bars for slope calculation
        
        Returns:
            VWAPContext
        """
        if not self.bars:
            return VWAPContext(
                vwap=current_price,
                price=current_price,
                distance_from_vwap=0,
                distance_pct=0,
                vwap_slope=0,
                state=VWAPState.VWAP_CHOP_NEUTRAL,
                volume_at_vwap=0,
                timestamp=datetime.now(),
            )
        
        # Calculate distance from VWAP
        distance = current_price - self.vwap
        distance_pct = (distance / self.vwap * 100) if self.vwap > 0 else 0
        
        # Calculate VWAP slope
        slope = self._calculate_slope(lookback_bars)
        
        # Determine VWAP state
        state = self._determine_state(current_price, distance_pct, slope)
        
        return VWAPContext(
            vwap=self.vwap,
            price=current_price,
            distance_from_vwap=distance,
            distance_pct=distance_pct,
            vwap_slope=slope,
            state=state,
            volume_at_vwap=self._get_volume_at_vwap(),
            timestamp=datetime.now(),
        )
    
    def _calculate_slope(self, lookback: int) -> float:
        """Calculate VWAP slope over lookback period."""
        if len(self.bars) < 2:
            return 0.0
        
        recent_bars = self.bars[-lookback:]
        
        if len(recent_bars) < 2:
            return 0.0
        
        # Simple linear regression for slope
        n = len(recent_bars)
        timestamps = list(range(n))
        vwaps = [self._get_bar_vwap(bar) for bar in recent_bars]
        
        x_mean = sum(timestamps) / n
        y_mean = sum(vwaps) / n
        
        numerator = sum((timestamps[i] - x_mean) * (vwaps[i] - y_mean) for i in range(n))
        denominator = sum((timestamps[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _get_bar_vwap(self, bar: VWAPBar) -> float:
        """Get VWAP contribution from a single bar."""
        return bar.typical_price
    
    def _get_volume_at_vwap(self) -> float:
        """Get volume concentration at VWAP level."""
        if not self.volume_profile:
            return 0.0
        
        # Find volume near VWAP
        vwap_volume = 0
        total_volume = 0
        
        for entry in self.volume_profile[-20:]:  # Recent bars
            vol = entry['volume']
            total_volume += vol
            
            # Within 0.1% of VWAP
            if self.vwap > 0:
                if abs(entry['close'] - self.vwap) / self.vwap < 0.001:
                    vwap_volume += vol
        
        return vwap_volume / total_volume if total_volume > 0 else 0
    
    def _determine_state(
        self,
        price: float,
        distance_pct: float,
        slope: float,
    ) -> VWAPState:
        """Determine VWAP state based on price position and slope."""
        
        # Overextension check
        if abs(distance_pct) > 0.5:  # More than 0.5% from VWAP
            return VWAPState.OVEREXTENDED_FROM_VWAP
        
        # Above VWAP acceptance
        if distance_pct > 0.1 and slope > 0:
            # Price above VWAP and VWAP trending up
            if self._is_accepting(price, above=True):
                return VWAPState.ABOVE_VWAP_ACCEPTANCE
            elif self._is_reclaiming():
                return VWAPState.VWAP_RECLAIM_BULLISH
        
        # Below VWAP acceptance
        if distance_pct < -0.1 and slope < 0:
            # Price below VWAP and VWAP trending down
            if self._is_accepting(price, above=False):
                return VWAPState.BELOW_VWAP_ACCEPTANCE
            elif self._is_rejecting():
                return VWAPState.VWAP_REJECT_BEARISH
        
        # Check for reclaim (price crossing VWAP)
        if self._is_reclaiming():
            if distance_pct > 0:
                return VWAPState.VWAP_RECLAIM_BULLISH
            else:
                return VWAPState.VWAP_REJECT_BEARISH
        
        # Check for rejection
        if self._is_rejecting():
            if distance_pct > 0:
                return VWAPState.VWAP_REJECT_BEARISH
            else:
                return VWAPState.VWAP_RECLAIM_BULLISH
        
        # Default: chop around VWAP
        return VWAPState.VWAP_CHOP_NEUTRAL
    
    def _is_accepting(self, price: float, above: bool) -> bool:
        """Check if price is accepting VWAP (making higher lows or lower highs)."""
        if len(self.bars) < 3:
            return False
        
        recent = self.bars[-3:]
        
        if above:
            # For bullish acceptance: higher lows
            return recent[0].low < recent[1].low < recent[2].low
        else:
            # For bearish acceptance: lower highs
            return recent[0].high > recent[1].high > recent[2].high
    
    def _is_reclaiming(self) -> bool:
        """Check if price is reclaiming VWAP (crossing from one side to other)."""
        if len(self.bars) < 2:
            return False
        
        prev_price = self.bars[-2].close
        curr_price = self.bars[-1].close
        
        prev_vs_vwap = prev_price - self.vwap
        curr_vs_vwap = curr_price - self.vwap
        
        # Crossed VWAP
        return (prev_vs_vwap > 0 and curr_vs_vwap < 0) or (prev_vs_vwap < 0 and curr_vs_vwap > 0)
    
    def _is_rejecting(self) -> bool:
        """Check if price is rejecting VWAP (failing to cross)."""
        if len(self.bars) < 3:
            return False
        
        # Check for rejection pattern
        recent = self.bars[-3:]
        
        # Near VWAP but failing to cross
        for bar in recent:
            if abs(bar.close - self.vwap) / self.vwap < 0.001:
                # Close near VWAP but not crossing
                if bar.high > self.vwap and bar.close < self.vwap:
                    return True  # Rejected above
                if bar.low < self.vwap and bar.close > self.vwap:
                    return True  # Rejected below
        
        return False
    
    def get_vwap_stats(self) -> dict:
        """Get VWAP statistics."""
        return {
            "bar_count": len(self.bars),
            "current_vwap": self.vwap,
            "volume_profile_entries": len(self.volume_profile),
        }
    
    def reset(self) -> None:
        """Reset VWAP calculation."""
        self.bars = []
        self.vwap = 0.0
        self.volume_profile = []


def create_vwap_engine() -> VWAPEngine:
    """Factory function to create VWAP engine."""
    return VWAPEngine()
