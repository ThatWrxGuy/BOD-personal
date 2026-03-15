"""Execution Service - Central orchestration for plan execution."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.intelligence.planning.planning_models import StrategicPlan
from app.intelligence.planning.execution_models import (
    ExecutionProgram,
    ExecutionTask,
    ExecutionMilestone,
    ExecutionAlert,
    ExecutionSummary,
    ExecutionStatus,
)
from app.intelligence.planning.plan_executor import get_plan_executor
from app.intelligence.planning.execution_scheduler import get_execution_scheduler
from app.intelligence.planning.execution_tracker import get_execution_tracker
from app.intelligence.planning.execution_escalation import get_execution_escalation
from app.intelligence.planning.execution_policy import get_execution_policy_manager


class ExecutionService:
    """Central orchestration for plan execution."""
    
    def __init__(self):
        self.executor = get_plan_executor()
        self.scheduler = get_execution_scheduler()
        self.tracker = get_execution_tracker()
        self.escalation = get_execution_escalation()
        self.policy = get_execution_policy_manager()
        
        # Storage
        self.tasks: Dict[str, List[ExecutionTask]] = {}
        self.milestones: Dict[str, List[ExecutionMilestone]] = {}
    
    def create_execution_program(
        self,
        plan: StrategicPlan,
    ) -> ExecutionProgram:
        """Create an execution program from a strategic plan."""
        
        # Execute plan
        program = self.executor.execute_plan(plan)
        
        # Get tasks (need to create them)
        tasks = self._create_tasks_from_plan(plan, program.id)
        
        # Schedule tasks
        scheduled_tasks = self.scheduler.schedule_tasks(tasks, program)
        
        # Store tasks
        self.tasks[program.id] = scheduled_tasks
        
        # Apply policy
        self._apply_policy(scheduled_tasks)
        
        # Create milestones
        milestones = self._create_milestones(plan, program.id)
        self.milestones[program.id] = milestones
        
        # Initialize progress
        self.tracker.update_program_progress(program, scheduled_tasks)
        
        return program
    
    def _create_tasks_from_plan(
        self,
        plan: StrategicPlan,
        program_id: str,
    ) -> List[ExecutionTask]:
        """Create tasks from plan steps."""
        
        from app.intelligence.planning.execution_models import ExecutionTask, TaskPriority, ExecutionType
        
        tasks = []
        
        for i, step in enumerate(plan.steps):
            priority = TaskPriority.CRITICAL if i == 0 else TaskPriority.MEDIUM
            exec_type = ExecutionType.ASSISTED
            
            task = ExecutionTask(
                id=str(uuid.uuid4())[:8],
                execution_program_id=program_id,
                step_id=step.step_id,
                title=step.action,
                description=step.description,
                priority=priority,
                status=ExecutionStatus.PENDING,
                depends_on=[tasks[-1].id] if tasks else [],
                required_resources=step.required_resources,
                execution_type=exec_type,
                is_critical_path=(i == 0 or i == len(plan.steps) - 1),
            )
            
            tasks.append(task)
        
        return tasks
    
    def _create_milestones(
        self,
        plan: StrategicPlan,
        program_id: str,
    ) -> List[ExecutionMilestone]:
        """Create milestones from plan."""
        
        from app.intelligence.planning.execution_models import ExecutionMilestone
        
        milestones = []
        
        # Create completion milestone
        milestone = ExecutionMilestone(
            id=str(uuid.uuid4())[:8],
            execution_program_id=program_id,
            name="Plan Completion",
            description=f"Complete: {plan.title}",
            status=ExecutionStatus.PENDING,
            tasks_total=len(plan.steps),
        )
        
        milestones.append(milestone)
        
        return milestones
    
    def _apply_policy(self, tasks: List[ExecutionTask]) -> None:
        """Apply execution policy to tasks."""
        
        for task in tasks:
            exec_type = self.policy.get_execution_type(task.title, "medium")
            task.execution_type = exec_type
    
    def get_program_status(
        self,
        program_id: str,
    ) -> Optional[ExecutionProgram]:
        """Get status of an execution program."""
        
        return self.executor.get_program(program_id)
    
    def get_tasks(
        self,
        program_id: str,
    ) -> List[ExecutionTask]:
        """Get tasks for a program."""
        
        return self.tasks.get(program_id, [])
    
    def get_alerts(
        self,
        program_id: str,
    ) -> List[ExecutionAlert]:
        """Get alerts for a program."""
        
        return self.escalation.get_alerts(program_id)
    
    def update_task_status(
        self,
        task_id: str,
        program_id: str,
        new_status: ExecutionStatus,
    ) -> bool:
        """Update task status and propagate changes."""
        
        # Update status
        updated = self.tracker.update_task_status(task_id, new_status)
        
        if updated:
            # Get program
            program = self.executor.get_program(program_id)
            
            if program:
                tasks = self.tasks.get(program_id, [])
                
                # Update progress
                self.tracker.update_program_progress(program, tasks)
                
                # Check for alerts
                self.escalation.check_execution(program, tasks)
        
        return updated
    
    def get_execution_summary(
        self,
        program_id: str,
    ) -> Optional[ExecutionSummary]:
        """Get execution summary for a program."""
        
        program = self.executor.get_program(program_id)
        
        if not program:
            return None
        
        tasks = self.tasks.get(program_id, [])
        alerts = self.escalation.get_alerts(program_id, unresolved_only=True)
        
        # Determine health
        health = "healthy"
        if program.status == ExecutionStatus.BLOCKED:
            health = "blocked"
        elif program.status == ExecutionStatus.FAILED:
            health = "failed"
        elif program.progress_percent < 50 and program.overdue_steps > 0:
            health = "degraded"
        
        # Get next deadline
        next_deadline = self.tracker.get_next_deadline(tasks)
        
        # Build recommendation
        recommendation = ""
        if health == "blocked":
            recommendation = "Resolve blocked tasks to continue execution"
        elif health == "degraded":
            recommendation = "Address overdue tasks to get back on track"
        elif program.progress_percent == 100:
            recommendation = "Execution complete - review results"
        
        return ExecutionSummary(
            program_id=program_id,
            overall_health=health,
            progress_percent=program.progress_percent,
            tasks_total=program.total_steps,
            tasks_completed=program.completed_steps,
            tasks_blocked=program.blocked_steps,
            tasks_overdue=program.overdue_steps,
            active_alerts=len(alerts),
            critical_alerts=len([a for a in alerts if a.severity.value == "critical"]),
            next_deadline=next_deadline,
            recommendation=recommendation,
        )
    
    def get_all_programs(self) -> List[ExecutionProgram]:
        """Get all execution programs."""
        
        return self.executor.get_all_programs()


# Global service
_execution_service: Optional[ExecutionService] = None


def get_execution_service() -> ExecutionService:
    """Get the global execution service."""
    global _execution_service
    if _execution_service is None:
        _execution_service = ExecutionService()
    return _execution_service
