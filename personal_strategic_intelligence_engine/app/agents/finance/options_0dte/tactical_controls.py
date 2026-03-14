"""Time-of-Day and Cooldown Controls for SPY 0DTE Tactical Agent.

Implements tactical constraints for trading windows, cooldowns, and signal deduplication.
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional
from enum import Enum


class TradingWindow(str, Enum):
    """Trading window classification."""
    PRE_MARKET = "pre_market"
    OPENING_VOLATILITY = "opening_volatility"
    MIDDAY = "midday"
    CLOSING_VOLATILITY = "closing_volatility"
    AFTER_HOURS = "after_hours"
    CLOSED = "closed"


@dataclass
class CooldownEntry:
    """Cooldown entry for a signal."""
    signal_id: str
    strike: float
    option_type: str
    direction: str  # "call" or "put"
    cooldown_end: datetime
    reason: str


@dataclass
class TimeOfDayConfig:
    """Configuration for time-of-day controls."""
    # Market hours (ET)
    market_open: time = time(9, 30)
    market_close: time = time(16, 0)
    
    # Opening volatility window (minutes from open)
    opening_window_minutes: int = 15
    
    # Midday suppression window
    midday_start: time = time(11, 0)
    midday_end: time = time(14, 0)
    
    # Closing volatility window (minutes before close)
    closing_window_minutes: int = 30
    
    # Cooldown settings
    cooldown_minutes: int = 15
    min_cooldown_trades: int = 3
    
    # Suppression thresholds
    midday_confidence_reduction: float = 0.3
    opening_volatility_confidence_reduction: float = 0.2


class TimeOfDayController:
    """
    Controls for time-of-day trading constraints.
    
    Manages opening volatility window, midday suppression,
    end-of-day cutoff, and cooldown periods.
    """
    
    def __init__(self, config: Optional[TimeOfDayConfig] = None):
        self.config = config or TimeOfDayConfig()
        self.cooldowns: list[CooldownEntry] = []
    
    def get_current_window(self) -> TradingWindow:
        """Get current trading window."""
        now = datetime.now()
        current_time = now.time()
        
        # Before market open
        if current_time < self.config.market_open:
            return TradingWindow.PRE_MARKET
        
        # Opening volatility window
        minutes_from_open = (
            datetime.combine(now.date(), current_time) - 
            datetime.combine(now.date(), self.config.market_open)
        ).seconds / 60
        if minutes_from_open <= self.config.opening_window_minutes:
            return TradingWindow.OPENING_VOLATILITY
        
        # Midday suppression window
        if self.config.midday_start <= current_time <= self.config.midday_end:
            return TradingWindow.MIDDAY
        
        # Closing volatility window
        minutes_to_close = (
            datetime.combine(now.date(), self.config.market_close) - 
            datetime.combine(now.date(), current_time)
        ).seconds / 60
        if minutes_to_close <= self.config.closing_window_minutes:
            return TradingWindow.CLOSING_VOLATILITY
        
        # After hours
        if current_time > self.config.market_close:
            return TradingWindow.AFTER_HOURS
        
        return TradingWindow.MIDDAY
    
    def get_confidence_adjustment(self, window: Optional[TradingWindow] = None) -> float:
        """
        Get confidence adjustment based on trading window.
        
        Returns multiplier (0-1) to reduce confidence in suboptimal windows.
        """
        if window is None:
            window = self.get_current_window()
        
        if window == TradingWindow.OPENING_VOLATILITY:
            return 1.0 - self.config.opening_volatility_confidence_reduction
        elif window == TradingWindow.MIDDAY:
            return 1.0 - self.config.midday_confidence_reduction
        elif window == TradingWindow.CLOSING_VOLATILITY:
            return 0.9  # Slight reduction
        else:
            return 1.0  # Full confidence
    
    def should_suppress_by_time(self, regime_confidence: float = 1.0) -> tuple[bool, str]:
        """
        Check if signal should be suppressed based on time.
        
        Args:
            regime_confidence: Base regime confidence
        
        Returns:
            Tuple of (should_suppress, reason)
        """
        window = self.get_current_window()
        
        if window == TradingWindow.CLOSED:
            return True, "Market closed"
        
        if window == TradingWindow.PRE_MARKET:
            return True, "Pre-market - waiting for open"
        
        if window == TradingWindow.AFTER_HOURS:
            return True, "After hours - waiting for close"
        
        # Adjust confidence for window
        adjusted_confidence = regime_confidence * self.get_confidence_adjustment(window)
        
        # If adjusted confidence too low, suppress
        if adjusted_confidence < 0.4:
            return True, f"Low confidence in {window.value} window ({adjusted_confidence:.2f})"
        
        return False, ""
    
    def add_cooldown(
        self,
        signal_id: str,
        strike: float,
        option_type: str,
        direction: str,
        reason: str = "signal_completed",
    ) -> None:
        """Add a cooldown entry."""
        cooldown_end = datetime.now() + timedelta(minutes=self.config.cooldown_minutes)
        
        entry = CooldownEntry(
            signal_id=signal_id,
            strike=strike,
            option_type=option_type,
            direction=direction,
            cooldown_end=cooldown_end,
            reason=reason,
        )
        
        self.cooldowns.append(entry)
        
        # Clean old cooldowns
        self._clean_cooldowns()
    
    def is_in_cooldown(
        self,
        strike: float,
        option_type: str,
    ) -> tuple[bool, Optional[CooldownEntry]]:
        """
        Check if a strike/direction is in cooldown.
        
        Returns:
            Tuple of (is_in_cooldown, cooldown_entry)
        """
        self._clean_cooldowns()
        
        now = datetime.now()
        
        for entry in self.cooldowns:
            # Check if same direction and similar strike (within $2)
            if (entry.option_type == option_type and 
                abs(entry.strike - strike) < 2 and
                entry.cooldown_end > now):
                return True, entry
        
        return False, None
    
    def get_active_cooldowns(self) -> list[CooldownEntry]:
        """Get list of active cooldown entries."""
        self._clean_cooldowns()
        now = datetime.now()
        return [c for c in self.cooldowns if c.cooldown_end > now]
    
    def _clean_cooldowns(self) -> None:
        """Remove expired cooldown entries."""
        now = datetime.now()
        self.cooldowns = [c for c in self.cooldowns if c.cooldown_end > now]
    
    def get_suppressed_by_cooldown(
        self,
        contracts: list,
    ) -> list[tuple]:
        """
        Get list of contracts that should be suppressed due to cooldowns.
        
        Returns:
            List of (contract, reason) tuples
        """
        suppressed = []
        
        for contract in contracts:
            is_cooldown, entry = self.is_in_cooldown(
                contract.strike,
                contract.option_type.value if hasattr(contract.option_type, 'value') else contract.option_type,
            )
            
            if is_cooldown:
                suppressed.append((contract, f"In cooldown until {entry.cooldown_end.strftime('%H:%M')}"))
        
        return suppressed


class SignalDeduplicator:
    """
    Prevents duplicate signals for the same directional thesis.
    """
    
    def __init__(self, same_strike_tolerance: float = 1.0):
        """
        Initialize deduplicator.
        
        Args:
            same_strike_tolerance: Tolerance in dollars for same strike
        """
        self.same_strike_tolerance = same_strike_tolerance
        self.recent_signals: list[dict] = []
        self.max_signal_age_minutes: int = 30
    
    def add_signal(
        self,
        strike: float,
        option_type: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a signal to recent history."""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.recent_signals.append({
            "strike": strike,
            "option_type": option_type,
            "timestamp": timestamp,
        })
        
        self._clean_old_signals()
    
    def is_duplicate(
        self,
        strike: float,
        option_type: str,
    ) -> tuple[bool, Optional[dict]]:
        """
        Check if signal is a duplicate of recent signal.
        
        Returns:
            Tuple of (is_duplicate, matched_signal)
        """
        self._clean_old_signals()
        
        for signal in self.recent_signals:
            if (signal["option_type"] == option_type and 
                abs(signal["strike"] - strike) < self.same_strike_tolerance):
                return True, signal
        
        return False, None
    
    def _clean_old_signals(self) -> None:
        """Remove signals older than max age."""
        cutoff = datetime.now() - timedelta(minutes=self.max_signal_age_minutes)
        self.recent_signals = [
            s for s in self.recent_signals 
            if s["timestamp"] > cutoff
        ]


@dataclass
class TacticalConstraints:
    """Combined tactical constraints container."""
    time_controller: TimeOfDayController
    deduplicator: SignalDeduplicator
    
    # Suppression counts
    suppressed_by_time: int = 0
    suppressed_by_cooldown: int = 0
    suppressed_by_duplicate: int = 0
    suppressed_by_regime: int = 0
    
    def get_suppression_counts(self) -> dict:
        return {
            "by_time": self.suppressed_by_time,
            "by_cooldown": self.suppressed_by_cooldown,
            "by_duplicate": self.suppressed_by_duplicate,
            "by_regime": self.suppressed_by_regime,
            "total": self.suppressed_by_time + self.suppressed_by_cooldown + 
                    self.suppressed_by_duplicate + self.suppressed_by_regime,
        }
    
    def reset_counts(self) -> None:
        """Reset suppression counts."""
        self.suppressed_by_time = 0
        self.suppressed_by_cooldown = 0
        self.suppressed_by_duplicate = 0
        self.suppressed_by_regime = 0


def create_tactical_constraints() -> TacticalConstraints:
    """Factory function to create tactical constraints."""
    return TacticalConstraints(
        time_controller=TimeOfDayController(),
        deduplicator=SignalDeduplicator(),
    )
