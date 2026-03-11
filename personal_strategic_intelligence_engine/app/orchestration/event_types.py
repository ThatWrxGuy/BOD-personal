"""Event types for PSIE orchestration."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Domain event types for PSIE."""
    
    # Signal events
    SIGNAL_CREATED = "SIGNAL_CREATED"
    SIGNAL_CLASSIFIED = "SIGNAL_CLASSIFIED"
    SIGNAL_PROCESSED = "SIGNAL_PROCESSED"
    
    # Decision events
    DECISION_PROPOSAL_CREATED = "DECISION_PROPOSAL_CREATED"
    DECISION_PROPOSAL_UPDATED = "DECISION_PROPOSAL_UPDATED"
    
    # Debate events
    DEBATE_STARTED = "DEBATE_STARTED"
    DEBATE_ROUND_COMPLETED = "DEBATE_ROUND_COMPLETED"
    DEBATE_COMPLETED = "DEBATE_COMPLETED"
    CONSENSUS_CALCULATED = "CONSENSUS_CALCULATED"
    
    # Governance events
    GOVERNANCE_REVIEW_REQUESTED = "GOVERNANCE_REVIEW_REQUESTED"
    DECISION_APPROVED = "DECISION_APPROVED"
    DECISION_REJECTED = "DECISION_REJECTED"
    
    # Execution events
    EXECUTION_REQUESTED = "EXECUTION_REQUESTED"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_CANCELLED = "EXECUTION_CANCELLED"
    
    # Learning events
    OUTCOME_EVALUATED = "OUTCOME_EVALUATED"
    LESSON_EXTRACTED = "LESSON_EXTRACTED"
    PATTERN_DETECTED = "PATTERN_DETECTED"
    DOCTRINE_UPDATED = "DOCTRINE_UPDATED"
    
    # System events
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_STATE_CHANGED = "WORKFLOW_STATE_CHANGED"


class DomainEvent:
    """Base domain event."""
    
    def __init__(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source_module: str,
        correlation_id: Optional[uuid.UUID] = None,
        workflow_id: Optional[uuid.UUID] = None,
    ):
        self.event_id = uuid.uuid4()
        self.event_type = event_type
        self.timestamp = datetime.utcnow()
        self.source_module = source_module
        self.payload = payload
        self.correlation_id = correlation_id or uuid.uuid4()
        self.workflow_id = workflow_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source_module": self.source_module,
            "payload": self.payload,
            "correlation_id": str(self.correlation_id),
            "workflow_id": str(self.workflow_id) if self.workflow_id else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """Create event from dictionary."""
        event = cls(
            event_type=data["event_type"],
            payload=data.get("payload", {}),
            source_module=data.get("source_module", "unknown"),
            correlation_id=uuid.UUID(data["correlation_id"]) if data.get("correlation_id") else None,
            workflow_id=uuid.UUID(data["workflow_id"]) if data.get("workflow_id") else None,
        )
        if data.get("event_id"):
            event.event_id = uuid.UUID(data["event_id"])
        if data.get("timestamp"):
            event.timestamp = datetime.fromisoformat(data["timestamp"])
        return event


# Event factory functions
def create_signal_created_event(signal_data: Dict[str, Any], source: str = "signals") -> DomainEvent:
    """Create a SIGNAL_CREATED event."""
    return DomainEvent(
        event_type=EventType.SIGNAL_CREATED,
        payload=signal_data,
        source_module=source,
    )


def create_decision_proposal_event(decision_data: Dict[str, Any], correlation_id: uuid.UUID = None) -> DomainEvent:
    """Create a DECISION_PROPOSAL_CREATED event."""
    return DomainEvent(
        event_type=EventType.DECISION_PROPOSAL_CREATED,
        payload=decision_data,
        source_module="governance",
        correlation_id=correlation_id,
    )


def create_debate_started_event(debate_id: uuid.UUID, proposal_id: uuid.UUID) -> DomainEvent:
    """Create a DEBATE_STARTED event."""
    return DomainEvent(
        event_type=EventType.DEBATE_STARTED,
        payload={
            "debate_id": str(debate_id),
            "proposal_id": str(proposal_id),
        },
        source_module="debate_engine",
        correlation_id=proposal_id,
    )


def create_debate_completed_event(debate_id: uuid.UUID, result: Dict[str, Any]) -> DomainEvent:
    """Create a DEBATE_COMPLETED event."""
    return DomainEvent(
        event_type=EventType.DEBATE_COMPLETED,
        payload={
            "debate_id": str(debate_id),
            "result": result,
        },
        source_module="debate_engine",
    )


def create_decision_approved_event(decision_id: uuid.UUID, approved_by: str = "governance") -> DomainEvent:
    """Create a DECISION_APPROVED event."""
    return DomainEvent(
        event_type=EventType.DECISION_APPROVED,
        payload={
            "decision_id": str(decision_id),
            "approved_by": approved_by,
        },
        source_module="governance",
        correlation_id=decision_id,
    )


def create_execution_requested_event(decision_id: uuid.UUID, action: Dict[str, Any]) -> DomainEvent:
    """Create an EXECUTION_REQUESTED event."""
    return DomainEvent(
        event_type=EventType.EXECUTION_REQUESTED,
        payload={
            "decision_id": str(decision_id),
            "action": action,
        },
        source_module="execution_engine",
        correlation_id=decision_id,
    )


def create_execution_completed_event(execution_id: uuid.UUID, result: Dict[str, Any]) -> DomainEvent:
    """Create an EXECUTION_COMPLETED event."""
    return DomainEvent(
        event_type=EventType.EXECUTION_COMPLETED,
        payload={
            "execution_id": str(execution_id),
            "result": result,
        },
        source_module="execution_engine",
    )


def create_outcome_evaluated_event(decision_id: uuid.UUID, outcome: Dict[str, Any]) -> DomainEvent:
    """Create an OUTCOME_EVALUATED event."""
    return DomainEvent(
        event_type=EventType.OUTCOME_EVALUATED,
        payload={
            "decision_id": str(decision_id),
            "outcome": outcome,
        },
        source_module="learning_layer",
        correlation_id=decision_id,
    )
