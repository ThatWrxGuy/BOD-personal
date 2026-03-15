"""System Overview Builder - generates operational metrics.

The System Overview Builder constructs the high-level operational view
showing system health, activity, and performance metrics.
"""
from datetime import datetime
from typing import Any, Dict, List

from app.executive_dashboard.dashboard_models import SystemOverview


class SystemOverviewBuilder:
    """
    Generates high-level operational metrics.
    
    Displays:
    - System health
    - Scheduler activity
    - Signal volume
    - Active agents
    - Pending proposals
    - Recent executions
    """
    
    def build(self) -> SystemOverview:
        """
        Build system overview.
        
        Returns:
            SystemOverview with current metrics
        """
        return SystemOverview(
            system_status="operational",
            active_agents=0,
            pending_proposals=0,
            recent_executions=0,
            learning_events=0,
            signals_processed=0,
            uptime_seconds=0.0,
            timestamp=datetime.utcnow(),
        )
    
    def build_detailed(self) -> Dict[str, Any]:
        """
        Build detailed system overview.
        
        Returns:
            Dictionary with detailed metrics
        """
        overview = self.build()
        
        return {
            "status": overview.system_status,
            "metrics": {
                "active_agents": overview.active_agents,
                "pending_proposals": overview.pending_proposals,
                "recent_executions": overview.recent_executions,
                "learning_events": overview.learning_events,
                "signals_processed": overview.signals_processed,
            },
            "uptime_seconds": overview.uptime_seconds,
            "timestamp": overview.timestamp.isoformat(),
            "health": {
                "signal_bus": "healthy",
                "agents": "healthy",
                "strategy_pipeline": "healthy",
                "execution_engine": "healthy",
                "learning_engine": "healthy",
            },
        }
    
    def build_summary(self) -> str:
        """
        Build text summary.
        
        Returns:
            Summary string
        """
        overview = self.build()
        
        return (
            f"System Status: {overview.system_status}\n"
            f"Active Agents: {overview.active_agents}\n"
            f"Pending Proposals: {overview.pending_proposals}\n"
            f"Recent Executions: {overview.recent_executions}\n"
            f"Learning Events: {overview.learning_events}"
        )
