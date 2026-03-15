"""Meta-cognition types and enumerations."""
from enum import Enum


class ValidationStatus(str, Enum):
    """Status of strategic decision validation."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class ContradictionSeverity(str, Enum):
    """Severity of detected contradictions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceTier(str, Enum):
    """Tier classification for confidence scores."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PolicyComplianceStatus(str, Enum):
    """Policy compliance status."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


class OriginEngine(str, Enum):
    """Origin engines for strategic recommendations."""
    FORECAST = "forecast"
    SIMULATION = "simulation"
    MONTE_CARLO = "monte_carlo"
    SYNTHESIZER = "synthesizer"
    STRATEGY_LOOP = "strategy_loop"


class ReasoningQuality(str, Enum):
    """Quality assessment of reasoning."""
    INSUFFICIENT = "insufficient"
    PARTIAL = "partial"
    ADEQUATE = "adequate"
    COMPREHENSIVE = "comprehensive"
