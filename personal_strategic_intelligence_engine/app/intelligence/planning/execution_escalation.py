"""Execution Escalation - Detects problems and triggers alerts."""
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.planning.execution_models import (
    ExecutionTask,
    ExecutionProgram,
    ExecutionAlert,
    ExecutionStatus,
    AlertSeverity,
)


class ExecutionEscalation:
    """Detects execution problems and triggers escalation."""
    
    def __init__(self):
        self.alerts: Dict[str, List[ExecutionAlert]] = {}
        self.escalation_count: int = 0
    
    def check_execution(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
    ) -> List[ExecutionAlert]:
        """Check execution and generate alerts."""
        
        alerts = []
        
        # Check for overdue tasks
        overdue = self._check_overdue(tasks)
        alerts.extend(overdue)
        
        # Check for blocked tasks
        blocked = self._check_blocked(tasks)
        alerts.extend(blocked)
        
        # Check for failed tasks
        failed = self._check_failed(tasks)
        alerts.extend(failed)
        
        # Check for milestone risks
        milestone_alerts = self._check_milestones(program, tasks)
        alerts.extend(milestone_alerts)
        
        # Store alerts
        if program.id not in self.alerts:
            self.alerts[program.id] = []
        
        self.alerts[program.id].extend(alerts)
        self.escalation_count += len(alerts)
        
        return alerts
    
    def _check_overdue(self, tasks: List[ExecutionTask]) -> List[ExecutionAlert]:
        """Check for overdue tasks."""
        
        alerts = []
        now = datetime.utcnow()
        
        for task in tasks:
            if task.due_at and now > task.due_at:
                if task.status not in [ExecutionStatus.COMPLETED, ExecutionStatus.CANCELLED]:
                    alert = ExecutionAlert(
                        id=str(uuid.uuid4())[:8],
                        execution_program_id=task.execution_program_id,
                        alert_type="overdue",
                        severity=AlertSeverity.HIGH if task.priority.value == "critical" else AlertSeverity.MEDIUM,
                        message=f"Task '{task.title}' is overdue",
                        description=f"Task was due {task.due_at}",
                        recommended_action="complete_or_extend",
                        task_id=task.id,
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _check_blocked(self, tasks: List[ExecutionTask]) -> List[ExecutionAlert]:
        """Check for blocked tasks."""
        
        alerts = []
        
        for task in tasks:
            if task.status == ExecutionStatus.BLOCKED:
                alert = ExecutionAlert(
                    id=str(uuid.uuid4())[:8],
                    execution_program_id=task.execution_program_id,
                    alert_type="blocked",
                    severity=AlertSeverity.HIGH,
                    message=f"Task '{task.title}' is blocked",
                    description="Task is waiting on dependencies",
                    recommended_action="resolve_dependency",
                    task_id=task.id,
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_failed(self, tasks: List[ExecutionTask]) -> List[ExecutionAlert]:
        """Check for failed tasks."""
        
        alerts = []
        
        for task in tasks:
            if task.status == ExecutionStatus.FAILED:
                alert = ExecutionAlert(
                    id=str(uuid.uuid4())[:8],
                    execution_program_id=task.execution_program_id,
                    alert_type="failed",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Task '{task.title}' has failed",
                    description=f"Task failed after {task.retry_count} retries",
                    recommended_action="retry_or_replan",
                    task_id=task.id,
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_milestones(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
    ) -> List[ExecutionAlert]:
        """Check milestone progress."""
        
        alerts = []
        
        # If progress is very slow, warn
        if program.progress_percent < 10 and program.total_steps > 2:
            # Could add milestone-specific checks here
            pass
        
        return alerts
    
    def get_alerts(
        self,
        program_id: str,
        unresolved_only: bool = True,
    ) -> List[ExecutionAlert]:
        """Get alerts for a program."""
        
        if program_id not in self.alerts:
            return []
        
        alerts = self.alerts[program_id]
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        return alerts
    
    def get_critical_alerts(
        self,
        program_id: str,
    ) -> List[ExecutionAlert]:
        """Get critical alerts for a program."""
        
        alerts = self.get_alerts(program_id, unresolved_only=True)
        
        return [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
    
    def resolve_alert(self, alert_id: str, program_id: str) -> bool:
        """Mark an alert as resolved."""
        
        if program_id not in self.alerts:
            return False
        
        for alert in self.alerts[program_id]:
            if alert.id == alert_id:
                alert.resolved = True
                return True
        
        return False


_escalation: Optional[ExecutionEscalation] = None


def get_execution_escalation() -> ExecutionEscalation:
    """Get the global execution escalation."""
    global _escalation
    if _escalation is None:
        _escalation = ExecutionEscalation()
    return _escalation
