"""Breakout Confirmation for Execution Timing.

Validates breakouts before entry.
"""

from datetime import datetime
from typing import Optional
from collections import deque

from app.agents.finance.tactical.execution_timing.timing_models import (
    BreakoutConfirmation,
    BreakoutState,
)


class BreakoutConfirmationEngine:
    """Validates breakouts before entry."""
    
    def __init__(self):
        self.bars = deque(maxlen=30)
        self.breakout_level = None
        self.breakout_time = None
        self.breakout_type = None
    
    def add_bar(self, timestamp: datetime, high: float, low: float, close: float) -> None:
        self.bars.append({
            'timestamp': timestamp,
            'high': high,
            'low': low,
            'close': close,
        })
        
        if len(self.bars) >= 2:
            prev_high = self.bars[-2]['high']
            prev_low = self.bars[-2]['low']
            
            if close > prev_high:
                self.breakout_level = prev_high
                self.breakout_time = timestamp
                self.breakout_type = 'up'
            elif close < prev_low:
                self.breakout_level = prev_low
                self.breakout_time = timestamp
                self.breakout_type = 'down'
    
    def analyze(self, current_price: float, key_level: Optional[float] = None) -> BreakoutConfirmation:
        if len(self.bars) < 3:
            return BreakoutConfirmation(
                state=BreakoutState.RANGE_CONTAINMENT,
                breakout_level=None,
                bars_since_breakout=0,
                confirmation_bars=0,
                rejection_detected=False,
                confidence=0.3,
            )
        
        if self.breakout_level is None:
            if key_level:
                if current_price > key_level:
                    return self._analyze_breakout(current_price, 'up', key_level)
                elif current_price < key_level:
                    return self._analyze_breakout(current_price, 'down', key_level)
            
            return BreakoutConfirmation(
                state=BreakoutState.RANGE_CONTAINMENT,
                breakout_level=key_level,
                bars_since_breakout=0,
                confirmation_bars=0,
                rejection_detected=False,
                confidence=0.5,
            )
        
        return self._analyze_breakout(current_price, self.breakout_type, self.breakout_level)
    
    def _analyze_breakout(self, current_price: float, breakout_type: str, breakout_level: float) -> BreakoutConfirmation:
        bars_since = 0
        confirmation_bars = 0
        rejection_detected = False
        
        for i in range(len(self.bars) - 1, -1, -1):
            bar = self.bars[i]
            
            if breakout_type == 'up':
                if bar['close'] > bar['open']:
                    confirmation_bars += 1
                if bar['low'] < breakout_level:
                    rejection_detected = True
            else:
                if bar['close'] < bar['open']:
                    confirmation_bars += 1
                if bar['high'] > breakout_level:
                    rejection_detected = True
            
            bars_since += 1
            if bars_since >= 5:
                break
        
        state, confidence = self._determine_state(breakout_type, confirmation_bars, rejection_detected, current_price, breakout_level)
        
        return BreakoutConfirmation(
            state=state,
            breakout_level=breakout_level,
            bars_since_breakout=bars_since,
            confirmation_bars=confirmation_bars,
            rejection_detected=rejection_detected,
            confidence=confidence,
        )
    
    def _determine_state(self, breakout_type: str, confirmation_bars: int, rejection_detected: bool, current_price: float, breakout_level: float) -> tuple:
        if rejection_detected:
            return BreakoutState.FAILED_BREAKOUT, 0.7
        
        if confirmation_bars >= 2:
            if breakout_type == 'up' and current_price > breakout_level:
                return BreakoutState.CONFIRMED_BREAKOUT, 0.8
            elif breakout_type == 'down' and current_price < breakout_level:
                return BreakoutState.CONFIRMED_BREAKOUT, 0.8
        
        if confirmation_bars == 1:
            return BreakoutState.UNCONFIRMED_BREAKOUT, 0.5
        
        return BreakoutState.BREAKOUT_PENDING, 0.4
    
    def reset(self) -> None:
        self.breakout_level = None
        self.breakout_time = None
        self.breakout_type = None


def create_breakout_confirmation() -> BreakoutConfirmationEngine:
    return BreakoutConfirmationEngine()
