"""Execution monitor - tracks execution progress and reports status."""
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.execution_engine.execution_types import ExecutionStatus
from app.execution_engine.execution_models import (
    ExecutionTask,
    ExecutionWorkflow,
    ExecutionResult,
    ExecutionSummary,
)


class ExecutionMonitor:
    """Tracks execution progress and reports system status.
    
    Metrics include:
    - Tasks completed
    - Tasks failed
    - Execution latency
    - Resource utilization
    
    Produces execution summaries for:
    - State Engine
    - Agent Council
    """
    
    def __init__(self):
        self._active_tasks: Dict[str, ExecutionTask] = {}
        self._completed_tasks: List[ExecutionTask] = []
        self._task_results: Dict[str, ExecutionResult] = {}
        self._active_workflows: Dict[str, ExecutionWorkflow] = {}
    
    def register_task(self, task: ExecutionTask):
        """Register a task for monitoring.
        
        Args:
            task: Task to register
        """
        self._active_tasks[task.task_id] = task
    
    def start_task(self, task_id: str):
        """Mark task as started.
        
        Args:
            task_id: ID of task to start
        """
        if task_id in self._active_tasks:
            task = self._active_tasks[task_id]
            task.status = ExecutionStatus.IN_PROGRESS
            task.started_timestamp = datetime.utcnow()
    
    def complete_task(
        self,
        task_id: str,
        result: Optional[ExecutionResult] = None,
    ):
        """Mark task as completed.
        
        Args:
            task_id: ID of completed task
            result: Optional execution result
        """
        if task_id in self._active_tasks:
            task = self._active_tasks[task_id]
            task.status = ExecutionStatus.COMPLETED
            task.completed_timestamp = datetime.utcnow()
            
            # Calculate execution time
            if task.started_timestamp:
                delta = task.completed_timestamp - task.started_timestamp
                task.execution_time_seconds = delta.total_seconds()
            
            # Move to completed
            self._completed_tasks.append(task)
            del self._active_tasks[task_id]
            
            # Store result
            if result:
                self._task_results[task_id] = result
    
    def fail_task(
        self,
        task_id: str,
        error_message: str,
    ):
        """Mark task as failed.
        
        Args:
            task_id: ID of failed task
            error_message: Error details
        """
        if task_id in self._active_tasks:
            task = self._active_tasks[task_id]
            task.status = ExecutionStatus.FAILED
            task.completed_timestamp = datetime.utcnow()
            task.error_message = error_message
            
            # Calculate execution time
            if task.started_timestamp:
                delta = task.completed_timestamp - task.started_timestamp
                task.execution_time_seconds = delta.total_seconds()
            
            # Move to completed
            self._completed_tasks.append(task)
            del self._active_tasks[task_id]
    
    def register_workflow(self, workflow: ExecutionWorkflow):
        """Register a workflow for monitoring.
        
        Args:
            workflow: Workflow to register
        """
        self._active_workflows[workflow.workflow_id] = workflow
    
    def start_workflow(self, workflow_id: str):
        """Mark workflow as started.
        
        Args:
            workflow_id: ID of workflow to start
        """
        if workflow_id in self._active_workflows:
            workflow = self._active_workflows[workflow_id]
            workflow.status = ExecutionStatus.IN_PROGRESS
            workflow.started_timestamp = datetime.utcnow()
    
    def complete_workflow(self, workflow_id: str):
        """Mark workflow as completed.
        
        Args:
            workflow_id: ID of completed workflow
        """
        if workflow_id in self._active_workflows:
            workflow = self._active_workflows[workflow_id]
            workflow.status = ExecutionStatus.COMPLETED
            workflow.completed_timestamp = datetime.utcnow()
    
    def get_task_status(self, task_id: str) -> Optional[ExecutionTask]:
        """Get status of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task if found
        """
        if task_id in self._active_tasks:
            return self._active_tasks[task_id]
        
        for task in self._completed_tasks:
            if task.task_id == task_id:
                return task
        
        return None
    
    def get_execution_summary(self) -> ExecutionSummary:
        """Get execution summary.
        
        Returns:
            Current execution summary
        """
        total = len(self._completed_tasks) + len(self._active_tasks)
        completed = len([t for t in self._completed_tasks if t.status == ExecutionStatus.COMPLETED])
        failed = len([t for t in self._completed_tasks if t.status == ExecutionStatus.FAILED])
        pending = len([t for t in self._active_tasks.values() if t.status == ExecutionStatus.PENDING])
        in_progress = len([t for t in self._active_tasks.values() if t.status == ExecutionStatus.IN_PROGRESS])
        
        # Calculate execution times
        completed_with_time = [
            t for t in self._completed_tasks
            if t.execution_time_seconds is not None
        ]
        
        total_time = sum(t.execution_time_seconds for t in completed_with_time)
        avg_time = total_time / len(completed_with_time) if completed_with_time else 0.0
        
        return ExecutionSummary(
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=failed,
            pending_tasks=pending,
            in_progress_tasks=in_progress,
            total_execution_time=total_time,
            average_task_time=avg_time,
            active_workflows=len(self._active_workflows),
        )
    
    def get_task_timeline(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get timeline of task executions.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            Timeline data
        """
        timeline = []
        
        for task in self._completed_tasks[-limit:]:
            timeline.append({
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status.value,
                "start_time": task.started_timestamp.isoformat() if task.started_timestamp else None,
                "end_time": task.completed_timestamp.isoformat() if task.completed_timestamp else None,
                "duration": task.execution_time_seconds,
            })
        
        return timeline
    
    def get_active_workflow_status(self) -> List[Dict[str, Any]]:
        """Get status of active workflows.
        
        Returns:
            List of active workflow statuses
        """
        status_list = []
        
        for workflow in self._active_workflows.values():
            status_list.append({
                "workflow_id": workflow.workflow_id,
                "status": workflow.status.value,
                "priority": workflow.priority.value,
                "tasks_count": len(workflow.tasks),
                "tasks_completed": sum(
                    1 for t in workflow.tasks if t.status == ExecutionStatus.COMPLETED
                ),
            })
        
        return status_list
    
    def clear_completed(self):
        """Clear completed tasks from memory."""
        self._completed_tasks.clear()
        self._task_results.clear()
