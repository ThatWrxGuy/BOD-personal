"""Dashboard Models - schemas for dashboard responses.

Defines data models for the Executive Dashboard API responses.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CommandCategory(str, Enum):
    """Categories of dashboard commands."""
    GOVERNANCE = "governance"
    EXECUTION = "execution"
    AGENT = "agent"
    LEARNING = "learning"
    GRAPH = "graph"
    SYSTEM = "system"


class CommandStatus(str, Enum):
    """Status of command execution."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class SystemOverview(BaseModel):
    """High-level system overview."""
    system_status: str = "operational"
    active_agents: int = 0
    pending_proposals: int = 0
    recent_executions: int = 0
    learning_events: int = 0
    signals_processed: int = 0
    uptime_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StrategyOverview(BaseModel):
    """Strategy pipeline overview."""
    active_proposals: int = 0
    pending_debate: int = 0
    pending_simulation: int = 0
    pending_governance: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    recent_proposals: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutionOverview(BaseModel):
    """Execution activity overview."""
    total_executions: int = 0
    completed: int = 0
    failed: int = 0
    pending: int = 0
    success_rate: float = 0.0
    recent_executions: List[Dict[str, Any]] = Field(default_factory=list)
    by_action_type: Dict[str, int] = Field(default_factory=dict)


class AgentOverview(BaseModel):
    """Agent performance overview."""
    total_agents: int = 0
    active_agents: int = 0
    agent_performance: List[Dict[str, Any]] = Field(default_factory=list)


class LearningOverview(BaseModel):
    """Learning engine overview."""
    memory_records: int = 0
    outcome_evaluations: int = 0
    active_alerts: int = 0
    confidence_adjustments: int = 0
    recent_insights: List[Dict[str, Any]] = Field(default_factory=list)


class GraphOverview(BaseModel):
    """Knowledge graph overview."""
    total_entities: int = 0
    total_relationships: int = 0
    recent_entities: List[Dict[str, Any]] = Field(default_factory=list)


class DashboardStatistics(BaseModel):
    """Overall dashboard statistics."""
    total_signals: int = 0
    total_proposals: int = 0
    total_executions: int = 0
    total_agents: int = 0
    total_memory_records: int = 0
    uptime_seconds: float = 0.0


class CommandRequest(BaseModel):
    """Request to execute a dashboard command."""
    command: str
    category: CommandCategory
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requester: str = "executive"
    reason: Optional[str] = None


class CommandResult(BaseModel):
    """Result of command execution."""
    command_id: str
    command: str
    category: CommandCategory
    status: CommandStatus
    message: str
    result: Optional[Dict[str, Any]] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalRequest(BaseModel):
    """Request to approve or reject a proposal."""
    proposal_id: str
    decision: str  # "approve" or "reject"
    reason: Optional[str] = None
    approver: str = "executive"


class ApprovalResult(BaseModel):
    """Result of approval action."""
    proposal_id: str
    decision: str
    status: str
    message: str
