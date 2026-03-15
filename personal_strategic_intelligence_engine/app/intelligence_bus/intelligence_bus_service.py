"""Strategic Intelligence Bus Service.

Main service interface for the intelligence bus.
"""

from typing import Dict, List, Optional

from app.intelligence_bus.signal_models import (
    Signal, SignalDomain, SignalPriority, SignalResolution
)
from app.intelligence_bus.signal_bus import get_bus, publish_signal
from app.intelligence_bus.signal_router import get_router
from app.intelligence_bus.signal_registry import get_registry
from app.intelligence_bus.priority_queue import get_queue
from app.intelligence_bus.event_log import get_event_log


class IntelligenceBusService:
    """Main service for the Strategic Intelligence Bus."""
    
    def __init__(self):
        self.bus = get_bus()
        self.router = get_router()
        self.registry = get_registry()
        self.queue = get_queue()
        self.event_log = get_event_log()
    
    def publish(self, signal: Signal) -> str:
        """Publish a signal to the bus."""
        self.event_log.log_signal(signal)
        return self.bus.publish_signal(signal)
    
    def subscribe_agent(self, agent: str, signal_types: List[str]) -> None:
        """Subscribe an agent to signal types."""
        for signal_type in signal_types:
            self.router.add_subscriber(signal_type, agent)
    
    def get_pending(self, agent: str) -> List[Dict]:
        """Get pending signals for an agent."""
        signals = self.bus.get_pending_signals(agent)
        return [s.to_dict() for s in signals]
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get signal history."""
        signals = self.bus.get_signal_history(limit)
        return [s.to_dict() for s in signals]
    
    def get_stats(self) -> Dict:
        """Get bus statistics."""
        return self.bus.get_bus_stats()
    
    def list_signals(self) -> List[str]:
        """List all registered signal types."""
        return self.registry.list_all()
    
    def list_routes(self) -> Dict[str, List[str]]:
        """List all routing rules."""
        return self.router.list_routes()


def create_service() -> IntelligenceBusService:
    """Create intelligence bus service."""
    return IntelligenceBusService()
