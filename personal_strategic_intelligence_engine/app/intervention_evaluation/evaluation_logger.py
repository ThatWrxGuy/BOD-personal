"""Evaluation Logger - Logs evaluation events."""
from datetime import datetime
from typing import List, Dict, Any


class EvaluationLogger:
    """Logs evaluation events."""
    
    def __init__(self):
        self._logs: List[Dict] = []
    
    def log_evaluation_cycle(self, cycle_id: str, metrics: Dict) -> None:
        """Log an evaluation cycle."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "evaluation_cycle",
            "cycle_id": cycle_id,
            "metrics": metrics,
        })
    
    def log_protocol_score(self, protocol_id: str, score: float) -> None:
        """Log protocol scoring."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "protocol_score",
            "protocol_id": protocol_id,
            "score": score,
        })
    
    def log_threshold_recommendation(self, trigger: str, recommendation: str) -> None:
        """Log threshold recommendation."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "threshold_recommendation",
            "trigger_type": trigger,
            "recommendation": recommendation,
        })
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent logs."""
        return self._logs[-limit:]


# Global logger
_logger: EvaluationLogger = None


def get_evaluation_logger() -> EvaluationLogger:
    """Get the global logger."""
    global _logger
    if _logger is None:
        _logger = EvaluationLogger()
    return _logger
