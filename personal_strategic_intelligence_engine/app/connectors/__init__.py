"""Connectors Module.

Signal Connector Layer for external data source integration.
"""
from app.connectors.connector_models import (
    ConnectorConfig,
    ConnectorEvent,
    ConnectorHealth,
    ConnectorSignal,
    ConnectorSource,
    ConnectorStatus,
    ConnectorType,
    SignalPriority,
    # Safety constants
    LIVE_EXECUTION_ENABLED,
    CONNECTOR_WRITE_MODE,
)
from app.connectors.connector_controller import (
    ConnectorController,
    get_connector_controller,
)
from app.connectors.connector_registry import (
    ConnectorRegistry,
    get_connector_registry,
)
from app.connectors.connector_store import (
    ConnectorStore,
    get_connector_store,
)
from app.connectors.connector_health_monitor import (
    ConnectorHealthMonitor,
    get_health_monitor,
)
from app.connectors.connector_scheduler import (
    ConnectorScheduler,
    get_connector_scheduler,
)
from app.connectors.signal_mapper import (
    SignalMapper,
    get_signal_mapper,
)

__all__ = [
    # Models
    "ConnectorConfig",
    "ConnectorEvent",
    "ConnectorHealth",
    "ConnectorSignal",
    "ConnectorSource",
    "ConnectorStatus",
    "ConnectorType",
    "SignalPriority",
    # Safety
    "LIVE_EXECUTION_ENABLED",
    "CONNECTOR_WRITE_MODE",
    # Components
    "ConnectorController",
    "get_connector_controller",
    "ConnectorRegistry",
    "get_connector_registry",
    "ConnectorStore",
    "get_connector_store",
    "ConnectorHealthMonitor",
    "get_health_monitor",
    "ConnectorScheduler",
    "get_connector_scheduler",
    "SignalMapper",
    "get_signal_mapper",
]
