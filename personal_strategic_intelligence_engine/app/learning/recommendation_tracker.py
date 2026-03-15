"""Recommendation tracker for managing recommendation lifecycles."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.learning.outcome_models import (
    LifecycleStatus,
    RecommendationOutcomeRecord,
    ObservationWindow,
)

logger = logging.getLogger(__name__)


class RecommendationTracker:
    """Tracks recommendation lifecycle states."""

    def __init__(self):
        # In-memory storage
        self._recommendations: Dict[str, RecommendationOutcomeRecord] = {}
        self._cycle_recommendations: Dict[str, List[str]] = {}  # cycle_id -> [rec_ids]
        self._domain_index: Dict[str, List[str]] = {}  # domain -> [rec_ids]

    def register_recommendation(
        self,
        recommendation_id: str,
        cycle_id: str,
        target_domain: str,
        action: str,
        issued_timestamp: datetime,
        baseline_state: Dict[str, Any] = None,
    ) -> bool:
        """Register a newly issued recommendation."""
        try:
            record = RecommendationOutcomeRecord(
                recommendation_id=recommendation_id,
                cycle_id=cycle_id,
                target_domain=target_domain,
                action=action,
                issued_timestamp=issued_timestamp,
                baseline_state=baseline_state or {},
                lifecycle_status=LifecycleStatus.ISSUED,
            )

            # Store
            self._recommendations[recommendation_id] = record

            # Index by cycle
            if cycle_id not in self._cycle_recommendations:
                self._cycle_recommendations[cycle_id] = []
            self._cycle_recommendations[cycle_id].append(recommendation_id)

            # Index by domain
            if target_domain not in self._domain_index:
                self._domain_index[target_domain] = []
            self._domain_index[target_domain].append(recommendation_id)

            logger.info(f"Registered recommendation: {recommendation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register recommendation: {e}")
            return False

    def update_status(
        self,
        recommendation_id: str,
        status: LifecycleStatus,
    ) -> bool:
        """Update the lifecycle status of a recommendation."""
        if recommendation_id not in self._recommendations:
            return False

        self._recommendations[recommendation_id].lifecycle_status = status
        logger.info(f"Updated status for {recommendation_id}: {status.value}")
        return True

    def add_followup_signals(
        self,
        recommendation_id: str,
        signals: List[Dict[str, Any]],
    ) -> bool:
        """Add follow-up signals to a recommendation."""
        if recommendation_id not in self._recommendations:
            return False

        record = self._recommendations[recommendation_id]
        record.followup_signals.extend(signals)

        # Update status to observed
        if record.lifecycle_status == LifecycleStatus.ISSUED:
            record.lifecycle_status = LifecycleStatus.OBSERVED

        return True

    def set_observation_window(
        self,
        recommendation_id: str,
        window: ObservationWindow,
    ) -> bool:
        """Set the observation window for a recommendation."""
        if recommendation_id not in self._recommendations:
            return False

        self._recommendations[recommendation_id].observation_window = window
        return True

    def get_recommendation(self, recommendation_id: str) -> Optional[RecommendationOutcomeRecord]:
        """Get a recommendation record by ID."""
        return self._recommendations.get(recommendation_id)

    def get_recommendations_for_cycle(self, cycle_id: str) -> List[RecommendationOutcomeRecord]:
        """Get all recommendations for a cycle."""
        rec_ids = self._cycle_recommendations.get(cycle_id, [])
        return [self._recommendations[rid] for rid in rec_ids if rid in self._recommendations]

    def get_recommendations_by_domain(self, domain: str) -> List[RecommendationOutcomeRecord]:
        """Get all recommendations for a domain."""
        rec_ids = self._domain_index.get(domain, [])
        return [self._recommendations[rid] for rid in rec_ids if rid in self._recommendations]

    def get_recommendations_by_status(
        self,
        status: LifecycleStatus,
        limit: int = 100
    ) -> List[RecommendationOutcomeRecord]:
        """Get recommendations by lifecycle status."""
        recs = [r for r in self._recommendations.values() if r.lifecycle_status == status]
        # Sort by issued timestamp
        recs.sort(key=lambda r: r.issued_timestamp, reverse=True)
        return recs[:limit]

    def get_pending_evaluations(
        self,
        max_age_hours: int = 168
    ) -> List[RecommendationOutcomeRecord]:
        """Get recommendations pending outcome evaluation."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        recs = [
            r for r in self._recommendations.values()
            if r.lifecycle_status in [LifecycleStatus.ISSUED, LifecycleStatus.OBSERVED]
            and r.issued_timestamp < cutoff
        ]
        return recs

    def get_statistics(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        status_counts = {}
        for rec in self._recommendations.values():
            status = rec.lifecycle_status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_recommendations": len(self._recommendations),
            "status_distribution": status_counts,
            "domains_tracked": len(self._domain_index),
        }

    def clear(self):
        """Clear all tracked data."""
        self._recommendations.clear()
        self._cycle_recommendations.clear()
        self._domain_index.clear()


# Global tracker instance
_tracker: Optional[RecommendationTracker] = None


def get_recommendation_tracker() -> RecommendationTracker:
    """Get the global recommendation tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = RecommendationTracker()
    return _tracker
