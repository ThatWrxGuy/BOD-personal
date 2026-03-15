"""Approval Policy Layer for Tiered Execution Governance.

This module provides tiered approval policies based on action characteristics,
reliability scores, reversibility, and risk assessments.

All auto-execution remains disabled by default - this is classification only.
"""
from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    EligibilityStatus,
    PolicyTransitionType,
    ApprovalTier,
    ApprovalPolicyRule,
    TierEligibility,
    AutoExecutionEligibility,
    PolicyTransitionEvent,
    DEFAULT_TIERS,
    AUTO_EXECUTION_ENABLED,
)

from app.approval_policy.approval_policy_controller import (
    ApprovalPolicyController,
    get_approval_policy_controller,
)

from app.approval_policy.approval_tier_classifier import (
    ApprovalTierClassifier,
    get_approval_tier_classifier,
)

from app.approval_policy.policy_thresholds import (
    PolicyThresholds,
    get_policy_thresholds,
)

from app.approval_policy.auto_execution_guard import (
    AutoExecutionGuard,
    get_auto_execution_guard,
)

from app.approval_policy.tier_registry import (
    TierRegistry,
    get_tier_registry,
)

from app.approval_policy.policy_transition_analyzer import (
    PolicyTransitionAnalyzer,
    get_policy_transition_analyzer,
)

from app.approval_policy.policy_store import (
    PolicyStore,
    get_policy_store,
)

__all__ = [
    # Enums
    "ApprovalTierLevel",
    "EligibilityStatus",
    "PolicyTransitionType",
    # Models
    "ApprovalTier",
    "ApprovalPolicyRule",
    "TierEligibility",
    "AutoExecutionEligibility",
    "PolicyTransitionEvent",
    "DEFAULT_TIERS",
    # Safety
    "AUTO_EXECUTION_ENABLED",
    # Components
    "ApprovalPolicyController",
    "ApprovalTierClassifier",
    "PolicyThresholds",
    "AutoExecutionGuard",
    "TierRegistry",
    "PolicyTransitionAnalyzer",
    "PolicyStore",
    # Factories
    "get_approval_policy_controller",
    "get_approval_tier_classifier",
    "get_policy_thresholds",
    "get_auto_execution_guard",
    "get_tier_registry",
    "get_policy_transition_analyzer",
    "get_policy_store",
]
