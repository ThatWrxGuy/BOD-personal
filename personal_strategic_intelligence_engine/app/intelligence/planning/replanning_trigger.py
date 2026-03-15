"""Replanning Trigger - Converts drift signals into replanning triggers."""
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.planning.replanning_models import (
    ReplanningTrigger,
    PlanDriftSignal,
    TriggerSeverity,
    ReplanningAction,
)


class ReplanningTriggerManager:
    """Manages replanning triggers based on drift signals."""
    
    def __init__(self):
        self.triggers: Dict[str, List[ReplanningTrigger]] = {}
        
        # Thresholds
        self.minor_threshold = 1  # Max signals for minor
        self.moderate_threshold = 3  # Max signals for moderate
        self.major_threshold = 5  # Max signals for major
    
    def create_trigger(
        self,
        execution_program_id: str,
        signals: List[PlanDriftSignal],
    ) -> ReplanningTrigger:
        """Create a replanning trigger from drift signals."""
        
        if not signals:
            # No signals - no trigger needed
            trigger = ReplanningTrigger(
                id=str(uuid.uuid4())[:8],
                execution_program_id=execution_program_id,
                trigger_type="none",
                severity=TriggerSeverity.LOW,
                reason="No drift detected",
                resolved=True,
                action_taken=ReplanningAction.CONTINUE,
            )
            return trigger
        
        # Analyze signals to determine trigger type
        trigger_type, severity, reason = self._analyze_signals(signals)
        
        trigger = ReplanningTrigger(
            id=str(uuid.uuid4())[:8],
            execution_program_id=execution_program_id,
            trigger_type=trigger_type,
            severity=severity,
            reason=reason,
            drift_signals=[s.id for s in signals],
        )
        
        # Store
        if execution_program_id not in self.triggers:
            self.triggers[execution_program_id] = []
        
        self.triggers[execution_program_id].append(trigger)
        
        return trigger
    
    def _analyze_signals(
        self,
        signals: List[PlanDriftSignal],
    ) -> tuple:
        """Analyze signals to determine trigger type."""
        
        # Count by severity
        critical = sum(1 for s in signals if s.severity == TriggerSeverity.CRITICAL)
        high = sum(1 for s in signals if s.severity == TriggerSeverity.HIGH)
        medium = sum(1 for s in signals if s.severity == TriggerSeverity.MEDIUM)
        low = sum(1 for s in signals if s.severity == TriggerSeverity.LOW)
        
        # Check for critical patterns
        if critical >= 1:
            return (
                "critical_escalation",
                TriggerSeverity.CRITICAL,
                f"{critical} critical drift signals detected - immediate action required"
            )
        
        # Check for high severity
        if high >= 2:
            return (
                "major_replacement",
                TriggerSeverity.HIGH,
                f"{high} high-severity drift signals - major replanning needed"
            )
        
        if high >= 1:
            return (
                "moderate_replanning",
                TriggerSeverity.HIGH,
                f"High severity drift detected - moderate replanning needed"
            )
        
        # Check for moderate
        if medium + high >= 2:
            return (
                "moderate_replanning",
                TriggerSeverity.MEDIUM,
                f"Multiple moderate signals - replanning recommended"
            )
        
        if medium >= 1:
            return (
                "minor_adjustment",
                TriggerSeverity.MEDIUM,
                f"Minor drift detected - adjustment may help"
            )
        
        # Low severity only
        return (
            "minor_adjustment",
            TriggerSeverity.LOW,
            f"Low severity drift - monitoring recommended"
        )
    
    def determine_action(
        self,
        trigger: ReplanningTrigger,
    ) -> ReplanningAction:
        """Determine what action to take based on trigger."""
        
        severity = trigger.severity
        
        if severity == TriggerSeverity.CRITICAL:
            return ReplanningAction.ESCALATE_FOR_REVIEW
        elif severity == TriggerSeverity.HIGH:
            if "major" in trigger.trigger_type:
                return ReplanningAction.SWITCH_TO_ALTERNATE_PLAN
            else:
                return ReplanningAction.REGENERATE_CURRENT_PLAN
        elif severity == TriggerSeverity.MEDIUM:
            return ReplanningAction.ADJUST_CURRENT_PLAN
        else:
            return ReplanningAction.CONTINUE
    
    def get_triggers(
        self,
        execution_program_id: str,
        unresolved_only: bool = True,
    ) -> List[ReplanningTrigger]:
        """Get triggers for a program."""
        
        if execution_program_id not in self.triggers:
            return []
        
        triggers = self.triggers[execution_program_id]
        
        if unresolved_only:
            triggers = [t for t in triggers if not t.resolved]
        
        return triggers
    
    def resolve_trigger(
        self,
        trigger_id: str,
        execution_program_id: str,
        action: ReplanningAction,
    ) -> bool:
        """Mark a trigger as resolved."""
        
        if execution_program_id not in self.triggers:
            return False
        
        for trigger in self.triggers[execution_program_id]:
            if trigger.id == trigger_id:
                trigger.resolved = True
                trigger.action_taken = action
                return True
        
        return False


_trigger_manager: Optional[ReplanningTriggerManager] = None


def get_replanning_trigger_manager() -> ReplanningTriggerManager:
    """Get the global replanning trigger manager."""
    global _trigger_manager
    if _trigger_manager is None:
        _trigger_manager = ReplanningTriggerManager()
    return _trigger_manager
