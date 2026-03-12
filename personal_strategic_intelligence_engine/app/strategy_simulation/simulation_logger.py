"""Simulation Logger - Logs all simulation runs, outcomes, and recommendations."""
from datetime import datetime
from typing import List, Dict, Any, Optional


class SimulationLogger:
    """Logs simulation events and results."""
    
    def __init__(self):
        self._logs: List[Dict] = []
    
    def log_simulation_start(
        self,
        cycle_id: str,
        current_domains: Dict[str, float],
        num_strategies: int,
    ) -> None:
        """Log start of simulation cycle."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "simulation_start",
            "cycle_id": cycle_id,
            "current_domains": current_domains,
            "num_strategies": num_strategies,
        })
    
    def log_simulation_complete(
        self,
        cycle_id: str,
        best_strategy: str,
        recommended: bool,
        confidence: float,
    ) -> None:
        """Log completion of simulation cycle."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "simulation_complete",
            "cycle_id": cycle_id,
            "best_strategy": best_strategy,
            "execution_recommended": recommended,
            "confidence": confidence,
        })
    
    def log_strategy_evaluated(
        self,
        cycle_id: str,
        strategy_id: str,
        score: float,
        rank: int,
    ) -> None:
        """Log strategy evaluation."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "strategy_evaluated",
            "cycle_id": cycle_id,
            "strategy_id": strategy_id,
            "score": score,
            "rank": rank,
        })
    
    def log_recommendation(
        self,
        cycle_id: str,
        recommended_strategy: str,
        reasoning: str,
    ) -> None:
        """Log recommendation generation."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "recommendation",
            "cycle_id": cycle_id,
            "recommended_strategy": recommended_strategy,
            "reasoning": reasoning,
        })
    
    def log_error(
        self,
        cycle_id: str,
        error: str,
    ) -> None:
        """Log simulation error."""
        self._logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error",
            "cycle_id": cycle_id,
            "error": error,
        })
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent logs."""
        return self._logs[-limit:]
    
    def get_cycle_logs(self, cycle_id: str) -> List[Dict]:
        """Get logs for a specific cycle."""
        return [l for l in self._logs if l.get("cycle_id") == cycle_id]
    
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
_simulation_logger: Optional[SimulationLogger] = None


def get_simulation_logger() -> SimulationLogger:
    """Get the global simulation logger."""
    global _simulation_logger
    if _simulation_logger is None:
        _simulation_logger = SimulationLogger()
    return _simulation_logger
