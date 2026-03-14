"""Momentum Analyzer for Execution Timing.

Analyzes short-term directional strength.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from collections import deque

from app.agents.finance.tactical.execution_timing.timing_models import (
    MomentumStateOutput,
    MomentumState,
)


@dataclass
class MomentumBar:
    """Bar data for momentum analysis."""
    timestamp: datetime
    close: float
    high: float
    low: float
    volume: int
    range_pct: float = 0.0


class MomentumAnalyzer:
    """
    Analyzes short-term momentum characteristics.
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.bars = deque(maxlen=lookback * 2)
        self.volume_avg = 0.0
    
    def add_bar(
        self,
        timestamp: datetime,
        close: float,
        high: float,
        low: float,
        volume: int,
    ) -> None:
        """Add a bar for momentum analysis."""
        range_pct = ((high - low) / low * 100) if low > 0 else 0
        
        bar = MomentumBar(
            timestamp=timestamp,
            close=close,
            high=high,
            low=low,
            volume=volume,
            range_pct=range_pct,
        )
        
        self.bars.append(bar)
        
        # Update volume average
        if len(self.bars) > 1:
            self.volume_avg = sum(b.volume for b in self.bars) / len(self.bars)
    
    def analyze(self, current_price: float) -> MomentumStateOutput:
        """
        Analyze momentum state.
        
        Args:
            current_price: Current price
        
        Returns:
            MomentumStateOutput
        """
        if len(self.bars) < 3:
            return MomentumStateOutput(
                state=MomentumState.WEAK_MOMENTUM,
                slope_1min=0.0,
                slope_3min=0.0,
                volume_expansion=1.0,
                acceleration=0.0,
                confidence=0.3,
            )
        
        # Calculate slopes
        slope_1min = self._calculate_slope(1)
        slope_3min = self._calculate_slope(3)
        
        # Volume expansion
        volume_expansion = self._calculate_volume_expansion()
        
        # Acceleration
        acceleration = self._calculate_acceleration()
        
        # Determine state
        state = self._determine_state(slope_1min, slope_3min, volume_expansion, acceleration)
        
        # Calculate confidence
        confidence = self._calculate_confidence(state, slope_1min, slope_3min, volume_expansion)
        
        return MomentumStateOutput(
            state=state,
            slope_1min=slope_1min,
            slope_3min=slope_3min,
            volume_expansion=volume_expansion,
            acceleration=acceleration,
            confidence=confidence,
        )
    
    def _calculate_slope(self, minutes: int) -> float:
        """Calculate price slope over N minutes."""
        if len(self.bars) < minutes:
            return 0.0
        
        recent = list(self.bars)[-minutes:]
        
        if len(recent) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(recent)
        timestamps = list(range(n))
        prices = [b.close for b in recent]
        
        x_mean = sum(timestamps) / n
        y_mean = sum(prices) / n
        
        numerator = sum((timestamps[i] - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((timestamps[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _calculate_volume_expansion(self) -> float:
        """Calculate volume expansion ratio."""
        if not self.bars or self.volume_avg == 0:
            return 1.0
        
        current_volume = self.bars[-1].volume
        return current_volume / self.volume_avg
    
    def _calculate_acceleration(self) -> float:
        """Calculate momentum acceleration."""
        if len(self.bars) < 3:
            return 0.0
        
        recent = list(self.bars)[-3:]
        
        # Calculate rate of change
        changes = []
        for i in range(1, len(recent)):
            change = (recent[i].close - recent[i-1].close) / recent[i-1].close
            changes.append(change)
        
        if len(changes) < 2:
            return 0.0
        
        # Acceleration = change in rate of change
        acceleration = changes[-1] - changes[0]
        
        return acceleration
    
    def _determine_state(
        self,
        slope_1min: float,
        slope_3min: float,
        volume_expansion: float,
        acceleration: float,
    ) -> MomentumState:
        """Determine momentum state."""
        
        # Strong acceleration
        if acceleration > 0.001 and volume_expansion > 1.5:
            if slope_1min > 0.1:
                return MomentumState.STRONG_ACCELERATION
        
        # Healthy continuation
        if slope_3min > 0.05 and 0.8 < volume_expansion < 1.5:
            return MomentumState.HEALTHY_CONTINUATION
        
        # Weak momentum
        if abs(slope_3min) < 0.02:
            return MomentumState.WEAK_MOMENTUM
        
        # Momentum exhaustion
        if acceleration < -0.001 and slope_1min < 0:
            return MomentumState.MOMENTUM_EXHAUSTION
        
        # Momentum reversal
        if slope_1min * slope_3min < 0:
            return MomentumState.MOMENTUM_REVERSAL
        
        # Default
        return MomentumState.HEALTHY_CONTINUATION
    
    def _calculate_confidence(
        self,
        state: MomentumState,
        slope_1min: float,
        slope_3min: float,
        volume_expansion: float,
    ) -> float:
        """Calculate confidence in momentum state."""
        
        base_confidence = 0.5
        
        # Stronger slopes = higher confidence
        if abs(slope_3min) > 0.1:
            base_confidence += 0.2
        elif abs(slope_3min) > 0.05:
            base_confidence += 0.1
        
        # Volume confirmation
        if volume_expansion > 1.2:
            base_confidence += 0.1
        elif volume_expansion < 0.8:
            base_confidence -= 0.1
        
        return max(0.3, min(0.9, base_confidence))


def create_momentum_analyzer() -> MomentumAnalyzer:
    """Factory function to create momentum analyzer."""
    return MomentumAnalyzer()
