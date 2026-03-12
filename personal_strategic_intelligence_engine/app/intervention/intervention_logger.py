"""Intervention Logger - Records intervention events and decisions."""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.intervention.intervention_types import Intervention, TriggerCondition

logger = logging.getLogger(__name__)


class InterventionLogger:
    """Logs intervention events and decisions."""
    
    def __init__(self):
        self._logs: List[Dict] = []
    
    def log_trigger_detected(self, trigger: TriggerCondition) -> None:
        """Log when a trigger is detected."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "trigger_detected",
            "trigger_type": trigger.trigger_type.value,
            "domain": trigger.domain,
            "severity": trigger.severity,
            "occurrence": trigger.occurrence_count,
        }
        self._logs.append(entry)
        logger.info(f"Trigger: {trigger.trigger_type.value} on {trigger.domain} (severity: {trigger.severity:.2f})")
    
    def log_intervention_selected(self, intervention: Intervention) -> None:
        """Log when an intervention is selected."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "intervention_selected",
            "intervention_id": intervention.intervention_id,
            "intervention_type": intervention.intervention_type.value,
            "target_domain": intervention.target_domain,
            "confidence": intervention.confidence_score,
        }
        self._logs.append(entry)
        logger.info(f"Selected: {intervention.intervention_type.value} for {intervention.target_domain}")
    
    def log_intervention_executed(self, intervention: Intervention, results: Dict) -> None:
        """Log when an intervention is executed."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "intervention_executed",
            "intervention_id": intervention.intervention_id,
            "status": intervention.status.value,
            "actions_executed": len(results.get("actions_executed", [])),
            "actions_failed": len(results.get("actions_failed", [])),
        }
        self._logs.append(entry)
        logger.info(f"Executed: {intervention.intervention_id} - {intervention.status.value}")
    
    def log_intervention_skipped(self, reason: str) -> None:
        """Log when an intervention is skipped."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "intervention_skipped",
            "reason": reason,
        }
        self._logs.append(entry)
        logger.info(f"Skipped: {reason}")
    
    def log_policy_violation(self, intervention: Intervention, reason: str) -> None:
        """Log policy violation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "policy_violation",
            "intervention_id": intervention.intervention_id,
            "reason": reason,
        }
        self._logs.append(entry)
        logger.warning(f"Policy violation: {reason}")
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent logs."""
        return self._logs[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get log summary."""
        return {
            "total_logs": len(self._logs),
            "by_type": self._count_by_type(),
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count logs by type."""
        counts = {}
        for log in self._logs:
            log_type = log.get("type", "unknown")
            counts[log_type] = counts.get(log_type, 0) + 1
        return counts
    
    def clear(self) -> None:
        """Clear logs."""
        self._logs.clear()


# Global logger
_intervention_logger: Optional[InterventionLogger] = None


def get_intervention_logger() -> InterventionLogger:
    """Get the global intervention logger."""
    global _intervention_logger
    if _intervention_logger is None:
        _intervention_logger = InterventionLogger()
    return _intervention_logger
