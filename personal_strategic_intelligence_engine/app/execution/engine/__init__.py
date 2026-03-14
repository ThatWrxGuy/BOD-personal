"""Execution Engine - Canonical Import Path.

This module provides a canonical import path for execution engine components.
The canonical execution domain is app.execution.

Note: The actual implementations are in app.execution_engine (deprecated).
This module provides the canonical import path and re-exports for compatibility.
"""
# Re-export from deprecated but functional execution_engine (direct module imports)
from app.execution_engine.execution_monitor import ExecutionMonitor
from app.execution_engine.failure_handler import FailureHandler
from app.execution_engine.permission_manager import PermissionManager
from app.execution_engine.task_generator import TaskGenerator
from app.execution_engine.workflow_planner import WorkflowPlanner

# Get ExecutionController from canonical location
from app.execution.execution_controller import ExecutionController

# Types
from app.execution_engine.execution_types import (
    ExecutionStatus,
    ExecutionPriority,
    PermissionLevel,
    FailureSeverity,
    TaskType,
)

# Models
from app.execution_engine.execution_models import (
    ExecutionTask,
    ExecutionWorkflow,
    ExecutionResult,
    WorkflowResult,
    PermissionDecision,
    FailureRecord,
    ExecutionSummary,
)

__all__ = [
    # Components
    "ExecutionMonitor",
    "ExecutionController",
    "FailureHandler",
    "PermissionManager",
    "TaskGenerator",
    "WorkflowPlanner",
    # Types
    "ExecutionStatus",
    "ExecutionPriority",
    "PermissionLevel",
    "FailureSeverity",
    "TaskType",
    # Models
    "ExecutionTask",
    "ExecutionWorkflow",
    "ExecutionResult",
    "WorkflowResult",
    "PermissionDecision",
    "FailureRecord",
    "ExecutionSummary",
]
