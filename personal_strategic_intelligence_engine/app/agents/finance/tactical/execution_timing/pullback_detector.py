"""Pullback Detector for Execution Timing.

Identifies healthy retracement entries.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from collections import deque

from app.agents.finance.tactical.execution_timing.timing_models import (
    PullbackStructure,
    PullbackState,
)


class PullbackDetector:
    """
    Detects pullback patterns for entry timing.
    """
    
    def __init__(self):
        self.bars = deque(maxlen=30)
        self.swing_high = 0.0
        self.swing_low = float('inf')
        self.last_extreme_price = 0.0
        self.last_extreme_type = None  # 'high' or 'low'
    
    def add_bar(
        self,
        timestamp: datetime,
        high: float,
        low: float,
        close: float,
    ) -> None:
        """Add a bar for pullback analysis."""
        self.bars.append({
            'timestamp': timestamp,
            'high': high,
            'low': low,
            'close': close,
        })
        
        # Update swing extremes
        if high > self.swing_high:
            self.swing_high = high
            self.last_extreme_price = high
            self.last_extreme_type = 'high'
        
        if low < self.swing_low:
            self.swing_low = low
            self.last_extreme_price = low
            self.last_extreme_type = 'low'
    
    def analyze(
        self,
        current_price: float,
        direction: str,  # 'bullish' or 'bearish'
        vwap: Optional[float] = None,
        support_level: Optional[float] = None,
    ) -> PullbackStructure:
        """
        Analyze pullback state.
        
        Args:
            current_price: Current price
            direction: Trade direction ('bullish' or 'bearish')
            vwap: Optional VWAP level
            support_level: Optional support level
        
        Returns:
            PullbackStructure
        """
        if len(self.bars) < 3:
            return PullbackStructure(
                state=PullbackState.NO_PULLBACK_PRESENT,
                depth_percent=0.0,
                target_level=None,
                entry_zone_low=current_price,
                entry_zone_high=current_price,
                confidence=0.3,
            )
        
        # Determine direction
        is_bullish = direction == 'bullish'
        
        # Calculate pullback depth
        if is_bullish and self.swing_high > 0:
            depth_pct = (self.swing_high - current_price) / self.swing_high * 100
            target = self.swing_high
        elif not is_bullish and self.swing_low < float('inf'):
            depth_pct = (current_price - self.swing_low) / self.swing_low * 100
            target = self.swing_low
        else:
            depth_pct = 0.0
            target = None
        
        # Determine state
        state, confidence = self._determine_state(
            current_price, depth_pct, is_bullish, vwap, support_level
        )
        
        # Calculate entry zones
        entry_low, entry_high = self._calculate_entry_zones(
            current_price, state, depth_pct, is_bullish
        )
        
        return PullbackStructure(
            state=state,
            depth_percent=depth_pct,
            target_level=target,
            entry_zone_low=entry_low,
            entry_zone_high=entry_high,
            confidence=confidence,
        )
    
    def _determine_state(
        self,
        current_price: float,
        depth_pct: float,
        is_bullish: bool,
        vwap: Optional[float],
        support_level: Optional[float],
    ) -> tuple:
        """Determine pullback state."""
        
        # No pullback present
        if depth_pct < 0.1:
            return PullbackState.NO_PULLBACK_PRESENT, 0.3
        
        # Healthy pullback (shallow, toward support)
        if is_bullish:
            if depth_pct < 0.5:  # Less than 0.5% pullback
                # Check if near support
                if support_level and abs(current_price - support_level) < 0.5:
                    return PullbackState.HEALTHY_PULLBACK, 0.8
                elif vwap and current_price > vwap and abs(current_price - vwap) < 0.3:
                    return PullbackState.HEALTHY_PULLBACK, 0.75
                return PullbackState.HEALTHY_PULLBACK, 0.6
            elif depth_pct < 1.0:
                return PullbackState.DEEP_PULLBACK, 0.5
            else:
                return PullbackState.FAILED_PULLBACK, 0.4
        else:
            # Bearish direction
            if depth_pct < 0.5:
                if support_level and abs(current_price - support_level) < 0.5:
                    return PullbackState.HEALTHY_PULLBACK, 0.8
                return PullbackState.HEALTHY_PULLBACK, 0.6
            elif depth_pct < 1.0:
                return PullbackState.DEEP_PULLBACK, 0.5
            else:
                return PullbackState.FAILED_PULLBACK, 0.4
    
    def _calculate_entry_zones(
        self,
        current_price: float,
        state: PullbackState,
        depth_pct: float,
        is_bullish: bool,
    ) -> tuple:
        """Calculate entry zones."""
        
        if state == PullbackState.NO_PULLBACK_PRESENT:
            # Enter on breakout continuation
            if is_bullish:
                return current_price, current_price + 0.3
            else:
                return current_price - 0.3, current_price
        
        if state == PullbackState.HEALTHY_PULLBACK:
            # Enter on pullback
            zone_size = 0.2
            if is_bullish:
                return current_price, current_price + zone_size
            else:
                return current_price - zone_size, current_price
        
        if state == PullbackState.DEEP_PULLBACK:
            # Wait for confirmation
            zone_size = 0.3
            if is_bullish:
                return current_price, current_price + zone_size
            else:
                return current_price - zone_size, current_price
        
        # Failed or no entry
        return current_price, current_price
    
    def is_pullback_complete(
        self,
        current_price: float,
        direction: str,
    ) -> bool:
        """Check if pullback is complete (price resuming direction)."""
        if len(self.bars) < 2:
            return False
        
        prev_close = self.bars[-2]['close']
        
        if direction == 'bullish':
            return current_price > prev_close
        else:
            return current_price < prev_close


def create_pullback_detector() -> PullbackDetector:
    """Factory function to create pullback detector."""
    return PullbackDetector()
