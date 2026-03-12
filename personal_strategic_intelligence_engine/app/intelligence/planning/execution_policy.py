"""Execution Policy - Defines execution automation policies."""
from typing import List, Dict, Any

from app.intelligence.planning.execution_models import ExecutionPolicy, ExecutionType


class ExecutionPolicyManager:
    """Manages execution policies and automation rules."""
    
    def __init__(self):
        self.policy = ExecutionPolicy()
        self.custom_rules: Dict[str, str] = {}
    
    def can_autocomplete(self, task_description: str, risk_level: str) -> bool:
        """Determine if a task can be auto-completed."""
        
        # Check manual-only list
        for action in self.policy.manual_only_actions:
            if action.lower() in task_description.lower():
                return False
        
        # High risk actions require manual
        if risk_level == "high":
            return False
        
        # Check threshold
        if "transfer" in task_description.lower() or "payment" in task_description.lower():
            return False
        
        return True
    
    def get_execution_type(
        self,
        task_title: str,
        risk_assessment: str,
    ) -> ExecutionType:
        """Determine execution type for a task."""
        
        # Check manual-only
        for action in self.policy.manual_only_actions:
            if action.lower() in task_title.lower():
                return ExecutionType.MANUAL
        
        # Check if can be automated
        if self.can_autocomplete(task_title, risk_assessment):
            if self.policy.auto_execute_low_risk:
                return ExecutionType.AUTOMATED
        
        return ExecutionType.ASSISTED
    
    def requires_approval(
        self,
        task_title: str,
        resource_value: float = 0.0,
    ) -> bool:
        """Determine if a task requires approval."""
        
        # Check value threshold
        if resource_value > self.policy.requires_approval_above:
            return True
        
        # Check high-risk actions
        for action in self.policy.high_risk_actions:
            if action.lower() in task_title.lower():
                return True
        
        return False
    
    def get_task_timeout(self, task_type: str) -> int:
        """Get timeout in hours for a task type."""
        
        return self.policy.task_timeout_hours
    
    def add_custom_rule(self, trigger: str, action: str) -> None:
        """Add a custom execution rule."""
        
        self.custom_rules[trigger] = action
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get policy summary."""
        
        return {
            "auto_approve_threshold": self.policy.auto_approve_threshold,
            "auto_execute_low_risk": self.policy.auto_execute_low_risk,
            "high_risk_actions": self.policy.high_risk_actions,
            "manual_only_actions": self.policy.manual_only_actions,
            "task_timeout_hours": self.policy.task_timeout_hours,
            "requires_approval_above": self.policy.requires_approval_above,
            "custom_rules_count": len(self.custom_rules),
        }


_policy_manager: ExecutionPolicyManager = None


def get_execution_policy_manager() -> ExecutionPolicyManager:
    """Get the global execution policy manager."""
    global _policy_manager
    if _policy_manager is None:
        _policy_manager = ExecutionPolicyManager()
    return _policy_manager
