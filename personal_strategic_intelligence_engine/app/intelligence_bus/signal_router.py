"""Signal Router for the Strategic Intelligence Bus.

Routes signals to subscribed agents.
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass

from app.intelligence_bus.signal_models import Signal, SignalPriority


@dataclass
class RouteRule:
    """Routing rule configuration."""
    signal_type: str
    subscribers: List[str]
    priority_override: Optional[SignalPriority] = None


class SignalRouter:
    """Routes signals to subscribed agents."""
    
    def __init__(self):
        self._routes: Dict[str, RouteRule] = {}
        self._agent_subscriptions: Dict[str, Set[str]] = {}
        self._initialize_default_routes()
    
    def _initialize_default_routes(self):
        """Initialize default routing rules."""
        
        # Finance signals
        self.add_route("spy_delta_velocity_event", ["FinanceAgent", "InvestmentStrategist", "RiskManagementAgent"])
        self.add_route("volatility_regime_shift", ["FinanceAgent", "OptionsIntelligence"])
        self.add_route("gamma_acceleration_event", ["FinanceAgent", "OptionsIntelligence"])
        self.add_route("options_liquidity_spike", ["FinanceAgent", "MarketStructureEngine"])
        self.add_route("debt_risk_detected", ["FinanceAgent", "RiskManagementAgent"])
        self.add_route("investment_opportunity_signal", ["FinanceAgent", "InvestmentStrategist"])
        self.add_route("market_volatility_spike", ["FinanceAgent", "RiskManagementAgent"])
        
        # Health signals
        self.add_route("sleep_degradation_signal", ["HealthAgent"])
        self.add_route("health_routine_breakdown", ["HealthAgent"])
        
        # Relationship signals
        self.add_route("relationship_conflict_signal", ["RelationshipAgent"])
        
        # Career signals
        self.add_route("career_opportunity_detected", ["CareerAgent"])
        
        # Strategic signals
        self.add_route("mkp_framework_added", ["KnowledgePlatform", "InvestmentStrategist"])
        self.add_route("governance_approval_required", ["GovernanceSystem"])
    
    def add_route(self, signal_type: str, subscribers: List[str]) -> None:
        """Add a routing rule."""
        self._routes[signal_type] = RouteRule(
            signal_type=signal_type,
            subscribers=subscribers,
        )
    
    def remove_route(self, signal_type: str) -> bool:
        """Remove a routing rule."""
        if signal_type in self._routes:
            del self._routes[signal_type]
            return True
        return False
    
    def route_signal(self, signal: Signal) -> List[str]:
        """Route a signal to subscribers."""
        
        # Get route for signal type
        route = self._routes.get(signal.type)
        
        if not route:
            return []
        
        # Filter by priority
        subscribers = route.subscribers
        
        # Apply priority override if exists
        if route.priority_override:
            if signal.priority.value < route.priority_override.value:
                return []
        
        return subscribers
    
    def add_subscriber(self, signal_type: str, agent: str) -> None:
        """Add a subscriber to a signal type."""
        
        if signal_type not in self._routes:
            self._routes[signal_type] = RouteRule(
                signal_type=signal_type,
                subscribers=[],
            )
        
        if agent not in self._routes[signal_type].subscribers:
            self._routes[signal_type].subscribers.append(agent)
        
        # Track agent subscriptions
        if agent not in self._agent_subscriptions:
            self._agent_subscriptions[agent] = set()
        self._agent_subscriptions[agent].add(signal_type)
    
    def remove_subscriber(self, signal_type: str, agent: str) -> bool:
        """Remove a subscriber from a signal type."""
        
        if signal_type in self._routes:
            if agent in self._routes[signal_type].subscribers:
                self._routes[signal_type].subscribers.remove(agent)
                if agent in self._agent_subscriptions:
                    self._agent_subscriptions[agent].discard(signal_type)
                return True
        return False
    
    def get_subscribers(self, signal_type: str) -> List[str]:
        """Get all subscribers for a signal type."""
        route = self._routes.get(signal_type)
        return route.subscribers if route else []
    
    def get_agent_subscriptions(self, agent: str) -> Set[str]:
        """Get all signal types an agent subscribes to."""
        return self._agent_subscriptions.get(agent, set())
    
    def list_routes(self) -> Dict[str, List[str]]:
        """List all routing rules."""
        return {
            signal_type: route.subscribers
            for signal_type, route in self._routes.items()
        }


# Global router
_router = None

def get_router() -> SignalRouter:
    """Get global signal router."""
    global _router
    if _router is None:
        _router = SignalRouter()
    return _router
