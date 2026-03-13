"""Audit store - persistent storage for execution audit data."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_audit.outcome_models import (
    ExecutionOutcomeSnapshot,
    OutcomeEvaluation,
    ExecutionReliabilityScore,
    ApprovalPolicyRecommendation,
)

logger = logging.getLogger(__name__)


class AuditStore:
    """Stores execution audit data."""

    def __init__(self):
        self._snapshots: Dict[str, ExecutionOutcomeSnapshot] = {}
        self._evaluations: Dict[str, OutcomeEvaluation] = {}
        self._reliability_scores: Dict[str, ExecutionReliabilityScore] = {}
        self._policy_recommendations: Dict[str, ApprovalPolicyRecommendation] = {}

    # Snapshot methods
    def store_snapshot(self, snapshot: ExecutionOutcomeSnapshot) -> bool:
        """Store an outcome snapshot."""
        try:
            self._snapshots[snapshot.snapshot_id] = snapshot
            logger.info(f"Stored snapshot: {snapshot.snapshot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store snapshot: {e}")
            return False

    def get_snapshot(self, snapshot_id: str) -> Optional[ExecutionOutcomeSnapshot]:
        """Get a snapshot by ID."""
        return self._snapshots.get(snapshot_id)

    def get_all_snapshots(self) -> List[ExecutionOutcomeSnapshot]:
        """Get all snapshots."""
        return list(self._snapshots.values())

    # Evaluation methods
    def store_evaluation(self, evaluation: OutcomeEvaluation) -> bool:
        """Store an outcome evaluation."""
        try:
            self._evaluations[evaluation.evaluation_id] = evaluation
            logger.info(f"Stored evaluation: {evaluation.evaluation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store evaluation: {e}")
            return False

    def get_evaluation(self, evaluation_id: str) -> Optional[OutcomeEvaluation]:
        """Get an evaluation by ID."""
        return self._evaluations.get(evaluation_id)

    def get_evaluations_by_snapshot(self, snapshot_id: str) -> List[OutcomeEvaluation]:
        """Get evaluations for a snapshot."""
        return [e for e in self._evaluations.values() if e.snapshot_id == snapshot_id]

    # Reliability score methods
    def store_reliability_score(self, score: ExecutionReliabilityScore) -> bool:
        """Store a reliability score."""
        try:
            key = f"{score.action_type}:{score.domain}"
            self._reliability_scores[key] = score
            logger.info(f"Stored reliability score: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store reliability score: {e}")
            return False

    def get_reliability_score(self, action_type: str, domain: str) -> Optional[ExecutionReliabilityScore]:
        """Get reliability score for an action type and domain."""
        key = f"{action_type}:{domain}"
        return self._reliability_scores.get(key)

    def get_all_reliability_scores(self) -> List[ExecutionReliabilityScore]:
        """Get all reliability scores."""
        return list(self._reliability_scores.values())

    # Policy recommendation methods
    def store_policy_recommendation(self, recommendation: ApprovalPolicyRecommendation) -> bool:
        """Store a policy recommendation."""
        try:
            key = f"{recommendation.action_type}:{recommendation.domain}"
            self._policy_recommendations[key] = recommendation
            logger.info(f"Stored policy recommendation: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store policy recommendation: {e}")
            return False

    def get_policy_recommendation(self, action_type: str, domain: str) -> Optional[ApprovalPolicyRecommendation]:
        """Get policy recommendation for an action type and domain."""
        key = f"{action_type}:{domain}"
        return self._policy_recommendations.get(key)

    def get_all_policy_recommendations(self) -> List[ApprovalPolicyRecommendation]:
        """Get all policy recommendations."""
        return list(self._policy_recommendations.values())

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "snapshots": len(self._snapshots),
            "evaluations": len(self._evaluations),
            "reliability_scores": len(self._reliability_scores),
            "policy_recommendations": len(self._policy_recommendations),
        }

    def clear(self):
        """Clear all stored data."""
        self._snapshots.clear()
        self._evaluations.clear()
        self._reliability_scores.clear()
        self._policy_recommendations.clear()


# Global store instance
_store: Optional["AuditStore"] = None


def get_audit_store() -> AuditStore:
    """Get the global audit store instance."""
    global _store
    if _store is None:
        _store = AuditStore()
    return _store
