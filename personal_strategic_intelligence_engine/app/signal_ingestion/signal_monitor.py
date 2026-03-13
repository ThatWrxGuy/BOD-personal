"""Signal monitor for tracking provider health and signal quality."""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.signal_ingestion.signal_models import (
    SignalHealthStatus,
    SignalIngestionEvent,
)

logger = logging.getLogger(__name__)


class SignalMonitor:
    """Monitors signal provider health and signal quality."""

    def __init__(self):
        self._ingestion_history: Dict[str, List[SignalIngestionEvent]] = defaultdict(list)
        self._provider_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_signals": 0,
            "successful_signals": 0,
            "failed_signals": 0,
            "total_latency_ms": 0.0,
            "last_success": None,
            "last_failure": None,
            "stale_count": 0,
        })
        self._stale_threshold = 300  # 5 minutes

    def record_ingestion(self, event: SignalIngestionEvent):
        """Record an ingestion event."""
        # Add to history
        self._ingestion_history[event.source_id].append(event)

        # Update stats
        stats = self._provider_stats[event.source_id]
        stats["total_signals"] += 1

        if event.validation_status == "valid":
            stats["successful_signals"] += 1
            stats["last_success"] = event.ingestion_timestamp
        else:
            stats["failed_signals"] += 1
            stats["last_failure"] = event.ingestion_timestamp

        if event.freshness_score < 0.3:
            stats["stale_count"] += 1

        stats["total_latency_ms"] += event.processing_latency_ms

        # Trim history to last 1000 events
        if len(self._ingestion_history[event.source_id]) > 1000:
            self._ingestion_history[event.source_id] = \
                self._ingestion_history[event.source_id][-1000:]

    def get_health_status(self, source_id: str) -> SignalHealthStatus:
        """Get health status for a source."""
        stats = self._provider_stats.get(source_id, {})
        
        if not stats or stats["total_signals"] == 0:
            return SignalHealthStatus(
                source_id=source_id,
                status="unknown",
            )

        # Calculate uptime
        uptime = 100.0
        if stats["total_signals"] > 0:
            uptime = (stats["successful_signals"] / stats["total_signals"]) * 100

        # Determine status
        if uptime >= 95:
            status = "healthy"
        elif uptime >= 70:
            status = "degraded"
        elif stats["total_signals"] > 0:
            status = "down"
        else:
            status = "unknown"

        # Calculate avg latency
        avg_latency = 0.0
        if stats["total_signals"] > 0:
            avg_latency = stats["total_latency_ms"] / stats["total_signals"]

        return SignalHealthStatus(
            source_id=source_id,
            status=status,
            uptime_percentage=uptime,
            avg_latency_ms=avg_latency,
            last_success=stats.get("last_success"),
            last_failure=stats.get("last_failure"),
            stale_signal_count=stats["stale_count"],
        )

    def get_all_health_status(self) -> List[SignalHealthStatus]:
        """Get health status for all monitored sources."""
        source_ids = set(self._provider_stats.keys()) | set(self._ingestion_history.keys())
        return [self.get_health_status(sid) for sid in source_ids]

    def get_recent_events(
        self,
        source_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SignalIngestionEvent]:
        """Get recent ingestion events."""
        if source_id:
            events = self._ingestion_history.get(source_id, [])
        else:
            # Combine all events
            events = []
            for history in self._ingestion_history.values():
                events.extend(history)

        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def detect_stale_providers(self) -> List[str]:
        """Detect providers with stale signals."""
        stale = []
        for source_id, events in self._ingestion_history.items():
            if not events:
                continue
            
            latest = max(e.timestamp for e in events)
            age = (datetime.utcnow() - latest).total_seconds()
            
            if age > self._stale_threshold:
                stale.append(source_id)
        
        return stale

    def get_provider_metrics(self, source_id: str) -> Dict:
        """Get detailed metrics for a provider."""
        return self._provider_stats.get(source_id, {})

    def get_reliability_score(self, source_id: str) -> float:
        """Calculate reliability score (0-1) for a source."""
        stats = self._provider_stats.get(source_id, {})
        
        if not stats or stats["total_signals"] == 0:
            return 0.0

        # Calculate success rate
        success_rate = stats["successful_signals"] / stats["total_signals"]

        # Factor in latency (prefer lower latency)
        avg_latency = stats["total_latency_ms"] / stats["total_signals"]
        latency_score = max(0, 1 - (avg_latency / 1000))  # Penalize > 1 second

        # Factor in staleness
        stale_ratio = stats["stale_count"] / stats["total_signals"]
        freshness_score = 1 - stale_ratio

        # Weighted average
        reliability = (
            success_rate * 0.5 +
            latency_score * 0.25 +
            freshness_score * 0.25
        )

        return min(1.0, reliability)

    def clear_history(self, source_id: Optional[str] = None):
        """Clear ingestion history."""
        if source_id:
            if source_id in self._ingestion_history:
                del self._ingestion_history[source_id]
            if source_id in self._provider_stats:
                del self._provider_stats[source_id]
        else:
            self._ingestion_history.clear()
            self._provider_stats.clear()


# Global monitor instance
_monitor: Optional[SignalMonitor] = None


def get_signal_monitor() -> SignalMonitor:
    """Get the global signal monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = SignalMonitor()
    return _monitor
