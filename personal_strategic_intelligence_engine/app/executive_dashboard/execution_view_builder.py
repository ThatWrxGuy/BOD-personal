"""Execution View Builder - displays operational actions.

The Execution View Builder constructs the execution view showing
execution history, success rates, and action categories.
"""
from datetime import datetime
from typing import Any, Dict, List

from app.executive_dashboard.dashboard_models import ExecutionOverview


class ExecutionViewBuilder:
    """
    Displays operational actions.
    
    Includes:
    - Execution history
    - Execution success rate
    - Action categories
    - Recent trades or operations
    """
    
    def build(self) -> ExecutionOverview:
        """
        Build execution overview.
        
        Returns:
            ExecutionOverview with execution metrics
        """
        return ExecutionOverview(
            total_executions=0,
            completed=0,
            failed=0,
            pending=0,
            success_rate=0.0,
            recent_executions=[],
            by_action_type={},
        )
    
    def build_detailed(self) -> Dict[str, Any]:
        """
        Build detailed execution view.
        
        Returns:
            Dictionary with detailed execution data
        """
        overview = self.build()
        
        return {
            "summary": overview.dict(),
            "metrics": {
                "total": overview.total_executions,
                "completed": overview.completed,
                "failed": overview.failed,
                "pending": overview.pending,
                "success_rate": overview.success_rate,
            },
            "by_action_type": overview.by_action_type,
            "recent_executions": overview.recent_executions,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def build_execution_detail(self, execution_id: str) -> Dict[str, Any]:
        """
        Build detailed view for a specific execution.
        
        Args:
            execution_id: The execution ID
            
        Returns:
            Dictionary with execution details
        """
        return {
            "execution_id": execution_id,
            "status": "completed",
            "action_type": "trade_execution",
            "parameters": {},
            "result": {},
            "timestamp": datetime.utcnow().isoformat(),
        }
