"""Execution logger - logs execution decisions and outcomes."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution.execution_models import ExecutionDecision, ExecutionOutcome

logger = logging.getLogger(__name__)


class ExecutionLogger:
    """Logs execution decisions and outcomes."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def log_decision(self, decision: ExecutionDecision):
        """Log an execution decision."""
        entry = {
            "event_type": "decision",
            "decision_id": decision.decision_id,
            "intent_id": decision.intent_id,
            "approved": decision.approved,
            "status": decision.status.value,
            "policy_passed": decision.policy_gate.passed,
            "doctrine_aligned": decision.doctrine_gate.aligned,
            "risk_passed": decision.risk_gate.passed,
            "timestamp": decision.decided_at.isoformat(),
            "rationale": decision.rationale,
        }
        
        self._logs.append(entry)
        logger.info(f"Logged decision: {decision.decision_id} - approved={decision.approved}")

    def log_outcome(self, outcome: ExecutionOutcome):
        """Log an execution outcome."""
        entry = {
            "event_type": "outcome",
            "outcome_id": outcome.outcome_id,
            "decision_id": outcome.decision_id,
            "intent_id": outcome.intent_id,
            "status": outcome.status.value,
            "result": outcome.result,
            "error": outcome.error,
            "timestamp": outcome.completed_at.isoformat() if outcome.completed_at else datetime.utcnow().isoformat(),
        }
        
        self._logs.append(entry)
        logger.info(f"Logged outcome: {outcome.outcome_id} - status={outcome.status.value}")

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution logs."""
        return self._logs[-limit:]

    def get_logs_by_intent(self, intent_id: str) -> List[Dict[str, Any]]:
        """Get logs for a specific intent."""
        return [log for log in self._logs if log.get("intent_id") == intent_id]

    def get_logs_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get logs by event type."""
        return [log for log in self._logs if log.get("event_type") == event_type]

    def clear(self):
        """Clear all logs."""
        self._logs.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get log statistics."""
        decisions = [log for log in self._logs if log.get("event_type") == "decision"]
        outcomes = [log for log in self._logs if log.get("event_type") == "outcome"]
        
        approved = sum(1 for d in decisions if d.get("approved"))
        rejected = sum(1 for d in decisions if not d.get("approved"))
        
        executed = sum(1 for o in outcomes if o.get("status") == "executed")
        failed = sum(1 for o in outcomes if o.get("status") == "failed")
        
        return {
            "total_logs": len(self._logs),
            "decisions": len(decisions),
            "outcomes": len(outcomes),
            "approved": approved,
            "rejected": rejected,
            "executed": executed,
            "failed": failed,
        }


# Global logger instance
_logger: Optional["ExecutionLogger"] = None


def get_execution_logger() -> ExecutionLogger:
    """Get the global execution logger instance."""
    global _logger
    if _logger is None:
        _logger = ExecutionLogger()
    return _logger
