"""Execution reliability analyzer - analyzes historical execution success."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.execution_audit.outcome_models import (
    ExecutionOutcomeSnapshot,
    ExecutionReliabilityScore,
    OutcomeCategory,
)

logger = logging.getLogger(__name__)


class ExecutionReliabilityAnalyzer:
    """Analyzes historical execution reliability."""

    def __init__(self, min_samples: int = 5):
        self._min_samples = min_samples
        self._scores: Dict[str, ExecutionReliabilityScore] = {}  # (action_type, domain) -> score

    def analyze(
        self,
        snapshots: List[ExecutionOutcomeSnapshot],
    ) -> List[ExecutionReliabilityScore]:
        """
        Analyze execution reliability from snapshots.
        
        Args:
            snapshots: List of outcome snapshots
            
        Returns:
            List of reliability scores
        """
        # Group by action_type and domain
        by_key: Dict[str, List[ExecutionOutcomeSnapshot]] = {}
        
        for snapshot in snapshots:
            key = self._make_key(snapshot.action_type, snapshot.domain)
            if key not in by_key:
                by_key[key] = []
            by_key[key].append(snapshot)
        
        # Calculate scores
        scores = []
        for key, group in by_key.items():
            score = self._calculate_score(key, group)
            self._scores[key] = score
            scores.append(score)
        
        return scores

    def get_score(self, action_type: str, domain: str) -> Optional[ExecutionReliabilityScore]:
        """Get reliability score for an action type and domain."""
        key = self._make_key(action_type, domain)
        return self._scores.get(key)

    def get_all_scores(self) -> List[ExecutionReliabilityScore]:
        """Get all reliability scores."""
        return list(self._scores.values())

    def is_reliable(self, action_type: str, domain: str, threshold: float = 0.7) -> bool:
        """
        Check if an action is considered reliable.
        
        Args:
            action_type: Type of action
            domain: Domain
            threshold: Minimum success rate threshold
            
        Returns:
            True if action is reliable
        """
        score = self.get_score(action_type, domain)
        
        if not score:
            return False
        
        if score.total_executions < self._min_samples:
            return False
        
        return score.success_rate >= threshold

    def _calculate_score(
        self,
        key: str,
        snapshots: List[ExecutionOutcomeSnapshot],
    ) -> ExecutionReliabilityScore:
        """Calculate reliability score for a group of snapshots."""
        
        total = len(snapshots)
        
        # For now, we don't have outcome evaluations stored
        # This would be connected to outcome_evaluator in production
        # Simplified: treat all as successful for demonstration
        
        successful = total  # Placeholder
        failed = 0  # Placeholder
        
        # Determine trend
        trend = self._calculate_trend(snapshots)
        
        # Parse key
        action_type, domain = self._parse_key(key)
        
        return ExecutionReliabilityScore(
            action_type=action_type,
            domain=domain,
            total_executions=total,
            successful_executions=successful,
            failed_executions=failed,
            success_rate=successful / total if total > 0 else 0,
            recent_trend=trend,
            min_samples=self._min_samples,
        )

    def _calculate_trend(self, snapshots: List[ExecutionOutcomeSnapshot]) -> str:
        """Calculate trend from recent snapshots."""
        
        if len(snapshots) < 3:
            return "stable"
        
        # Sort by time
        sorted_snapshots = sorted(
            snapshots,
            key=lambda s: s.executed_at,
        )
        
        # Take last 5
        recent = sorted_snapshots[-5:]
        
        # Check if improving or declining based on state changes
        improvements = 0
        declines = 0
        
        for i in range(1, len(recent)):
            prev = recent[i - 1]
            curr = recent[i]
            
            # Simple heuristic: if post-state > pre-state, it's improvement
            for key in curr.post_execution_state:
                if key in prev.post_execution_state:
                    try:
                        if curr.post_execution_state[key] > prev.post_execution_state[key]:
                            improvements += 1
                        elif curr.post_execution_state[key] < prev.post_execution_state[key]:
                            declines += 1
                    except (TypeError, ValueError):
                        pass
        
        if improvements > declines * 2:
            return "improving"
        elif declines > improvements * 2:
            return "declining"
        else:
            return "stable"

    def _make_key(self, action_type: str, domain: str) -> str:
        """Create key for action/domain pair."""
        return f"{action_type}:{domain}"

    def _parse_key(self, key: str) -> tuple:
        """Parse key into action_type and domain."""
        parts = key.split(":")
        if len(parts) == 2:
            return parts[0], parts[1]
        return key, "default"

    def get_statistics(self) -> Dict[str, Any]:
        """Get reliability statistics."""
        
        if not self._scores:
            return {
                "total_action_types": 0,
                "reliable_actions": 0,
                "unreliable_actions": 0,
            }
        
        reliable = sum(1 for s in self._scores.values() if s.success_rate >= 0.7)
        
        return {
            "total_action_types": len(self._scores),
            "reliable_actions": reliable,
            "unreliable_actions": len(self._scores) - reliable,
            "average_success_rate": sum(s.success_rate for s in self._scores.values()) / len(self._scores),
        }


# Global analyzer instance
_analyzer: Optional["ExecutionReliabilityAnalyzer"] = None


def get_reliability_analyzer() -> ExecutionReliabilityAnalyzer:
    """Get the global reliability analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = ExecutionReliabilityAnalyzer()
    return _analyzer
