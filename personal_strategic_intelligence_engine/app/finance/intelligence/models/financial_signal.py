"""Financial Signal - represents a detected financial insight."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class SignalType(str, Enum):
    """Types of financial signals."""
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    TREND = "trend"
    ANOMALY = "anomaly"


class Severity(str, Enum):
    """Severity levels for signals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FinancialSignal:
    """Represents a detected financial insight derived from financial metrics."""
    signal_id: str
    profile_id: int
    signal_type: SignalType
    severity: Severity
    title: str
    description: str
    metric_reference: str
    metric_value: Any
    threshold_reference: Optional[Any] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "signal_id": self.signal_id,
            "profile_id": self.profile_id,
            "signal_type": self.signal_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "metric_reference": self.metric_reference,
            "metric_value": self.metric_value,
            "threshold_reference": self.threshold_reference,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }

    @classmethod
    def create(
        cls,
        profile_id: int,
        signal_type: SignalType,
        severity: Severity,
        title: str,
        description: str,
        metric_reference: str,
        metric_value: Any,
        threshold_reference: Optional[Any] = None,
    ) -> "FinancialSignal":
        """Create a new financial signal."""
        import uuid
        return cls(
            signal_id=str(uuid.uuid4()),
            profile_id=profile_id,
            signal_type=signal_type,
            severity=severity,
            title=title,
            description=description,
            metric_reference=metric_reference,
            metric_value=metric_value,
            threshold_reference=threshold_reference,
        )
