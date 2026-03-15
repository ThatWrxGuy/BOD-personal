"""Cross-Agent Finance Coordination for SPY 0DTE Tactical Agent.

Coordinates tactical signals with other finance intelligence components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class FinanceAgentType(str, Enum):
    """Types of finance agents."""
    TACTICAL_OPTIONS = "tactical_options"
    PORTFOLIO_ALLOCATOR = "portfolio_allocator"
    INVESTMENT_STRATEGIST = "investment_strategist"
    RISK_MANAGER = "risk_manager"
    LIQUIDITY_MONITOR = "liquidity_monitor"
    MACRO_ENGINE = "macro_engine"


class ConflictType(str, Enum):
    """Types of conflicts between finance agents."""
    DIRECTIONAL = "directional"
    CAPITAL = "capital"
    EXPOSURE = "exposure"
    REGIME = "regime"
    CONCENTRATION = "concentration"
    POLICY = "policy"


@dataclass
class FinanceAgentState:
    """State of a finance agent at a point in time."""
    agent_type: FinanceAgentType
    timestamp: datetime
    current_position: str
    confidence: float
    risk_posture: str
    key_thesis: str


@dataclass
class FinanceConflict:
    """Conflict detected between finance agents."""
    conflict_id: str
    timestamp: datetime
    conflict_type: ConflictType
    involved_agents: list[FinanceAgentType]
    description: str
    severity: str
    resolution: Optional[str] = None
    resolved: bool = False
    
    def to_dict(self) -> dict:
        return {
            "conflict_id": self.conflict_id,
            "timestamp": self.timestamp.isoformat(),
            "conflict_type": self.conflict_type.value,
            "involved_agents": [a.value for a in self.involved_agents],
            "description": self.description,
            "severity": self.severity,
            "resolution": self.resolution,
            "resolved": self.resolved,
        }


@dataclass
class CoordinationResult:
    """Result of cross-agent coordination."""
    has_conflicts: bool
    conflicts: list[FinanceConflict]
    warnings: list[str]
    recommendations: list[str]
    consensus_position: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "has_conflicts": self.has_conflicts,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "consensus_position": self.consensus_position,
        }


class CrossAgentCoordinator:
    """
    Coordinates tactical signals with other finance agents.
    """
    
    def __init__(self):
        self.agent_states: dict = {}
        self.conflicts: list = []
        self.conflict_counter: int = 0
    
    def register_agent_state(self, state: FinanceAgentState) -> None:
        """Register current state of a finance agent."""
        self.agent_states[state.agent_type] = state
    
    def check_tactical_conflicts(self, tactical_signal, regime_context=None) -> CoordinationResult:
        """Check tactical signal for conflicts with other agents."""
        conflicts = []
        warnings = []
        recommendations = []
        
        tactical_direction = "bullish" if tactical_signal.option_type.value == "call" else "bearish"
        
        for agent_type, state in self.agent_states.items():
            if agent_type == FinanceAgentType.TACTICAL_OPTIONS:
                continue
            
            if state.current_position in ["bearish", "defensive"] and tactical_direction == "bullish":
                conflict = self._create_conflict(
                    ConflictType.DIRECTIONAL,
                    [FinanceAgentType.TACTICAL_OPTIONS, agent_type],
                    f"Tactical bullish vs {agent_type.value} {state.current_position}",
                    "high" if state.current_position == "defensive" else "medium",
                )
                conflicts.append(conflict)
                recommendations.append(f"Review: Tactical bullish conflicts with {agent_type.value}")
            
            elif state.current_position == "bullish" and tactical_direction == "bearish":
                conflict = self._create_conflict(
                    ConflictType.DIRECTIONAL,
                    [FinanceAgentType.TACTICAL_OPTIONS, agent_type],
                    f"Tactical bearish vs {agent_type.value} bullish",
                    "medium",
                )
                conflicts.append(conflict)
            
            if state.risk_posture == "defensive":
                warnings.append(f"{agent_type.value} in defensive posture")
                recommendations.append("Consider reduced position size")
        
        if regime_context:
            if regime_context.regime.value == "volatility_expansion":
                warnings.append("Volatility expansion regime - reduce exposure")
            if regime_context.regime.value == "range_chop":
                warnings.append("Range/chop regime - consider deferring")
        
        return CoordinationResult(
            has_conflicts=len(conflicts) > 0,
            conflicts=conflicts,
            warnings=warnings,
            recommendations=recommendations,
            consensus_position=None,
        )
    
    def _create_conflict(self, conflict_type, involved_agents, description, severity):
        self.conflict_counter += 1
        return FinanceConflict(
            conflict_id=f"CONFLICT-{self.conflict_counter:06d}",
            timestamp=datetime.now(),
            conflict_type=conflict_type,
            involved_agents=involved_agents,
            description=description,
            severity=severity,
        )
    
    def get_active_conflicts(self) -> list:
        return [c for c in self.conflicts if not c.resolved]
    
    def resolve_conflict(self, conflict_id: str, resolution: str) -> bool:
        for conflict in self.conflicts:
            if conflict.conflict_id == conflict_id:
                conflict.resolved = True
                conflict.resolution = resolution
                return True
        return False
    
    def get_conflict_summary(self) -> dict:
        active = self.get_active_conflicts()
        by_type = {}
        by_severity = {}
        for conflict in active:
            ct = conflict.conflict_type.value
            by_type[ct] = by_type.get(ct, 0) + 1
            sev = conflict.severity
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {"total_active": len(active), "by_type": by_type, "by_severity": by_severity}
    
    def register_default_states(self) -> None:
        self.register_agent_state(FinanceAgentState(
            agent_type=FinanceAgentType.RISK_MANAGER,
            timestamp=datetime.now(),
            current_position="neutral",
            confidence=0.7,
            risk_posture="neutral",
            key_thesis="Monitor volatility",
        ))
        self.register_agent_state(FinanceAgentState(
            agent_type=FinanceAgentType.INVESTMENT_STRATEGIST,
            timestamp=datetime.now(),
            current_position="neutral",
            confidence=0.6,
            risk_posture="neutral",
            key_thesis="Balanced allocation",
        ))


_coordinator: Optional[CrossAgentCoordinator] = None

def get_coordinator() -> CrossAgentCoordinator:
    global _coordinator
    if _coordinator is None:
        _coordinator = CrossAgentCoordinator()
        _coordinator.register_default_states()
    return _coordinator
