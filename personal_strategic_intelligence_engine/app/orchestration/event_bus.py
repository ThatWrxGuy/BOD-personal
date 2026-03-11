"""Event Bus - Central messaging mechanism for domain events."""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestration.event_types import DomainEvent, EventType
from app.models.orchestration import EventRecord
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """Central event bus for PSIE domain events."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe a synchronous handler to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")
    
    def subscribe_async(self, event_type: str, handler: Callable) -> None:
        """Subscribe an async handler to an event type."""
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
        self._async_subscribers[event_type].append(handler)
        logger.info(f"Subscribed async handler to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]
    
    async def publish_event(
        self,
        event: DomainEvent,
        persist: bool = True,
    ) -> None:
        """Publish an event to all subscribers."""
        
        logger.info(f"Publishing event: {event.event_type}")
        
        # Persist event
        if persist:
            await self._persist_event(event)
        
        # Call synchronous handlers
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in sync handler for {event.event_type}: {e}")
        
        # Call async handlers
        async_handlers = self._async_subscribers.get(event.event_type, [])
        for handler in async_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in async handler for {event.event_type}: {e}")
        
        # Also call wildcard subscribers
        wildcard_handlers = self._subscribers.get("*", [])
        for handler in wildcard_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in wildcard handler: {e}")
        
        wildcard_async = self._async_subscribers.get("*", [])
        for handler in wildcard_async:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in wildcard async handler: {e}")
    
    async def _persist_event(self, event: DomainEvent) -> None:
        """Persist event to database."""
        
        record = EventRecord(
            event_id=event.event_id,
            event_type=event.event_type,
            source=event.source_module,
            payload=event.payload,
            timestamp=event.timestamp,
            correlation_id=event.correlation_id,
            workflow_id=event.workflow_id,
        )
        
        self.session.add(record)
        await self.session.commit()
        
        logger.debug(f"Persisted event {event.event_id}")
    
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Get list of subscribers for an event type."""
        return self._subscribers.get(event_type, [])


class InMemoryEventBus(EventBus):
    """In-memory event bus for testing."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable]] = {}
        self._published_events: List[DomainEvent] = []
    
    async def publish_event(
        self,
        event: DomainEvent,
        persist: bool = False,
    ) -> None:
        """Publish event in memory."""
        self._published_events.append(event)
        await super().publish_event(event, persist=False)
    
    def get_published_events(self) -> List[DomainEvent]:
        """Get all published events."""
        return self._published_events
    
    def clear_events(self) -> None:
        """Clear published events."""
        self._published_events.clear()


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus(session: Optional[AsyncSession] = None) -> EventBus:
    """Get or create the global event bus."""
    global _event_bus
    
    if session is None:
        # Return in-memory bus for testing
        return InMemoryEventBus()
    
    if _event_bus is None:
        _event_bus = EventBus(session)
    
    return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _event_bus
    _event_bus = None
