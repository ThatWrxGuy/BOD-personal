"""Execution outcome evaluator - evaluates outcome effectiveness."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_audit.outcome_models import (
    ExecutionOutcomeSnapshot,
    OutcomeEvaluation,
    OutcomeCategory,
)

logger = logging.getLogger(__name__)


class OutcomeEvaluator:
    """Evaluates execution outcomes."""

    def __init__(self):
        self._min_change_threshold = 0.05  # Minimum change to consider meaningful

    def evaluate(
        self,
        snapshot: ExecutionOutcomeSnapshot,
    ) -> OutcomeEvaluation:
        """
        Evaluate an execution outcome.
        
        Args:
            snapshot: The outcome snapshot to evaluate
            
        Returns:
            OutcomeEvaluation with category and score
        """
        # Handle errors
        if snapshot.error_message:
            return self._create_error_evaluation(
                snapshot.snapshot_id,
                snapshot.error_message,
            )
        
        # Compare states
        comparison = self._compare_states(
            snapshot.pre_execution_state,
            snapshot.post_execution_state,
        )
        
        # Determine category
        category, score, metrics = self._determine_outcome(comparison)
        
        # Build evaluation
        evaluation = OutcomeEvaluation(
            snapshot_id=snapshot.snapshot_id,
            category=category,
            score=score,
            metrics_improved=metrics["improved"],
            metrics_deteriorated=metrics["deteriorated"],
            metrics_unchanged=metrics["unchanged"],
            confidence=self._calculate_confidence(snapshot),
            rationale=self._build_rationale(category, metrics),
        )
        
        logger.info(f"Evaluated outcome {snapshot.snapshot_id}: {category.value} (score={score:.2f})")
        
        return evaluation

    def _compare_states(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> Dict[str, Dict[str, float]]:
        """Compare pre and post execution states."""
        results = {}
        
        # Get all keys
        all_keys = set(pre.keys()) | set(post.keys())
        
        for key in all_keys:
            pre_val = pre.get(key)
            post_val = post.get(key)
            
            if pre_val is None or post_val is None:
                continue
            
            # Try to get numeric values
            try:
                pre_num = float(pre_val)
                post_num = float(post_val)
                
                change = post_num - pre_num
                percent_change = (change / pre_num) if pre_num != 0 else 0
                
                results[key] = {
                    "pre": pre_num,
                    "post": post_num,
                    "change": change,
                    "percent_change": percent_change,
                }
            except (TypeError, ValueError):
                # Non-numeric values - skip
                continue
        
        return results

    def _determine_outcome(
        self,
        comparison: Dict[str, Dict[str, float]],
    ) -> tuple:
        """Determine outcome category and score."""
        
        if not comparison:
            return OutcomeCategory.UNKNOWN, 0.0, {
                "improved": [],
                "deteriorated": [],
                "unchanged": [],
            }
        
        improved = []
        deteriorated = []
        unchanged = []
        
        for key, values in comparison.items():
            change = values.get("change", 0)
            abs_change = abs(change)
            
            if abs_change < self._min_change_threshold:
                unchanged.append(key)
            elif change > 0:
                improved.append(key)
            else:
                deteriorated.append(key)
        
        # Determine category
        total = len(comparison)
        
        if len(improved) > 0 and len(deteriorated) == 0:
            if len(improved) == total:
                category = OutcomeCategory.IMPROVEMENT
                score = sum(comparison[k]["percent_change"] for k in improved) / total
            else:
                category = OutcomeCategory.MIXED
                score = 0.2
        elif len(deteriorated) > 0 and len(improved) == 0:
            if len(deteriorated) == total:
                category = OutcomeCategory.DETERIORATION
                score = sum(comparison[k]["percent_change"] for k in deteriorated) / total
            else:
                category = OutcomeCategory.MIXED
                score = -0.2
        elif len(improved) > 0 and len(deteriorated) > 0:
            category = OutcomeCategory.MIXED
            score = (len(improved) - len(deteriorated)) / total * 0.5
        else:
            category = OutcomeCategory.NO_CHANGE
            score = 0.0
        
        # Clamp score
        score = max(-1.0, min(1.0, score))
        
        return category, score, {
            "improved": improved,
            "deteriorated": deteriorated,
            "unchanged": unchanged,
        }

    def _calculate_confidence(self, snapshot: ExecutionOutcomeSnapshot) -> float:
        """Calculate confidence in the evaluation."""
        
        confidence = 0.5  # Base
        
        # Boost from having state data
        if snapshot.pre_execution_state and snapshot.post_execution_state:
            confidence += 0.2
        
        # Boost from having signals
        if snapshot.observed_signals:
            confidence += 0.1
        
        # Boost from execution confidence
        confidence += snapshot.confidence * 0.2
        
        return min(0.95, confidence)

    def _create_error_evaluation(
        self,
        snapshot_id: str,
        error: str,
    ) -> OutcomeEvaluation:
        """Create an error evaluation."""
        
        return OutcomeEvaluation(
            snapshot_id=snapshot_id,
            category=OutcomeCategory.ERROR,
            score=-0.5,
            confidence=1.0,
            rationale=f"Execution error: {error}",
        )

    def _build_rationale(
        self,
        category: OutcomeCategory,
        metrics: Dict[str, List[str]],
    ) -> str:
        """Build rationale string."""
        
        parts = []
        
        if category == OutcomeCategory.IMPROVEMENT:
            parts.append(f"Improved metrics: {', '.join(metrics['improved'])}")
        elif category == OutcomeCategory.DETERIORATION:
            parts.append(f"Deteriorated metrics: {', '.join(metrics['deteriorated'])}")
        elif category == OutcomeCategory.MIXED:
            parts.append(f"Improved: {', '.join(metrics['improved'])}, deteriorated: {', '.join(metrics['deteriorated'])}")
        elif category == OutcomeCategory.NO_CHANGE:
            parts.append("No meaningful change detected")
        else:
            parts.append("Unable to determine outcome")
        
        return "; ".join(parts)


# Global evaluator instance
_evaluator: Optional["OutcomeEvaluator"] = None


def get_outcome_evaluator() -> OutcomeEvaluator:
    """Get the global outcome evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = OutcomeEvaluator()
    return _evaluator
