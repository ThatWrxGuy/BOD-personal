"""Workflow planner - groups tasks into executable workflows."""
import uuid
from typing import List, Dict, Any, Optional, Set

from app.execution_engine.execution_types import ExecutionPriority, ExecutionStatus
from app.execution_engine.execution_models import ExecutionTask, ExecutionWorkflow


class WorkflowPlanner:
    """Groups tasks into workflows with proper execution order.
    
    Handles:
    - Dependency resolution
    - Priority inheritance
    - Parallel execution planning
    """
    
    def __init__(self):
        pass
    
    def create_workflow(
        self,
        tasks: List[ExecutionTask],
        origin_decision: str,
        priority: Optional[ExecutionPriority] = None,
    ) -> ExecutionWorkflow:
        """Create a workflow from a list of tasks.
        
        Args:
            tasks: List of tasks to include in workflow
            origin_decision: ID of the origin decision
            priority: Optional priority (inherited from tasks if not provided)
            
        Returns:
            Configured workflow
        """
        if not tasks:
            raise ValueError("Cannot create workflow with no tasks")
        
        # Determine priority
        if priority is None:
            priority = self._inherit_priority(tasks)
        
        # Resolve execution order based on dependencies
        execution_order = self._resolve_execution_order(tasks)
        
        workflow = ExecutionWorkflow(
            workflow_id=f"wf_{origin_decision}_{uuid.uuid4().hex[:8]}",
            origin_decision=origin_decision,
            tasks=tasks,
            execution_order=execution_order,
            priority=priority,
            status=ExecutionStatus.PENDING,
        )
        
        return workflow
    
    def _inherit_priority(self, tasks: List[ExecutionTask]) -> ExecutionPriority:
        """Inherit priority from tasks (highest priority wins)."""
        priority_values = {
            ExecutionPriority.LOW: 1,
            ExecutionPriority.NORMAL: 2,
            ExecutionPriority.HIGH: 3,
            ExecutionPriority.CRITICAL: 4,
        }
        
        max_priority = ExecutionPriority.LOW
        max_value = 0
        
        for task in tasks:
            value = priority_values.get(task.priority, 0)
            if value > max_value:
                max_value = value
                max_priority = task.priority
        
        return max_priority
    
    def _resolve_execution_order(self, tasks: List[ExecutionTask]) -> List[str]:
        """Resolve execution order based on dependencies.
        
        Uses topological sort to ensure dependencies are met.
        
        Args:
            tasks: Tasks to order
            
        Returns:
            List of task IDs in execution order
        """
        if not tasks:
            return []
        
        # Build dependency graph
        task_map = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: 0 for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.task_id] += 1
        
        # Kahn's algorithm for topological sort
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort by priority (higher priority first)
            queue.sort(key=lambda tid: (
                0 if task_map[tid].priority == ExecutionPriority.CRITICAL else
                1 if task_map[tid].priority == ExecutionPriority.HIGH else
                2 if task_map[tid].priority == ExecutionPriority.NORMAL else 3
            ), reverse=True)
            
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree for dependent tasks
            for task in tasks:
                if current in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)
        
        # Check for cycles
        if len(result) != len(tasks):
            # Circular dependency - fallback to original order
            result = [t.task_id for t in tasks]
        
        return result
    
    def detect_circular_dependencies(self, tasks: List[ExecutionTask]) -> bool:
        """Check for circular dependencies in tasks.
        
        Args:
            tasks: Tasks to check
            
        Returns:
            True if circular dependencies detected
        """
        # Build adjacency list
        task_ids = set(t.task_id for t in tasks)
        graph = {t.task_id: set(t.dependencies) & task_ids for t in tasks}
        
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task in tasks:
            if task.task_id not in visited:
                if has_cycle(task.task_id):
                    return True
        
        return False
    
    def identify_parallel_tasks(self, tasks: List[ExecutionTask]) -> List[List[str]]:
        """Identify tasks that can be executed in parallel.
        
        Args:
            tasks: Tasks to analyze
            
        Returns:
            Lists of task IDs that can run in parallel
        """
        execution_order = self._resolve_execution_order(tasks)
        
        # Tasks with no dependencies can run in parallel (first batch)
        parallel_groups = []
        remaining = set(execution_order)
        completed = set()
        
        while remaining:
            # Find tasks with all dependencies satisfied
            ready = []
            for task_id in remaining:
                task = next((t for t in tasks if t.task_id == task_id), None)
                if task and all(dep in completed for dep in task.dependencies):
                    ready.append(task_id)
            
            if not ready:
                break
            
            parallel_groups.append(ready)
            
            # Mark as completed
            for task_id in ready:
                remaining.remove(task_id)
                completed.add(task_id)
        
        return parallel_groups
    
    def validate_workflow(self, workflow: ExecutionWorkflow) -> Dict[str, Any]:
        """Validate a workflow for potential issues.
        
        Args:
            workflow: Workflow to validate
            
        Returns:
            Validation result
        """
        issues = []
        
        # Check for empty workflow
        if not workflow.tasks:
            issues.append("Workflow has no tasks")
        
        # Check for circular dependencies
        if self.detect_circular_dependencies(workflow.tasks):
            issues.append("Circular dependencies detected")
        
        # Check that all dependencies exist
        task_ids = {t.task_id for t in workflow.tasks}
        for task in workflow.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    issues.append(f"Task {task.task_id} has missing dependency: {dep}")
        
        # Check execution order matches dependencies
        order_set = set(workflow.execution_order)
        if order_set != task_ids:
            issues.append("Execution order doesn't match tasks")
        
        is_valid = len(issues) == 0
        
        return {
            "is_valid": is_valid,
            "issues": issues,
        }
