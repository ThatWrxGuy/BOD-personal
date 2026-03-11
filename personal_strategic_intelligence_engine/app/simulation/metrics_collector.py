"""Metrics Collector for simulation metrics."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation_run import SimulationEvent
from app.core.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects system metrics during simulation."""

    def __init__(self, session: AsyncSession, run_id: uuid.UUID):
        self.session = session
        self.run_id = run_id
        self.metrics = {
            "signals_ingested": 0,
            "high_urgency_signals": 0,
            "triggers_fired": 0,
            "meetings_executed": 0,
            "agent_responses": 0,
            "decisions_logged": 0,
            "goals_updated": 0,
            "forecasts_generated": 0,
            "component_failures": 0,
            "exceptions": [],
            "latencies": [],
        }

    async def record_event(
        self,
        event_type: str,
        title: str,
        description: str = None,
        component: str = None,
        severity: str = "MEDIUM",
        metadata: dict = None,
    ) -> SimulationEvent:
        """Record a simulation event."""
        event = SimulationEvent(
            simulation_run_id=self.run_id,
            event_day=metadata.get("day", 1) if metadata else 1,
            event_type=event_type,
            title=title,
            description=description,
            component=component,
            severity=severity,
            metadata=metadata or {},
        )
        
        self.session.add(event)
        await self.session.commit()
        
        return event

    def increment(self, metric: str, value: int = 1) -> None:
        """Increment a metric counter."""
        if metric in self.metrics:
            self.metrics[metric] += value

    def add_exception(self, component: str, error: str) -> None:
        """Record an exception."""
        self.metrics["component_failures"] += 1
        self.metrics["exceptions"].append({
            "component": component,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def add_latency(self, component: str, latency_ms: float) -> None:
        """Record a latency measurement."""
        self.metrics["latencies"].append({
            "component": component,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_metrics(self) -> dict:
        """Get collected metrics."""
        return self.metrics.copy()

    def get_summary(self) -> dict:
        """Get a summary of collected metrics."""
        return {
            "signals_ingested": self.metrics["signals_ingested"],
            "high_urgency_signals": self.metrics["high_urgency_signals"],
            "triggers_fired": self.metrics["triggers_fired"],
            "meetings_executed": self.metrics["meetings_executed"],
            "agent_responses": self.metrics["agent_responses"],
            "decisions_logged": self.metrics["decisions_logged"],
            "goals_updated": self.metrics["goals_updated"],
            "forecasts_generated": self.metrics["forecasts_generated"],
            "component_failures": self.metrics["component_failures"],
            "total_exceptions": len(self.metrics["exceptions"]),
        }


async def get_metrics_collector(session: AsyncSession, run_id: uuid.UUID) -> MetricsCollector:
    """Get a metrics collector instance."""
    return MetricsCollector(session, run_id)
