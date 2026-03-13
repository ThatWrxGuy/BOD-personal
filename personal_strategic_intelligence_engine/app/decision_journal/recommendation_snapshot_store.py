"""Recommendation snapshot store for persisting and querying recommendations."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.decision_journal.journal_models import RecommendationSnapshot

logger = logging.getLogger(__name__)


class RecommendationSnapshotStore:
    """Handles recommendation-level persistence and lookup."""

    def __init__(self):
        # In-memory storage
        self._recommendations: Dict[str, RecommendationSnapshot] = {}  # rec_id -> snapshot
        self._cycle_recommendations: Dict[str, List[str]] = {}  # cycle_id -> [rec_ids]
        self._domain_index: Dict[str, List[str]] = {}  # domain -> [rec_ids]
        self._urgency_index: Dict[str, List[str]] = {}  # urgency -> [rec_ids]
        self._action_index: Dict[str, List[str]] = {}  # action -> [rec_ids]

    def store_recommendation(
        self,
        cycle_id: str,
        recommendation: RecommendationSnapshot
    ) -> bool:
        """Store a recommendation snapshot."""
        try:
            rec_id = recommendation.recommendation_id
            
            # Store
            self._recommendations[rec_id] = recommendation
            
            # Index by cycle
            if cycle_id not in self._cycle_recommendations:
                self._cycle_recommendations[cycle_id] = []
            self._cycle_recommendations[cycle_id].append(rec_id)
            
            # Index by domain
            domain = recommendation.target_domain
            if domain not in self._domain_index:
                self._domain_index[domain] = []
            self._domain_index[domain].append(rec_id)
            
            # Index by urgency
            urgency = recommendation.urgency
            if urgency not in self._urgency_index:
                self._urgency_index[urgency] = []
            self._urgency_index[urgency].append(rec_id)
            
            # Index by action
            action = recommendation.action
            if action not in self._action_index:
                self._action_index[action] = []
            self._action_index[action].append(rec_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store recommendation: {e}")
            return False

    def store_batch(
        self,
        cycle_id: str,
        recommendations: List[RecommendationSnapshot]
    ) -> int:
        """Store multiple recommendations."""
        count = 0
        for rec in recommendations:
            if self.store_recommendation(cycle_id, rec):
                count += 1
        return count

    def get_recommendation(self, recommendation_id: str) -> Optional[RecommendationSnapshot]:
        """Get a recommendation by ID."""
        return self._recommendations.get(recommendation_id)

    def get_recommendations_for_cycle(self, cycle_id: str) -> List[RecommendationSnapshot]:
        """Get all recommendations for a cycle."""
        rec_ids = self._cycle_recommendations.get(cycle_id, [])
        return [self._recommendations[rid] for rid in rec_ids if rid in self._recommendations]

    def find_by_domain(self, domain: str, limit: int = 100) -> List[RecommendationSnapshot]:
        """Find recommendations by domain."""
        rec_ids = self._domain_index.get(domain, [])
        recs = [self._recommendations[rid] for rid in rec_ids if rid in self._recommendations]
        return recs[:limit]

    def find_by_urgency(self, urgency: str, limit: int = 100) -> List[RecommendationSnapshot]:
        """Find recommendations by urgency level."""
        rec_ids = self._urgency_index.get(urgency, [])
        recs = [self._recommendations[rid] for rid in rec_ids if rid in self._recommendations]
        return recs[:limit]

    def find_by_confidence_band(
        self,
        min_confidence: float,
        max_confidence: float,
        limit: int = 100
    ) -> List[RecommendationSnapshot]:
        """Find recommendations by confidence band."""
        recs = [
            r for r in self._recommendations.values()
            if min_confidence <= r.confidence <= max_confidence
        ]
        return recs[:limit]

    def find_by_action(self, action: str, limit: int = 100) -> List[RecommendationSnapshot]:
        """Find recommendations by action type."""
        rec_ids = self._action_index.get(action, [])
        recs = [self._recommendations[rid] for rid in rec_ids if rid in self._recommendations]
        return recs[:limit]

    def find_blocked_recommendations(self, limit: int = 100) -> List[RecommendationSnapshot]:
        """Find blocked recommendations."""
        recs = [r for r in self._recommendations.values() if r.is_blocked]
        return recs[:limit]

    def find_active_recommendations(self, limit: int = 100) -> List[RecommendationSnapshot]:
        """Find non-blocked recommendations."""
        recs = [r for r in self._recommendations.values() if not r.is_blocked]
        return recs[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get recommendation store statistics."""
        return {
            "total_recommendations": len(self._recommendations),
            "cycles_stored": len(self._cycle_recommendations),
            "domains_indexed": len(self._domain_index),
            "blocked_count": sum(1 for r in self._recommendations.values() if r.is_blocked),
            "avg_confidence": sum(r.confidence for r in self._recommendations.values()) / max(1, len(self._recommendations)),
        }

    def clear(self):
        """Clear all stored data."""
        self._recommendations.clear()
        self._cycle_recommendations.clear()
        self._domain_index.clear()
        self._urgency_index.clear()
        self._action_index.clear()


# Global store instance
_store: Optional[RecommendationSnapshotStore] = None


def get_recommendation_snapshot_store() -> RecommendationSnapshotStore:
    """Get the global recommendation snapshot store instance."""
    global _store
    if _store is None:
        _store = RecommendationSnapshotStore()
    return _store
