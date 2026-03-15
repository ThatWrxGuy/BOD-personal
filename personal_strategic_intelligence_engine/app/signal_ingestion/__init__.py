"""Live Signal Integration Layer.

This module provides infrastructure for ingesting, normalizing, validating,
and routing real-world signals into the strategic intelligence engine.

All operations are read-only - no autonomous execution is permitted.
"""
from app.signal_ingestion.signal_models import (
    LIVE_EXECUTION_ENABLED,
    SignalSource,
    SignalSourceCategory,
    SignalType,
    LiveSignal,
    NormalizedSignal,
    SignalIntegrityReport,
    SignalIngestionEvent,
    SignalHealthStatus,
)

from app.signal_ingestion.signal_registry import (
    SignalRegistry,
    get_signal_registry,
)

from app.signal_ingestion.signal_normalizer import (
    SignalNormalizer,
    get_signal_normalizer,
)

from app.signal_ingestion.signal_validator import (
    SignalValidator,
    get_signal_validator,
)

from app.signal_ingestion.signal_router import (
    SignalRouter,
    get_signal_router,
)

from app.signal_ingestion.signal_monitor import (
    SignalMonitor,
    get_signal_monitor,
)

from app.signal_ingestion.ingestion_controller import (
    IngestionController,
    get_ingestion_controller,
)

__all__ = [
    # Constants
    "LIVE_EXECUTION_ENABLED",
    # Models
    "SignalSource",
    "SignalSourceCategory",
    "SignalType",
    "LiveSignal",
    "NormalizedSignal",
    "SignalIntegrityReport",
    "SignalIngestionEvent",
    "SignalHealthStatus",
    # Components
    "SignalRegistry",
    "SignalNormalizer",
    "SignalValidator",
    "SignalRouter",
    "SignalMonitor",
    "IngestionController",
    # Factories
    "get_signal_registry",
    "get_signal_normalizer",
    "get_signal_validator",
    "get_signal_router",
    "get_signal_monitor",
    "get_ingestion_controller",
]
