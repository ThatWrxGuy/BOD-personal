"""Freshness Evaluator.

Evaluates how recent a signal is relative to expected update cadence.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.signal_calibration.calibration_models import (
    FreshnessLevel,
    SignalFreshnessScore,
)


class FreshnessEvaluator:
    """Evaluates signal freshness."""
    
    # Default expected intervals by domain (seconds)
    DEFAULT_INTERVALS = {
        "calendar": 300,       # 5 minutes
        "finance": 1800,      # 30 minutes
        "tasks": 600,         # 10 minutes
        "health": 3600,      # 60 minutes
        "default": 300,       # 5 minutes default
    }
    
    # Freshness level thresholds (as ratio of age to expected interval)
    FRESH_THRESHOLD = 1.0      # Within expected interval
    AGING_THRESHOLD = 3.0      # Up to 3x expected interval
    STALE_THRESHOLD = 10.0     # Up to 10x expected interval
    
    def __init__(self, custom_intervals: Optional[Dict[str, float]] = None):
        self.intervals = {**self.DEFAULT_INTERVALS}
        if custom_intervals:
            self.intervals.update(custom_intervals)
    
    def evaluate_freshness(
        self,
        signal_id: str,
        signal_type: str,
        last_update: Optional[datetime],
        expected_interval_seconds: Optional[float] = None,
    ) -> SignalFreshnessScore:
        """Evaluate how fresh a signal is."""
        
        # Determine expected interval
        if expected_interval_seconds is None:
            expected_interval_seconds = self._get_expected_interval(signal_type)
        
        # Calculate age
        if last_update is None:
            # No timestamp - treat as expired
            return SignalFreshnessScore(
                signal_id=signal_id,
                signal_type=signal_type,
                freshness_score=0.0,
                freshness_level=FreshnessLevel.EXPIRED,
                expected_update_interval_seconds=expected_interval_seconds,
                reason="No timestamp available - treated as expired",
            )
        
        age_seconds = (datetime.utcnow() - last_update).total_seconds()
        age_ratio = age_seconds / expected_interval_seconds if expected_interval_seconds > 0 else float('inf')
        
        # Determine freshness level and score
        if age_ratio <= self.FRESH_THRESHOLD:
            # Fresh - within expected interval
            freshness_score = 1.0
            freshness_level = FreshnessLevel.FRESH
            reason = f"Signal is fresh ({age_seconds:.0f}s old)"
            
        elif age_ratio <= self.AGING_THRESHOLD:
            # Aging - slightly stale but usable
            freshness_score = 1.0 - ((age_ratio - self.FRESH_THRESHOLD) / 
                                     (self.AGING_THRESHOLD - self.FRESH_THRESHOLD)) * 0.5
            freshness_level = FreshnessLevel.AGING
            reason = f"Signal is aging ({age_ratio:.1f}x expected interval)"
            
        elif age_ratio <= self.STALE_THRESHOLD:
            # Stale - significantly outdated
            freshness_score = 0.5 - ((age_ratio - self.AGING_THRESHOLD) / 
                                    (self.STALE_THRESHOLD - self.AGING_THRESHOLD)) * 0.4
            freshness_level = FreshnessLevel.STALE
            reason = f"Signal is stale ({age_ratio:.1f}x expected interval)"
            
        else:
            # Expired - too old to use
            freshness_score = 0.0
            freshness_level = FreshnessLevel.EXPIRED
            reason = f"Signal is expired ({age_ratio:.1f}x expected interval)"
        
        # Ensure score is bounded
        freshness_score = max(0.0, min(1.0, freshness_score))
        
        return SignalFreshnessScore(
            signal_id=signal_id,
            signal_type=signal_type,
            last_update=last_update,
            age_seconds=age_seconds,
            freshness_score=freshness_score,
            freshness_level=freshness_level,
            expected_update_interval_seconds=expected_interval_seconds,
            reason=reason,
        )
    
    def _get_expected_interval(self, signal_type: str) -> float:
        """Get expected update interval for a signal type."""
        # Try to match by domain/type prefix
        for domain, interval in self.intervals.items():
            if domain in signal_type.lower():
                return interval
        return self.intervals["default"]
    
    def evaluate_batch(
        self,
        signals: list,
    ) -> Dict[str, SignalFreshnessScore]:
        """Evaluate freshness for multiple signals."""
        results = {}
        
        for signal in signals:
            score = self.evaluate_freshness(
                signal_id=signal.get("signal_id", ""),
                signal_type=signal.get("signal_type", ""),
                last_update=signal.get("last_update"),
                expected_interval_seconds=signal.get("expected_interval_seconds"),
            )
            results[score.signal_id] = score
        
        return results


# Global evaluator instance
_freshness_evaluator: Optional[FreshnessEvaluator] = None


def get_freshness_evaluator() -> FreshnessEvaluator:
    """Get the global freshness evaluator instance."""
    global _freshness_evaluator
    if _freshness_evaluator is None:
        _freshness_evaluator = FreshnessEvaluator()
    return _freshness_evaluator
