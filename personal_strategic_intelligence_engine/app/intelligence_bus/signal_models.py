"""Signal Models for the Strategic Intelligence Bus.

Defines the core signal structure used across PSIE.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class SignalDomain(str, Enum):
    FINANCE = "finance"
    HEALTH = "health"
    RELATIONSHIP = "relationship"
    CAREER = "career"
    OPERATIONS = "operations"
    STRATEGIC = "strategic"


class SignalPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class SignalResolution(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


@dataclass
class Signal:
    """Core signal structure for the intelligence bus."""
    id: str
    type: str
    domain: SignalDomain
    source: str
    timestamp: datetime
    priority: SignalPriority
    payload: Dict[str, Any]
    confidence: float
    context_tags: List[str] = field(default_factory=list)
    resolution: SignalResolution = SignalResolution.PENDING
    outcome: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "domain": self.domain.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "payload": self.payload,
            "confidence": self.confidence,
            "context_tags": self.context_tags,
            "resolution": self.resolution.value,
            "outcome": self.outcome,
        }
    
    @staticmethod
    def create(
        signal_type: str,
        domain: SignalDomain,
        source: str,
        priority: SignalPriority,
        payload: Dict[str, Any],
        confidence: float = 0.5,
        context_tags: Optional[List[str]] = None,
    ) -> "Signal":
        """Create a new signal."""
        return Signal(
            id=str(uuid.uuid4()),
            type=signal_type,
            domain=domain,
            source=source,
            timestamp=datetime.now(),
            priority=priority,
            payload=payload,
            confidence=confidence,
            context_tags=context_tags or [],
        )


# Predefined signal types
FINANCE_SIGNALS = [
    "spy_delta_velocity_event",
    "volatility_regime_shift",
    "gamma_acceleration_event",
    "options_liquidity_spike",
    "debt_risk_detected",
    "investment_opportunity_signal",
    "portfolio_risk_alert",
    "market_volatility_spike",
]

HEALTH_SIGNALS = [
    "sleep_degradation_signal",
    "nutrition_breakdown_signal",
    "exercise_missed_signal",
    "health_routine_breakdown",
    "biomarker_anomaly",
]

RELATIONSHIP_SIGNALS = [
    "relationship_conflict_signal",
    "connection_weakness_detected",
    "social_battery_depleted",
    "important_date_approaching",
]

CAREER_SIGNALS = [
    "career_opportunity_detected",
    "skill_gap_identified",
    "network_expansion_opportunity",
    "workload_escalation",
]

STRATEGIC_SIGNALS = [
    "mkp_framework_added",
    "mkp_strategy_pattern_created",
    "mkp_implementation_mapping_updated",
    "strategic_insight_generated",
    "governance_approval_required",
]


@dataclass
class SignalSubscription:
    """Signal subscription configuration."""
    agent_name: str
    signal_types: List[str]
    min_priority: SignalPriority
    callback_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "signal_types": self.signal_types,
            "min_priority": self.min_priority.value,
            "callback_url": self.callback_url,
        }


@dataclass
class SignalEvent:
    """Signal event for logging."""
    signal_id: str
    event_type: str
    timestamp: datetime
    details: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }
