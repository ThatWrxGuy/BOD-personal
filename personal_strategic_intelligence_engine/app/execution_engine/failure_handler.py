"""Failure handler - manages execution failures and rollbacks."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from app.execution_engine.execution_types import ExecutionStatus, FailureSeverity
from app.execution_engine.execution_models import ExecutionTask, ExecutionResult, FailureRecord


class FailureHandler:
    """Responds to execution failures.
    
    Possible responses:
    - retry task
    - skip task
    - rollback workflow
    - trigger council review
    
    Failure severity determines escalation level.
    """
    
    # Severity thresholds for automatic actions
    SEVERITY_THRESHOLDS = {
        FailureSeverity.MINOR: {"retry": True, "escalate": False},
        FailureSeverity.MODERATE: {"retry": True, "escalate": False},
        FailureSeverity.MAJOR: {"retry": False, "escalate": True},
        FailureSeverity.CRITICAL: {"retry": False, "escalate": True},
    }
    
    def __init__(self):
        self._failure_history: List[FailureRecord] = []
        self._max_retries = 3
    
    def handle_failure(
        self,
        task: ExecutionTask,
        error: Exception,
    ) -> Dict[str, Any]:
        """Handle a task failure.
        
        Args:
            task: The task that failed
            error: The error that occurred
            
        Returns:
            Action to take
        """
        # Determine severity
        severity = self._determine_severity(task, error)
        
        # Record failure
        failure = FailureRecord(
            failure_id=f"fail_{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            severity=severity,
            error_message=str(error),
            error_details={
                "error_type": type(error).__name__,
                "task_description": task.description,
            },
        )
        
        self._failure_history.append(failure)
        
        # Determine action based on severity
        action = self._determine_action(severity, task)
        
        return {
            "failure_id": failure.failure_id,
            "severity": severity.value,
            "action": action,
            "should_retry": self.SEVERITY_THRESHOLDS[severity]["retry"],
            "should_escalate": self.SEVERITY_THRESHOLDS[severity]["escalate"],
        }
    
    def _determine_severity(
        self,
        task: ExecutionTask,
        error: Exception,
    ) -> FailureSeverity:
        """Determine failure severity."""
        error_msg = str(error).lower()
        
        # Check error type and message
        if any(word in error_msg for word in ["critical", "fatal", "system"]):
            return FailureSeverity.CRITICAL
        
        if any(word in error_msg for word in ["major", "significant", "policy"]):
            return FailureSeverity.MAJOR
        
        if any(word in error_msg for word in ["moderate", "warning"]):
            return FailureSeverity.MODERATE
        
        # Default to minor
        return FailureSeverity.MINOR
    
    def _determine_action(
        self,
        severity: FailureSeverity,
        task: ExecutionTask,
    ) -> str:
        """Determine action to take based on severity."""
        thresholds = self.SEVERITY_THRESHOLDS[severity]
        
        if thresholds["retry"]:
            return "retry"
        elif thresholds["escalate"]:
            return "escalate"
        else:
            return "skip"
    
    def should_retry(self, task: ExecutionTask) -> bool:
        """Check if a task should be retried.
        
        Args:
            task: Task to check
            
        Returns:
            True if task should be retried
        """
        # Check failure history
        failures = [f for f in self._failure_history if f.task_id == task.task_id]
        
        if len(failures) >= self._max_retries:
            return False
        
        # Check if task was marked as resolved
        recent_failures = [f for f in failures if not f.resolved]
        
        return len(recent_failures) < self._max_retries
    
    def create_retry_task(self, task: ExecutionTask) -> ExecutionTask:
        """Create a retry version of a task.
        
        Args:
            task: Original task
            
        Returns:
            New task for retry
        """
        retry_task = ExecutionTask(
            task_id=f"{task.task_id}_retry_{uuid.uuid4().hex[:6]}",
            origin_decision=task.origin_decision,
            task_type=task.task_type,
            description=f"RETRY: {task.description}",
            priority=task.priority,
            permission_level=task.permission_level,
            dependencies=task.dependencies,
            required_resources=task.required_resources,
        )
        
        return retry_task
    
    def mark_resolved(self, failure_id: str, resolution: str):
        """Mark a failure as resolved.
        
        Args:
            failure_id: ID of the failure
            resolution: Resolution description
        """
        for failure in self._failure_history:
            if failure.failure_id == failure_id:
                failure.resolved = True
                failure.resolution = resolution
    
    def get_failure_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[FailureRecord]:
        """Get failure history.
        
        Args:
            task_id: Optional task ID to filter by
            limit: Maximum records to return
            
        Returns:
            List of failure records
        """
        if task_id:
            failures = [f for f in self._failure_history if f.task_id == task_id]
        else:
            failures = self._failure_history
        
        return failures[-limit:]
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """Get summary of failures.
        
        Returns:
            Summary statistics
        """
        if not self._failure_history:
            return {
                "total_failures": 0,
                "resolved": 0,
                "unresolved": 0,
            }
        
        total = len(self._failure_history)
        resolved = sum(1 for f in self._failure_history if f.resolved)
        
        severity_counts = {
            "critical": 0,
            "major": 0,
            "moderate": 0,
            "minor": 0,
        }
        
        for f in self._failure_history:
            severity_counts[f.severity.value] += 1
        
        return {
            "total_failures": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "by_severity": severity_counts,
        }
