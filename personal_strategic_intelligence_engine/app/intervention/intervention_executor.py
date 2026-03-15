"""Intervention Executor - Applies intervention changes to system state."""
import logging
from typing import Dict, Any, List
from datetime import datetime

from app.intervention.intervention_types import (
    Intervention,
    InterventionStatus,
    DomainState,
)

logger = logging.getLogger(__name__)


class InterventionExecutor:
    """Executes interventions by modifying system state."""
    
    def __init__(self):
        self.execution_log: List[Dict] = []
    
    def execute_intervention(
        self,
        intervention: Intervention,
        current_domains: List[DomainState],
    ) -> Dict[str, Any]:
        """Execute an intervention and return results."""
        
        logger.info(f"Executing intervention {intervention.intervention_id}")
        
        results = {
            "intervention_id": intervention.intervention_id,
            "executed_at": datetime.utcnow().isoformat(),
            "actions_executed": [],
            "actions_failed": [],
            "domain_changes": {},
        }
        
        intervention.status = InterventionStatus.EXECUTING
        
        # Execute each action
        for action in intervention.actions:
            try:
                result = self._execute_action(action, current_domains)
                results["actions_executed"].append({
                    "action_type": action.action_type,
                    "result": result,
                })
                logger.info(f"  Executed: {action.action_type} -> {result}")
            except Exception as e:
                results["actions_failed"].append({
                    "action_type": action.action_type,
                    "error": str(e),
                })
                logger.error(f"  Failed: {action.action_type} -> {e}")
        
        # Calculate final state changes
        for domain in current_domains:
            results["domain_changes"][domain.name] = {
                "performance": domain.performance_score,
                "risk": domain.risk_score,
                "resource_allocation": domain.resource_allocation,
            }
        
        # Mark as completed
        intervention.status = InterventionStatus.COMPLETED
        intervention.results = results
        
        return results
    
    def _execute_action(
        self,
        action,
        domains: List[DomainState],
    ) -> Dict[str, Any]:
        """Execute a single action."""
        
        action_type = action.action_type
        target = action.target
        value = action.value
        
        result = {"success": True, "changes": {}}
        
        if action_type == "reduce_active_tasks":
            # Reduce task load on target domain
            for domain in domains:
                if domain.name == target:
                    # Simulate improvement from reduced load
                    domain.performance_score = min(10, domain.performance_score + 0.5)
                    domain.risk_score = max(0, domain.risk_score - 0.3)
                    result["changes"]["performance"] = domain.performance_score
                    result["changes"]["risk"] = domain.risk_score
        
        elif action_type == "compress_focus_domains":
            # Limit focus to fewer domains
            result["changes"]["focus_domains"] = value
            result["message"] = f"Focus compressed to {value} domains"
        
        elif action_type == "add_recovery_block":
            # Add recovery time
            result["changes"]["recovery_hours_added"] = value
            # Recovery improves all domains slightly
            for domain in domains:
                domain.performance_score = min(10, domain.performance_score + 0.2)
            result["message"] = f"Added {value} recovery hours"
        
        elif action_type == "delay_initiatives":
            # Delay non-critical work
            result["changes"]["initiatives_delayed"] = value
            result["message"] = "Non-critical initiatives delayed"
        
        elif action_type == "increase_liquidity":
            # Increase liquidity (wealth domain)
            for domain in domains:
                if domain.name == target:
                    domain.performance_score = min(10, domain.performance_score + value * 2)
                    domain.risk_score = max(0, domain.risk_score - value)
            result["changes"]["liquidity_increased"] = True
        
        elif action_type == "reduce_spending":
            # Reduce spending
            result["changes"]["spending_reduced"] = value * 100
            result["message"] = f"Spending reduced by {value*100}%"
        
        elif action_type == "prioritize_income":
            # Focus on income generation
            for domain in domains:
                if domain.name == "wealth":
                    domain.performance_score = min(10, domain.performance_score + 0.5)
            result["changes"]["income_prioritized"] = True
        
        elif action_type == "pause_investments":
            # Pause new investments
            result["changes"]["investments_paused"] = value
            result["message"] = "New investments paused"
        
        elif action_type == "reduce_workload":
            # Reduce work hours
            result["changes"]["workload_reduced"] = abs(value)
            # Less work improves performance
            for domain in domains:
                if domain.name in ["health", "personal_development"]:
                    domain.performance_score = min(10, domain.performance_score + 0.3)
            result["message"] = f"Workload reduced by {abs(value)} hours"
        
        elif action_type == "enforce_recovery":
            # Enforce recovery
            for domain in domains:
                domain.performance_score = min(10, domain.performance_score + 0.2)
            result["changes"]["recovery_enforced"] = True
            result["message"] = "Recovery time enforced"
        
        elif action_type == "reduce_strategic_work":
            # Reduce strategic workload
            for domain in domains:
                if domain.name == "strategic_projects":
                    domain.risk_score = max(0, domain.risk_score - value * 2)
            result["changes"]["strategic_reduced"] = value
            result["message"] = f"Strategic work reduced by {value*100}%"
        
        elif action_type == "add_breaks":
            # Add mandatory breaks
            result["changes"]["breaks_added"] = value
            result["message"] = f"{value} mandatory breaks added"
        
        elif action_type == "realign_priorities":
            # Realign with goals
            for domain in domains:
                domain.alignment_score = min(10, domain.alignment_score + 0.3)
            result["changes"]["priorities_realigned"] = True
            result["message"] = "Priorities realigned with goals"
        
        elif action_type == "suspend_conflicting":
            # Suspend conflicting initiatives
            result["changes"]["initiatives_suspended"] = value
            result["message"] = "Conflicting initiatives suspended"
        
        elif action_type == "reset_weekly_focus":
            # Reset weekly focus
            result["changes"]["focus_reset"] = True
            result["message"] = "Weekly focus reset"
        
        elif action_type == "lock_priorities":
            # Lock priorities for a period
            result["changes"]["priority_lock_days"] = value
            result["message"] = f"Priorities locked for {value} days"
        
        elif action_type == "add_cooldown":
            # Add cooldown between changes
            result["changes"]["cooldown_hours"] = value
            result["message"] = f"{value}-hour cooldown added"
        
        elif action_type == "force_balance":
            # Force balanced allocation
            total = len(domains)
            for domain in domains:
                domain.resource_allocation = 100.0 / total
            result["changes"]["balanced"] = True
            result["message"] = "Resource allocation balanced"
        
        elif action_type == "defer_tasks":
            # Defer tasks
            result["changes"]["tasks_deferred"] = value * 100
            result["message"] = f"{value*100}% of tasks deferred"
        
        elif action_type == "automate_where_possible":
            # Automate tasks
            result["changes"]["automation_recommended"] = True
            result["message"] = "Automation recommended"
        
        elif action_type == "reduce_daily_targets":
            # Reduce daily targets
            result["changes"]["targets_reduced"] = value * 100
            result["message"] = f"Daily targets reduced by {value*100}%"
        
        elif action_type == "rebalance_resources":
            # Rebalance resources
            underfunded = [d for d in domains if d.resource_allocation < 10]
            for domain in underfunded:
                domain.resource_allocation += 2
            result["changes"]["rebalanced_domains"] = len(underfunded)
            result["message"] = "Resources rebalanced"
        
        elif action_type == "emergency_allocation":
            # Emergency allocation
            for domain in domains:
                if domain.resource_allocation < 10:
                    domain.resource_allocation += value * 100
            result["changes"]["emergency_added"] = True
            result["message"] = f"Emergency allocation added"
        
        elif action_type == "reduce_wealthy_domains":
            # Reduce overfunded domains
            overfunded = [d for d in domains if d.resource_allocation > 15]
            for domain in overfunded:
                domain.resource_allocation -= value * 100
            result["changes"]["reduced_domains"] = len(overfunded)
            result["message"] = f"Reduced {len(overfunded)} overfunded domains"
        
        elif action_type == "halt_non_essential":
            # Halt non-essential activities
            result["changes"]["halted"] = True
            result["message"] = "Non-essential activities halted"
        
        elif action_type == "focus_recovery":
            # Focus all on recovery
            for domain in domains:
                domain.performance_score = min(10, domain.performance_score + 0.5)
                domain.risk_score = max(0, domain.risk_score - 0.3)
            result["changes"]["recovery_focused"] = True
            result["message"] = "All focus on recovery"
        
        elif action_type == "notify_executive":
            # Notify command center
            result["changes"]["notification_sent"] = True
            result["message"] = "Executive notified"
        
        else:
            result["success"] = False
            result["message"] = f"Unknown action type: {action_type}"
        
        return result
    
    def can_execute(self, intervention: Intervention) -> bool:
        """Check if intervention can be executed."""
        
        # Check if already executing
        if intervention.status == InterventionStatus.EXECUTING:
            return False
        
        # Check if already completed
        if intervention.status == InterventionStatus.COMPLETED:
            return False
        
        return True
