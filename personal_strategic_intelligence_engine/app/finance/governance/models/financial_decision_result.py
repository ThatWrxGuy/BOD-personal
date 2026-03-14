"""Financial Decision Result - represents the result of a governance decision."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class DecisionOutcome(str, Enum):
    """Decision outcome values."""
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass
class FinancialDecisionResult:
    """Represents the result of a governance decision."""
    result_id: str
    decision_id: str
    decision_outcome: DecisionOutcome
    reviewer: str = "system"
    review_notes: str = ""
    resolved_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result_id": self.result_id,
            "decision_id": self.decision_id,
            "decision_outcome": self.decision_outcome.value,
            "reviewer": self.reviewer,
            "review_notes": self.review_notes,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    @classmethod
    def create(
        cls,
        decision_id: str,
        decision_outcome: DecisionOutcome,
        reviewer: str = "system",
        review_notes: str = "",
    ) -> "FinancialDecisionResult":
        """Create a new financial decision result."""
        import uuid
        return cls(
            result_id=str(uuid.uuid4()),
            decision_id=decision_id,
            decision_outcome=decision_outcome,
            reviewer=reviewer,
            review_notes=review_notes,
        )
