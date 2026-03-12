"""State models for the Unified State Engine."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

from app.state_engine.state_types import (
    ExecutionStatus,
    RiskLevel,
)


class OperationalState(BaseModel):
    """Current operational state of the system."""
    current_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    active_priorities: List[str] = Field(default_factory=list)
    execution_status: ExecutionStatus = ExecutionStatus.PENDING
    active_cycles: int = 0
    completed_cycles: int = 0


class StrategicState(BaseModel):
    """Current strategic state."""
    active_strategies: List[str] = Field(default_factory=list)
    forecast_summary: Dict[str, Any] = Field(default_factory=dict)
    simulation_summary: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.5
    strategic_priority: str = "maintain"


class RiskState(BaseModel):
    """Current risk state."""
    identified_risks: List[Dict[str, Any]] = Field(default_factory=list)
    risk_severity_index: float = 0.0
    stress_test_results: Dict[str, Any] = Field(default_factory=dict)
    high_priority_risks: List[str] = Field(default_factory=list)


class GoalState(BaseModel):
    """Current goal state."""
    active_goals: List[Dict[str, Any]] = Field(default_factory=list)
    progress_metrics: Dict[str, float] = Field(default_factory=dict)
    goal_probability_scores: Dict[str, float] = Field(default_factory=dict)


class ResourceState(BaseModel):
    """Current resource state."""
    financial_state: Dict[str, Any] = Field(default_factory=dict)
    time_allocation: Dict[str, float] = Field(default_factory=dict)
    system_capacity: float = 1.0


class SystemStateSnapshot(BaseModel):
    """Complete system state snapshot."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cycle_id: Optional[str] = None
    operational_state: OperationalState = Field(default_factory=OperationalState)
    strategic_state: StrategicState = Field(default_factory=StrategicState)
    risk_state: RiskState = Field(default_factory=RiskState)
    goal_state: GoalState = Field(default_factory=GoalState)
    resource_state: ResourceState = Field(default_factory=ResourceState)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()


class StateUpdate(BaseModel):
    """Update to a specific state component."""
    component: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "system"


class MemoryEntry(BaseModel):
    """Entry in the memory system."""
    entry_id: str
    memory_type: str
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance: float = 0.5
    tags: List[str] = Field(default_factory=list)


class DoctrineEntry(BaseModel):
    """Strategic doctrine entry."""
    doctrine_id: str
    strategic_rule: str
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_level: float = 0.5
    origin_cycle: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class SnapshotRecord(BaseModel):
    """Historical state snapshot record."""
    snapshot_id: str
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state: SystemStateSnapshot
    metadata: Dict[str, Any] = Field(default_factory=dict)
