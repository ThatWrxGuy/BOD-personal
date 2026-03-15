"""Execution Engine - converts strategic decisions into actionable tasks.

This module provides autonomous operational capability:
- Task generation from council decisions
- Workflow planning with dependency resolution
- Permission management for task execution
- Failure handling and rollback
- Execution monitoring and reporting

Additionally provides V48-004 Execution Engine:
- Execution request validation
- Action routing to appropriate handlers
- Safety validation before execution
- Complete execution logging and audit trail
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

# V48-004 Components
from app.execution_engine.execution_engine import (
    ExecutionEngine as V48ExecutionEngine,
    get_execution_engine,
    reset_execution_engine,
)

from app.execution_engine.action_router import (
    ActionRouter,
    get_action_router,
)

from app.execution_engine.execution_handlers import (
    BaseExecutionHandler,
    TradeExecutionHandler,
    PortfolioAdjustmentHandler,
    NotificationHandler,
    SystemActionHandler,
    ResearchHandler,
)

from app.execution_engine.safety_validator import (
    SafetyValidator,
    get_safety_validator,
)

from app.execution_engine.execution_logger import (
    ExecutionLogger,
    get_execution_logger,
    reset_execution_logger,
)

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
    # V48-004 Components
    "V48ExecutionEngine",
    "get_execution_engine",
    "reset_execution_engine",
    "ActionRouter",
    "get_action_router",
    "BaseExecutionHandler",
    "TradeExecutionHandler",
    "PortfolioAdjustmentHandler",
    "NotificationHandler",
    "SystemActionHandler",
    "ResearchHandler",
    "SafetyValidator",
    "get_safety_validator",
    "ExecutionLogger",
    "get_execution_logger",
    "reset_execution_logger",
]
