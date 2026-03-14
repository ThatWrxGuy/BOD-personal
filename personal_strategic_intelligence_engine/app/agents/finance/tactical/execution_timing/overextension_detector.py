"""Overextension Detector for Execution Timing.

Prevents chasing extended moves.
"""

from datetime import datetime
from typing import Optional
from collections import deque

from app.agents.finance.tactical.execution_timing.timing_models import (
    OverextensionOutput,
    OverextensionCondition,
)


class OverextensionDetector:
    """Detects overextended moves to prevent chasing."""
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.bars = deque(maxlen=lookback)
        self.avg_range = 0.0
    
    def add_bar(self, timestamp: datetime, high: float, low: float, close: float) -> None:
        range_pct = ((high - low) / low * 100) if low > 0 else 0
        self.bars.append({
            'timestamp': timestamp,
            'high': high,
            'low': low,
            'close': close,
            'range_pct': range_pct,
        })
        
        if len(self.bars) > 1:
            self.avg_range = sum(b['range_pct'] for b in self.bars) / len(self.bars)
    
    def analyze(self, current_price: float, vwap: Optional[float] = None) -> OverextensionOutput:
        if len(self.bars) < 3:
            return OverextensionOutput(
                condition=OverextensionCondition.NORMAL_DISTANCE,
                distance_from_vwap_pct=0.0,
                bar_range_vs_avg=1.0,
                exhaustion_candles=0,
                risk_score=0.3,
            )
        
        # Distance from VWAP
        if vwap and vwap > 0:
            distance_pct = (current_price - vwap) / vwap * 100
        else:
            distance_pct = 0.0
        
        # Bar range vs average
        current_range = self.bars[-1]['range_pct']
        range_ratio = current_range / self.avg_range if self.avg_range > 0 else 1.0
        
        # Exhaustion candles
        exhaustion = self._count_exhaustion_candles()
        
        # Determine condition
        condition, risk_score = self._determine_condition(distance_pct, range_ratio, exhaustion)
        
        return OverextensionOutput(
            condition=condition,
            distance_from_vwap_pct=distance_pct,
            bar_range_vs_avg=range_ratio,
            exhaustion_candles=exhaustion,
            risk_score=risk_score,
        )
    
    def _count_exhaustion_candles(self) -> int:
        if len(self.bars) < 3:
            return 0
        
        count = 0
        for bar in list(self.bars)[-3:]:
            body = abs(bar['close'] - bar['high'] if bar['close'] > bar['open'] else bar['low'] - bar['close'])
            wick = bar['high'] - bar['low'] - body
            # Large wick relative to body
            if wick > body * 2:
                count += 1
        
        return count
    
    def _determine_condition(self, distance_pct: float, range_ratio: float, exhaustion: int) -> tuple:
        if exhaustion >= 2:
            return OverextensionCondition.EXHAUSTION_RISK, 0.8
        
        if abs(distance_pct) > 1.0:
            return OverextensionCondition.OVEREXTENDED_MOVE, 0.7
        
        if abs(distance_pct) > 0.5:
            return OverextensionCondition.EXTENDED_MOVE, 0.5
        
        if range_ratio > 2.5:
            return OverextensionCondition.EXTENDED_MOVE, 0.5
        
        return OverextensionCondition.NORMAL_DISTANCE, 0.3


def create_overextension_detector() -> OverextensionDetector:
    return OverextensionDetector()
