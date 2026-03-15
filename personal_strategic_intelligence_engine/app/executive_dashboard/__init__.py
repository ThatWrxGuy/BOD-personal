"""Executive Dashboard - PSIE command and observation interface.

This module provides the Executive Dashboard subsystem:
- System overview and metrics
- Strategy pipeline views
- Execution history and status
- Learning insights and performance
- Knowledge graph visualization
- Command execution interface

The dashboard provides CEO-level control for:
- Observing system intelligence in real-time
- Reviewing strategy proposals and decisions
- Monitoring execution results
- Approving or overriding governance decisions
- Issuing system commands
"""
from app.executive_dashboard.dashboard_models import (
    CommandCategory,
    CommandStatus,
    SystemOverview,
    StrategyOverview,
    ExecutionOverview,
    AgentOverview,
    LearningOverview,
    GraphOverview,
    DashboardStatistics,
    CommandRequest,
    CommandResult,
    ApprovalRequest,
    ApprovalResult,
)

from app.executive_dashboard.dashboard_service import (
    DashboardService,
    get_dashboard_service,
    reset_dashboard_service,
)

from app.executive_dashboard.command_router import (
    CommandRouter,
    get_command_router,
    reset_command_router,
)

from app.executive_dashboard.system_overview_builder import SystemOverviewBuilder

from app.executive_dashboard.strategy_view_builder import StrategyViewBuilder

from app.executive_dashboard.execution_view_builder import ExecutionViewBuilder

from app.executive_dashboard.learning_view_builder import LearningViewBuilder

from app.executive_dashboard.graph_view_builder import GraphViewBuilder

from app.executive_dashboard.routes import router

__all__ = [
    # Models
    "CommandCategory",
    "CommandStatus",
    "SystemOverview",
    "StrategyOverview",
    "ExecutionOverview",
    "AgentOverview",
    "LearningOverview",
    "GraphOverview",
    "DashboardStatistics",
    "CommandRequest",
    "CommandResult",
    "ApprovalRequest",
    "ApprovalResult",
    # Services
    "DashboardService",
    "get_dashboard_service",
    "reset_dashboard_service",
    "CommandRouter",
    "get_command_router",
    "reset_command_router",
    # View Builders
    "SystemOverviewBuilder",
    "StrategyViewBuilder",
    "ExecutionViewBuilder",
    "LearningViewBuilder",
    "GraphViewBuilder",
    # Routes
    "router",
]
