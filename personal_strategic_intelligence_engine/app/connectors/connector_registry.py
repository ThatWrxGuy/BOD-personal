"""Connector Registry.

Central registry for managing connectors.
"""
from typing import Any, Dict, List, Optional, Type

from app.connectors.connector_models import (
    ConnectorSource,
    ConnectorStatus,
    ConnectorType,
)
from app.connectors.connector_store import get_connector_store


class ConnectorRegistry:
    """Central registry for connectors."""
    
    def __init__(self):
        self.store = get_connector_store()
        self._connector_classes: Dict[str, Type] = {}
    
    def register_connector_class(
        self,
        name: str,
        connector_class: Type,
    ) -> None:
        """Register a connector class."""
        self._connector_classes[name] = connector_class
    
    def get_connector_class(self, name: str) -> Optional[Type]:
        """Get a connector class by name."""
        return self._connector_classes.get(name)
    
    def register_connector(
        self,
        name: str,
        connector_type: ConnectorType,
        config: Optional[Dict[str, Any]] = None,
        credentials: Optional[Dict[str, str]] = None,
        interval_seconds: int = 300,
    ) -> ConnectorSource:
        """Register a new connector."""
        source = ConnectorSource(
            name=name,
            connector_type=connector_type,
            status=ConnectorStatus.INACTIVE,
            enabled=False,
            config=config or {},
            credentials=credentials or {},
            interval_seconds=interval_seconds,
        )
        
        self.store.save_source(source)
        return source
    
    def enable_connector(self, name: str) -> bool:
        """Enable a connector."""
        source = self.store.get_source(name)
        if not source:
            return False
        
        source.enabled = True
        source.status = ConnectorStatus.ACTIVE
        self.store.save_source(source)
        return True
    
    def disable_connector(self, name: str) -> bool:
        """Disable a connector."""
        source = self.store.get_source(name)
        if not source:
            return False
        
        source.enabled = False
        source.status = ConnectorStatus.DISABLED
        self.store.save_source(source)
        return True
    
    def get_connector(self, name: str) -> Optional[ConnectorSource]:
        """Get a connector by name."""
        return self.store.get_source(name)
    
    def get_all_connectors(self) -> List[ConnectorSource]:
        """Get all registered connectors."""
        return self.store.get_all_sources()
    
    def get_enabled_connectors(self) -> List[ConnectorSource]:
        """Get all enabled connectors."""
        all_connectors = self.store.get_all_sources()
        return [c for c in all_connectors if c.enabled]
    
    def update_connector(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        credentials: Optional[Dict[str, str]] = None,
        interval_seconds: Optional[int] = None,
    ) -> bool:
        """Update connector configuration."""
        source = self.store.get_source(name)
        if not source:
            return False
        
        if config:
            source.config.update(config)
        if credentials:
            source.credentials.update(credentials)
        if interval_seconds:
            source.interval_seconds = interval_seconds
        
        self.store.save_source(source)
        return True
    
    def delete_connector(self, name: str) -> bool:
        """Delete a connector."""
        return self.store.delete_source(name) is not None
    
    def list_connector_types(self) -> List[str]:
        """List available connector types."""
        return list(self._connector_classes.keys())


# Global registry instance
_connector_registry: Optional[ConnectorRegistry] = None


def get_connector_registry() -> ConnectorRegistry:
    """Get the global connector registry instance."""
    global _connector_registry
    if _connector_registry is None:
        _connector_registry = ConnectorRegistry()
    return _connector_registry
