"""Executive agent data models."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.agents.executive.agent_types import (
    ExecutiveRole,
    ProposalStatus,
    DebatePosition,
    ProposalPriority,
)


class AgentProposal(BaseModel):
    """A strategic proposal from an executive agent."""
    proposal_id: str
    origin_agent: ExecutiveRole
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    strategy_summary: str
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 0.5
    status: ProposalStatus = ProposalStatus.PROPOSED
    priority: ProposalPriority = ProposalPriority.MEDIUM
    financial_impact: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    operational_feasibility: Optional[float] = None
    alignment_score: float = 0.5


class DebateArgument(BaseModel):
    """An argument in a council debate."""
    argument_id: str
    agent_role: ExecutiveRole
    target_proposal: str
    position: DebatePosition
    argument_summary: str
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    strength: float = 0.5  # How strong the argument is


class DebateRound(BaseModel):
    """A round of debate on a proposal."""
    round_id: str
    proposal_id: str
    arguments: List[DebateArgument] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class DebateSummary(BaseModel):
    """Summary of a debate."""
    debate_id: str
    proposal_id: str
    arguments_for: List[DebateArgument] = Field(default_factory=list)
    arguments_against: List[DebateArgument] = Field(default_factory=list)
    neutral_arguments: List[DebateArgument] = Field(default_factory=list)
    consensus_reached: bool = False
    dominant_position: DebatePosition = DebatePosition.NEUTRAL
    strength_score: float = 0.5


class CouncilDecision(BaseModel):
    """Final decision from the agent council."""
    decision_id: str
    selected_proposal: Optional[AgentProposal] = None
    selected_proposal_id: Optional[str] = None
    participating_agents: List[ExecutiveRole] = Field(default_factory=list)
    confidence_score: float = 0.0
    debate_summary: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alternatives_considered: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)


class CouncilCycle(BaseModel):
    """A complete council cycle."""
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    proposals: List[AgentProposal] = Field(default_factory=list)
    debates: List[DebateRound] = Field(default_factory=list)
    decision: Optional[CouncilDecision] = None
    state_snapshot_summary: Dict[str, Any] = Field(default_factory=dict)
