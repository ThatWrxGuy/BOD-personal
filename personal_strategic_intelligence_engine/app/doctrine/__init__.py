"""Doctrine Layer for Strategic Alignment & Policy Evaluation.

This module provides doctrine evaluation, rule management, and
strategic alignment assessment.

All operations are advisory only - no execution permitted.
"""
from app.doctrine.doctrine_models import (
    LIVE_EXECUTION_ENABLED,
    DOCTRINE_VERSION,
    AlignmentLevel,
    RiskLevel,
    PolicyRuleType,
    PolicyRule,
    AlignmentScore,
    DoctrineConflict,
    DoctrineRecommendation,
    DecisionContext,
    DoctrineAssessment,
    DoctrineEvent,
)

from app.doctrine.doctrine_controller import (
    DoctrineController,
    get_doctrine_controller,
)

from app.doctrine.doctrine_evaluator import (
    DoctrineEvaluator,
    get_doctrine_evaluator,
)

from app.doctrine.doctrine_registry import (
    DoctrineRegistry,
    get_doctrine_registry,
)

from app.doctrine.doctrine_explanations import (
    DoctrineExplainer,
    get_doctrine_explainer,
)

from app.doctrine.doctrine_store import (
    DoctrineStore,
    get_doctrine_store,
)

from app.doctrine.doctrine_rules import (
    DoctrineRule,
    create_default_rules,
)

__all__ = [
    # Constants
    "LIVE_EXECUTION_ENABLED",
    "DOCTRINE_VERSION",
    # Models
    "AlignmentLevel",
    "RiskLevel",
    "PolicyRuleType",
    "PolicyRule",
    "AlignmentScore",
    "DoctrineConflict",
    "DoctrineRecommendation",
    "DecisionContext",
    "DoctrineAssessment",
    "DoctrineEvent",
    # Components
    "DoctrineController",
    "DoctrineEvaluator",
    "DoctrineRegistry",
    "DoctrineExplainer",
    "DoctrineStore",
    "DoctrineRule",
    # Factories
    "get_doctrine_controller",
    "get_doctrine_evaluator",
    "get_doctrine_registry",
    "get_doctrine_explainer",
    "get_doctrine_store",
    "create_default_rules",
]
