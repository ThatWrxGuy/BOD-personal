"""Signal Bus for the Strategic Intelligence Bus.

Core event distribution engine.
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime
from collections import defaultdict
import asyncio
import uuid

from app.intelligence_bus.signal_models import Signal, SignalDomain, SignalPriority
from app.intelligence_bus.signal_router import SignalRouter, get_router
from app.intelligence_bus.signal_registry import SignalRegistry, get_registry


class SignalBus:
    """Core event distribution engine for PSIE."""
    
    def __init__(self):
        self.router: SignalRouter = get_router()
        self.registry: SignalRegistry = get_registry()
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._signal_history: List[Signal] = []
        self._pending_signals: Dict[str, List[Signal]] = defaultdict(list)
    
    def publish_signal(self, signal: Signal) -> str:
        """Publish a signal to the bus."""
        
        # Validate signal
        if not self._validate_signal(signal):
            raise ValueError(f"Invalid signal: {signal.type}")
        
        # Store in history
        self._signal_history.append(signal)
        
        # Route to subscribers
        subscribers = self.router.route_signal(signal)
        
        # Queue signal for each subscriber
        for subscriber in subscribers:
            self._pending_signals[subscriber].append(signal)
        
        # Trigger handlers
        self._trigger_handlers(signal)
        
        return signal.id
    
    def _validate_signal(self, signal: Signal) -> bool:
        """Validate signal against registry."""
        
        definition = self.registry.get(signal.type)
        
        if not definition:
            # Allow unregistered signals
            return True
        
        # Validate payload keys
        for key in definition.expected_payload.keys():
            if key not in signal.payload:
                return False
        
        return True
    
    def _trigger_handlers(self, signal: Signal):
        """Trigger registered handlers."""
        
        handlers = self._handlers.get(signal.type, [])
        
        for handler in handlers:
            try:
                handler(signal)
            except Exception as e:
                print(f"Handler error: {e}")
    
    def subscribe_handler(self, signal_type: str, handler: Callable) -> str:
        """Subscribe a handler to a signal type."""
        
        handler_id = str(uuid.uuid4())
        self._handlers[signal_type].append(handler)
        
        return handler_id
    
    def unsubscribe_handler(self, signal_type: str, handler_id: str) -> bool:
        """Unsubscribe a handler."""
        # Note: This is simplified - in production would need handler_id mapping
        return True
    
    def get_pending_signals(self, agent: str) -> List[Signal]:
        """Get pending signals for an agent."""
        
        signals = self._pending_signals.get(agent, [])
        self._pending_signals[agent] = []  # Clear after fetch
        
        return signals
    
    def get_signal_history(self, limit: int = 100) -> List[Signal]:
        """Get signal history."""
        
        return self._signal_history[-limit:]
    
    def get_signals_by_type(self, signal_type: str, limit: int = 50) -> List[Signal]:
        """Get signals by type."""
        
        return [
            s for s in self._signal_history[-200:]
            if s.type == signal_type
        ][-limit:]
    
    def get_signals_by_domain(self, domain: SignalDomain, limit: int = 50) -> List[Signal]:
        """Get signals by domain."""
        
        return [
            s for s in self._signal_history[-200:]
            if s.domain == domain
        ][-limit:]
    
    def get_signals_by_priority(self, priority: SignalPriority, limit: int = 50) -> List[Signal]:
        """Get signals by priority."""
        
        return [
            s for s in self._signal_history[-200:]
            if s.priority == priority
        ][-limit:]
    
    def get_bus_stats(self) -> Dict:
        """Get bus statistics."""
        
        return {
            "total_signals": len(self._signal_history),
            "by_domain": {
                domain.value: len([s for s in self._signal_history if s.domain == domain])
                for domain in SignalDomain
            },
            "by_priority": {
                priority.value: len([s for s in self._signal_history if s.priority == priority])
                for priority in SignalPriority
            },
            "subscribers": len(set(
                sub for route in self.router.list_routes().values()
                for sub in route
            )),
            "handlers": len(self._handlers),
        }


# Global bus
_bus = None

def get_bus() -> SignalBus:
    """Get global signal bus."""
    global _bus
    if _bus is None:
        _bus = SignalBus()
    return _bus


def publish_signal(
    signal_type: str,
    domain: SignalDomain,
    source: str,
    priority: SignalPriority,
    payload: Dict,
    confidence: float = 0.5,
    context_tags: Optional[List[str]] = None,
) -> str:
    """Helper to publish a signal."""
    
    signal = Signal.create(
        signal_type=signal_type,
        domain=domain,
        source=source,
        priority=priority,
        payload=payload,
        confidence=confidence,
        context_tags=context_tags,
    )
    
    bus = get_bus()
    return bus.publish_signal(signal)
