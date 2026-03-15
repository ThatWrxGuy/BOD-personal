"""Execution controller - orchestrates task and workflow execution."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from app.execution_engine.execution_types import ExecutionStatus, ExecutionPriority
from app.execution_engine.execution_models import (
    ExecutionTask,
    ExecutionWorkflow,
    ExecutionResult,
    WorkflowResult,
)
from app.execution_engine.task_generator import TaskGenerator
from app.execution_engine.workflow_planner import WorkflowPlanner
from app.execution_engine.permission_manager import PermissionManager
from app.execution_engine.failure_handler import FailureHandler
from app.execution_engine.execution_monitor import ExecutionMonitor


class ExecutionController:
    """Orchestrates task and workflow execution.
    
    Integrates with:
    - State Engine
    - Meta-Cognition Layer
    - Agent Council
    """
    
    def __init__(self):
        self.task_generator = TaskGenerator()
        self.workflow_planner = WorkflowPlanner()
        self.permission_manager = PermissionManager()
        self.failure_handler = FailureHandler()
        self.monitor = ExecutionMonitor()
        
        # Task execution function (can be customized)
        self._task_executor: Optional[Callable] = None
    
    def set_task_executor(self, executor: Callable[[ExecutionTask], ExecutionResult]):
        """Set custom task executor function.
        
        Args:
            executor: Function that executes a task and returns result
        """
        self._task_executor = executor
    
    def create_workflow_from_decision(
        self,
        decision_summary: str,
        decision_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionWorkflow:
        """Create a workflow from a council decision.
        
        Args:
            decision_summary: Summary of the decision
            decision_id: ID of the council decision
            context: Optional context
            
        Returns:
            Created workflow
        """
        # Generate tasks
        tasks = self.task_generator.generate_tasks(
            decision_summary=decision_summary,
            decision_id=decision_id,
            context=context,
        )
        
        # Create workflow
        workflow = self.workflow_planner.create_workflow(
            tasks=tasks,
            origin_decision=decision_id,
        )
        
        # Register with monitor
        self.monitor.register_workflow(workflow)
        
        return workflow
    
    def execute_workflow(
        self,
        workflow: ExecutionWorkflow,
    ) -> WorkflowResult:
        """Execute a workflow.
        
        Args:
            workflow: Workflow to execute
            
        Returns:
            Execution result
        """
        # Validate workflow
        validation = self.workflow_planner.validate_workflow(workflow)
        if not validation["is_valid"]:
            return WorkflowResult(
                workflow_id=workflow.workflow_id,
                status=ExecutionStatus.FAILED,
                task_results=[],
                failures_count=len(workflow.tasks),
            )
        
        # Start workflow
        self.monitor.start_workflow(workflow.workflow_id)
        workflow.status = ExecutionStatus.IN_PROGRESS
        
        results = []
        start_time = datetime.utcnow()
        
        # Execute tasks in order
        for task_id in workflow.execution_order:
            task = next((t for t in workflow.tasks if t.task_id == task_id), None)
            if task is None:
                continue
            
            # Check dependencies
            if not self._dependencies_satisfied(task, results):
                # Skip task if dependencies failed
                task.status = ExecutionStatus.FAILED
                continue
            
            # Check permissions
            permission = self.permission_manager.evaluate_permission(task)
            if not permission.approved:
                task.status = ExecutionStatus.FAILED
                results.append(ExecutionResult(
                    task_id=task.task_id,
                    status=ExecutionStatus.FAILED,
                    execution_log=[f"Permission denied: {permission.reason}"],
                ))
                continue
            
            # Execute task
            result = self.execute_task(task)
            results.append(result)
            
            # Check for failure
            if result.status == ExecutionStatus.FAILED:
                # Handle failure
                failure_action = self.failure_handler.handle_failure(
                    task, Exception(result.error_details.get("error", "Unknown error") if result.error_details else "Unknown error")
                )
                
                if failure_action["should_retry"] and self.failure_handler.should_retry(task):
                    # Retry task
                    retry_task = self.failure_handler.create_retry_task(task)
                    retry_result = self.execute_task(retry_task)
                    results[-1] = retry_result
        
        # Complete workflow
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        
        completed = sum(1 for r in results if r.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == ExecutionStatus.FAILED)
        
        if failed > 0:
            workflow.status = ExecutionStatus.FAILED
        else:
            workflow.status = ExecutionStatus.COMPLETED
        
        workflow.completed_timestamp = end_time
        
        self.monitor.complete_workflow(workflow.workflow_id)
        
        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=workflow.status,
            task_results=results,
            total_execution_time=total_time,
            failures_count=failed,
            completions_count=completed,
        )
    
    def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute a single task.
        
        Args:
            task: Task to execute
            
        Returns:
            Execution result
        """
        # Register with monitor
        self.monitor.register_task(task)
        self.monitor.start_task(task.task_id)
        
        task.status = ExecutionStatus.IN_PROGRESS
        
        log = [f"Starting task: {task.description}"]
        
        try:
            # Use custom executor if provided
            if self._task_executor:
                result = self._task_executor(task)
            else:
                # Default execution (simulated)
                result = self._default_execute(task)
            
            # Mark as completed
            task.status = ExecutionStatus.COMPLETED
            log.append(f"Task completed successfully")
            
            self.monitor.complete_task(task.task_id, result)
            
            return result
            
        except Exception as e:
            # Mark as failed
            task.status = ExecutionStatus.FAILED
            log.append(f"Task failed: {str(e)}")
            
            result = ExecutionResult(
                task_id=task.task_id,
                status=ExecutionStatus.FAILED,
                execution_log=log,
                error_details={"error": str(e)},
            )
            
            self.monitor.fail_task(task.task_id, str(e))
            
            return result
    
    def _default_execute(self, task: ExecutionTask) -> ExecutionResult:
        """Default task execution (simulated)."""
        return ExecutionResult(
            task_id=task.task_id,
            status=ExecutionStatus.COMPLETED,
            execution_log=[f"Executed: {task.description}"],
            output_data={"success": True},
        )
    
    def _dependencies_satisfied(
        self,
        task: ExecutionTask,
        results: List[ExecutionResult],
    ) -> bool:
        """Check if task dependencies are satisfied."""
        completed_ids = {r.task_id for r in results if r.status == ExecutionStatus.COMPLETED}
        
        for dep in task.dependencies:
            if dep not in completed_ids:
                return False
        
        return True
    
    def get_execution_summary(self):
        """Get execution summary."""
        return self.monitor.get_execution_summary()
    
    def get_failure_summary(self):
        """Get failure summary."""
        return self.failure_handler.get_failure_summary()
