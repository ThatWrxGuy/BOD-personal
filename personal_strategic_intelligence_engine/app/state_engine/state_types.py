"""State types and enumerations for the State Engine."""
from enum import Enum


class StateComponent(str, Enum):
    """Components of system state."""
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    RISK = "risk"
    GOAL = "goal"
    RESOURCE = "resource"


class MemoryTier(str, Enum):
    """Memory tier levels."""
    SHORT_TERM = "short_term"
    STRATEGIC = "strategic"
    DOCTRINE = "doctrine"


class ExecutionStatus(str, Enum):
    """Status of task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CyclePhase(str, Enum):
    """Strategy cycle phases."""
    PLANNING = "planning"
    EXECUTION = "execution"
    EVALUATION = "evaluation"
    SYNTHESIS = "synthesis"
