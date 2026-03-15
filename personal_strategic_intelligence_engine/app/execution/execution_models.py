"""Execution data models for controlled decision execution."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    """Execution mode status."""
    DISABLED = "disabled"
    CONTROLLED = "controlled"
    AUTOMATED = "automated"


class ExecutionStatus(str, Enum):
    """Status of an execution."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalGateResult(BaseModel):
    """Result of approval gate validation."""
    approved: bool
    status: ApprovalStatus
    approver_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PolicyGateResult(BaseModel):
    """Result of policy gate validation."""
    passed: bool
    policy_rules_checked: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DoctrineGateResult(BaseModel):
    """Result of doctrine gate validation."""
    aligned: bool
    alignment_score: float = 0.0
    alignment_level: str = "neutral"
    risk_flags: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskGateResult(BaseModel):
    """Result of risk gate validation."""
    passed: bool
    risk_level: str = "low"
    risk_score: float = 0.0
    risk_flags: List[str] = Field(default_factory=list)
    threshold: float = 0.5
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionIntent(BaseModel):
    """Intent to execute an action."""
    intent_id: str = Field(default_factory=lambda: f"intent_{datetime.utcnow().timestamp()}")
    recommendation_id: str
    
    # Action details
    domain: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Gate results (populated during validation)
    policy_result: Optional[PolicyGateResult] = None
    doctrine_result: Optional[DoctrineGateResult] = None
    risk_result: Optional[RiskGateResult] = None


class ExecutionApproval(BaseModel):
    """Approval record for execution."""
    approval_id: str = Field(default_factory=lambda: f"approval_{datetime.utcnow().timestamp()}")
    intent_id: str
    
    # Approval details
    status: ApprovalStatus
    approver_id: str = "system"  # Default to system, human override possible
    
    # Timing
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None
    
    # Reasoning
    reason: str = ""
    conditions: Dict[str, Any] = Field(default_factory=dict)


class ExecutionDecision(BaseModel):
    """Final decision on execution."""
    decision_id: str = Field(default_factory=lambda: f"decision_{datetime.utcnow().timestamp()}")
    intent_id: str
    
    # Decision
    approved: bool
    status: ExecutionStatus
    
    # Gate results
    policy_gate: PolicyGateResult
    doctrine_gate: DoctrineGateResult
    risk_gate: RiskGateResult
    approval: ExecutionApproval
    
    # Timing
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Audit
    rationale: str = ""


class ExecutionOutcome(BaseModel):
    """Outcome of an execution attempt."""
    outcome_id: str = Field(default_factory=lambda: f"outcome_{datetime.utcnow().timestamp()}")
    decision_id: str
    intent_id: str
    
    # Outcome
    status: ExecutionStatus
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    
    # Timing
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ExecutionRecord(BaseModel):
    """Complete execution record."""
    record_id: str
    intent: ExecutionIntent
    decision: ExecutionDecision
    outcome: Optional[ExecutionOutcome] = None
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # For learning integration
    feedback_ready: bool = False


# Safety constants
EXECUTION_MODE = ExecutionMode.DISABLED  # Default to disabled
LIVE_EXECUTION_ENABLED = False  # Always false for safety
APPROVAL_REQUIRED = True  # Always require approval by default
CONFIDENCE_THRESHOLD = 0.75  # Minimum confidence for execution
RISK_THRESHOLD = 0.5  # Maximum allowed risk score
DOCTRINE_VALIDATION_REQUIRED = True  # Doctrine alignment mandatory
EXECUTION_COOLDOWN_HOURS = 1  # Cooldown between executions
