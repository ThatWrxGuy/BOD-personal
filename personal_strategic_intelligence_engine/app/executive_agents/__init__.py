"""Compatibility module for executive agents.

DEPRECATED: This module is maintained for backward compatibility.
Please use app.agents.executive instead.

This module re-exports all executive agents from the canonical location.
"""
import warnings

# Emit deprecation warning
warnings.warn(
    "app.executive_agents is deprecated. Please use app.agents.executive instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from app.agents.executive import (
    # Types
    ExecutiveRole,
    ProposalStatus,
    DebatePosition,
    ProposalPriority,
    # Models
    AgentProposal,
    DebateArgument,
    DebateRound,
    DebateSummary,
    CouncilDecision,
    CouncilCycle,
    # Base
    BaseExecutiveAgent,
    # Council
    AgentCouncil,
    get_agent_council,
    reset_agent_council,
    # Debate
    DebateEngine,
    # Individual Agents
    CEOAgent,
    CFOAgent,
    COOAgent,
    CSOAgent,
    CROAgent,
    CKOAgent,
    CPOAgent,
)

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
