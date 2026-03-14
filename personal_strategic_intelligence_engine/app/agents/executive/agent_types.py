"""Executive agent types and enumerations."""
from enum import Enum


class ExecutiveRole(str, Enum):
    """Executive roles in the agent council."""
    CEO = "ceo"
    CFO = "cfo"
    COO = "coo"
    CSO = "cso"
    CRO = "cro"
    CKO = "cko"
    CPO = "cpo"


class ProposalStatus(str, Enum):
    """Status of a proposal in the council."""
    PROPOSED = "proposed"
    UNDER_DEBATE = "under_debate"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DebatePosition(str, Enum):
    """Position an agent takes in a debate."""
    SUPPORT = "support"
    OPPOSE = "oppose"
    NEUTRAL = "neutral"


class ProposalPriority(str, Enum):
    """Priority level of proposals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
