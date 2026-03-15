"""Task generator - converts CouncilDecision into executable tasks."""
import uuid
from typing import List, Dict, Any, Optional

from app.execution_engine.execution_types import (
    ExecutionPriority,
    PermissionLevel,
    TaskType,
)
from app.execution_engine.execution_models import ExecutionTask


class TaskGenerator:
    """Converts CouncilDecision objects into executable tasks.
    
    Example:
    Council Decision: "Rebalance financial allocation"
    
    Generated tasks:
    - analyze_allocation_distribution
    - adjust_allocation_targets
    - update_financial_model
    - validate_strategy_alignment
    """
    
    def __init__(self):
        self._task_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize task templates for common decision types."""
        return {
            "allocation": [
                {
                    "task_type": TaskType.ANALYSIS,
                    "description": "Analyze current allocation distribution",
                    "priority": ExecutionPriority.HIGH,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
                {
                    "task_type": TaskType.UPDATE,
                    "description": "Adjust allocation targets based on strategy",
                    "priority": ExecutionPriority.HIGH,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
                {
                    "task_type": TaskType.VALIDATION,
                    "description": "Validate new allocation against strategy",
                    "priority": ExecutionPriority.HIGH,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
            ],
            "rebalance": [
                {
                    "task_type": TaskType.ANALYSIS,
                    "description": "Analyze current portfolio positions",
                    "priority": ExecutionPriority.NORMAL,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
                {
                    "task_type": TaskType.UPDATE,
                    "description": "Execute rebalancing trades",
                    "priority": ExecutionPriority.CRITICAL,
                    "permission": PermissionLevel.REQUIRES_APPROVAL,
                },
                {
                    "task_type": TaskType.VALIDATION,
                    "description": "Validate rebalancing results",
                    "priority": ExecutionPriority.NORMAL,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
            ],
            "risk": [
                {
                    "task_type": TaskType.ANALYSIS,
                    "description": "Analyze current risk exposure",
                    "priority": ExecutionPriority.HIGH,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
                {
                    "task_type": TaskType.ADJUSTMENT,
                    "description": "Implement risk mitigation measures",
                    "priority": ExecutionPriority.HIGH,
                    "permission": PermissionLevel.REQUIRES_APPROVAL,
                },
            ],
            "growth": [
                {
                    "task_type": TaskType.ANALYSIS,
                    "description": "Analyze growth opportunities",
                    "priority": ExecutionPriority.NORMAL,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
                {
                    "task_type": TaskType.UPDATE,
                    "description": "Update growth strategy parameters",
                    "priority": ExecutionPriority.NORMAL,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
            ],
            "maintain": [
                {
                    "task_type": TaskType.MONITORING,
                    "description": "Monitor current strategy performance",
                    "priority": ExecutionPriority.LOW,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
                {
                    "task_type": TaskType.REPORTING,
                    "description": "Generate status report",
                    "priority": ExecutionPriority.LOW,
                    "permission": PermissionLevel.AUTONOMOUS,
                },
            ],
        }
    
    def generate_tasks(
        self,
        decision_summary: str,
        decision_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ExecutionTask]:
        """Generate execution tasks from a council decision.
        
        Args:
            decision_summary: Summary text of the decision
            decision_id: ID of the council decision
            context: Optional additional context
            
        Returns:
            List of executable tasks
        """
        tasks = []
        context = context or {}
        
        # Determine decision type
        decision_type = self._classify_decision(decision_summary)
        
        # Get task templates
        templates = self._task_templates.get(decision_type, self._task_templates["maintain"])
        
        # Generate tasks from templates
        for i, template in enumerate(templates):
            task = ExecutionTask(
                task_id=f"task_{decision_id}_{i}",
                origin_decision=decision_id,
                task_type=template["task_type"],
                description=template["description"],
                priority=template["priority"],
                permission_level=template["permission"],
                dependencies=[],
                required_resources={},
            )
            
            # Add dependencies
            if i > 0:
                task.dependencies = [tasks[i-1].task_id]
            
            tasks.append(task)
        
        # Override priority based on context if provided
        if context.get("priority"):
            for task in tasks:
                task.priority = context["priority"]
        
        return tasks
    
    def _classify_decision(self, decision_summary: str) -> str:
        """Classify decision type based on summary text."""
        summary_lower = decision_summary.lower()
        
        if any(word in summary_lower for word in ["rebalanc", "allocat", "portfolio"]):
            return "allocation"
        elif any(word in summary_lower for word in ["risk", "exposure", "mitigation"]):
            return "risk"
        elif any(word in summary_lower for word in ["growth", "expand", "increase"]):
            return "growth"
        elif any(word in summary_lower for word in ["maintain", "monitor", "status"]):
            return "maintain"
        
        return "maintain"  # Default
    
    def generate_single_task(
        self,
        description: str,
        decision_id: str,
        task_type: TaskType = TaskType.ANALYSIS,
        priority: ExecutionPriority = ExecutionPriority.NORMAL,
        permission_level: PermissionLevel = PermissionLevel.AUTONOMOUS,
    ) -> ExecutionTask:
        """Generate a single task.
        
        Args:
            description: Task description
            decision_id: Origin decision ID
            task_type: Type of task
            priority: Task priority
            permission_level: Required permission level
            
        Returns:
            Generated task
        """
        return ExecutionTask(
            task_id=f"task_{decision_id}_{uuid.uuid4().hex[:6]}",
            origin_decision=decision_id,
            task_type=task_type,
            description=description,
            priority=priority,
            permission_level=permission_level,
        )
