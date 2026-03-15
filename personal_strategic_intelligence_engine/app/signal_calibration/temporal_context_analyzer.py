"""Temporal Context Analyzer.

Analyzes signals within time context to distinguish anomalies from trends.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.signal_calibration.calibration_models import (
    TemporalContext,
    TemporalSignalContext,
)


class TemporalContextAnalyzer:
    """Analyzes temporal context of signals."""
    
    # Time windows for analysis (hours)
    SHORT_TERM_WINDOW = 24       # 1 day
    MEDIUM_TERM_WINDOW = 168     # 1 week
    LONG_TERM_WINDOW = 720       # 1 month
    
    # Trend detection thresholds
    TREND_THRESHOLD = 0.15       # 15% change indicates trend
    SUSTAINED_THRESHOLD = 72     # 72 hours for sustained
    
    def __init__(self):
        self._historical_values: Dict[str, List[float]] = {}
        self._timestamps: Dict[str, List[datetime]] = {}
    
    def record_value(
        self,
        signal_id: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record a signal value for temporal analysis."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if signal_id not in self._historical_values:
            self._historical_values[signal_id] = []
            self._timestamps[signal_id] = []
        
        self._historical_values[signal_id].append(value)
        self._timestamps[signal_id].append(timestamp)
        
        # Keep only last 1000 values
        if len(self._historical_values[signal_id]) > 1000:
            self._historical_values[signal_id] = self._historical_values[signal_id][-1000:]
            self._timestamps[signal_id] = self._timestamps[signal_id][-1000:]
    
    def analyze_context(
        self,
        signal_id: str,
        current_value: float,
    ) -> TemporalSignalContext:
        """Analyze temporal context of a signal."""
        
        values = self._historical_values.get(signal_id, [])
        timestamps = self._timestamps.get(signal_id, [])
        
        if len(values) < 2:
            # Not enough history - treat as anomaly
            return TemporalSignalContext(
                signal_id=signal_id,
                temporal_context=TemporalContext.ANOMALY,
                context_score=0.3,
                is_trend=False,
                trend_duration_hours=0.0,
                vs_historical_avg=0.0,
                vs_short_term_avg=0.0,
                reason="Insufficient history - treated as anomaly",
            )
        
        # Calculate averages
        historical_avg = sum(values) / len(values)
        
        # Short-term average (last 24 hours or last 10 values)
        cutoff_time = datetime.utcnow() - timedelta(hours=self.SHORT_TERM_WINDOW)
        recent_values = []
        for i, ts in enumerate(timestamps):
            if ts >= cutoff_time:
                recent_values.append(values[i])
        
        if recent_values:
            short_term_avg = sum(recent_values) / len(recent_values)
        else:
            short_term_avg = historical_avg
        
        # Compare to averages
        vs_historical = current_value - historical_avg
        vs_short_term = current_value - short_term_avg
        
        # Determine if this is a trend
        is_trend = abs(vs_historical / historical_avg) > self.TREND_THRESHOLD if historical_avg != 0 else False
        
        # Determine temporal context
        if len(values) < 3:
            # Not enough data - could be anomaly or short-term shift
            if abs(vs_short_term) > 0.3:
                temporal_context = TemporalContext.SHORT_TERM_SHIFT
                context_score = 0.6
                reason = "Recent significant change - short-term shift"
            else:
                temporal_context = TemporalContext.ANOMALY
                context_score = 0.3
                reason = "Insufficient data - treated as anomaly"
                
        elif is_trend:
            # Check if sustained
            trend_duration = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
            
            if trend_duration >= self.SUSTAINED_THRESHOLD:
                temporal_context = TemporalContext.SUSTAINED_TREND
                context_score = 0.9
                reason = f"Sustained trend over {trend_duration:.0f} hours"
            else:
                temporal_context = TemporalContext.SHORT_TERM_SHIFT
                context_score = 0.7
                reason = f"Emerging trend over {trend_duration:.0f} hours"
        else:
            # Not a trend - could be structural or anomaly
            if abs(vs_historical) > 0.2:
                temporal_context = TemporalContext.STRUCTURAL
                context_score = 0.8
                reason = "Consistent deviation from historical - structural condition"
            else:
                temporal_context = TemporalContext.ANOMALY
                context_score = 0.4
                reason = "Minor deviation within normal range"
        
        return TemporalSignalContext(
            signal_id=signal_id,
            temporal_context=temporal_context,
            context_score=context_score,
            is_trend=is_trend,
            trend_duration_hours=(timestamps[-1] - timestamps[0]).total_seconds() / 3600 if len(timestamps) > 1 else 0.0,
            vs_historical_avg=vs_historical,
            vs_short_term_avg=vs_short_term,
            reason=reason,
        )
    
    def is_sustained(
        self,
        signal_id: str,
        threshold_hours: float = 72.0,
    ) -> bool:
        """Check if a signal represents a sustained condition."""
        timestamps = self._timestamps.get(signal_id, [])
        
        if len(timestamps) < 2:
            return False
        
        duration_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        return duration_hours >= threshold_hours
    
    def get_trend_direction(
        self,
        signal_id: str,
    ) -> str:
        """Get trend direction for a signal."""
        values = self._historical_values.get(signal_id, [])
        
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first * 1.1:
            return "increasing"
        elif avg_second < avg_first * 0.9:
            return "decreasing"
        else:
            return "stable"


# Global analyzer instance
_temporal_context_analyzer: Optional[TemporalContextAnalyzer] = None


def get_temporal_context_analyzer() -> TemporalContextAnalyzer:
    """Get the global temporal context analyzer instance."""
    global _temporal_context_analyzer
    if _temporal_context_analyzer is None:
        _temporal_context_analyzer = TemporalContextAnalyzer()
    return _temporal_context_analyzer
