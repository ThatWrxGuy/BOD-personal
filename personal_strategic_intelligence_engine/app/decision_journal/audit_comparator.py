"""Audit comparator for comparing historical and replayed outputs."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.decision_journal.journal_models import (
    AuditComparisonResult,
    DecisionCycleSnapshot,
    DriftClassification,
    RecommendationSnapshot,
)

logger = logging.getLogger(__name__)


class AuditComparator:
    """Compares historical and replayed outputs for auditability and regression analysis."""

    def __init__(self):
        self._comparison_history: List[AuditComparisonResult] = []

    def compare_cycles(
        self,
        original: DecisionCycleSnapshot,
        replayed: DecisionCycleSnapshot,
    ) -> AuditComparisonResult:
        """Compare two decision cycles."""
        
        comparison = AuditComparisonResult(
            cycle_id=original.cycle_id,
            compared_timestamp=datetime.utcnow(),
        )

        # Compare recommendation counts
        comparison.recommendation_count_delta = (
            len(replayed.recommendations) - len(original.recommendations)
        )

        # Compare recommendations
        self._compare_recommendations(
            original.recommendations,
            replayed.recommendations,
            comparison
        )

        # Compare conflicts
        self._compare_conflicts(
            original.detected_conflicts,
            replayed.detected_conflicts,
            comparison
        )

        # Classify drift
        comparison.drift_classification = self._classify_drift(comparison)

        # Store comparison
        self._comparison_history.append(comparison)

        return comparison

    def compare_recommendation_sets(
        self,
        original: List[RecommendationSnapshot],
        replayed: List[RecommendationSnapshot],
    ) -> AuditComparisonResult:
        """Compare just recommendation sets."""
        
        comparison = AuditComparisonResult(
            cycle_id="manual_comparison",
            compared_timestamp=datetime.utcnow(),
        )

        comparison.recommendation_count_delta = len(replayed) - len(original)
        self._compare_recommendations(original, replayed, comparison)
        comparison.drift_classification = self._classify_drift(comparison)

        return comparison

    def _compare_recommendations(
        self,
        original: List[RecommendationSnapshot],
        replayed: List[RecommendationSnapshot],
        comparison: AuditComparisonResult
    ):
        """Compare recommendation details."""
        
        # Build lookup by domain
        orig_by_domain = {r.target_domain: r for r in original}
        repl_by_domain = {r.target_domain: r for r in replayed}

        all_domains = set(list(orig_by_domain.keys()) + list(repl_by_domain.keys()))

        for domain in all_domains:
            orig = orig_by_domain.get(domain)
            repl = repl_by_domain.get(domain)

            if orig and repl:
                # Compare priority
                if orig.priority != repl.priority:
                    comparison.priority_differences.append({
                        "domain": domain,
                        "original_priority": orig.priority,
                        "replayed_priority": repl.priority,
                        "difference": repl.priority - orig.priority,
                    })

                # Compare confidence
                confidence_delta = repl.confidence - orig.confidence
                if abs(confidence_delta) > 0.05:
                    comparison.confidence_differences.append({
                        "domain": domain,
                        "original_confidence": orig.confidence,
                        "replayed_confidence": repl.confidence,
                        "delta": confidence_delta,
                    })

            elif orig and not repl:
                comparison.priority_differences.append({
                    "domain": domain,
                    "original_priority": orig.priority,
                    "replayed_priority": None,
                    "note": "Recommendation missing in replay",
                })

            elif not orig and repl:
                comparison.priority_differences.append({
                    "domain": domain,
                    "original_priority": None,
                    "replayed_priority": repl.priority,
                    "note": "New recommendation in replay",
                })

    def _compare_conflicts(
        self,
        original: List,
        replayed: List,
        comparison: AuditComparisonResult
    ):
        """Compare detected conflicts."""
        
        orig_types = set(c.conflict_type for c in original) if original else set()
        repl_types = set(c.conflict_type for c in replayed) if replayed else set()

        added = repl_types - orig_types
        removed = orig_types - repl_types

        if added or removed:
            comparison.conflict_differences = []
            
            for t in added:
                comparison.conflict_differences.append({
                    "type": t,
                    "change": "added_in_replay",
                })
            
            for t in removed:
                comparison.conflict_differences.append({
                    "type": t,
                    "change": "removed_in_replay",
                })

    def _classify_drift(
        self,
        comparison: AuditComparisonResult
    ) -> DriftClassification:
        """Classify the level of behavioral drift."""
        
        # Count significant differences
        sig_confidence = len([
            d for d in comparison.confidence_differences
            if abs(d.get("delta", 0)) > 0.2
        ])
        
        sig_priority = len(comparison.priority_differences)
        sig_conflicts = len(comparison.conflict_differences)

        # Classification logic
        if sig_confidence == 0 and sig_priority == 0 and sig_conflicts == 0:
            return DriftClassification.NONE
        elif sig_confidence <= 1 and sig_priority <= 1 and sig_conflicts == 0:
            return DriftClassification.MINOR
        elif sig_confidence <= 2 and sig_priority <= 2 and sig_conflicts <= 1:
            return DriftClassification.MODERATE
        else:
            return DriftClassification.SIGNIFICANT

    def get_comparison_history(
        self,
        limit: int = 100
    ) -> List[AuditComparisonResult]:
        """Get recent comparison results."""
        return self._comparison_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get comparator statistics."""
        if not self._comparison_history:
            return {
                "total_comparisons": 0,
                "drift_distribution": {},
            }

        drift_counts = {}
        for c in self._comparison_history:
            drift = c.drift_classification.value
            drift_counts[drift] = drift_counts.get(drift, 0) + 1

        return {
            "total_comparisons": len(self._comparison_history),
            "drift_distribution": drift_counts,
        }


# Global comparator instance
_comparator: Optional[AuditComparator] = None


def get_audit_comparator() -> AuditComparator:
    """Get the global audit comparator instance."""
    global _comparator
    if _comparator is None:
        _comparator = AuditComparator()
    return _comparator
