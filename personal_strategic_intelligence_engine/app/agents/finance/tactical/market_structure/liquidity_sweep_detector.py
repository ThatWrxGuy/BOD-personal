"""Liquidity Sweep Detector for Market Structure Analysis.

Detects liquidity sweeps, stop runs, and failed directional moves.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import uuid

from app.agents.finance.tactical.market_structure.structure_models import (
    LiquiditySweepEvent,
    SweepType,
    SweepDirection,
    SweepOutcome,
)


class SweepDetector:
    """
    Detects liquidity sweep events.
    
    Identifies stop runs and failed directional moves.
    """
    
    def __init__(self):
        self.sweeps: List[LiquiditySweepEvent] = []
        self.recent_high: float = 0.0
        self.recent_low: float = float('inf')
        self.or_high: float = 0.0
        self.or_low: float = float('inf')
        self.last_price: float = 0.0
        self.last_high: float = 0.0
        self.last_low: float = float('inf')
    
    def set_opening_range(self, high: float, low: float) -> None:
        """Set opening range for sweep detection."""
        self.or_high = high
        self.or_low = low
    
    def update(
        self,
        timestamp: datetime,
        high: float,
        low: float,
        close: float,
        volume: int,
    ) -> Optional[LiquiditySweepEvent]:
        """
        Update with new bar and detect sweeps.
        
        Returns sweep event if detected.
        """
        sweep_detected = None
        
        # Check for sweep above recent high
        if self.recent_high > 0 and high > self.recent_high:
            # Sweep above high
            if close < self.recent_high:
                # Rejected - bullish trap
                sweep_detected = self._create_sweep(
                    timestamp=timestamp,
                    sweep_type=SweepType.SWEEP_ABOVE_HIGH,
                    direction=SweepDirection.BULLISH,
                    price=high,
                    target_level=self.recent_high,
                    outcome=SweepOutcome.BULLISH_TRAP,
                    rejection_price=close,
                    volume=volume,
                )
            elif close > high:
                # Continued - confirmed
                sweep_detected = self._create_sweep(
                    timestamp=timestamp,
                    sweep_type=SweepType.SWEEP_ABOVE_HIGH,
                    direction=SweepDirection.BULLISH,
                    price=high,
                    target_level=self.recent_high,
                    outcome=SweepOutcome.CONFIRMED_CONTINUATION,
                    rejection_price=None,
                    volume=volume,
                )
        
        # Check for sweep below recent low
        if self.recent_low < float('inf') and low < self.recent_low:
            # Sweep below low
            if close > self.recent_low:
                # Rejected - bearish trap
                sweep_detected = self._create_sweep(
                    timestamp=timestamp,
                    sweep_type=SweepType.SWEEP_BELOW_LOW,
                    direction=SweepDirection.BEARISH,
                    price=low,
                    target_level=self.recent_low,
                    outcome=SweepOutcome.BEARISH_TRAP,
                    rejection_price=close,
                    volume=volume,
                )
            elif close < low:
                # Continued - confirmed
                sweep_detected = self._create_sweep(
                    timestamp=timestamp,
                    sweep_type=SweepType.SWEEP_BELOW_LOW,
                    direction=SweepDirection.BEARISH,
                    price=low,
                    target_level=self.recent_low,
                    outcome=SweepOutcome.CONFIRMED_CONTINUATION,
                    rejection_price=None,
                    volume=volume,
                )
        
        # Check for OR sweep
        if self.or_high > 0 and high > self.or_high:
            sweep_detected = self._create_sweep(
                timestamp=timestamp,
                sweep_type=SweepType.OPENING_RANGE_SWEEP,
                direction=SweepDirection.BULLISH,
                price=high,
                target_level=self.or_high,
                outcome=None,
                rejection_price=None,
                volume=volume,
            )
        
        if self.or_low < float('inf') and low < self.or_low:
            sweep_detected = self._create_sweep(
                timestamp=timestamp,
                sweep_type=SweepType.OPENING_RANGE_SWEEP,
                direction=SweepDirection.BEARISH,
                price=low,
                target_level=self.or_low,
                outcome=None,
                rejection_price=None,
                volume=volume,
            )
        
        # Update recent levels
        if self.recent_high == 0 or high > self.recent_high:
            self.recent_high = high
        
        if self.recent_low == float('inf') or low < self.recent_low:
            self.recent_low = low
        
        self.last_price = close
        self.last_high = high
        self.last_low = low
        
        if sweep_detected:
            self.sweeps.append(sweep_detected)
        
        return sweep_detected
    
    def _create_sweep(
        self,
        timestamp: datetime,
        sweep_type: SweepType,
        direction: SweepDirection,
        price: float,
        target_level: float,
        outcome: Optional[SweepOutcome],
        rejection_price: Optional[float],
        volume: int,
    ) -> LiquiditySweepEvent:
        """Create a sweep event."""
        return LiquiditySweepEvent(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            sweep_type=sweep_type,
            direction=direction,
            price=price,
            target_level=target_level,
            outcome=outcome,
            rejection_price=rejection_price,
            volume=volume,
        )
    
    def get_recent_sweeps(
        self,
        minutes: int = 60,
    ) -> List[LiquiditySweepEvent]:
        """Get sweeps from the last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [s for s in self.sweeps if s.timestamp > cutoff]
    
    def get_sweep_summary(self) -> dict:
        """Get summary of sweep events."""
        recent = self.get_recent_sweeps(120)  # Last 2 hours
        
        bullish_traps = sum(1 for s in recent if s.outcome == SweepOutcome.BULLISH_TRAP)
        bearish_traps = sum(1 for s in recent if s.outcome == SweepOutcome.BEARISH_TRAP)
        continuations = sum(1 for s in recent if s.outcome == SweepOutcome.CONFIRMED_CONTINUATION)
        
        return {
            "total_sweeps": len(recent),
            "bullish_traps": bullish_traps,
            "bearish_traps": bearish_traps,
            "confirmed_continuations": continuations,
            "net_bullish": bullish_traps - bearish_traps,
        }
    
    def get_trap_bias(self) -> str:
        """Get current trap bias."""
        summary = self.get_sweep_summary()
        
        if summary["net_bullish"] > 2:
            return "bullish_trap_bias"
        elif summary["net_bullish"] < -2:
            return "bearish_trap_bias"
        
        return "neutral"


def create_sweep_detector() -> SweepDetector:
    """Factory function to create sweep detector."""
    return SweepDetector()
