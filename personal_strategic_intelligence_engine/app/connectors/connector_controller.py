"""Connector Controller.

Primary orchestration for connector management.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.connectors.connector_models import (
    ConnectorEvent,
    ConnectorSignal,
    ConnectorSource,
    ConnectorStatus,
    ConnectorType,
)
from app.connectors.connector_registry import get_connector_registry
from app.connectors.connector_health_monitor import get_health_monitor
from app.connectors.connector_store import get_connector_store
from app.connectors.signal_mapper import get_signal_mapper
from app.connectors.connectors.calendar_connector import CalendarConnector
from app.connectors.connectors.finance_connector import FinanceConnector
from app.connectors.connectors.tasks_connector import TasksConnector
from app.connectors.connectors.health_connector import HealthConnector

logger = logging.getLogger(__name__)


class ConnectorController:
    """Primary controller for connector management."""
    
    def __init__(self):
        self.registry = get_connector_registry()
        self.health_monitor = get_health_monitor()
        self.store = get_connector_store()
        self.mapper = get_signal_mapper()
        
        # Initialize connector classes
        self._connector_classes = {
            "calendar": CalendarConnector,
            "finance": FinanceConnector,
            "tasks": TasksConnector,
            "health": HealthConnector,
        }
    
    # Registration Methods
    
    def register_connector(
        self,
        name: str,
        connector_type: ConnectorType,
        config: Optional[Dict[str, Any]] = None,
        credentials: Optional[Dict[str, str]] = None,
        interval_seconds: int = 300,
        enabled: bool = False,
    ) -> ConnectorSource:
        """Register a new connector."""
        source = self.registry.register_connector(
            name=name,
            connector_type=connector_type,
            config=config,
            credentials=credentials,
            interval_seconds=interval_seconds,
        )
        
        if enabled:
            self.registry.enable_connector(name)
        
        logger.info(f"Registered connector: {name} ({connector_type})")
        return source
    
    def enable_connector(self, name: str) -> bool:
        """Enable a connector."""
        result = self.registry.enable_connector(name)
        if result:
            logger.info(f"Enabled connector: {name}")
        return result
    
    def disable_connector(self, name: str) -> bool:
        """Disable a connector."""
        result = self.registry.disable_connector(name)
        if result:
            logger.info(f"Disabled connector: {name}")
        return result
    
    # Execution Methods
    
    async def run_connector(self, connector_name: str) -> List[ConnectorSignal]:
        """Run a specific connector and collect signals."""
        start_time = datetime.utcnow()
        signals = []
        
        # Get connector source
        source = self.registry.get_connector(connector_name)
        if not source:
            logger.warning(f"Connector not found: {connector_name}")
            return signals
        
        # Record run start
        self.health_monitor.record_run_start(connector_name)
        
        try:
            # Get connector instance
            connector_class = self._connector_classes.get(source.connector_type.value)
            if not connector_class:
                raise ValueError(f"Unknown connector type: {source.connector_type}")
            
            connector = connector_class(config=source.config)
            
            # Validate connection
            if not await connector.validate_connection():
                raise ConnectionError(f"Failed to validate connection for {connector_name}")
            
            # Fetch signals from connector
            raw_signals = await connector.fetch_signals()
            
            # Map to internal format
            for raw in raw_signals:
                signal = self.mapper.map_signal(connector_name, raw.model_dump())
                if signal and self.mapper.validate_signal(signal):
                    signals.append(signal)
            
            # Record success
            self.health_monitor.record_run_complete(
                connector_name=connector_name,
                signals_count=len(signals),
                success=True,
            )
            
            # Log event
            self.store.add_event(ConnectorEvent(
                connector_name=connector_name,
                event_type="sync_complete",
                status="success",
                message=f"Produced {len(signals)} signals",
                signals_count=len(signals),
            ))
            
            # Update source
            source.last_sync = datetime.utcnow()
            source.last_success = datetime.utcnow()
            self.registry.update_connector(
                connector_name,
                config=source.config,
                credentials=source.credentials,
            )
            
            logger.info(f"Connector {connector_name} produced {len(signals)} signals")
            
        except Exception as e:
            logger.error(f"Error running connector {connector_name}: {e}")
            
            # Record failure
            self.health_monitor.record_run_complete(
                connector_name=connector_name,
                signals_count=0,
                success=False,
                error=str(e),
            )
            
            # Log event
            self.store.add_event(ConnectorEvent(
                connector_name=connector_name,
                event_type="sync_error",
                status="failure",
                message=str(e),
                error_type=type(e).__name__,
                error_message=str(e),
            ))
        
        return signals
    
    async def run_all_connectors(self) -> Dict[str, List[ConnectorSignal]]:
        """Run all enabled connectors."""
        results = {}
        connectors = self.registry.get_enabled_connectors()
        
        for connector in connectors:
            signals = await self.run_connector(connector.name)
            results[connector.name] = signals
        
        return results
    
    # Query Methods
    
    def get_connector(self, name: str) -> Optional[ConnectorSource]:
        """Get a connector by name."""
        return self.registry.get_connector(name)
    
    def get_all_connectors(self) -> List[ConnectorSource]:
        """Get all registered connectors."""
        return self.registry.get_all_connectors()
    
    def get_enabled_connectors(self) -> List[ConnectorSource]:
        """Get all enabled connectors."""
        return self.registry.get_enabled_connectors()
    
    def get_connector_health(self, name: str) -> Optional[Any]:
        """Get health metrics for a connector."""
        return self.health_monitor.get_health(name)
    
    def get_all_health(self) -> List[Any]:
        """Get health for all connectors."""
        return self.health_monitor.get_all_health()
    
    def get_recent_signals(
        self,
        connector_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[ConnectorSignal]:
        """Get recent signals from connectors."""
        events = self.store.get_events(
            connector_name=connector_name,
            limit=limit,
        )
        
        # Filter for sync_complete events and extract signals
        signals = []
        for event in events:
            if event.event_type == "sync_complete" and event.signals_count > 0:
                # This is a simplified version - in production you'd query a signal store
                pass
        
        return signals
    
    def get_connector_status(self) -> Dict[str, Any]:
        """Get status of all connectors."""
        connectors = self.get_all_connectors()
        health = {h.connector_name: h for h in self.get_all_health()}
        
        status = {
            "total": len(connectors),
            "active": sum(1 for c in connectors if c.enabled),
            "inactive": sum(1 for c in connectors if not c.enabled),
            "connectors": [],
        }
        
        for conn in connectors:
            conn_health = health.get(conn.name)
            status["connectors"].append({
                "name": conn.name,
                "type": conn.connector_type.value,
                "enabled": conn.enabled,
                "status": conn_health.status.value if conn_health else "unknown",
                "last_sync": conn.last_sync.isoformat() if conn.last_sync else None,
                "last_success": conn.last_success.isoformat() if conn.last_success else None,
            })
        
        return status
    
    # Initialization
    
    def initialize_default_connectors(self) -> None:
        """Initialize default connectors."""
        # Calendar connector
        if not self.registry.get_connector("calendar"):
            self.register_connector(
                name="calendar",
                connector_type=ConnectorType.CALENDAR,
                interval_seconds=300,  # 5 minutes
                enabled=False,
            )
        
        # Finance connector
        if not self.registry.get_connector("finance"):
            self.register_connector(
                name="finance",
                connector_type=ConnectorType.FINANCE,
                interval_seconds=1800,  # 30 minutes
                enabled=False,
            )
        
        # Tasks connector
        if not self.registry.get_connector("tasks"):
            self.register_connector(
                name="tasks",
                connector_type=ConnectorType.TASKS,
                interval_seconds=600,  # 10 minutes
                enabled=False,
            )
        
        # Health connector
        if not self.registry.get_connector("health"):
            self.register_connector(
                name="health",
                connector_type=ConnectorType.HEALTH,
                interval_seconds=3600,  # 60 minutes
                enabled=False,
            )
        
        logger.info("Initialized default connectors")


# Global controller instance
_connector_controller: Optional[ConnectorController] = None


def get_connector_controller() -> ConnectorController:
    """Get the global connector controller instance."""
    global _connector_controller
    if _connector_controller is None:
        _connector_controller = ConnectorController()
        _connector_controller.initialize_default_connectors()
    return _connector_controller
