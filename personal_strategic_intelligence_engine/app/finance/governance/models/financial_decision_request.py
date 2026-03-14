"""Financial Decision Request - represents a recommendation requiring governance review."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class DecisionClass(str, Enum):
    """Decision classification levels."""
    INFORMATIONAL = "informational"
    USER_APPROVAL = "user_approval"
    BOARD_REVIEW = "board_review"


class DecisionStatus(str, Enum):
    """Decision status values."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass
class FinancialDecisionRequest:
    """Represents a recommendation requiring governance review."""
    decision_id: str
    recommendation_id: str
    profile_id: int
    decision_class: DecisionClass
    title: str
    summary: str
    expected_impact: str
    downside_risk: str
    confidence_score: float
    status: DecisionStatus = DecisionStatus.PENDING
    submitted_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision_id": self.decision_id,
            "recommendation_id": self.recommendation_id,
            "profile_id": self.profile_id,
            "decision_class": self.decision_class.value,
            "title": self.title,
            "summary": self.summary,
            "expected_impact": self.expected_impact,
            "downside_risk": self.downside_risk,
            "confidence_score": self.confidence_score,
            "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }

    @classmethod
    def create(
        cls,
        recommendation_id: str,
        profile_id: int,
        decision_class: DecisionClass,
        title: str,
        summary: str,
        expected_impact: str,
        downside_risk: str,
        confidence_score: float,
    ) -> "FinancialDecisionRequest":
        """Create a new financial decision request."""
        import uuid
        return cls(
            decision_id=str(uuid.uuid4()),
            recommendation_id=recommendation_id,
            profile_id=profile_id,
            decision_class=decision_class,
            title=title,
            summary=summary,
            expected_impact=expected_impact,
            downside_risk=downside_risk,
            confidence_score=confidence_score,
        )
