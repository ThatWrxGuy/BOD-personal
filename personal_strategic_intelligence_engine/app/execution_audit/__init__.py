"""Execution Audit Layer for Outcome Tracking and Adaptive Approval Policy.

This module provides execution outcome auditing, reliability analysis,
and approval policy recommendations.

All recommendations are advisory - execution remains controlled and approval-gated.
"""
from app.execution_audit.outcome_models import (
    OutcomeCategory,
    ReversibilityLevel,
    ApprovalPolicyLevel,
    ExecutionOutcomeSnapshot,
    OutcomeEvaluation,
    ExecutionReliabilityScore,
    ReversibilityClassification,
    ApprovalPolicyRecommendation,
    LIVE_EXECUTION_ENABLED,
)

from app.execution_audit.execution_audit_controller import (
    ExecutionAuditController,
    get_execution_audit_controller,
)

from app.execution_audit.outcome_tracker import (
    OutcomeTracker,
    get_outcome_tracker,
)

from app.execution_audit.outcome_evaluator import (
    OutcomeEvaluator,
    get_outcome_evaluator,
)

from app.execution_audit.reversibility_classifier import (
    ReversibilityClassifier,
    get_reversibility_classifier,
)

from app.execution_audit.execution_reliability_analyzer import (
    ExecutionReliabilityAnalyzer,
    get_reliability_analyzer,
)

from app.execution_audit.approval_policy_advisor import (
    ApprovalPolicyAdvisor,
    get_approval_policy_advisor,
)

from app.execution_audit.audit_store import (
    AuditStore,
    get_audit_store,
)

__all__ = [
    # Enums
    "OutcomeCategory",
    "ReversibilityLevel",
    "ApprovalPolicyLevel",
    # Models
    "ExecutionOutcomeSnapshot",
    "OutcomeEvaluation",
    "ExecutionReliabilityScore",
    "ReversibilityClassification",
    "ApprovalPolicyRecommendation",
    # Safety
    "LIVE_EXECUTION_ENABLED",
    # Components
    "ExecutionAuditController",
    "OutcomeTracker",
    "OutcomeEvaluator",
    "ReversibilityClassifier",
    "ExecutionReliabilityAnalyzer",
    "ApprovalPolicyAdvisor",
    "AuditStore",
    # Factories
    "get_execution_audit_controller",
    "get_outcome_tracker",
    "get_outcome_evaluator",
    "get_reversibility_classifier",
    "get_reliability_analyzer",
    "get_approval_policy_advisor",
    "get_audit_store",
]
