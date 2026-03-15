"""Tasks Connector.

Provides productivity and task management signals.
"""
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from app.connectors.connector_models import ConnectorSignal


class TasksConnector:
    """Connector for task management data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_key = os.environ.get("TASKS_API_KEY")
        self.task_provider = os.environ.get("TASKS_PROVIDER", "todoist")
    
    async def fetch_signals(self) -> List[ConnectorSignal]:
        """Fetch signals from task management."""
        signals = []
        
        # If no API key is configured, return demo signals
        if not self.api_key:
            signals.extend(self._generate_demo_signals())
            return signals
        
        # TODO: Implement real task API integration
        # This would typically use Todoist, Asana, Trello, etc.
        signals.extend(self._generate_demo_signals())
        return signals
    
    def _generate_demo_signals(self) -> List[ConnectorSignal]:
        """Generate demo signals for testing."""
        signals = []
        now = datetime.utcnow()
        
        # Backlog growth signal
        signals.append(ConnectorSignal(
            connector_name="tasks",
            signal_type="backlog_growth",
            category="tasks",
            priority="high",
            title="Task Backlog Status",
            description="Number of incomplete tasks",
            value=0.55,
            unit="count",
            confidence=0.9,
            tags=["productivity", "backlog"],
            metadata={"backlog_count": 12},
        ))
        
        # Overdue task signal
        signals.append(ConnectorSignal(
            connector_name="tasks",
            signal_type="overdue_task",
            category="tasks",
            priority="high",
            title="Overdue Tasks",
            description="Tasks past their due date",
            value=0.3,
            unit="count",
            confidence=0.95,
            tags=["productivity", "deadline"],
            metadata={"overdue_count": 2},
        ))
        
        # Priority shift signal
        signals.append(ConnectorSignal(
            connector_name="tasks",
            signal_type="priority_shift",
            category="tasks",
            priority="medium",
            title="Priority Changes",
            description="Recent priority rebalancing",
            value=0.4,
            unit="count",
            confidence=0.8,
            tags=["productivity", "planning"],
            metadata={"reprioritized_count": 3},
        ))
        
        # Project progress signal
        signals.append(ConnectorSignal(
            connector_name="tasks",
            signal_type="project_progress",
            category="tasks",
            priority="medium",
            title="Project Milestones",
            description="Progress on active projects",
            value=0.65,
            unit="percentage",
            confidence=0.85,
            tags=["productivity", "projects"],
            metadata={"completion_rate": 0.65},
        ))
        
        # Completion rate signal
        signals.append(ConnectorSignal(
            connector_name="tasks",
            signal_type="completion_rate",
            category="tasks",
            priority="medium",
            title="Task Completion Rate",
            description="Weekly task completion efficiency",
            value=0.7,
            unit="percentage",
            confidence=0.88,
            tags=["productivity", "efficiency"],
            metadata={"tasks_completed": 15, "tasks_added": 18},
        ))
        
        return signals
    
    async def validate_connection(self) -> bool:
        """Validate the tasks connection."""
        # In production, this would test the API connection
        return True
    
    def get_tasks(
        self,
        status: Optional[str] = None,
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get tasks with optional filters."""
        # TODO: Implement actual task API call
        return []
    
    def calculate_backlog_ratio(
        self,
        completed: int,
        created: int,
    ) -> float:
        """Calculate backlog growth ratio."""
        if created == 0:
            return 0.0
        return completed / created
    
    def find_blockers(self, tasks: List[Dict]) -> List[Dict]:
        """Find tasks that are blocked."""
        # Simplified implementation
        return [t for t in tasks if t.get("blocked", False)]
