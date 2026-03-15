"""Intervention Types - Core models and enums for the Strategic Intervention Engine."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class InterventionType(str, Enum):
    """Types of strategic interventions."""
    WORKLOAD_REDUCTION = "workload_reduction"
    RECOVERY_PROTOCOL = "recovery_protocol"
    RISK_MITIGATION = "risk_mitigation"
    RESOURCE_REALLOCATION = "resource_reallocation"
    PRIORITY_COMPRESSION = "priority_compression"
    AUTOMATION_RECOMMENDATION = "automation_recommendation"
    FOCUS_REALIGNMENT = "focus_realignment"
    DOMAIN_STABILIZATION = "domain_stabilization"
    EMERGENCY_RESPONSE = "emergency_response"
    PREVENTIVE_ACTION = "preventive_action"


class TriggerType(str, Enum):
    """Types of triggers that can initiate interventions."""
    DOMAIN_PERFORMANCE_COLLAPSE = "domain_performance_collapse"
    RISK_ESCALATION = "risk_escalation"
    PRIORITY_OSCILLATION = "priority_oscillation"
    SUSTAINED_IMBALANCE = "sustained_imbalance"
    EXCESSIVE_ALERTS = "excessive_alerts"
    EXECUTION_OVERLOAD = "execution_overload"
    RESOURCE_STARVATION = "resource_starvation"
    STRATEGIC_DRIFT = "strategic_drift"


class InterventionStatus(str, Enum):
    """Status of an intervention."""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DomainState(BaseModel):
    """Current state of a domain."""
    name: str
    performance_score: float = Field(ge=0, le=10)
    risk_score: float = Field(ge=0, le=10)
    opportunity_score: float = Field(ge=0, le=10)
    momentum_score: float = Field(ge=-10, le=10)
    alignment_score: float = Field(ge=0, le=10)
    resource_allocation: float = Field(ge=0, le=100)


class TriggerCondition(BaseModel):
    """Condition that can trigger an intervention."""
    trigger_type: TriggerType
    domain: str
    severity: float = Field(ge=0, le=1)
    duration_days: int = 0
    occurrence_count: int = 0
    first_detected: Optional[datetime] = None
    last_detected: Optional[datetime] = None


class InterventionAction(BaseModel):
    """Specific action to take as part of an intervention."""
    action_type: str
    target: str
    value: Any
    reason: str


class Intervention(BaseModel):
    """A strategic intervention."""
    intervention_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trigger_reason: str
    trigger_type: TriggerType
    target_domain: str
    intervention_type: InterventionType
    expected_effect: str
    confidence_score: float = Field(ge=0, le=1)
    status: InterventionStatus = InterventionStatus.PENDING
    actions: List[InterventionAction] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None


class InterventionProtocol(BaseModel):
    """A structured protocol for handling specific failure modes."""
    protocol_id: str
    name: str
    description: str
    trigger_conditions: List[TriggerType]
    intervention_type: InterventionType
    actions: List[Dict[str, Any]]
    cooldown_hours: int = 24
    max_per_day: int = 2
    confidence_threshold: float = 0.5
    is_emergency: bool = False


class InterventionPolicy(BaseModel):
    """Policy constraints for interventions."""
    max_interventions_per_day: int = 3
    cooldown_hours: int = 6
    confidence_threshold: float = 0.6
    enable_auto_execution: bool = True
    emergency_override: bool = False
    require_approval_for_emergency: bool = True


class InterventionHistory(BaseModel):
    """History of interventions."""
    interventions: List[Intervention] = Field(default_factory=list)
    total_executed: int = 0
    total_failed: int = 0
    last_intervention_time: Optional[datetime] = None


class InterventionStatistics(BaseModel):
    """Statistics about interventions."""
    total_interventions: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    by_domain: Dict[str, int] = Field(default_factory=dict)
    success_rate: float = 0.0
    average_confidence: float = 0.0
    recent_trends: Dict[str, Any] = Field(default_factory=dict)


class SystemStateSnapshot(BaseModel):
    """Snapshot of system state for intervention decisions."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    domains: List[DomainState]
    active_risks: List[str]
    recent_events: List[str]
    oscillation_count: int = 0
    alert_count_24h: int = 0
