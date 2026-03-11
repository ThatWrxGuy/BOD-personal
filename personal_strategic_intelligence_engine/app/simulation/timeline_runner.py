"""Timeline Runner for advancing simulation through time."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.simulation.metrics_collector import MetricsCollector
from app.core.logging import get_logger

logger = get_logger(__name__)


class TimelineRunner:
    """Advances simulation through discrete time steps."""

    def __init__(
        self,
        session: AsyncSession,
        metrics_collector: MetricsCollector,
    ):
        self.session = session
        self.metrics = metrics_collector

    async def run_day(
        self,
        day: int,
        scenario: dict,
    ) -> dict:
        """Run a single simulated day."""
        logger.info(f"Running simulation day {day}")
        
        day_events = []
        
        # Get signals for this day
        signals_config = scenario.get("signals", [])
        day_signals = [s for s in signals_config if s.get("day") == day]
        
        # Process signals for the day
        for signal_config in day_signals:
            await self._process_signal(signal_config, day)
            day_events.append(f"Signal: {signal_config.get('title')}")
            self.metrics.increment("signals_ingested")
            
            if signal_config.get("urgency", 0) >= 7:
                self.metrics.increment("high_urgency_signals")
        
        # Check for trigger conditions
        if len(day_signals) >= 3:
            trigger_fired = await self._check_triggers(day)
            if trigger_fired:
                day_events.append("Trigger fired due to signal cluster")
                self.metrics.increment("triggers_fired")
        
        # Check if board meeting should be triggered
        meeting_triggered = await self._check_meeting_trigger(day, day_signals)
        if meeting_triggered:
            day_events.append("Board meeting triggered")
            self.metrics.increment("meetings_executed")
        
        return {
            "day": day,
            "events": day_events,
            "signals_processed": len(day_signals),
        }

    async def _process_signal(self, signal_config: dict, day: int) -> None:
        """Process a single signal."""
        await self.metrics.record_event(
            event_type="SIGNAL",
            title=signal_config.get("title", "Signal"),
            description=f"Processed signal: {signal_config.get('title')}",
            component="signal_collector",
            severity=signal_config.get("urgency", 5) >= 7 and "HIGH" or "MEDIUM",
            metadata={"day": day, "category": signal_config.get("category")},
        )

    async def _check_triggers(self, day: int) -> bool:
        """Check if trigger conditions are met."""
        # Check high urgency signal count
        await self.metrics.record_event(
            event_type="TRIGGER",
            title="High Urgency Signal Cluster",
            description="Multiple high urgency signals detected - trigger condition met",
            component="trigger_engine",
            severity="HIGH",
            metadata={"day": day},
        )
        return True

    async def _check_meeting_trigger(self, day: int, signals: list) -> bool:
        """Check if board meeting should be triggered."""
        high_urgency = [s for s in signals if s.get("urgency", 0) >= 8]
        
        if len(high_urgency) >= 2:
            await self.metrics.record_event(
                event_type="MEETING",
                title="Emergency Board Meeting",
                description="High urgency signals triggered emergency board meeting",
                component="board_orchestrator",
                severity="HIGH",
                metadata={"day": day, "signals_count": len(high_urgency)},
            )
            return True
        
        # Weekly meetings on day 7, 14
        if day % 7 == 0:
            await self.metrics.record_event(
                event_type="MEETING",
                title="Weekly Strategic Review",
                description="Scheduled weekly board meeting",
                component="board_scheduler",
                severity="MEDIUM",
                metadata={"day": day},
            )
            return True
        
        return False

    async def run_full_timeline(
        self,
        scenario: dict,
        simulated_days: int,
    ) -> dict:
        """Run the full simulation timeline."""
        logger.info(f"Starting timeline: {simulated_days} days")
        
        timeline_results = []
        
        for day in range(1, simulated_days + 1):
            day_result = await self.run_day(day, scenario)
            timeline_results.append(day_result)
        
        return {
            "total_days": simulated_days,
            "results": timeline_results,
        }


async def get_timeline_runner(
    session: AsyncSession,
    metrics_collector: MetricsCollector,
) -> TimelineRunner:
    """Get a timeline runner instance."""
    return TimelineRunner(session, metrics_collector)
