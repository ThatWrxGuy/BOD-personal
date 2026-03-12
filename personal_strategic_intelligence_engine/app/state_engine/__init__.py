"""Unified State Engine - Single Source of Truth for System State.

This module provides:
- State management (StateEngine)
- Historical snapshots (StateSnapshotter)
- Three-tier memory (MemoryManager)
- Strategic doctrine (DoctrineManager)
- Persistence (StateRepository)

All intelligence engines should read from and write to the State Engine.
"""
from app.state_engine.state_types import (
    StateComponent,
    MemoryTier,
    ExecutionStatus,
    RiskLevel,
    CyclePhase,
)

from app.state_engine.state_models import (
    SystemStateSnapshot,
    OperationalState,
    StrategicState,
    RiskState,
    GoalState,
    ResourceState,
    StateUpdate,
    MemoryEntry,
    DoctrineEntry,
    SnapshotRecord,
)

from app.state_engine.state_engine import (
    StateEngine,
    get_state_engine,
    reset_state_engine,
)

from app.state_engine.state_snapshotter import (
    StateSnapshotter,
)

from app.state_engine.memory_manager import (
    MemoryManager,
)

from app.state_engine.doctrine_manager import (
    DoctrineManager,
)

from app.state_engine.state_repository import (
    StateRepository,
)

__all__ = [
    # Types
    "StateComponent",
    "MemoryTier",
    "ExecutionStatus",
    "RiskLevel",
    "CyclePhase",
    # Models
    "SystemStateSnapshot",
    "OperationalState",
    "StrategicState",
    "RiskState",
    "GoalState",
    "ResourceState",
    "StateUpdate",
    "MemoryEntry",
    "DoctrineEntry",
    "SnapshotRecord",
    # Core
    "StateEngine",
    "get_state_engine",
    "reset_state_engine",
    # Components
    "StateSnapshotter",
    "MemoryManager",
    "DoctrineManager",
    "StateRepository",
]
