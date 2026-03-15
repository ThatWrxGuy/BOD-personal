"""Execution outcome tracker - captures and stores execution outcomes."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_audit.outcome_models import ExecutionOutcomeSnapshot

logger = logging.getLogger(__name__)


class OutcomeTracker:
    """Captures and stores execution outcomes."""

    def __init__(self):
        self._snapshots: Dict[str, ExecutionOutcomeSnapshot] = {}
        self._execution_history: Dict[str, List[str]] = {}  # execution_id -> snapshot_ids

    def capture_outcome(
        self,
        execution_id: str,
        recommendation_id: str,
        action_type: str,
        domain: str,
        pre_execution_state: Optional[Dict[str, Any]] = None,
        post_execution_state: Optional[Dict[str, Any]] = None,
        observed_signals: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 0.5,
        error_message: Optional[str] = None,
    ) -> ExecutionOutcomeSnapshot:
        """
        Capture an execution outcome.
        
        Args:
            execution_id: ID of the execution
            recommendation_id: ID of the source recommendation
            action_type: Type of action executed
            domain: Domain of the action
            pre_execution_state: State before execution
            post_execution_state: State after execution
            observed_signals: Signals observed post-execution
            confidence: Confidence in the execution
            error_message: Error message if execution failed
            
        Returns:
            ExecutionOutcomeSnapshot
        """
        snapshot = ExecutionOutcomeSnapshot(
            execution_id=execution_id,
            recommendation_id=recommendation_id,
            action_type=action_type,
            domain=domain,
            pre_execution_state=pre_execution_state or {},
            post_execution_state=post_execution_state or {},
            observed_signals=observed_signals or [],
            confidence=confidence,
            error_message=error_message,
            observed_at=datetime.utcnow(),
        )
        
        self._snapshots[snapshot.snapshot_id] = snapshot
        
        # Track history
        if execution_id not in self._execution_history:
            self._execution_history[execution_id] = []
        self._execution_history[execution_id].append(snapshot.snapshot_id)
        
        logger.info(f"Captured outcome snapshot: {snapshot.snapshot_id} for execution: {execution_id}")
        
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[ExecutionOutcomeSnapshot]:
        """Get a snapshot by ID."""
        return self._snapshots.get(snapshot_id)

    def get_snapshots_for_execution(self, execution_id: str) -> List[ExecutionOutcomeSnapshot]:
        """Get all snapshots for an execution."""
        snapshot_ids = self._execution_history.get(execution_id, [])
        return [self._snapshots[sid] for sid in snapshot_ids if sid in self._snapshots]

    def get_recent_snapshots(self, limit: int = 100) -> List[ExecutionOutcomeSnapshot]:
        """Get recent outcome snapshots."""
        snapshots = sorted(
            self._snapshots.values(),
            key=lambda s: s.observed_at or s.executed_at,
            reverse=True,
        )
        return snapshots[:limit]

    def get_snapshots_by_domain(self, domain: str) -> List[ExecutionOutcomeSnapshot]:
        """Get snapshots for a specific domain."""
        return [
            s for s in self._snapshots.values()
            if s.domain == domain
        ]

    def get_snapshots_by_action_type(self, action_type: str) -> List[ExecutionOutcomeSnapshot]:
        """Get snapshots for a specific action type."""
        return [
            s for s in self._snapshots.values()
            if s.action_type == action_type
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get outcome tracking statistics."""
        total = len(self._snapshots)
        errors = sum(1 for s in self._snapshots.values() if s.error_message)
        
        domains = {}
        action_types = {}
        
        for s in self._snapshots.values():
            domains[s.domain] = domains.get(s.domain, 0) + 1
            action_types[s.action_type] = action_types.get(s.action_type, 0) + 1
        
        return {
            "total_snapshots": total,
            "errors": errors,
            "domains": domains,
            "action_types": action_types,
        }

    def clear(self):
        """Clear all tracked outcomes."""
        self._snapshots.clear()
        self._execution_history.clear()


# Global tracker instance
_tracker: Optional["OutcomeTracker"] = None


def get_outcome_tracker() -> OutcomeTracker:
    """Get the global outcome tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = OutcomeTracker()
    return _tracker
