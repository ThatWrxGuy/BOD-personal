"""Execution Tracker - Tracks execution progress."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.intelligence.planning.execution_models import (
    ExecutionTask,
    ExecutionProgram,
    ExecutionStatus,
)


class ExecutionTracker:
    """Tracks execution progress of programs."""
    
    def __init__(self):
        self.task_status: Dict[str, ExecutionStatus] = {}
    
    def update_task_status(
        self,
        task_id: str,
        new_status: ExecutionStatus,
    ) -> bool:
        """Update status of a task."""
        
        old_status = self.task_status.get(task_id)
        self.task_status[task_id] = new_status
        
        return old_status != new_status
    
    def update_program_progress(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
    ) -> ExecutionProgram:
        """Update program progress based on task status."""
        
        completed = 0
        blocked = 0
        overdue = 0
        
        now = datetime.utcnow()
        
        for task in tasks:
            status = self.task_status.get(task.id, task.status)
            
            if status == ExecutionStatus.COMPLETED:
                completed += 1
            elif status == ExecutionStatus.BLOCKED:
                blocked += 1
            elif status == ExecutionStatus.PENDING and task.due_at:
                if now > task.due_at:
                    overdue += 1
        
        program.completed_steps = completed
        program.blocked_steps = blocked
        program.overdue_steps = overdue
        program.progress_percent = (
            (completed / program.total_steps * 100)
            if program.total_steps > 0 else 0
        )
        
        # Update program status
        if completed == program.total_steps:
            program.status = ExecutionStatus.COMPLETED
            program.completed_at = datetime.utcnow()
        elif blocked > 0:
            program.status = ExecutionStatus.BLOCKED
        elif program.status == ExecutionStatus.PENDING:
            program.status = ExecutionStatus.ACTIVE
            if not program.started_at:
                program.started_at = datetime.utcnow()
        
        return program
    
    def get_overdue_tasks(
        self,
        tasks: List[ExecutionTask],
    ) -> List[ExecutionTask]:
        """Get tasks that are overdue."""
        
        now = datetime.utcnow()
        overdue = []
        
        for task in tasks:
            if task.due_at and now > task.due_at:
                if task.status not in [ExecutionStatus.COMPLETED, ExecutionStatus.CANCELLED]:
                    overdue.append(task)
        
        return overdue
    
    def get_blocked_tasks(
        self,
        tasks: List[ExecutionTask],
    ) -> List[ExecutionTask]:
        """Get tasks that are blocked."""
        
        blocked = []
        
        for task in tasks:
            if task.status == ExecutionStatus.BLOCKED:
                blocked.append(task)
        
        return blocked
    
    def get_next_deadline(
        self,
        tasks: List[ExecutionTask],
    ) -> Optional[datetime]:
        """Get the next upcoming deadline."""
        
        now = datetime.utcnow()
        next_deadline = None
        
        for task in tasks:
            if task.due_at and task.due_at > now:
                if task.status not in [ExecutionStatus.COMPLETED, ExecutionStatus.CANCELLED]:
                    if next_deadline is None or task.due_at < next_deadline:
                        next_deadline = task.due_at
        
        return next_deadline


_tracker: Optional[ExecutionTracker] = None


def get_execution_tracker() -> ExecutionTracker:
    """Get the global execution tracker."""
    global _tracker
    if _tracker is None:
        _tracker = ExecutionTracker()
    return _tracker
