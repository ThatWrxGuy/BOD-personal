"""Execution Engine - converts strategic decisions into actionable tasks.

This module provides autonomous operational capability:
- Task generation from council decisions
- Workflow planning with dependency resolution
- Permission management for task execution
- Failure handling and rollback
- Execution monitoring and reporting
"""
from app.execution_engine.execution_types import (
    ExecutionStatus,
    ExecutionPriority,
    PermissionLevel,
    FailureSeverity,
    TaskType,
)

from app.execution_engine.execution_models import (
    ExecutionTask,
    ExecutionWorkflow,
    ExecutionResult,
    WorkflowResult,
    PermissionDecision,
    FailureRecord,
    ExecutionSummary,
)

from app.execution_engine.task_generator import TaskGenerator

from app.execution_engine.workflow_planner import WorkflowPlanner

from app.execution_engine.permission_manager import PermissionManager

from app.execution_engine.failure_handler import FailureHandler

from app.execution_engine.execution_monitor import ExecutionMonitor

from app.execution_engine.execution_controller import ExecutionController

__all__ = [
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
    # Components
    "TaskGenerator",
    "WorkflowPlanner",
    "PermissionManager",
    "FailureHandler",
    "ExecutionMonitor",
    "ExecutionController",
]
