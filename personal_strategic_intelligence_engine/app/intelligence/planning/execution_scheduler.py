"""Execution Scheduler - Schedules tasks in execution programs."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.intelligence.planning.execution_models import (
    ExecutionTask,
    ExecutionProgram,
    ExecutionStatus,
)


class ExecutionScheduler:
    """Schedules execution tasks based on dependencies and priorities."""
    
    def __init__(self):
        self.scheduled_tasks: Dict[str, List[ExecutionTask]] = {}
    
    def schedule_tasks(
        self,
        tasks: List[ExecutionTask],
        program: ExecutionProgram,
    ) -> List[ExecutionTask]:
        """Schedule tasks respecting dependencies."""
        
        scheduled = []
        
        # Sort by dependencies
        sorted_tasks = self._topological_sort(tasks)
        
        # Calculate start times
        current_time = datetime.utcnow()
        
        for task in sorted_tasks:
            # Adjust based on dependencies
            if task.depends_on:
                # Find latest completion time of dependencies
                dep_end_time = self._find_dependency_end_time(task.depends_on, scheduled)
                if dep_end_time:
                    task.scheduled_at = dep_end_time + timedelta(hours=1)
            
            # Set due date (7 days from scheduled for simplicity)
            if task.scheduled_at:
                task.due_at = task.scheduled_at + timedelta(days=7)
            else:
                task.scheduled_at = current_time
                task.due_at = current_time + timedelta(days=7)
            
            scheduled.append(task)
        
        self.scheduled_tasks[program.id] = scheduled
        
        return scheduled
    
    def _topological_sort(self, tasks: List[ExecutionTask]) -> List[ExecutionTask]:
        """Sort tasks by dependencies (simple approach)."""
        
        # For now, return as-is since dependencies are simple
        return tasks
    
    def _find_dependency_end_time(
        self,
        dependency_ids: List[str],
        scheduled: List[ExecutionTask],
    ) -> Optional[datetime]:
        """Find the latest end time of dependencies."""
        
        end_time = None
        
        for task in scheduled:
            if task.id in dependency_ids:
                if task.due_at:
                    if end_time is None or task.due_at > end_time:
                        end_time = task.due_at
        
        return end_time
    
    def get_ready_tasks(
        self,
        program_id: str,
    ) -> List[ExecutionTask]:
        """Get tasks that are ready to execute."""
        
        if program_id not in self.scheduled_tasks:
            return []
        
        ready = []
        
        for task in self.scheduled_tasks[program_id]:
            if task.status != ExecutionStatus.PENDING:
                continue
            
            # Check if dependencies are complete
            if self._dependencies_complete(task):
                ready.append(task)
        
        return ready
    
    def _dependencies_complete(self, task: ExecutionTask) -> bool:
        """Check if all dependencies are completed."""
        
        # In a real system, would check task status
        # For now, assume dependencies complete if there are none
        return len(task.depends_on) == 0
    
    def identify_critical_path(
        self,
        tasks: List[ExecutionTask],
    ) -> List[str]:
        """Identify the critical path through tasks."""
        
        # Simple: first and last tasks are critical
        critical = []
        
        if tasks:
            critical.append(tasks[0].id)
            if len(tasks) > 1:
                critical.append(tasks[-1].id)
        
        return critical


_scheduler: Optional[ExecutionScheduler] = None


def get_execution_scheduler() -> ExecutionScheduler:
    """Get the global execution scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ExecutionScheduler()
    return _scheduler
