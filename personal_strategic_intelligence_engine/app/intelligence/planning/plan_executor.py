"""Plan Executor - Converts strategic plans into execution programs."""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.intelligence.planning.planning_models import StrategicPlan, PlanStep
from app.intelligence.planning.execution_models import (
    ExecutionProgram,
    ExecutionTask,
    ExecutionMilestone,
    ExecutionStatus,
    TaskPriority,
    ExecutionType,
)


class PlanExecutor:
    """Converts strategic plans into execution programs."""
    
    def __init__(self):
        self.programs: Dict[str, ExecutionProgram] = {}
    
    def execute_plan(self, plan: StrategicPlan) -> ExecutionProgram:
        """Convert a strategic plan into an execution program."""
        
        # Create program
        program = ExecutionProgram(
            id=str(uuid.uuid4())[:8],
            plan_id=plan.id,
            goal_id=plan.goal_id,
            goal_title=plan.title,
            status=ExecutionStatus.PENDING,
            total_steps=len(plan.steps),
            execution_mode=self._determine_execution_mode(plan),
        )
        
        # Create tasks from steps
        tasks = self._create_tasks(plan.steps, program.id)
        
        # Create milestones
        milestones = self._create_milestones(plan, program.id)
        
        # Store
        self.programs[program.id] = program
        
        return program
    
    def _determine_execution_mode(self, plan: StrategicPlan) -> ExecutionType:
        """Determine execution mode based on plan type."""
        
        # Conservative and resilience plans are more manual
        if plan.plan_type.value in ["conservative", "resilience"]:
            return ExecutionType.ASSISTED
        elif plan.plan_type.value == "aggressive":
            return ExecutionType.MANUAL
        else:
            return ExecutionType.ASSISTED
    
    def _create_tasks(
        self,
        steps: List[PlanStep],
        program_id: str,
    ) -> List[ExecutionTask]:
        """Create execution tasks from plan steps."""
        
        tasks = []
        
        for i, step in enumerate(steps):
            # Determine priority based on position
            priority = self._determine_priority(i, len(steps))
            
            # Determine execution type
            exec_type = self._determine_task_type(step)
            
            # Schedule (simple sequential scheduling)
            scheduled = datetime.utcnow() + timedelta(days=i * 7)
            due = scheduled + timedelta(days=step.estimated_duration_days)
            
            # Determine dependencies
            depends_on = []
            if i > 0:
                # Depends on previous step
                depends_on = [tasks[i-1].id]
            
            task = ExecutionTask(
                id=str(uuid.uuid4())[:8],
                execution_program_id=program_id,
                step_id=step.step_id,
                title=step.action,
                description=step.description,
                priority=priority,
                status=ExecutionStatus.PENDING,
                scheduled_at=scheduled,
                due_at=due,
                dependency_ids=[],
                depends_on=depends_on,
                required_resources=step.required_resources,
                execution_type=exec_type,
                is_critical_path=(i == 0 or i == len(steps) - 1),
            )
            
            tasks.append(task)
        
        return tasks
    
    def _determine_priority(self, position: int, total: int) -> TaskPriority:
        """Determine task priority based on position."""
        
        if position == 0:
            return TaskPriority.CRITICAL
        elif position < total / 2:
            return TaskPriority.HIGH
        elif position < total - 1:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.MEDIUM
    
    def _determine_task_type(self, step: PlanStep) -> ExecutionType:
        """Determine execution type for a task."""
        
        # High impact tasks need assistance
        if step.expected_impact > 2.0:
            return ExecutionType.ASSISTED
        
        return ExecutionType.AUTOMATED
    
    def _create_milestones(
        self,
        plan: StrategicPlan,
        program_id: str,
    ) -> List[ExecutionMilestone]:
        """Create milestones from plan."""
        
        milestones = []
        
        # Create milestones at quarter points
        total = len(plan.steps)
        quarter = total // 4
        
        milestone_points = [quarter, quarter * 2, quarter * 3, total - 1]
        
        milestone_names = ["Foundation", "Progress", "Advanced", "Completion"]
        
        for i, point in enumerate(milestone_points):
            if point < len(plan.steps):
                milestone = ExecutionMilestone(
                    id=str(uuid.uuid4())[:8],
                    execution_program_id=program_id,
                    name=milestone_names[i],
                    description=f"Complete milestone: {milestone_names[i]}",
                    target_date=datetime.utcnow() + timedelta(days=(i + 1) * 21),
                    status=ExecutionStatus.PENDING,
                    tasks_total=point + 1 if i > 0 else 1,
                )
                milestones.append(milestone)
        
        return milestones
    
    def get_program(self, program_id: str) -> Optional[ExecutionProgram]:
        """Get an execution program."""
        return self.programs.get(program_id)
    
    def get_all_programs(self) -> List[ExecutionProgram]:
        """Get all programs."""
        return list(self.programs.values())


_executor: Optional[PlanExecutor] = None


def get_plan_executor() -> PlanExecutor:
    """Get the global plan executor."""
    global _executor
    if _executor is None:
        _executor = PlanExecutor()
    return _executor
