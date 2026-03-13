"""Outcome evaluator for assessing recommendation outcomes."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning.outcome_models import (
    OutcomeQuality,
    OutcomeEvaluationResult,
    LifecycleStatus,
)

logger = logging.getLogger(__name__)


class OutcomeEvaluator:
    """Evaluates recommendation outcomes."""

    # Thresholds for determining outcome quality
    IMPROVEMENT_THRESHOLD = 0.1  # 10% improvement
    DETERIORATION_THRESHOLD = -0.1  # 10% deterioration
    MIN_EVIDENCE_COUNT = 1  # Minimum signals needed

    def __init__(self):
        self._evaluation_cache: Dict[str, OutcomeEvaluationResult] = {}

    def evaluate_outcome(
        self,
        recommendation_id: str,
        lifecycle_status: LifecycleStatus,
        baseline_state: Dict[str, Any],
        followup_state: Dict[str, Any],
        evidence_summary: Dict[str, Any],
    ) -> OutcomeEvaluationResult:
        """Evaluate the outcome of a recommendation."""
        
        # Determine outcome quality based on status
        if lifecycle_status in [LifecycleStatus.BLOCKED, LifecycleStatus.IGNORED]:
            outcome_quality = OutcomeQuality.INSUFFICIENT_EVIDENCE
            rationale = f"Recommendation was {lifecycle_status.value}"
            confidence = 0.3
            
            return OutcomeEvaluationResult(
                recommendation_id=recommendation_id,
                cycle_id="",
                outcome_quality=outcome_quality,
                evidence_summary=evidence_summary,
                magnitude_of_change=0.0,
                direction="neutral",
                confidence_in_evaluation=confidence,
                evaluation_rationale=rationale,
            )

        # If no followup state, insufficient evidence
        if not followup_state:
            return OutcomeEvaluationResult(
                recommendation_id=recommendation_id,
                cycle_id="",
                outcome_quality=OutcomeQuality.INSUFFICIENT_EVIDENCE,
                evidence_summary=evidence_summary,
                magnitude_of_change=0.0,
                direction="neutral",
                confidence_in_evaluation=0.2,
                evaluation_rationale="No follow-up signals available for evaluation",
            )

        # Calculate changes
        changes = self._calculate_changes(baseline_state, followup_state)
        
        if not changes:
            return OutcomeEvaluationResult(
                recommendation_id=recommendation_id,
                cycle_id="",
                outcome_quality=OutcomeQuality.INSUFFICIENT_EVIDENCE,
                evidence_summary=evidence_summary,
                magnitude_of_change=0.0,
                direction="neutral",
                confidence_in_evaluation=0.2,
                evaluation_rationale="No comparable metrics found for evaluation",
            )

        # Determine outcome quality
        outcome_quality, direction, rationale = self._determine_outcome_quality(
            changes, evidence_summary
        )

        # Calculate magnitude
        magnitude = self._calculate_magnitude(changes)

        # Calculate confidence based on evidence
        confidence = self._calculate_confidence(evidence_summary, changes)

        result = OutcomeEvaluationResult(
            recommendation_id=recommendation_id,
            cycle_id="",
            outcome_quality=outcome_quality,
            evidence_summary=evidence_summary,
            magnitude_of_change=magnitude,
            direction=direction,
            confidence_in_evaluation=confidence,
            evaluation_rationale=rationale,
        )

        # Cache result
        self._evaluation_cache[recommendation_id] = result

        return result

    def _calculate_changes(
        self,
        baseline: Dict[str, Any],
        followup: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate changes between baseline and follow-up."""
        changes = {}
        
        # Key metrics to compare
        metrics = ["performance_score", "risk_score", "opportunity_score", 
                   "momentum_score", "composite_score"]
        
        for metric in metrics:
            if metric in baseline and metric in followup:
                baseline_val = baseline[metric]
                followup_val = followup[metric]
                
                if isinstance(baseline_val, (int, float)) and isinstance(followup_val, (int, float)):
                    changes[metric] = followup_val - baseline_val
        
        return changes

    def _determine_outcome_quality(
        self,
        changes: Dict[str, float],
        evidence_summary: Dict[str, Any]
    ) -> tuple[OutcomeQuality, str, str]:
        """Determine the quality of the outcome."""
        
        if not changes:
            return (
                OutcomeQuality.INSUFFICIENT_EVIDENCE,
                "neutral",
                "No measurable changes detected"
            )

        # Count positive and negative changes
        positive = sum(1 for v in changes.values() if v > self.IMPROVEMENT_THRESHOLD)
        negative = sum(1 for v in changes.values() if v < self.DETERIORATION_THRESHOLD)
        total = len(changes)

        # Determine outcome based on changes
        if positive >= total * 0.6:  # 60%+ positive
            if negative == 0:
                return (
                    OutcomeQuality.IMPROVEMENT,
                    "positive",
                    f"{positive}/{total} metrics improved"
                )
            else:
                return (
                    OutcomeQuality.MIXED,
                    "mixed",
                    f"{positive} improved, {negative} deteriorated"
                )
        
        elif negative >= total * 0.6:  # 60%+ negative
            if positive == 0:
                return (
                    OutcomeQuality.DETERIORATION,
                    "negative",
                    f"{negative}/{total} metrics deteriorated"
                )
            else:
                return (
                    OutcomeQuality.MIXED,
                    "mixed",
                    f"{positive} improved, {negative} deteriorated"
                )
        
        else:
            # Check signal count
            signal_count = evidence_summary.get("signal_count", 0)
            if signal_count < self.MIN_EVIDENCE_COUNT:
                return (
                    OutcomeQuality.INSUFFICIENT_EVIDENCE,
                    "neutral",
                    f"Insufficient evidence (only {signal_count} signals)"
                )
            
            return (
                OutcomeQuality.NO_CHANGE,
                "neutral",
                f"No meaningful change in {total} metrics"
            )

    def _calculate_magnitude(self, changes: Dict[str, float]) -> float:
        """Calculate the magnitude of changes."""
        if not changes:
            return 0.0
        
        # Average absolute change
        avg_change = sum(abs(v) for v in changes.values()) / len(changes)
        
        # Normalize to -1 to 1 scale
        return max(-1.0, min(1.0, avg_change / 5.0))

    def _calculate_confidence(
        self,
        evidence_summary: Dict[str, Any],
        changes: Dict[str, float]
    ) -> float:
        """Calculate confidence in the evaluation."""
        
        # Base confidence from signal count
        signal_count = evidence_summary.get("signal_count", 0)
        signal_factor = min(0.5, signal_count * 0.1)
        
        # Confidence from number of metrics changed
        metrics_factor = min(0.3, len(changes) * 0.05)
        
        # Base confidence
        base = 0.2
        
        return min(0.9, base + signal_factor + metrics_factor)

    def evaluate_batch(
        self,
        evaluations: List[Dict[str, Any]]
    ) -> List[OutcomeEvaluationResult]:
        """Evaluate a batch of outcomes."""
        
        results = []
        
        for eval_data in evaluations:
            result = self.evaluate_outcome(
                recommendation_id=eval_data.get("recommendation_id", ""),
                lifecycle_status=eval_data.get("lifecycle_status", LifecycleStatus.ISSUED),
                baseline_state=eval_data.get("baseline_state", {}),
                followup_state=eval_data.get("followup_state", {}),
                evidence_summary=eval_data.get("evidence_summary", {}),
            )
            results.append(result)
        
        return results


# Global evaluator instance
_evaluator: Optional[OutcomeEvaluator] = None


def get_outcome_evaluator() -> OutcomeEvaluator:
    """Get the global outcome evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = OutcomeEvaluator()
    return _evaluator
