"""Execution Layer for Controlled Decision Execution.

This module provides controlled execution capabilities with policy gating,
doctrine validation, approval workflows, and full audit logging.

All execution is governed by safety flags and requires explicit approval.
"""
from app.execution.execution_models import (
    ExecutionMode,
    ExecutionStatus,
    ApprovalStatus,
    ExecutionIntent,
    ExecutionApproval,
    ExecutionDecision,
    ExecutionOutcome,
    ExecutionRecord,
    EXECUTION_MODE,
    LIVE_EXECUTION_ENABLED,
    APPROVAL_REQUIRED,
    CONFIDENCE_THRESHOLD,
    RISK_THRESHOLD,
    DOCTRINE_VALIDATION_REQUIRED,
    EXECUTION_COOLDOWN_HOURS,
)

from app.execution.execution_controller import (
    ExecutionController,
    get_execution_controller,
)

from app.execution.execution_intent_builder import (
    ExecutionIntentBuilder,
    get_intent_builder,
)

from app.execution.policy_gate import (
    PolicyGate,
    get_policy_gate,
)

from app.execution.doctrine_gate import (
    DoctrineGate,
    get_doctrine_gate,
)

from app.execution.risk_gate import (
    RiskGate,
    get_risk_gate,
)

from app.execution.approval_gate import (
    ApprovalGate,
    get_approval_gate,
)

from app.execution.execution_registry import (
    ExecutionRegistry,
    get_execution_registry,
)

from app.execution.execution_logger import (
    ExecutionLogger,
    get_execution_logger,
)

from app.execution.execution_store import (
    ExecutionStore,
    get_execution_store,
)

__all__ = [
    # Constants
    "EXECUTION_MODE",
    "LIVE_EXECUTION_ENABLED",
    "APPROVAL_REQUIRED",
    "CONFIDENCE_THRESHOLD",
    "RISK_THRESHOLD",
    "DOCTRINE_VALIDATION_REQUIRED",
    "EXECUTION_COOLDOWN_HOURS",
    # Enums
    "ExecutionMode",
    "ExecutionStatus",
    "ApprovalStatus",
    # Models
    "ExecutionIntent",
    "ExecutionApproval",
    "ExecutionDecision",
    "ExecutionOutcome",
    "ExecutionRecord",
    # Components
    "ExecutionController",
    "ExecutionIntentBuilder",
    "PolicyGate",
    "DoctrineGate",
    "RiskGate",
    "ApprovalGate",
    "ExecutionRegistry",
    "ExecutionLogger",
    "ExecutionStore",
    # Factories
    "get_execution_controller",
    "get_intent_builder",
    "get_policy_gate",
    "get_doctrine_gate",
    "get_risk_gate",
    "get_approval_gate",
    "get_execution_registry",
    "get_execution_logger",
    "get_execution_store",
]
