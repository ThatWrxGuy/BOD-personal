"""Orchestration Data Models - BB-CORE-021

Core data models for the Strategic Intelligence Orchestrator.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class SystemStatus(str, Enum):
    """Overall system status."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    RESTRICTED = "restricted"
    EMERGENCY = "emergency"
    SHUTDOWN = "shutdown"


class CapitalPosture(str, Enum):
    """Capital deployment posture."""
    DEFENSIVE = "defensive"
    SELECTIVE = "selective"
    NEUTRAL = "neutral"
    OFFENSIVE = "offensive"
    RESTRICTED = "restricted"


class ActivationStatus(str, Enum):
    """Engine activation status."""
    ACTIVE = "active"
    SUPPRESSED = "suppressed"
    RESTRICTED = "restricted"
    UNAVAILABLE = "unavailable"


class PriorityLevel(str, Enum):
    """Priority level for routing."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RegimeType(str, Enum):
    """Market regime types."""
    RISK_ON_TREND = "RISK_ON_TREND"
    RISK_ON_MOMENTUM = "RISK_ON_MOMENTUM"
    NEUTRAL_MIXED = "NEUTRAL_MIXED"
    ROTATION_TRANSITION = "ROTATION_TRANSITION"
    RISK_OFF_DEFENSIVE = "RISK_OFF_DEFENSIVE"
    VOLATILITY_STRESS = "VOLATILITY_STRESS"
    LIQUIDITY_DISLOCATION = "LIQUIDITY_DISLOCATION"
    RANGE_COMPRESSION = "RANGE_COMPRESSION"
    MEAN_REVERSION = "MEAN_REVERSION"
    MACRO_EVENT_UNCERTAINTY = "MACRO_EVENT_UNCERTAINTY"


class EngineStatus(BaseModel):
    """Status of a single engine or subsystem."""
    engine_name: str
    status: ActivationStatus
    last_update: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PortfolioState(BaseModel):
    """Current portfolio state snapshot."""
    total_exposure: float = Field(ge=0.0, le=1.0)
    cash_position: float = Field(ge=0.0, le=1.0)
    sector_exposures: Dict[str, float] = Field(default_factory=dict)
    strategy_allocation: Dict[str, float] = Field(default_factory=dict)
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    drawdown_percent: float = 0.0
    risk_score: float = Field(ge=0.0, le=1.0)


class TacticalOpportunity(BaseModel):
    """A tactical trade or opportunity proposal."""
    opportunity_id: str
    source: str  # e.g., "spy_0dte_agent"
    description: str
    direction: str  # "long" or "short"
    confidence: float = Field(ge=0.0, le=1.0)
    expected_return: float = 0.0
    risk_level: str = "moderate"
    size_recommendation: float = 0.0  # As percent of portfolio


class SystemStateSnapshot(BaseModel):
    """Unified snapshot of all system state."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # System status
    system_status: SystemStatus = SystemStatus.INITIALIZING
    
    # Market context
    current_regime: Optional[RegimeType] = None
    regime_confidence: float = 0.0
    
    # Engine states
    engine_statuses: Dict[str, EngineStatus] = Field(default_factory=dict)
    
    # Portfolio state
    portfolio: Optional[PortfolioState] = None
    
    # Active strategies
    active_strategies: List[str] = Field(default_factory=list)
    approved_strategies: List[str] = Field(default_factory=list)
    restricted_strategies: List[str] = Field(default_factory=list)
    
    # Tactical opportunities
    tactical_opportunities: List[TacticalOpportunity] = Field(default_factory=list)
    
    # Risk state
    risk_status: str = "normal"
    drawdown_breach: bool = False
    max_drawdown_limit: float = 0.10
    
    # Governance
    execution_enabled: bool = True
    approval_required: bool = True
    pending_approvals: int = 0


class ActivationDecision(BaseModel):
    """Decision about which engines should be active."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Engine activation decisions
    engines: Dict[str, ActivationStatus] = Field(default_factory=dict)
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    
    # Key factors
    regime_factor: Optional[str] = None
    risk_factor: Optional[str] = None
    exposure_factor: Optional[str] = None


class CapitalPositionRecommendation(BaseModel):
    """Recommendation for capital deployment."""
    posture: CapitalPosture
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Allocation limits
    max_tactical_allocation: float = Field(ge=0.0, le=1.0)
    max_strategy_allocation: float = Field(ge=0.0, le=1.0)
    new_capital_available: bool = True
    
    # Specific allocations
    investment_allocation: str = "allowed"
    tactical_allocation: str = "allowed"
    income_allocation: str = "allowed"
    leverage_allocation: str = "restricted"
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    key_factors: Dict[str, str] = Field(default_factory=dict)


class FusedDecision(BaseModel):
    """Final fused decision from multiple engines."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Decision
    action: str  # "DEPLOY", "HOLD", "REDUCE", "WITHDRAW", "SUPPRESS"
    conviction: float = Field(ge=0.0, le=1.0)
    
    # Source inputs
    regime_input: Optional[str] = None
    strategy_input: Optional[str] = None
    portfolio_input: Optional[str] = None
    tactical_input: Optional[str] = None
    risk_input: Optional[str] = None
    
    # Conflict resolution
    conflicts: List[str] = Field(default_factory=list)
    resolution: str = ""
    
    # Reasoning
    reasoning: List[str] = Field(default_factory=list)
    supporting_factors: List[str] = Field(default_factory=list)
    opposing_factors: List[str] = Field(default_factory=list)


class RoutedPriorityItem(BaseModel):
    """Priority-routed item for executive attention."""
    item_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    priority: PriorityLevel
    category: str  # "risk", "opportunity", "governance", "strategy"
    title: str
    description: str
    
    # Action items
    requires_action: bool = False
    action_deadline: Optional[datetime] = None
    recommended_action: Optional[str] = None
    
    # Routing
    route_to: List[str] = Field(default_factory=list)  # e.g., ["CFO", "CEO"]


class ExecutiveBrief(BaseModel):
    """Top-level executive summary."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    system_status: SystemStatus
    capital_posture: CapitalPosture
    
    # Summary
    market_context: str = ""
    key_decision: str = ""
    
    # What's allowed
    allowed_systems: List[str] = Field(default_factory=list)
    restricted_systems: List[str] = Field(default_factory=list)
    
    # Top priority items
    priority_items: List[RoutedPriorityItem] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    
    # Conditions summary
    conditions_summary: Dict[str, str] = Field(default_factory=dict)


class OrchestrationCycleResult(BaseModel):
    """Result of one orchestration cycle."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # State snapshot
    state_snapshot: SystemStateSnapshot
    
    # Activation
    activation: ActivationDecision
    
    # Capital
    capital: CapitalPositionRecommendation
    
    # Decision
    decision: FusedDecision
    
    # Output
    executive_brief: ExecutiveBrief
    
    # Metadata
    cycle_duration_ms: float = 0.0
    engines_consulted: List[str] = Field(default_factory=list)
