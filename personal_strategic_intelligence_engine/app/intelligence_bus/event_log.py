"""Event Log for the Strategic Intelligence Bus.

Maintains a complete record of system signals.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from app.intelligence_bus.signal_models import Signal, SignalEvent


class EventLog:
    """Maintains a complete record of system signals."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.events_file = self.storage_path / "signal_events.jsonl"
    
    def log_signal(self, signal: Signal) -> None:
        """Log a signal event."""
        
        event = SignalEvent(
            signal_id=signal.id,
            event_type="signal_published",
            timestamp=datetime.now(),
            details={
                "type": signal.type,
                "domain": signal.domain.value,
                "source": signal.source,
                "priority": signal.priority.value,
                "confidence": signal.confidence,
            }
        )
        
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
    
    def log_resolution(self, signal_id: str, resolution: str, outcome: Optional[str] = None) -> None:
        """Log signal resolution."""
        
        event = SignalEvent(
            signal_id=signal_id,
            event_type="signal_resolved",
            timestamp=datetime.now(),
            details={
                "resolution": resolution,
                "outcome": outcome,
            }
        )
        
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
    
    def log_agent_action(self, signal_id: str, agent: str, action: str) -> None:
        """Log agent action on signal."""
        
        event = SignalEvent(
            signal_id=signal_id,
            event_type="agent_action",
            timestamp=datetime.now(),
            details={
                "agent": agent,
                "action": action,
            }
        )
        
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
    
    def get_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events."""
        
        if not self.events_file.exists():
            return []
        
        events = []
        with open(self.events_file, "r") as f:
            for line in f:
                try:
                    events.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return events[-limit:]
    
    def get_signal_events(self, signal_id: str) -> List[Dict]:
        """Get all events for a specific signal."""
        
        all_events = self.get_events(limit=10000)
        return [e for e in all_events if e.get("signal_id") == signal_id]
    
    def get_summary(self) -> Dict:
        """Get event log summary."""
        
        events = self.get_events(limit=1000)
        
        event_types = {}
        for event in events:
            etype = event.get("event_type", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1
        
        return {
            "total_events": len(events),
            "event_types": event_types,
        }


# Global log
_log = None

def get_event_log() -> EventLog:
    """Get global event log."""
    global _log
    if _log is None:
        _log = EventLog()
    return _log
