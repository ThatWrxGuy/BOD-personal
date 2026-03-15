"""Intervention Protocols - Structured protocols for common system failures."""
from typing import List, Dict, Any
from app.intervention.intervention_types import (
    InterventionProtocol,
    InterventionType,
    TriggerType,
)


class InterventionProtocols:
    """Collection of intervention protocols for common failure modes."""
    
    @staticmethod
    def get_all_protocols() -> List[InterventionProtocol]:
        """Get all defined protocols."""
        return [
            InterventionProtocols.operations_collapse_protocol(),
            InterventionProtocols.wealth_risk_protocol(),
            InterventionProtocols.burnout_risk_protocol(),
            InterventionProtocols.strategic_drift_protocol(),
            InterventionProtocols.domain_oscillation_protocol(),
            InterventionProtocols.execution_overload_protocol(),
            InterventionProtocols.resource_starvation_protocol(),
            InterventionProtocols.emergency_protocol(),
        ]
    
    @staticmethod
    def operations_collapse_protocol() -> InterventionProtocol:
        """Protocol for handling operations domain collapse."""
        return InterventionProtocol(
            protocol_id="ops_collapse_001",
            name="Operations Collapse Recovery",
            description="Reduce operational load when operations domain collapses",
            trigger_conditions=[
                TriggerType.DOMAIN_PERFORMANCE_COLLAPSE,
                TriggerType.EXECUTION_OVERLOAD,
            ],
            intervention_type=InterventionType.DOMAIN_STABILIZATION,
            actions=[
                {
                    "action_type": "reduce_active_tasks",
                    "target": "operations",
                    "value": 0.5,
                    "reason": "Halve active tasks to reduce load"
                },
                {
                    "action_type": "compress_focus_domains",
                    "target": "focus",
                    "value": 3,
                    "reason": "Limit focus to 3 domains"
                },
                {
                    "action_type": "add_recovery_block",
                    "target": "schedule",
                    "value": 2,
                    "reason": "Add 2 recovery hours daily"
                },
                {
                    "action_type": "delay_initiatives",
                    "target": "non_critical",
                    "value": True,
                    "reason": "Delay non-critical initiatives"
                },
            ],
            cooldown_hours=48,
            max_per_day=1,
            confidence_threshold=0.6,
            is_emergency=False,
        )
    
    @staticmethod
    def wealth_risk_protocol() -> InterventionProtocol:
        """Protocol for handling wealth domain risk escalation."""
        return InterventionProtocol(
            protocol_id="wealth_risk_001",
            name="Wealth Risk Mitigation",
            description="Reduce financial risk when wealth domain shows elevated risk",
            trigger_conditions=[
                TriggerType.RISK_ESCALATION,
                TriggerType.RESOURCE_STARVATION,
            ],
            intervention_type=InterventionType.RISK_MITIGATION,
            actions=[
                {
                    "action_type": "increase_liquidity",
                    "target": "wealth",
                    "value": 0.3,
                    "reason": "Increase liquidity by 30%"
                },
                {
                    "action_type": "reduce_spending",
                    "target": "non_essential",
                    "value": 0.2,
                    "reason": "Reduce non-essential spending by 20%"
                },
                {
                    "action_type": "prioritize_income",
                    "target": "revenue",
                    "value": True,
                    "reason": "Prioritize income generation"
                },
                {
                    "action_type": "pause_investments",
                    "target": "new_investments",
                    "value": True,
                    "reason": "Pause new investment commitments"
                },
            ],
            cooldown_hours=24,
            max_per_day=2,
            confidence_threshold=0.5,
            is_emergency=False,
        )
    
    @staticmethod
    def burnout_risk_protocol() -> InterventionProtocol:
        """Protocol for handling burnout risk."""
        return InterventionProtocol(
            protocol_id="burnout_001",
            name="Burnout Prevention",
            description="Reduce workload intensity to prevent burnout",
            trigger_conditions=[
                TriggerType.RISK_ESCALATION,
                TriggerType.EXECUTION_OVERLOAD,
            ],
            intervention_type=InterventionType.WORKLOAD_REDUCTION,
            actions=[
                {
                    "action_type": "reduce_workload",
                    "target": "daily_hours",
                    "value": -2,
                    "reason": "Reduce daily work hours by 2"
                },
                {
                    "action_type": "enforce_recovery",
                    "target": "schedule",
                    "value": True,
                    "reason": "Enforce recovery time blocks"
                },
                {
                    "action_type": "reduce_strategic_work",
                    "target": "strategic_projects",
                    "value": 0.5,
                    "reason": "Reduce strategic project load by 50%"
                },
                {
                    "action_type": "add_breaks",
                    "target": "schedule",
                    "value": 2,
                    "reason": "Add 2 mandatory break periods"
                },
            ],
            cooldown_hours=72,
            max_per_day=1,
            confidence_threshold=0.7,
            is_emergency=False,
        )
    
    @staticmethod
    def strategic_drift_protocol() -> InterventionProtocol:
        """Protocol for handling strategic drift."""
        return InterventionProtocol(
            protocol_id="drift_001",
            name="Strategic Drift Correction",
            description="Realign priorities when strategic drift is detected",
            trigger_conditions=[
                TriggerType.STRATEGIC_DRIFT,
                TriggerType.SUSTAINED_IMBALANCE,
            ],
            intervention_type=InterventionType.FOCUS_REALIGNMENT,
            actions=[
                {
                    "action_type": "realign_priorities",
                    "target": "goals",
                    "value": True,
                    "reason": "Realign with long-term strategic goals"
                },
                {
                    "action_type": "suspend_conflicting",
                    "target": "initiatives",
                    "value": True,
                    "reason": "Suspend conflicting initiatives"
                },
                {
                    "action_type": "reset_weekly_focus",
                    "target": "priorities",
                    "value": True,
                    "reason": "Reset weekly focus areas"
                },
            ],
            cooldown_hours=168,  # 1 week
            max_per_day=1,
            confidence_threshold=0.8,
            is_emergency=False,
        )
    
    @staticmethod
    def domain_oscillation_protocol() -> InterventionProtocol:
        """Protocol for handling priority oscillation."""
        return InterventionProtocol(
            protocol_id="oscillation_001",
            name="Priority Oscillation Stabilization",
            description="Stabilize domain priorities when oscillation detected",
            trigger_conditions=[
                TriggerType.PRIORITY_OSCILLATION,
            ],
            intervention_type=InterventionType.PRIORITY_COMPRESSION,
            actions=[
                {
                    "action_type": "lock_priorities",
                    "target": "weekly_focus",
                    "value": 7,
                    "reason": "Lock priorities for 7 days"
                },
                {
                    "action_type": "add_cooldown",
                    "target": "priority_changes",
                    "value": 48,
                    "reason": "Add 48-hour cooldown between changes"
                },
                {
                    "action_type": "force_balance",
                    "target": "resource_allocation",
                    "value": True,
                    "reason": "Force balanced resource allocation"
                },
            ],
            cooldown_hours=96,  # 4 days
            max_per_day=1,
            confidence_threshold=0.75,
            is_emergency=False,
        )
    
    @staticmethod
    def execution_overload_protocol() -> InterventionProtocol:
        """Protocol for handling execution overload."""
        return InterventionProtocol(
            protocol_id="overload_001",
            name="Execution Overload Relief",
            description="Reduce execution load when overwhelmed",
            trigger_conditions=[
                TriggerType.EXECUTION_OVERLOAD,
            ],
            intervention_type=InterventionType.WORKLOAD_REDUCTION,
            actions=[
                {
                    "action_type": "defer_tasks",
                    "target": "backlog",
                    "value": 0.3,
                    "reason": "Defer 30% of tasks"
                },
                {
                    "action_type": "automate_where_possible",
                    "target": "tasks",
                    "value": True,
                    "reason": "Identify automatable tasks"
                },
                {
                    "action_type": "reduce_daily_targets",
                    "target": "goals",
                    "value": 0.7,
                    "reason": "Reduce daily targets by 30%"
                },
            ],
            cooldown_hours=24,
            max_per_day=2,
            confidence_threshold=0.6,
            is_emergency=False,
        )
    
    @staticmethod
    def resource_starvation_protocol() -> InterventionProtocol:
        """Protocol for handling resource starvation."""
        return InterventionProtocol(
            protocol_id="starvation_001",
            name="Resource Starvation Relief",
            description="Reallocate resources when domains are starved",
            trigger_conditions=[
                TriggerType.RESOURCE_STARVATION,
                TriggerType.SUSTAINED_IMBALANCE,
            ],
            intervention_type=InterventionType.RESOURCE_REALLOCATION,
            actions=[
                {
                    "action_type": "rebalance_resources",
                    "target": "underfunded_domains",
                    "value": True,
                    "reason": "Rebalance to underfunded domains"
                },
                {
                    "action_type": "emergency_allocation",
                    "target": "starved_domain",
                    "value": 0.2,
                    "reason": "Add 20% emergency allocation"
                },
                {
                    "action_type": "reduce_wealthy_domains",
                    "target": "overfunded",
                    "value": 0.15,
                    "reason": "Reduce overfunded domains by 15%"
                },
            ],
            cooldown_hours=48,
            max_per_day=1,
            confidence_threshold=0.65,
            is_emergency=False,
        )
    
    @staticmethod
    def emergency_protocol() -> InterventionProtocol:
        """Emergency protocol for critical failures."""
        return InterventionProtocol(
            protocol_id="emergency_001",
            name="Emergency Response",
            description="Emergency intervention for critical system failures",
            trigger_conditions=[
                TriggerType.DOMAIN_PERFORMANCE_COLLAPSE,
                TriggerType.RISK_ESCALATION,
            ],
            intervention_type=InterventionType.EMERGENCY_RESPONSE,
            actions=[
                {
                    "action_type": "halt_non_essential",
                    "target": "all",
                    "value": True,
                    "reason": "Halt all non-essential activities"
                },
                {
                    "action_type": "focus_recovery",
                    "target": "critical_domain",
                    "value": True,
                    "reason": "Focus all resources on critical domain"
                },
                {
                    "action_type": "notify_executive",
                    "target": "command_center",
                    "value": True,
                    "reason": "Notify executive command center"
                },
            ],
            cooldown_hours=12,
            max_per_day=1,
            confidence_threshold=0.9,
            is_emergency=True,
        )
    
    @staticmethod
    def get_protocol_by_id(protocol_id: str) -> InterventionProtocol:
        """Get a specific protocol by ID."""
        protocols = InterventionProtocols.get_all_protocols()
        for p in protocols:
            if p.protocol_id == protocol_id:
                return p
        return protocols[0]
    
    @staticmethod
    def get_protocols_for_trigger(trigger_type: TriggerType) -> List[InterventionProtocol]:
        """Get all protocols that can handle a specific trigger type."""
        all_protocols = InterventionProtocols.get_all_protocols()
        return [p for p in all_protocols if trigger_type in p.trigger_conditions]
