"""Signal router for dispatching signals to subsystems."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.signal_ingestion.signal_models import (
    NormalizedSignal,
    SignalType,
)

logger = logging.getLogger(__name__)


class SignalRouter:
    """Routes validated signals to appropriate subsystems."""

    def __init__(self):
        self._routes: Dict[str, List[str]] = {
            # Performance signals
            SignalType.PERFORMANCE: ["forecasting", "optimization", "state"],
            SignalType.HEALTH: ["forecasting", "optimization", "state"],
            SignalType.WEALTH: ["forecasting", "optimization", "state"],
            SignalType.CAREER: ["forecasting", "optimization", "state"],
            SignalType.RELATIONSHIPS: ["forecasting", "optimization", "state"],
            SignalType.LEARNING: ["forecasting", "optimization", "state"],
            # Risk signals
            SignalType.RISK: ["forecasting", "optimization", "state"],
            # Opportunity signals
            SignalType.OPPORTUNITY: ["optimization", "state"],
            # Resource signals
            SignalType.RESOURCE: ["optimization", "state"],
            # Momentum signals
            SignalType.MOMENTUM: ["forecasting", "state"],
            # Alignment signals
            SignalType.ALIGNMENT: ["optimization", "state"],
            # Custom signals
            SignalType.CUSTOM: ["optimization"],
        }
        self._subscribers: Dict[str, List[callable]] = {}
        self._routing_log: List[Dict[str, Any]] = []

    def route_signal(
        self,
        signal: NormalizedSignal
    ) -> List[str]:
        """Route a signal to appropriate subsystems."""
        destinations = self._get_destinations(signal.signal_type)

        # Log routing decision
        routing_event = {
            "signal_id": signal.signal_id,
            "source_id": signal.source_id,
            "signal_type": signal.signal_type.value,
            "destinations": destinations,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._routing_log.append(routing_event)

        # Route to each destination
        for destination in destinations:
            self._dispatch_to_destination(signal, destination)

        logger.info(
            f"Routed signal {signal.signal_id} to {destinations}"
        )

        return destinations

    def _get_destinations(self, signal_type: SignalType) -> List[str]:
        """Get destination subsystems for a signal type."""
        return self._routes.get(signal_type, ["optimization"])

    def _dispatch_to_destination(
        self,
        signal: NormalizedSignal,
        destination: str
    ):
        """Dispatch signal to a specific destination subsystem."""
        # Check for subscribers
        if destination in self._subscribers:
            for callback in self._subscribers[destination]:
                try:
                    callback(signal)
                except Exception as e:
                    logger.error(
                        f"Error dispatching to {destination}: {e}"
                    )

        # Route based on destination type
        if destination == "forecasting":
            self._route_to_forecasting(signal)
        elif destination == "optimization":
            self._route_to_optimization(signal)
        elif destination == "state":
            self._route_to_state(signal)

    def _route_to_forecasting(self, signal: NormalizedSignal):
        """Route signal to forecasting engine."""
        try:
            from app.forecasting.trend_analyzer import TrendAnalyzer
            
            # Convert to domain and scores
            domain = self._signal_to_domain(signal.signal_type)
            if domain and "performance_score" in signal.normalized_payload:
                # Note: This would integrate with actual forecasting
                logger.debug(
                    f"Would route to forecasting: domain={domain}, "
                    f"perf={signal.normalized_payload.get('performance_score')}"
                )
        except Exception as e:
            logger.error(f"Forecasting routing error: {e}")

    def _route_to_optimization(self, signal: NormalizedSignal):
        """Route signal to optimization engine."""
        try:
            logger.debug(
                f"Would route to optimization: "
                f"type={signal.signal_type.value}, "
                f"payload={signal.normalized_payload}"
            )
        except Exception as e:
            logger.error(f"Optimization routing error: {e}")

    def _route_to_state(self, signal: NormalizedSignal):
        """Route signal to state engine."""
        try:
            logger.debug(
                f"Would route to state: "
                f"type={signal.signal_type.value}, "
                f"confidence={signal.confidence_score}"
            )
        except Exception as e:
            logger.error(f"State routing error: {e}")

    def _signal_to_domain(self, signal_type: SignalType) -> Optional[str]:
        """Convert signal type to domain name."""
        domain_map = {
            SignalType.HEALTH: "health",
            SignalType.WEALTH: "wealth",
            SignalType.CAREER: "career",
            SignalType.RELATIONSHIPS: "relationships",
            SignalType.LEARNING: "learning",
        }
        return domain_map.get(signal_type)

    def subscribe(self, destination: str, callback: callable):
        """Subscribe to signals for a destination."""
        if destination not in self._subscribers:
            self._subscribers[destination] = []
        self._subscribers[destination].append(callback)
        logger.info(f"Subscribed to {destination}")

    def unsubscribe(self, destination: str, callback: callable):
        """Unsubscribe from signals."""
        if destination in self._subscribers:
            try:
                self._subscribers[destination].remove(callback)
                logger.info(f"Unsubscribed from {destination}")
            except ValueError:
                pass

    def add_route(self, signal_type: SignalType, destinations: List[str]):
        """Add or update a route mapping."""
        self._routes[signal_type.value] = destinations

    def get_routing_log(self) -> List[Dict[str, Any]]:
        """Get the routing log."""
        return self._routing_log.copy()

    def clear_routing_log(self):
        """Clear the routing log."""
        self._routing_log.clear()


# Global router instance
_router: Optional[SignalRouter] = None


def get_signal_router() -> SignalRouter:
    """Get the global signal router instance."""
    global _router
    if _router is None:
        _router = SignalRouter()
    return _router
