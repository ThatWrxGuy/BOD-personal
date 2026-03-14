"""Microstructure Analyzer for Execution Timing.

Analyzes very short-term price behavior.
"""

from datetime import datetime
from typing import Optional
from collections import deque

from app.agents.finance.tactical.execution_timing.timing_models import (
    MicrostructureSnapshot,
    MicrostructurePattern,
)


class MicrostructureAnalyzer:
    """Analyzes microstructure patterns."""
    
    def __init__(self):
        self.bars = deque(maxlen=10)
    
    def add_bar(self, timestamp: datetime, open_price: float, high: float, low: float, close: float) -> None:
        self.bars.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
        })
    
    def analyze(self, current_price: float) -> MicrostructureSnapshot:
        if len(self.bars) < 3:
            return MicrostructureSnapshot(
                pattern=MicrostructurePattern.NEUTRAL,
                support_level=None,
                resistance_level=None,
                consolidation_range=0.0,
                ignition_strength=0.0,
            )
        
        # Calculate consolidation range
        highs = [b['high'] for b in self.bars]
        lows = [b['low'] for b in self.bars]
        consolidation_range = max(highs) - min(lows)
        
        # Determine pattern
        pattern, support, resistance, ignition = self._detect_pattern(
            current_price, highs, lows
        )
        
        return MicrostructureSnapshot(
            pattern=pattern,
            support_level=support,
            resistance_level=resistance,
            consolidation_range=consolidation_range,
            ignition_strength=ignition,
        )
    
    def _detect_pattern(self, current_price: float, highs: list, lows: list) -> tuple:
        recent = list(self.bars)[-5:]
        
        # Micro consolidation
        if len(set(round(b['close'], 2) for b in recent)) <= 3:
            return MicrostructurePattern.MICRO_CONSOLIDATION, min(lows), max(highs), 0.3
        
        # Momentum ignition - large range bar
        avg_range = sum(b['high'] - b['low'] for b in recent) / len(recent)
        last_range = recent[-1]['high'] - recent[-1]['low']
        
        if last_range > avg_range * 2:
            if recent[-1]['close'] > recent[-1]['open']:
                return MicrostructurePattern.MOMENTUM_IGNITION, min(lows), max(highs), 0.8
            else:
                return MicrostructurePattern.MOMENTUM_IGNITION, min(lows), max(highs), 0.6
        
        # Micro double top/bottom
        if len(recent) >= 4:
            if (recent[-1]['close'] < recent[-2]['close'] and 
                recent[-3]['close'] < recent[-4]['close'] and
                abs(recent[-1]['high'] - recent[-3]['high']) < avg_range * 0.5):
                return MicrostructurePattern.MICRO_DOUBLE_TOP, min(lows), max(highs), 0.5
            
            if (recent[-1]['close'] > recent[-2]['close'] and 
                recent[-3]['close'] > recent[-4]['close'] and
                abs(recent[-1]['low'] - recent[-3]['low']) < avg_range * 0.5):
                return MicrostructurePattern.MICRO_DOUBLE_BOTTOM, min(lows), max(highs), 0.5
        
        # Coil breakout
        if consolidation_range < avg_range * 0.5:
            return MicrostructurePattern.COIL_BREAKOUT, min(lows), max(highs), 0.7
        
        return MicrostructurePattern.NEUTRAL, min(lows), max(highs), 0.2


def create_microstructure_analyzer() -> MicrostructureAnalyzer:
    return MicrostructureAnalyzer()
