"""Simulation Logger - Captures all simulation events and decisions."""
import json
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SimulationLogger:
    """Captures simulation events and decisions."""
    
    def __init__(self):
        self._events: list[dict] = []
        self._decisions: list[dict] = []
        self._metrics: list[dict] = []
    
    def log_event(self, event_type: str, message: str, data: Optional[dict] = None) -> None:
        """Log a simulation event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "message": message,
            "data": data or {},
        }
        self._events.append(event)
        logger.info(f"[SIM] {event_type}: {message}")
    
    def log_decision(self, decision_type: str, reason: str, result: Any) -> None:
        """Log a decision made during simulation."""
        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": decision_type,
            "reason": reason,
            "result": str(result),
        }
        self._decisions.append(decision)
        logger.info(f"[DECISION] {decision_type}: {reason}")
    
    def log_metric(self, name: str, value: Any, step: int) -> None:
        """Log a metric value."""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "name": name,
            "value": value,
            "step": step,
        }
        self._metrics.append(metric)
    
    def log_day_start(self, day: int, state: dict) -> None:
        """Log the start of a simulation day."""
        self.log_event("day_start", f"Day {day} started", state)
    
    def log_day_end(self, day: int, summary: dict) -> None:
        """Log the end of a simulation day."""
        self.log_event("day_end", f"Day {day} completed", summary)
    
    def log_event_triggered(self, event: dict) -> None:
        """Log when an event is triggered."""
        self.log_event("event_triggered", f"Event: {event.get('description')}", event)
    
    def log_subsystem_invocation(
        self, 
        subsystem: str, 
        success: bool, 
        error: Optional[str] = None
    ) -> None:
        """Log subsystem invocation."""
        data = {"subsystem": subsystem, "success": success}
        if error:
            data["error"] = error
        self.log_event("subsystem_invocation", f"{subsystem} invoked", data)
    
    def log_warning(self, message: str, data: Optional[dict] = None) -> None:
        """Log a warning."""
        self.log_event("warning", message, data)
    
    def log_error(self, message: str, data: Optional[dict] = None) -> None:
        """Log an error."""
        self.log_event("error", message, data)
    
    def get_events(self) -> list[dict]:
        """Get all logged events."""
        return self._events
    
    def get_decisions(self) -> list[dict]:
        """Get all logged decisions."""
        return self._decisions
    
    def get_metrics(self) -> list[dict]:
        """Get all logged metrics."""
        return self._metrics
    
    def get_summary(self) -> dict:
        """Get a summary of logged data."""
        return {
            "total_events": len(self._events),
            "total_decisions": len(self._decisions),
            "total_metrics": len(self._metrics),
            "event_types": self._count_event_types(),
        }
    
    def _count_event_types(self) -> dict:
        """Count events by type."""
        counts = {}
        for event in self._events:
            event_type = event.get("type", "unknown")
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def clear(self) -> None:
        """Clear all logged data."""
        self._events.clear()
        self._decisions.clear()
        self._metrics.clear()
    
    def export_json(self) -> str:
        """Export all logs as JSON."""
        return json.dumps({
            "events": self._events,
            "decisions": self._decisions,
            "metrics": self._metrics,
        }, indent=2)


# Global logger instance
_simulation_logger: Optional[SimulationLogger] = None


def get_simulation_logger() -> SimulationLogger:
    """Get the global simulation logger."""
    global _simulation_logger
    if _simulation_logger is None:
        _simulation_logger = SimulationLogger()
    return _simulation_logger
