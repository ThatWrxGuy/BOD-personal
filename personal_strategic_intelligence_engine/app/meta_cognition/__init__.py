"""Meta-Cognitive Governance Layer.

This module provides self-evaluating reasoning capability:
- Confidence scoring for recommendations
- Contradiction detection across engines
- Policy and doctrine validation
- Reasoning completeness validation
- Decision audit trails
"""
from app.meta_cognition.meta_types import (
    ValidationStatus,
    ContradictionSeverity,
    ConfidenceTier,
    PolicyComplianceStatus,
    OriginEngine,
    ReasoningQuality,
)

from app.meta_cognition.meta_models import (
    StrategicDecision,
    ContradictionRecord,
    DecisionAuditRecord,
    PolicyRule,
    ReasoningValidationResult,
    ConfidenceScoreComponents,
    MetaEvaluationResult,
)

from app.meta_cognition.meta_engine import (
    MetaEngine,
    get_meta_engine,
    reset_meta_engine,
)

from app.meta_cognition.confidence_scorer import (
    ConfidenceScorer,
    calculate_contradiction_penalty,
)

from app.meta_cognition.contradiction_detector import (
    ContradictionDetector,
)

from app.meta_cognition.policy_validator import (
    PolicyValidator,
)

from app.meta_cognition.reasoning_validator import (
    ReasoningValidator,
)

from app.meta_cognition.decision_auditor import (
    DecisionAuditor,
)

__all__ = [
    # Types
    "ValidationStatus",
    "ContradictionSeverity",
    "ConfidenceTier",
    "PolicyComplianceStatus",
    "OriginEngine",
    "ReasoningQuality",
    # Models
    "StrategicDecision",
    "ContradictionRecord",
    "DecisionAuditRecord",
    "PolicyRule",
    "ReasoningValidationResult",
    "ConfidenceScoreComponents",
    "MetaEvaluationResult",
    # Core
    "MetaEngine",
    "get_meta_engine",
    "reset_meta_engine",
    # Components
    "ConfidenceScorer",
    "calculate_contradiction_penalty",
    "ContradictionDetector",
    "PolicyValidator",
    "ReasoningValidator",
    "DecisionAuditor",
]
