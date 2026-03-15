"""Signal Registry for the Strategic Intelligence Bus.

Maintains all signal types in the system.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from app.intelligence_bus.signal_models import SignalDomain


@dataclass
class SignalDefinition:
    """Definition of a signal type."""
    name: str
    description: str
    domain: SignalDomain
    expected_payload: Dict[str, type]
    default_priority: str
    domain_owner: str


class SignalRegistry:
    """Registry of all signal types in PSIE."""
    
    def __init__(self):
        self._registry: Dict[str, SignalDefinition] = {}
        self._initialize_default_signals()
    
    def _initialize_default_signals(self):
        """Initialize default signal definitions."""
        
        # Finance signals
        self.register(SignalDefinition(
            name="spy_delta_velocity_event",
            description="SPY delta velocity acceleration detected",
            domain=SignalDomain.FINANCE,
            expected_payload={"ticker": str, "direction": str, "velocity": float, "recommended_strike": str},
            default_priority="high",
            domain_owner="FinanceAgent"
        ))
        
        self.register(SignalDefinition(
            name="volatility_regime_shift",
            description="Volatility regime changed",
            domain=SignalDomain.FINANCE,
            expected_payload={"symbol": str, "old_regime": str, "new_regime": str, "iv_change": float},
            default_priority="high",
            domain_owner="OptionsIntelligence"
        ))
        
        self.register(SignalDefinition(
            name="gamma_acceleration_event",
            description="Gamma acceleration detected in options",
            domain=SignalDomain.FINANCE,
            expected_payload={"ticker": str, "gamma_level": float, "acceleration": float},
            default_priority="high",
            domain_owner="OptionsIntelligence"
        ))
        
        self.register(SignalDefinition(
            name="options_liquidity_spike",
            description="Options liquidity changed significantly",
            domain=SignalDomain.FINANCE,
            expected_payload={"ticker": str, "volume_change": float, "spread_change": float},
            default_priority="medium",
            domain_owner="MarketStructureEngine"
        ))
        
        self.register(SignalDefinition(
            name="debt_risk_detected",
            description="Debt risk level elevated",
            domain=SignalDomain.FINANCE,
            expected_payload={"account": str, "risk_level": float, "debt_amount": float},
            default_priority="critical",
            domain_owner="FinanceAgent"
        ))
        
        self.register(SignalDefinition(
            name="investment_opportunity_signal",
            description="Investment opportunity detected",
            domain=SignalDomain.FINANCE,
            expected_payload={"type": str, "confidence": float, "expected_return": float},
            default_priority="high",
            domain_owner="InvestmentStrategist"
        ))
        
        self.register(SignalDefinition(
            name="market_volatility_spike",
            description="Market volatility spike detected",
            domain=SignalDomain.FINANCE,
            expected_payload={"vix_change": float, "symbol": str, "severity": str},
            default_priority="critical",
            domain_owner="MarketStructureEngine"
        ))
        
        # Health signals
        self.register(SignalDefinition(
            name="sleep_degradation_signal",
            description="Sleep quality degraded",
            domain=SignalDomain.HEALTH,
            expected_payload={"hours": float, "quality_score": float, "deviation": float},
            default_priority="high",
            domain_owner="HealthAgent"
        ))
        
        self.register(SignalDefinition(
            name="health_routine_breakdown",
            description="Health routine deviation detected",
            domain=SignalDomain.HEALTH,
            expected_payload={"routine_type": str, "missed_count": int, "streak_broken": bool},
            default_priority="medium",
            domain_owner="HealthAgent"
        ))
        
        # Relationship signals
        self.register(SignalDefinition(
            name="relationship_conflict_signal",
            description="Relationship conflict detected",
            domain=SignalDomain.RELATIONSHIP,
            expected_payload={"person": str, "severity": float, "topic": str},
            default_priority="high",
            domain_owner="RelationshipAgent"
        ))
        
        # Career signals
        self.register(SignalDefinition(
            name="career_opportunity_detected",
            description="Career opportunity identified",
            domain=SignalDomain.CAREER,
            expected_payload={"type": str, "relevance": float, "effort_estimate": str},
            default_priority="medium",
            domain_owner="CareerAgent"
        ))
        
        # Strategic signals
        self.register(SignalDefinition(
            name="mkp_framework_added",
            description="New MKP framework added",
            domain=SignalDomain.STRATEGIC,
            expected_payload={"framework": str, "source": str},
            default_priority="low",
            domain_owner="KnowledgePlatform"
        ))
        
        self.register(SignalDefinition(
            name="governance_approval_required",
            description="Governance approval needed",
            domain=SignalDomain.STRATEGIC,
            expected_payload={"proposal_id": str, "type": str, "urgency": str},
            default_priority="high",
            domain_owner="GovernanceSystem"
        ))
    
    def register(self, definition: SignalDefinition) -> None:
        """Register a signal type."""
        self._registry[definition.name] = definition
    
    def get(self, signal_type: str) -> Optional[SignalDefinition]:
        """Get signal definition."""
        return self._registry.get(signal_type)
    
    def get_by_domain(self, domain: SignalDomain) -> List[SignalDefinition]:
        """Get all signals for a domain."""
        return [d for d in self._registry.values() if d.domain == domain]
    
    def list_all(self) -> List[str]:
        """List all registered signal types."""
        return list(self._registry.keys())
    
    def get_domain_owner(self, signal_type: str) -> Optional[str]:
        """Get domain owner for a signal type."""
        definition = self.get(signal_type)
        return definition.domain_owner if definition else None


# Global registry
_registry = None

def get_registry() -> SignalRegistry:
    """Get global signal registry."""
    global _registry
    if _registry is None:
        _registry = SignalRegistry()
    return _registry
