"""Connector Store.

Persists connector events and metadata.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.connectors.connector_models import (
    ConnectorEvent,
    ConnectorHealth,
    ConnectorSource,
    ConnectorStatus,
)


class ConnectorStore:
    """Store for connector data persistence."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to data directory
            base_path = Path(__file__).parent.parent.parent / "data" / "connectors"
            self.storage_path = base_path
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._sources_file = self.storage_path / "sources.json"
        self._health_file = self.storage_path / "health.json"
        self._events_file = self.storage_path / "events.json"
        
        # Initialize files if they don't exist
        if not self._sources_file.exists():
            self._write_json(self._sources_file, {})
        if not self._health_file.exists():
            self._write_json(self._health_file, {})
        if not self._events_file.exists():
            self._write_json(self._events_file, [])
    
    def _read_json(self, filepath: Path) -> Any:
        """Read JSON from file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _write_json(self, filepath: Path, data: Any) -> None:
        """Write JSON to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Connector Sources
    
    def save_source(self, source: ConnectorSource) -> None:
        """Save a connector source."""
        sources = self._read_json(self._sources_file) or {}
        sources[source.name] = source.model_dump()
        self._write_json(self._sources_file, sources)
    
    def get_source(self, name: str) -> Optional[ConnectorSource]:
        """Get a connector source by name."""
        sources = self._read_json(self._sources_file) or {}
        data = sources.get(name)
        if data:
            return ConnectorSource(**data)
        return None
    
    def get_all_sources(self) -> List[ConnectorSource]:
        """Get all connector sources."""
        sources = self._read_json(self._sources_file) or {}
        return [ConnectorSource(**v) for v in sources.values()]
    
    def delete_source(self, name: str) -> None:
        """Delete a connector source."""
        sources = self._read_json(self._sources_file) or {}
        sources.pop(name, None)
        self._write_json(self._sources_file, sources)
    
    # Connector Health
    
    def save_health(self, health: ConnectorHealth) -> None:
        """Save connector health metrics."""
        health_data = self._read_json(self._health_file) or {}
        health_data[health.connector_name] = health.model_dump()
        self._write_json(self._health_file, health_data)
    
    def get_health(self, name: str) -> Optional[ConnectorHealth]:
        """Get connector health by name."""
        health_data = self._read_json(self._health_file) or {}
        data = health_data.get(name)
        if data:
            return ConnectorHealth(**data)
        return None
    
    def get_all_health(self) -> List[ConnectorHealth]:
        """Get all connector health records."""
        health_data = self._read_json(self._health_file) or {}
        return [ConnectorHealth(**v) for v in health_data.values()]
    
    # Connector Events
    
    def add_event(self, event: ConnectorEvent) -> None:
        """Add a connector event."""
        events = self._read_json(self._events_file) or []
        events.append(event.model_dump())
        
        # Keep only last 1000 events
        if len(events) > 1000:
            events = events[-1000:]
        
        self._write_json(self._events_file, events)
    
    def get_events(
        self,
        connector_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[ConnectorEvent]:
        """Get connector events."""
        events = self._read_json(self._events_file) or []
        
        if connector_name:
            events = [e for e in events if e.get("connector_name") == connector_name]
        
        # Return most recent
        return [ConnectorEvent(**e) for e in events[-limit:]]
    
    def clear_events(self, connector_name: Optional[str] = None) -> None:
        """Clear connector events."""
        if connector_name:
            events = self._read_json(self._events_file) or []
            events = [e for e in events if e.get("connector_name") != connector_name]
            self._write_json(self._events_file, events)
        else:
            self._write_json(self._events_file, [])


# Global store instance
_connector_store: Optional[ConnectorStore] = None


def get_connector_store() -> ConnectorStore:
    """Get the global connector store instance."""
    global _connector_store
    if _connector_store is None:
        _connector_store = ConnectorStore()
    return _connector_store
