"""Decision journal data models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DriftClassification(str, Enum):
    """Classification of behavioral drift between original and replay."""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"


class ReplayStatus(str, Enum):
    """Status of a replay operation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SignalSnapshot(BaseModel):
    """Snapshot of a normalized signal used in a decision cycle."""
    signal_id: str
    source_id: str
    signal_type: str
    raw_payload: Dict[str, Any]
    normalized_payload: Dict[str, Any]
    timestamp: datetime
    ingestion_timestamp: datetime
    freshness_score: float = Field(ge=0, le=1)
    confidence_score: float = Field(ge=0, le=1)


class StateSnapshotReference(BaseModel):
    """Reference to a state snapshot used in a decision cycle."""
    state_id: str
    timestamp: datetime
    summary: Dict[str, Any]


class RecommendationSnapshot(BaseModel):
    """Snapshot of a recommendation from a decision cycle."""
    recommendation_id: str
    action: str
    target_domain: str
    priority: int
    reasoning: str
    expected_impact: float
    confidence: float
    urgency: str
    suggested_next_steps: List[str] = Field(default_factory=list)
    evidence_chain: Dict[str, Any] = Field(default_factory=dict)
    risk_factors: List[str] = Field(default_factory=list)
    confidence_factors: Dict[str, Any] = Field(default_factory=dict)
    policy_constraints_respected: bool = True
    is_blocked: bool = False


class ConflictSnapshot(BaseModel):
    """Snapshot of a detected conflict."""
    conflict_type: str
    domains_involved: List[str]
    severity: float
    description: str
    resolution: Optional[str] = None


class DecisionCycleSnapshot(BaseModel):
    """Complete snapshot of a decision cycle."""
    cycle_id: str
    timestamp: datetime
    source_signal_ids: List[str] = Field(default_factory=list)
    normalized_signals: List[SignalSnapshot] = Field(default_factory=list)
    state_summary: Dict[str, Any] = Field(default_factory=dict)
    detected_conditions: List[str] = Field(default_factory=list)
    detected_conflicts: List[ConflictSnapshot] = Field(default_factory=list)
    recommendations: List[RecommendationSnapshot] = Field(default_factory=list)
    confidence_summary: Dict[str, Any] = Field(default_factory=dict)
    rationale_summary: str = ""
    subsystem_versions: Dict[str, str] = Field(default_factory=dict)
    replayable_input_bundle: Dict[str, Any] = Field(default_factory=dict)


class ReplayRequest(BaseModel):
    """Request to replay a historical decision cycle."""
    cycle_id: str
    compare_outputs: bool = True


class ReplayResult(BaseModel):
    """Result of replaying a decision cycle."""
    original_cycle_id: str
    replay_timestamp: datetime
    status: ReplayStatus
    replayed_recommendations: List[RecommendationSnapshot] = Field(default_factory=list)
    original_recommendations: List[RecommendationSnapshot] = Field(default_factory=list)
    confidence_deltas: Any = Field(default_factory=dict)  # Can be dict or list
    conflict_deltas: Any = Field(default_factory=list)  # Can be list
    divergences: Any = Field(default_factory=list)  # Can be list
    drift_classification: DriftClassification = DriftClassification.NONE
    processing_latency_ms: float = 0.0
    error_message: Optional[str] = None


class AuditComparisonResult(BaseModel):
    """Result of comparing two decision cycles."""
    cycle_id: str
    compared_timestamp: datetime
    recommendation_count_delta: int = 0
    priority_differences: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_differences: List[Dict[str, Any]] = Field(default_factory=list)
    conflict_differences: List[Dict[str, Any]] = Field(default_factory=list)
    drift_classification: DriftClassification = DriftClassification.NONE


class JournalEvent(BaseModel):
    """Structured log event for journal operations."""
    event_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    event_type: str
    cycle_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    journal_write_status: Optional[str] = None
    snapshot_size: Optional[int] = None
    replay_requested: bool = False
    replay_completed: bool = False
    drift_classification: Optional[str] = None
    processing_latency_ms: float = 0.0
    error_message: Optional[str] = None


# Constants for safety
LIVE_EXECUTION_ENABLED = False  # No real execution
REPLAY_MODE = True  # Replay is analysis-only
