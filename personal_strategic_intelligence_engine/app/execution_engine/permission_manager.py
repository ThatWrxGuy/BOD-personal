"""Permission manager - governs task execution permissions."""
from typing import Dict, Any

from app.execution_engine.execution_types import PermissionLevel, ExecutionPriority
from app.execution_engine.execution_models import ExecutionTask, PermissionDecision


class PermissionManager:
    """Determines whether tasks may execute autonomously.
    
    Rules consider:
    - Risk level
    - Policy restrictions
    - Doctrine rules
    - Task priority
    
    Possible outcomes:
    - AUTONOMOUS: execute immediately
    - NOTIFY_ONLY: execute but log event
    - REQUIRES_APPROVAL: halt until approval
    """
    
    # Risk thresholds
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.4
    
    # Priority thresholds
    CRITICAL_PRIORITY = ExecutionPriority.CRITICAL
    HIGH_PRIORITY = ExecutionPriority.HIGH
    
    def __init__(self):
        self._policy_rules = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default permission rules."""
        # High priority tasks can run autonomously
        self._policy_rules["auto_high_priority"] = {
            "condition": lambda task: task.priority in [
                ExecutionPriority.CRITICAL,
                ExecutionPriority.HIGH,
            ],
            "permission": PermissionLevel.AUTONOMOUS,
            "reason": "High priority task",
        }
        
        # Risk tasks require approval
        self._policy_rules["risk_task"] = {
            "condition": lambda task: "risk" in task.description.lower(),
            "permission": PermissionLevel.REQUIRES_APPROVAL,
            "reason": "Risk-related tasks require approval",
        }
        
        # Financial tasks require approval
        self._policy_rules["financial_task"] = {
            "condition": lambda task: any(
                word in task.description.lower()
                for word in ["allocat", "rebalanc", "trade", "invest"]
            ),
            "permission": PermissionLevel.REQUIRES_APPROVAL,
            "reason": "Financial tasks require approval",
        }
        
        # Monitoring tasks are autonomous
        self._policy_rules["monitoring_task"] = {
            "condition": lambda task: any(
                word in task.description.lower()
                for word in ["monitor", "check", "validate", "report"]
            ),
            "permission": PermissionLevel.AUTONOMOUS,
            "reason": "Monitoring tasks are autonomous",
        }
    
    def evaluate_permission(
        self,
        task: ExecutionTask,
        context: Dict[str, Any] = None,
    ) -> PermissionDecision:
        """Evaluate permission for a task.
        
        Args:
            task: Task to evaluate
            context: Optional execution context
            
        Returns:
            Permission decision
        """
        context = context or {}
        
        # Check each policy rule in order
        for rule_name, rule in self._policy_rules.items():
            if rule["condition"](task):
                return PermissionDecision(
                    task_id=task.task_id,
                    permission_level=rule["permission"],
                    approved=rule["permission"] != PermissionLevel.REQUIRES_APPROVAL,
                    reason=rule["reason"],
                )
        
        # Default: autonomous for low-risk tasks
        return PermissionDecision(
            task_id=task.task_id,
            permission_level=PermissionLevel.AUTONOMOUS,
            approved=True,
            reason="Default autonomous permission",
        )
    
    def evaluate_batch(
        self,
        tasks: list[ExecutionTask],
        context: Dict[str, Any] = None,
    ) -> list[PermissionDecision]:
        """Evaluate permissions for multiple tasks.
        
        Args:
            tasks: Tasks to evaluate
            context: Optional execution context
            
        Returns:
            List of permission decisions
        """
        return [self.evaluate_permission(task, context) for task in tasks]
    
    def add_policy_rule(
        self,
        rule_name: str,
        condition,
        permission: PermissionLevel,
        reason: str,
    ):
        """Add a custom policy rule.
        
        Args:
            rule_name: Name of the rule
            condition: Function that takes a task and returns bool
            permission: Permission level to grant
            reason: Human-readable reason
        """
        self._policy_rules[rule_name] = {
            "condition": condition,
            "permission": permission,
            "reason": reason,
        }
    
    def remove_policy_rule(self, rule_name: str) -> bool:
        """Remove a policy rule.
        
        Args:
            rule_name: Name of the rule to remove
            
        Returns:
            True if rule was removed
        """
        if rule_name in self._policy_rules:
            del self._policy_rules[rule_name]
            return True
        return False
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Get summary of permission rules.
        
        Returns:
            Summary of rules
        """
        autonomous_count = sum(
            1 for r in self._policy_rules.values()
            if r["permission"] == PermissionLevel.AUTONOMOUS
        )
        
        approval_count = sum(
            1 for r in self._policy_rules.values()
            if r["permission"] == PermissionLevel.REQUIRES_APPROVAL
        )
        
        return {
            "total_rules": len(self._policy_rules),
            "autonomous_rules": autonomous_count,
            "approval_rules": approval_count,
        }
