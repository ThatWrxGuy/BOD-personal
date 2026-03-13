"""Journal store for persisting and retrieving decision cycles."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.decision_journal.journal_models import (
    DecisionCycleSnapshot,
    JournalEvent,
    LIVE_EXECUTION_ENABLED,
)

logger = logging.getLogger(__name__)


class JournalStore:
    """Provides storage and retrieval for decision journal entries."""

    def __init__(self):
        # In-memory storage (can be replaced with persistent backend)
        self._cycles: Dict[str, DecisionCycleSnapshot] = {}
        self._events: List[JournalEvent] = []
        self._cycle_index: Dict[str, List[str]] = {}  # domain -> cycle_ids

    def store_cycle(self, snapshot: DecisionCycleSnapshot) -> bool:
        """Store a decision cycle snapshot."""
        if LIVE_EXECUTION_ENABLED:
            logger.error("Cannot store cycles when LIVE_EXECUTION_ENABLED is True")
            return False

        try:
            # Store the cycle
            self._cycles[snapshot.cycle_id] = snapshot

            # Index by domains
            for rec in snapshot.recommendations:
                domain = rec.target_domain
                if domain not in self._cycle_index:
                    self._cycle_index[domain] = []
                if snapshot.cycle_id not in self._cycle_index[domain]:
                    self._cycle_index[domain].append(snapshot.cycle_id)

            # Log the event
            event = JournalEvent(
                event_type="cycle_stored",
                cycle_id=snapshot.cycle_id,
                journal_write_status="success",
                snapshot_size=len(snapshot.recommendations),
            )
            self._events.append(event)

            logger.info(f"Stored cycle {snapshot.cycle_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store cycle: {e}")

            # Log failure
            event = JournalEvent(
                event_type="cycle_store_failed",
                cycle_id=snapshot.cycle_id if snapshot else None,
                journal_write_status="failed",
                error_message=str(e),
            )
            self._events.append(event)
            return False

    def get_cycle(self, cycle_id: str) -> Optional[DecisionCycleSnapshot]:
        """Fetch a cycle by ID."""
        return self._cycles.get(cycle_id)

    def list_recent_cycles(self, limit: int = 100) -> List[DecisionCycleSnapshot]:
        """List recent cycles, most recent first."""
        cycles = sorted(
            self._cycles.values(),
            key=lambda c: c.timestamp,
            reverse=True
        )
        return cycles[:limit]

    def list_cycles_by_domain(self, domain: str, limit: int = 100) -> List[DecisionCycleSnapshot]:
        """List cycles for a specific domain."""
        cycle_ids = self._cycle_index.get(domain, [])
        cycles = [self._cycles[cid] for cid in cycle_ids if cid in self._cycles]
        # Sort by timestamp
        cycles.sort(key=lambda c: c.timestamp, reverse=True)
        return cycles[:limit]

    def list_cycles_by_date_range(
        self,
        start: datetime,
        end: datetime,
        limit: int = 100
    ) -> List[DecisionCycleSnapshot]:
        """List cycles within a date range."""
        cycles = [
            c for c in self._cycles.values()
            if start <= c.timestamp <= end
        ]
        cycles.sort(key=lambda c: c.timestamp, reverse=True)
        return cycles[:limit]

    def list_cycles_with_conflicts(self, limit: int = 100) -> List[DecisionCycleSnapshot]:
        """List cycles that had detected conflicts."""
        cycles = [
            c for c in self._cycles.values()
            if len(c.detected_conflicts) > 0
        ]
        cycles.sort(key=lambda c: c.timestamp, reverse=True)
        return cycles[:limit]

    def list_cycles_by_recommendation_type(
        self,
        action_type: str,
        limit: int = 100
    ) -> List[DecisionCycleSnapshot]:
        """List cycles with a specific recommendation action type."""
        cycles = [
            c for c in self._cycles.values()
            if any(rec.action == action_type for rec in c.recommendations)
        ]
        cycles.sort(key=lambda c: c.timestamp, reverse=True)
        return cycles[:limit]

    def get_replay_bundle(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get a replay-ready bundle for a cycle."""
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            return None

        return {
            "cycle": cycle.model_dump(),
            "signals": [s.model_dump() for s in cycle.normalized_signals],
            "recommendations": [r.model_dump() for r in cycle.recommendations],
            "conflicts": [c.model_dump() for c in cycle.detected_conflicts],
        }

    def get_journal_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[JournalEvent]:
        """Get journal events."""
        events = self._events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get journal statistics."""
        return {
            "total_cycles": len(self._cycles),
            "total_events": len(self._events),
            "domains_indexed": len(self._cycle_index),
            "cycles_with_conflicts": sum(
                1 for c in self._cycles.values() if c.detected_conflicts
            ),
            "total_recommendations": sum(
                len(c.recommendations) for c in self._cycles.values()
            ),
        }

    def clear(self):
        """Clear all journal data (for testing)."""
        self._cycles.clear()
        self._events.clear()
        self._cycle_index.clear()


# Global store instance
_store: Optional[JournalStore] = None


def get_journal_store() -> JournalStore:
    """Get the global journal store instance."""
    global _store
    if _store is None:
        _store = JournalStore()
    return _store
