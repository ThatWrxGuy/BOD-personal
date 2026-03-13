"""Decision Journal & Replay Layer.

This module provides persistent storage, inspection, and replay
capabilities for strategic decision cycles.

All operations are read-only - no autonomous execution is permitted.
"""
from app.decision_journal.journal_models import (
    LIVE_EXECUTION_ENABLED,
    REPLAY_MODE,
    DriftClassification,
    ReplayStatus,
    SignalSnapshot,
    StateSnapshotReference,
    RecommendationSnapshot,
    ConflictSnapshot,
    DecisionCycleSnapshot,
    ReplayRequest,
    ReplayResult,
    AuditComparisonResult,
    JournalEvent,
)

from app.decision_journal.journal_store import (
    JournalStore,
    get_journal_store,
)

from app.decision_journal.cycle_snapshot_builder import (
    CycleSnapshotBuilder,
    get_cycle_snapshot_builder,
)

from app.decision_journal.recommendation_snapshot_store import (
    RecommendationSnapshotStore,
    get_recommendation_snapshot_store,
)

from app.decision_journal.signal_snapshot_store import (
    SignalSnapshotStore,
    get_signal_snapshot_store,
)

from app.decision_journal.replay_engine import (
    ReplayEngine,
    get_replay_engine,
)

from app.decision_journal.audit_comparator import (
    AuditComparator,
    get_audit_comparator,
)

__all__ = [
    # Constants
    "LIVE_EXECUTION_ENABLED",
    "REPLAY_MODE",
    # Models
    "DriftClassification",
    "ReplayStatus",
    "SignalSnapshot",
    "StateSnapshotReference",
    "RecommendationSnapshot",
    "ConflictSnapshot",
    "DecisionCycleSnapshot",
    "ReplayRequest",
    "ReplayResult",
    "AuditComparisonResult",
    "JournalEvent",
    # Components
    "JournalStore",
    "CycleSnapshotBuilder",
    "RecommendationSnapshotStore",
    "SignalSnapshotStore",
    "ReplayEngine",
    "AuditComparator",
    # Factories
    "get_journal_store",
    "get_cycle_snapshot_builder",
    "get_recommendation_snapshot_store",
    "get_signal_snapshot_store",
    "get_replay_engine",
    "get_audit_comparator",
]
