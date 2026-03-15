"""Learning View Builder - displays adaptive intelligence metrics.

The Learning View Builder constructs the learning view showing
strategy performance, agent performance, degradation alerts, and insights.
"""
from datetime import datetime
from typing import Any, Dict, List

from app.executive_dashboard.dashboard_models import LearningOverview


class LearningViewBuilder:
    """
    Displays adaptive intelligence metrics.
    
    Includes:
    - Strategy performance
    - Agent performance
    - Degradation alerts
    - Confidence recalibrations
    - Learning insights
    """
    
    def build(self) -> LearningOverview:
        """
        Build learning overview.
        
        Returns:
            LearningOverview with learning metrics
        """
        return LearningOverview(
            memory_records=0,
            outcome_evaluations=0,
            active_alerts=0,
            confidence_adjustments=0,
            recent_insights=[],
        )
    
    def build_detailed(self) -> Dict[str, Any]:
        """
        Build detailed learning view.
        
        Returns:
            Dictionary with detailed learning data
        """
        overview = self.build()
        
        return {
            "summary": overview.dict(),
            "metrics": {
                "memory_records": overview.memory_records,
                "outcome_evaluations": overview.outcome_evaluations,
                "active_alerts": overview.active_alerts,
                "confidence_adjustments": overview.confidence_adjustments,
            },
            "recent_insights": overview.recent_insights,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def build_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """
        Build detailed performance view for a strategy.
        
        Args:
            strategy_id: The strategy ID
            
        Returns:
            Dictionary with strategy performance details
        """
        return {
            "strategy_id": strategy_id,
            "total_executions": 0,
            "successful_executions": 0,
            "win_rate": 0.0,
            "average_return": 0.0,
            "max_drawdown": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def build_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """
        Build detailed performance view for an agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Dictionary with agent performance details
        """
        return {
            "agent_id": agent_id,
            "total_proposals": 0,
            "accepted_proposals": 0,
            "approval_rate": 0.0,
            "average_confidence": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }
