"""
BB-APP-003: Event Bus

Internal event bus for application layer state synchronization.
Per BB-APP-003 Section 6 - Event Bus for Application Layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List
from enum import Enum


class ApplicationEventType(str, Enum):
    """Application event types."""
    # Recommendation events
    RECOMMENDATION_APPROVED = "recommendation_approved"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    RECOMMENDATION_DEFERRED = "recommendation_deferred"
    RECOMMENDATION_CONVERTED = "recommendation_converted"
    
    # Action events
    ACTION_CREATED = "action_created"
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    ACTION_BLOCKED = "action_blocked"
    ACTION_CANCELED = "action_canceled"
    ACTION_OUTCOME_RECORDED = "action_outcome_recorded"
    
    # Read model events
    READ_MODEL_UPDATED = "read_model_updated"
    
    # System events
    SYSTEM_STATE_CHANGED = "system_state_changed"


@dataclass
class ApplicationEvent:
    """Application event."""
    event_type: ApplicationEventType
    entity_type: str
    entity_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


EventHandler = Callable[[ApplicationEvent], None]


class EventBus:
    """Internal event bus for application layer."""
    
    def __init__(self):
        self._handlers: Dict[ApplicationEventType, List[EventHandler]] = {}
        self._event_history: List[ApplicationEvent] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: ApplicationEventType, handler: EventHandler):
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: ApplicationEventType, handler: EventHandler):
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
    
    def publish(self, event: ApplicationEvent):
        """Publish an event to all subscribers."""
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Notify handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log but don't fail
                    print(f"Event handler error: {e}")
    
    def get_event_history(
        self,
        event_type: ApplicationEventType = None,
        entity_type: str = None,
        limit: int = 100
    ) -> List[ApplicationEvent]:
        """Get event history with optional filters."""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if entity_type:
            events = [e for e in events if e.entity_type == entity_type]
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history."""
        self._event_history = []


# Singleton instance
event_bus = EventBus()


# ============== Event Factory ==============

class EventFactory:
    """Factory for creating application events."""
    
    @staticmethod
    def recommendation_approved(recommendation_id: str, user_id: str, domain: str) -> ApplicationEvent:
        """Create recommendation approved event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.RECOMMENDATION_APPROVED,
            entity_type="recommendation",
            entity_id=recommendation_id,
            data={
                "user_id": user_id,
                "domain": domain,
            }
        )
    
    @staticmethod
    def recommendation_rejected(recommendation_id: str, user_id: str, reason: str) -> ApplicationEvent:
        """Create recommendation rejected event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.RECOMMENDATION_REJECTED,
            entity_type="recommendation",
            entity_id=recommendation_id,
            data={
                "user_id": user_id,
                "reason": reason,
            }
        )
    
    @staticmethod
    def recommendation_deferred(recommendation_id: str, user_id: str, reason: str) -> ApplicationEvent:
        """Create recommendation deferred event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.RECOMMENDATION_DEFERRED,
            entity_type="recommendation",
            entity_id=recommendation_id,
            data={
                "user_id": user_id,
                "reason": reason,
            }
        )
    
    @staticmethod
    def recommendation_converted(recommendation_id: str, action_id: str, user_id: str) -> ApplicationEvent:
        """Create recommendation converted to action event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.RECOMMENDATION_CONVERTED,
            entity_type="recommendation",
            entity_id=recommendation_id,
            data={
                "user_id": user_id,
                "action_id": action_id,
            }
        )
    
    @staticmethod
    def action_created(action_id: str, user_id: str, domain: str, from_recommendation: bool = False) -> ApplicationEvent:
        """Create action created event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.ACTION_CREATED,
            entity_type="action",
            entity_id=action_id,
            data={
                "user_id": user_id,
                "domain": domain,
                "from_recommendation": from_recommendation,
            }
        )
    
    @staticmethod
    def action_started(action_id: str, user_id: str) -> ApplicationEvent:
        """Create action started event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.ACTION_STARTED,
            entity_type="action",
            entity_id=action_id,
            data={
                "user_id": user_id,
            }
        )
    
    @staticmethod
    def action_completed(action_id: str, user_id: str, success_score: float) -> ApplicationEvent:
        """Create action completed event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.ACTION_COMPLETED,
            entity_type="action",
            entity_id=action_id,
            data={
                "user_id": user_id,
                "success_score": success_score,
            }
        )
    
    @staticmethod
    def action_outcome_recorded(action_id: str, user_id: str, outcome_id: str) -> ApplicationEvent:
        """Create action outcome recorded event."""
        return ApplicationEvent(
            event_type=ApplicationEventType.ACTION_OUTCOME_RECORDED,
            entity_type="action",
            entity_id=action_id,
            data={
                "user_id": user_id,
                "outcome_id": outcome_id,
            }
        )


# ============== Event Handlers ==============

def update_dashboard_on_event(event: ApplicationEvent):
    """Event handler that would update dashboard read models."""
    # In production, this would trigger dashboard cache invalidation
    pass


def update_domain_view_on_event(event: ApplicationEvent):
    """Event handler that would update domain view read models."""
    # In production, this would trigger domain cache invalidation
    pass


def update_brief_on_event(event: ApplicationEvent):
    """Event handler that would update executive brief."""
    # In production, this would trigger brief cache invalidation
    pass


# Register default handlers
event_bus.subscribe(ApplicationEventType.RECOMMENDATION_APPROVED, update_dashboard_on_event)
event_bus.subscribe(ApplicationEventType.RECOMMENDATION_REJECTED, update_dashboard_on_event)
event_bus.subscribe(ApplicationEventType.RECOMMENDATION_DEFERRED, update_dashboard_on_event)
event_bus.subscribe(ApplicationEventType.RECOMMENDATION_CONVERTED, update_dashboard_on_event)
event_bus.subscribe(ApplicationEventType.ACTION_COMPLETED, update_dashboard_on_event)
