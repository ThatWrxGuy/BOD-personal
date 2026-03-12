"""Executive Agent System - AI Board of Directors.

This module provides multi-agent strategic deliberation:
- CEO, CFO, COO, CSO, CRO, CKO, CPO agents
- Debate engine for structured deliberation
- Agent council for final decision making
"""
from app.executive_agents.agent_types import (
    ExecutiveRole,
    ProposalStatus,
    DebatePosition,
    ProposalPriority,
)

from app.executive_agents.agent_models import (
    AgentProposal,
    DebateArgument,
    DebateRound,
    DebateSummary,
    CouncilDecision,
    CouncilCycle,
)

from app.executive_agents.base_agent import BaseExecutiveAgent

from app.executive_agents.agent_council import (
    AgentCouncil,
    get_agent_council,
    reset_agent_council,
)

from app.executive_agents.debate_engine import DebateEngine

# Individual agents
from app.executive_agents.ceo_agent import CEOAgent
from app.executive_agents.cfo_agent import CFOAgent
from app.executive_agents.coo_agent import COOAgent
from app.executive_agents.cso_agent import CSOAgent
from app.executive_agents.cro_agent import CROAgent
from app.executive_agents.cko_agent import CKOAgent
from app.executive_agents.cpo_agent import CPOAgent

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
