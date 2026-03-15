"""Signal snapshot store for persisting and retrieving signal snapshots."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.decision_journal.journal_models import SignalSnapshot

logger = logging.getLogger(__name__)


class SignalSnapshotStore:
    """Stores signal snapshots associated with decision cycles."""

    def __init__(self):
        # In-memory storage
        self._signals: Dict[str, SignalSnapshot] = {}  # signal_id -> snapshot
        self._cycle_signals: Dict[str, List[str]] = {}  # cycle_id -> [signal_ids]
        self._source_index: Dict[str, List[str]] = {}  # source_id -> [signal_ids]
        self._type_index: Dict[str, List[str]] = {}  # signal_type -> [signal_ids]

    def store_signal(
        self,
        cycle_id: str,
        signal: SignalSnapshot
    ) -> bool:
        """Store a signal snapshot."""
        try:
            signal_id = signal.signal_id
            
            # Store
            self._signals[signal_id] = signal
            
            # Index by cycle
            if cycle_id not in self._cycle_signals:
                self._cycle_signals[cycle_id] = []
            if signal_id not in self._cycle_signals[cycle_id]:
                self._cycle_signals[cycle_id].append(signal_id)
            
            # Index by source
            source_id = signal.source_id
            if source_id not in self._source_index:
                self._source_index[source_id] = []
            if signal_id not in self._source_index[source_id]:
                self._source_index[source_id].append(signal_id)
            
            # Index by type
            signal_type = signal.signal_type
            if signal_type not in self._type_index:
                self._type_index[signal_type] = []
            if signal_id not in self._type_index[signal_type]:
                self._type_index[signal_type].append(signal_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store signal: {e}")
            return False

    def store_batch(
        self,
        cycle_id: str,
        signals: List[SignalSnapshot]
    ) -> int:
        """Store multiple signals."""
        count = 0
        for sig in signals:
            if self.store_signal(cycle_id, sig):
                count += 1
        return count

    def get_signal(self, signal_id: str) -> Optional[SignalSnapshot]:
        """Get a signal by ID."""
        return self._signals.get(signal_id)

    def get_signals_for_cycle(self, cycle_id: str) -> List[SignalSnapshot]:
        """Get all signals for a cycle."""
        signal_ids = self._cycle_signals.get(cycle_id, [])
        return [self._signals[sid] for sid in signal_ids if sid in self._signals]

    def find_by_source(self, source_id: str, limit: int = 100) -> List[SignalSnapshot]:
        """Find signals by source."""
        signal_ids = self._source_index.get(source_id, [])
        signals = [self._signals[sid] for sid in signal_ids if sid in self._signals]
        # Sort by timestamp
        signals.sort(key=lambda s: s.timestamp, reverse=True)
        return signals[:limit]

    def find_by_type(self, signal_type: str, limit: int = 100) -> List[SignalSnapshot]:
        """Find signals by type."""
        signal_ids = self._type_index.get(signal_type, [])
        signals = [self._signals[sid] for sid in signal_ids if sid in self._signals]
        # Sort by timestamp
        signals.sort(key=lambda s: s.timestamp, reverse=True)
        return signals[:limit]

    def find_fresh_signals(self, threshold: float = 0.7, limit: int = 100) -> List[SignalSnapshot]:
        """Find fresh signals (high freshness score)."""
        signals = [s for s in self._signals.values() if s.freshness_score >= threshold]
        signals.sort(key=lambda s: s.freshness_score, reverse=True)
        return signals[:limit]

    def find_high_confidence_signals(self, threshold: float = 0.7, limit: int = 100) -> List[SignalSnapshot]:
        """Find high confidence signals."""
        signals = [s for s in self._signals.values() if s.confidence_score >= threshold]
        signals.sort(key=lambda s: s.confidence_score, reverse=True)
        return signals[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get signal store statistics."""
        avg_freshness = 0.0
        avg_confidence = 0.0
        if self._signals:
            avg_freshness = sum(s.freshness_score for s in self._signals.values()) / len(self._signals)
            avg_confidence = sum(s.confidence_score for s in self._signals.values()) / len(self._signals)
        
        return {
            "total_signals": len(self._signals),
            "cycles_stored": len(self._cycle_signals),
            "sources_indexed": len(self._source_index),
            "types_indexed": len(self._type_index),
            "avg_freshness": avg_freshness,
            "avg_confidence": avg_confidence,
        }

    def clear(self):
        """Clear all stored data."""
        self._signals.clear()
        self._cycle_signals.clear()
        self._source_index.clear()
        self._type_index.clear()


# Global store instance
_store: Optional[SignalSnapshotStore] = None


def get_signal_snapshot_store() -> SignalSnapshotStore:
    """Get the global signal snapshot store instance."""
    global _store
    if _store is None:
        _store = SignalSnapshotStore()
    return _store
