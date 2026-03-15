"""Financial Audit Event - represents a recorded governance or financial intelligence event."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AuditEventType(str, Enum):
    """Types of audit events."""
    RECOMMENDATION_GENERATED = "recommendation_generated"
    DECISION_REQUESTED = "decision_requested"
    DECISION_RESOLVED = "decision_resolved"
    BOARD_BRIEF_GENERATED = "board_brief_generated"
    SCENARIO_EXECUTED = "scenario_executed"


@dataclass
class FinancialAuditEvent:
    """Represents a recorded governance or financial intelligence event."""
    event_id: str
    profile_id: int
    event_type: AuditEventType
    event_reference: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "profile_id": self.profile_id,
            "event_type": self.event_type.value,
            "event_reference": self.event_reference,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        profile_id: int,
        event_type: AuditEventType,
        event_reference: str,
        description: str,
    ) -> "FinancialAuditEvent":
        """Create a new financial audit event."""
        import uuid
        return cls(
            event_id=str(uuid.uuid4()),
            profile_id=profile_id,
            event_type=event_type,
            event_reference=event_reference,
            description=description,
        )
