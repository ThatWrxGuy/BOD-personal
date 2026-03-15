"""Persistence Tracker.

Tracks whether signals represent transient or sustained conditions.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.signal_calibration.calibration_models import (
    PersistenceLevel,
    SignalPersistenceProfile,
)


class PersistenceTracker:
    """Tracks signal persistence patterns."""
    
    # Thresholds for persistence classification
    TRANSIENT_THRESHOLD = 1       # 1 occurrence
    EMERGING_THRESHOLD = 3       # 2-3 occurrences
    PERSISTENT_THRESHOLD = 7     # 4-7 occurrences
    CHRONIC_THRESHOLD = 14       # 8+ occurrences
    
    # Persistence scoring weights
    TRANSIENT_SCORE = 0.2
    EMERGING_SCORE = 0.5
    PERSISTENT_SCORE = 0.8
    CHRONIC_SCORE = 1.0
    
    def __init__(self):
        self._signal_history: Dict[str, List[datetime]] = {}
        self._persistence_cache: Dict[str, SignalPersistenceProfile] = {}
    
    def record_signal(
        self,
        signal_id: str,
        signal_type: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record a signal occurrence."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if signal_id not in self._signal_history:
            self._signal_history[signal_id] = []
        
        self._signal_history[signal_id].append(timestamp)
        
        # Invalidate cache
        self._persistence_cache.pop(signal_id, None)
    
    def evaluate_persistence(
        self,
        signal_id: str,
        signal_type: str,
        current_value: float = 0.0,
        history: Optional[List[datetime]] = None,
    ) -> SignalPersistenceProfile:
        """Evaluate how persistent a signal is."""
        
        # Use provided history or cached
        if history is not None:
            occurrences = len(history)
            timestamps = history
        else:
            timestamps = self._signal_history.get(signal_id, [])
            occurrences = len(timestamps)
        
        # Determine classification
        if occurrences <= self.TRANSIENT_THRESHOLD:
            persistence_level = PersistenceLevel.TRANSIENT
            persistence_score = self.TRANSIENT_SCORE
            reason = "Single occurrence - treated as transient event"
            
        elif occurrences <= self.EMERGING_THRESHOLD:
            persistence_level = PersistenceLevel.EMERGING
            persistence_score = self.EMERGING_SCORE
            reason = f"Recent occurrence ({occurrences} times) - emerging pattern"
            
        elif occurrences <= self.PERSISTENT_THRESHOLD:
            persistence_level = PersistenceLevel.PERSISTENT
            persistence_score = self.PERSISTENT_SCORE
            reason = f"Sustained pattern ({occurrences} occurrences) - persistent condition"
            
        else:
            persistence_level = PersistenceLevel.CHRONIC
            persistence_score = self.CHRONIC_SCORE
            reason = f"Chronic condition ({occurrences} occurrences) - long-standing issue"
        
        # Calculate trend
        trend_direction, trend_magnitude = self._calculate_trend(timestamps, current_value)
        
        # Get first and last seen
        first_seen = min(timestamps) if timestamps else None
        last_seen = max(timestamps) if timestamps else None
        
        return SignalPersistenceProfile(
            signal_id=signal_id,
            signal_type=signal_type,
            occurrences=occurrences,
            first_seen=first_seen,
            last_seen=last_seen,
            persistence_level=persistence_level,
            persistence_score=persistence_score,
            trend_direction=trend_direction,
            trend_magnitude=trend_magnitude,
            reason=reason,
        )
    
    def _calculate_trend(
        self,
        timestamps: List[datetime],
        current_value: float,
    ) -> tuple:
        """Calculate trend direction and magnitude."""
        
        if len(timestamps) < 2:
            return "stable", 0.0
        
        # Simple trend based on time between occurrences
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            time_diffs.append(diff)
        
        avg_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        
        # If signals are coming more frequently, trend is increasing
        if avg_diff < 3600:  # Less than 1 hour
            return "increasing", 0.7
        elif avg_diff < 86400:  # Less than 1 day
            return "stable", 0.3
        else:
            return "decreasing", 0.2
    
    def is_persistent(
        self,
        signal_id: str,
        threshold: PersistenceLevel = PersistenceLevel.PERSISTENT,
    ) -> bool:
        """Check if a signal meets persistence threshold."""
        profile = self._persistence_cache.get(signal_id)
        
        if profile is None:
            # Need to evaluate first
            return False
        
        # Check if level meets threshold
        level_order = [
            PersistenceLevel.TRANSIENT,
            PersistenceLevel.EMERGING,
            PersistenceLevel.PERSISTENT,
            PersistenceLevel.CHRONIC,
        ]
        
        try:
            current_idx = level_order.index(profile.persistence_level)
            threshold_idx = level_order.index(threshold)
            return current_idx >= threshold_idx
        except ValueError:
            return False
    
    def get_persistence_summary(
        self,
        signals: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """Get summary of persistence levels for a set of signals."""
        summary = {
            "transient": 0,
            "emerging": 0,
            "persistent": 0,
            "chronic": 0,
        }
        
        for signal in signals:
            signal_id = signal.get("signal_id", "")
            signal_type = signal.get("signal_type", "")
            
            profile = self.evaluate_persistence(signal_id, signal_type)
            summary[profile.persistence_level.value] += 1
        
        return summary
    
    def clear_history(self, signal_id: Optional[str] = None) -> None:
        """Clear signal history."""
        if signal_id:
            self._signal_history.pop(signal_id, None)
            self._persistence_cache.pop(signal_id, None)
        else:
            self._signal_history.clear()
            self._persistence_cache.clear()


# Global tracker instance
_persistence_tracker: Optional[PersistenceTracker] = None


def get_persistence_tracker() -> PersistenceTracker:
    """Get the global persistence tracker instance."""
    global _persistence_tracker
    if _persistence_tracker is None:
        _persistence_tracker = PersistenceTracker()
    return _persistence_tracker
