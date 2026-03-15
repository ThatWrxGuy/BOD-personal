"""Dashboard Service - central service for assembling dashboard views.

The Dashboard Service collects metrics and intelligence from all PSIE subsystems
and assembles unified views for the Executive Dashboard.
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.executive_dashboard.dashboard_models import (
    SystemOverview,
    StrategyOverview,
    ExecutionOverview,
    AgentOverview,
    LearningOverview,
    GraphOverview,
    DashboardStatistics,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Track uptime
_start_time = time.time()


class DashboardService:
    """
    Central service for assembling dashboard views.
    
    Responsibilities:
    - Collect subsystem metrics
    - Aggregate intelligence outputs
    - Construct unified system overview
    - Support real-time dashboard queries
    """
    
    def __init__(self):
        self._start_time = time.time()
    
    def get_system_overview(self) -> SystemOverview:
        """
        Build system overview.
        
        Returns:
            SystemOverview with current metrics
        """
        # Calculate uptime
        uptime = time.time() - self._start_time
        
        overview = SystemOverview(
            system_status="operational",
            active_agents=0,  # Would query agent registry
            pending_proposals=0,  # Would query strategy pipeline
            recent_executions=0,  # Would query execution engine
            learning_events=0,  # Would query learning engine
            signals_processed=0,  # Would query signal bus
            uptime_seconds=uptime,
            timestamp=datetime.utcnow(),
        )
        
        return overview
    
    def get_strategy_overview(self) -> StrategyOverview:
        """
        Build strategy pipeline overview.
        
        Returns:
            StrategyOverview with pipeline metrics
        """
        overview = StrategyOverview(
            active_proposals=0,
            pending_debate=0,
            pending_simulation=0,
            pending_governance=0,
            approved_count=0,
            rejected_count=0,
            recent_proposals=[],
        )
        
        return overview
    
    def get_execution_overview(self) -> ExecutionOverview:
        """
        Build execution overview.
        
        Returns:
            ExecutionOverview with execution metrics
        """
        overview = ExecutionOverview(
            total_executions=0,
            completed=0,
            failed=0,
            pending=0,
            success_rate=0.0,
            recent_executions=[],
            by_action_type={},
        )
        
        return overview
    
    def get_agent_overview(self) -> AgentOverview:
        """
        Build agent overview.
        
        Returns:
            AgentOverview with agent metrics
        """
        overview = AgentOverview(
            total_agents=0,
            active_agents=0,
            agent_performance=[],
        )
        
        return overview
    
    def get_learning_overview(self) -> LearningOverview:
        """
        Build learning engine overview.
        
        Returns:
            LearningOverview with learning metrics
        """
        overview = LearningOverview(
            memory_records=0,
            outcome_evaluations=0,
            active_alerts=0,
            confidence_adjustments=0,
            recent_insights=[],
        )
        
        return overview
    
    def get_graph_overview(self) -> GraphOverview:
        """
        Build knowledge graph overview.
        
        Returns:
            GraphOverview with graph metrics
        """
        overview = GraphOverview(
            total_entities=0,
            total_relationships=0,
            recent_entities=[],
        )
        
        return overview
    
    def get_statistics(self) -> DashboardStatistics:
        """
        Get overall dashboard statistics.
        
        Returns:
            DashboardStatistics with aggregate metrics
        """
        uptime = time.time() - self._start_time
        
        return DashboardStatistics(
            total_signals=0,
            total_proposals=0,
            total_executions=0,
            total_agents=0,
            total_memory_records=0,
            uptime_seconds=uptime,
        )
    
    def get_full_overview(self) -> Dict[str, Any]:
        """
        Get complete dashboard overview.
        
        Returns:
            Dictionary with all dashboard views
        """
        return {
            "system": self.get_system_overview().dict(),
            "strategy": self.get_strategy_overview().dict(),
            "execution": self.get_execution_overview().dict(),
            "agent": self.get_agent_overview().dict(),
            "learning": self.get_learning_overview().dict(),
            "graph": self.get_graph_overview().dict(),
            "statistics": self.get_statistics().dict(),
        }


# Singleton instance
_dashboard_service: Optional[DashboardService] = None


def get_dashboard_service() -> DashboardService:
    """Get the global dashboard service instance."""
    global _dashboard_service
    if _dashboard_service is None:
        _dashboard_service = DashboardService()
    return _dashboard_service


def reset_dashboard_service() -> None:
    """Reset the dashboard service (for testing)."""
    global _dashboard_service
    _dashboard_service = None
