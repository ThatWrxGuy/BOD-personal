"""Executive Agent System - AI Board of Directors.

This module provides multi-agent strategic deliberation:
- CEO, CFO, COO, CSO, CRO, CKO, CPO agents
- Debate engine for structured deliberation
- Agent council for final decision making
"""
from app.agents.executive.agent_types import (
    ExecutiveRole,
    ProposalStatus,
    DebatePosition,
    ProposalPriority,
)

from app.agents.executive.agent_models import (
    AgentProposal,
    DebateArgument,
    DebateRound,
    DebateSummary,
    CouncilDecision,
    CouncilCycle,
)

from app.agents.executive.base_agent import BaseExecutiveAgent

from app.agents.executive.agent_council import (
    AgentCouncil,
    get_agent_council,
    reset_agent_council,
)

from app.agents.executive.debate_engine import DebateEngine

# Individual agents
from app.agents.executive.ceo_agent import CEOAgent
from app.agents.executive.cfo_agent import CFOAgent
from app.agents.executive.coo_agent import COOAgent
from app.agents.executive.cso_agent import CSOAgent
from app.agents.executive.cro_agent import CROAgent
from app.agents.executive.cko_agent import CKOAgent
from app.agents.executive.cpo_agent import CPOAgent

__all__ = [
    # Types
    "ExecutiveRole",
    "ProposalStatus",
    "DebatePosition",
    "ProposalPriority",
    # Models
    "AgentProposal",
    "DebateArgument",
    "DebateRound",
    "DebateSummary",
    "CouncilDecision",
    "CouncilCycle",
    # Base
    "BaseExecutiveAgent",
    # Council
    "AgentCouncil",
    "get_agent_council",
    "reset_agent_council",
    # Debate
    "DebateEngine",
    # Individual Agents
    "CEOAgent",
    "CFOAgent",
    "COOAgent",
    "CSOAgent",
    "CROAgent",
    "CKOAgent",
    "CPOAgent",
]
