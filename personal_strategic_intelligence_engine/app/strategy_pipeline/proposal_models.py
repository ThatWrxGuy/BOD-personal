"""Strategy Proposal models for the PSIE Strategy Pipeline."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProposalStatus(str, Enum):
    """Status of a strategy proposal."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_DEBATE = "in_debate"
    SIMULATING = "simulating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


class ProposalCategory(str, Enum):
    """Category of strategy proposal."""
    TRADING = "trading"
    PORTFOLIO = "portfolio"
    RISK_MANAGEMENT = "risk_management"
    CAPITAL_ALLOCATION = "capital_allocation"
    MARKET_ENTRY = "market_entry"
    HEDGING = "hedging"
    SYSTEM = "system"
    EXECUTION = "execution"


class RiskLevel(str, Enum):
    """Risk level classification for proposals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DebateOutcome(str, Enum):
    """Outcome of debate evaluation."""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_MORE_DATA = "request_more_data"
    MODIFY = "modify"


class StrategyProposal(BaseModel):
    """Canonical schema for all system strategy proposals."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    
    agent_id: str
    category: ProposalCategory
    
    proposed_action: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    
    risk_level: RiskLevel = RiskLevel.MEDIUM
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    
    status: ProposalStatus = ProposalStatus.DRAFT
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    
    # Related entities
    debate_id: Optional[str] = None
    simulation_results: Optional[Dict[str, Any]] = None
    governance_decision: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    parent_proposal_id: Optional[str] = None
    
    class Config:
        use_enum_values = True


class ProposalSummary(BaseModel):
    """Summary view of a strategy proposal."""
    id: str
    title: str
    description: str
    agent_id: str
    category: str
    risk_level: str
    confidence_score: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class DebateFeedback(BaseModel):
    """Feedback from a debate participant agent."""
    agent_id: str
    agent_name: str
    role: str
    position: str
    argument_text: str
    reasoning: str
    risk_assessment: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    recommendation: DebateOutcome
    round_number: int = 1


class SimulationResult(BaseModel):
    """Results from proposal simulations."""
    simulation_type: str
    expected_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_probability: Optional[float] = None
    risk_metrics: Dict[str, Any] = Field(default_factory=dict)
    scenario_results: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GovernanceDecision(BaseModel):
    """Governance approval decision."""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    approver_level: str  # AUTOMATIC, EXECUTIVE, GOVERNANCE, CEO
    decision: str  # APPROVED, REJECTED, REQUIRES_MODIFICATION
    rationale: str
    conditions: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    simulation_summary: Dict[str, Any] = Field(default_factory=dict)
    debate_summary: List[Dict[str, Any]] = Field(default_factory=list)
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    decided_by: Optional[str] = None


class StrategyPipelineRequest(BaseModel):
    """Request to create a new strategy proposal."""
    title: str
    description: str
    agent_id: str
    category: ProposalCategory
    proposed_action: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    risk_level: RiskLevel = RiskLevel.MEDIUM
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    tags: List[str] = Field(default_factory=list)


class PipelineExecutionRequest(BaseModel):
    """Request to execute a full pipeline for a proposal."""
    proposal_id: str
    run_debate: bool = True
    run_simulation: bool = True
    submit_to_governance: bool = True


class PipelineExecutionResult(BaseModel):
    """Result of executing the pipeline."""
    proposal_id: str
    debate_completed: bool
    debate_outcome: Optional[DebateOutcome] = None
    debate_feedback: List[DebateFeedback] = Field(default_factory=list)
    simulation_completed: bool
    simulation_results: Optional[Dict[str, Any]] = None
    governance_completed: bool
    governance_decision: Optional[GovernanceDecision] = None
    final_status: ProposalStatus
    execution_time_ms: float = 0.0
