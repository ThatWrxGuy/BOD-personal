"""Source Reliability Adjuster.

Adjusts signal influence based on source quality.
"""
from datetime import datetime
from typing import Dict, Optional

from app.signal_calibration.calibration_models import SourceReliabilityScore


class SourceReliabilityAdjuster:
    """Adjusts signal weights based on source reliability."""
    
    # Reliability thresholds
    EXCELLENT_THRESHOLD = 0.95
    GOOD_THRESHOLD = 0.85
    ACCEPTABLE_THRESHOLD = 0.70
    POOR_THRESHOLD = 0.50
    
    def __init__(self):
        self._reliability_cache: Dict[str, SourceReliabilityScore] = {}
    
    def evaluate_source(
        self,
        source_id: str,
        source_type: str,
        uptime_percentage: float = 100.0,
        success_rate: float = 1.0,
        avg_latency_ms: float = 0.0,
        error_count: int = 0,
    ) -> SourceReliabilityScore:
        """Evaluate reliability of a signal source."""
        
        # Calculate reliability score as weighted average
        # Success rate is most important
        reliability_score = (
            success_rate * 0.5 +
            (uptime_percentage / 100.0) * 0.3 +
            max(0, 1.0 - (avg_latency_ms / 10000.0)) * 0.2  # Penalty for high latency
        )
        
        # Ensure bounded
        reliability_score = max(0.0, min(1.0, reliability_score))
        
        # Determine reason
        if reliability_score >= self.EXCELLENT_THRESHOLD:
            reason = f"Excellent source: {success_rate:.0%} success, {uptime_percentage:.0f}% uptime"
        elif reliability_score >= self.GOOD_THRESHOLD:
            reason = f"Good source: {success_rate:.0%} success, {uptime_percentage:.0f}% uptime"
        elif reliability_score >= self.ACCEPTABLE_THRESHOLD:
            reason = f"Acceptable source: {success_rate:.0%} success"
        elif reliability_score >= self.POOR_THRESHOLD:
            reason = f"Poor source: {success_rate:.0%} success, {error_count} errors"
        else:
            reason = f"Unreliable source: {success_rate:.0%} success, {error_count} errors"
        
        return SourceReliabilityScore(
            source_id=source_id,
            source_type=source_type,
            uptime_percentage=uptime_percentage,
            success_rate=success_rate,
            avg_latency_ms=avg_latency_ms,
            error_count=error_count,
            reliability_score=reliability_score,
            last_evaluation=datetime.utcnow(),
            reason=reason,
        )
    
    def get_reliability(
        self,
        source_id: str,
    ) -> Optional[SourceReliabilityScore]:
        """Get cached reliability score for a source."""
        return self._reliability_cache.get(source_id)
    
    def cache_reliability(
        self,
        reliability: SourceReliabilityScore,
    ) -> None:
        """Cache a reliability score."""
        self._reliability_cache[reliability.source_id] = reliability
    
    def get_reliability_for_connector(
        self,
        connector_name: str,
    ) -> SourceReliabilityScore:
        """Get reliability for a known connector."""
        
        # Default reliability scores for known connectors
        # In production, these would come from connector health monitor
        known_connectors = {
            "calendar": (99.0, 0.98, 150.0, 0),
            "finance": (98.0, 0.95, 200.0, 1),
            "tasks": (95.0, 0.90, 250.0, 2),
            "health": (97.0, 0.92, 180.0, 1),
        }
        
        if connector_name in known_connectors:
            uptime, success, latency, errors = known_connectors[connector_name]
            return self.evaluate_source(
                source_id=connector_name,
                source_type=connector_name,
                uptime_percentage=uptime,
                success_rate=success,
                avg_latency_ms=latency,
                error_count=errors,
            )
        
        # Unknown source - use conservative default
        return self.evaluate_source(
            source_id=connector_name,
            source_type="unknown",
            uptime_percentage=80.0,
            success_rate=0.75,
            avg_latency_ms=500.0,
            error_count=3,
        )
    
    def adjust_weight(
        self,
        base_weight: float,
        reliability_score: float,
    ) -> float:
        """Adjust a weight based on source reliability."""
        return base_weight * reliability_score


# Global adjuster instance
_source_reliability_adjuster: Optional[SourceReliabilityAdjuster] = None


def get_source_reliability_adjuster() -> SourceReliabilityAdjuster:
    """Get the global source reliability adjuster instance."""
    global _source_reliability_adjuster
    if _source_reliability_adjuster is None:
        _source_reliability_adjuster = SourceReliabilityAdjuster()
    return _source_reliability_adjuster
