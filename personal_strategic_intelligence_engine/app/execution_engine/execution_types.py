"""Execution engine types and enumerations."""
from enum import Enum


class ExecutionStatus(str, Enum):
    """Status of an execution task or workflow."""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class ExecutionPriority(str, Enum):
    """Priority levels for tasks and workflows."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionLevel(str, Enum):
    """Permission levels for task execution."""
    AUTONOMOUS = "autonomous"
    NOTIFY_ONLY = "notify_only"
    REQUIRES_APPROVAL = "requires_approval"


class FailureSeverity(str, Enum):
    """Severity of execution failures."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """Types of execution tasks."""
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    UPDATE = "update"
    MONITORING = "monitoring"
    REPORTING = "reporting"
    ADJUSTMENT = "adjustment"
