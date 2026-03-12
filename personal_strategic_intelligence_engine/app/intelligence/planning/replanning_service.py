"""Replanning Service - Central orchestration for dynamic replanning."""
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.planning.planning_models import StrategicPlan, StrategicGoal
from app.intelligence.planning.execution_models import ExecutionProgram, ExecutionTask
from app.intelligence.planning.replanning_models import (
    ReplanningDecision,
    ReplanningAction,
    PlanDriftSignal,
)
from app.intelligence.planning.drift_detector import get_drift_detector
from app.intelligence.planning.replanning_trigger import get_replanning_trigger_manager
from app.intelligence.planning.adjustment_engine import get_adjustment_engine
from app.intelligence.planning.scenario_replanner import get_scenario_replanner


class ReplanningService:
    """Central orchestration for dynamic replanning."""
    
    def __init__(self):
        self.drift_detector = get_drift_detector()
        self.trigger_manager = get_replanning_trigger_manager()
        self.adjustment_engine = get_adjustment_engine()
        self.scenario_replanner = get_scenario_replanner()
        
        # History
        self.decisions: List[ReplanningDecision] = []
    
    def run_replanning(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
        goal: StrategicGoal,
        current_state: Dict,
    ) -> ReplanningDecision:
        """Run the complete replanning process."""
        
        # Step 1: Detect drift
        signals = self.drift_detector.detect_drift(program, tasks, current_state)
        
        # Step 2: Create trigger
        trigger = self.trigger_manager.create_trigger(program.id, signals)
        
        # Step 3: Determine action
        action = self.trigger_manager.determine_action(trigger)
        
        # Step 4: Execute action
        new_plan = None
        adjustments = []
        
        if action == ReplanningAction.CONTINUE:
            # No action needed
            pass
        
        elif action == ReplanningAction.ADJUST_CURRENT_PLAN:
            # Generate adjustments
            adjustments = self.adjustment_engine.generate_adjustments(
                program.goal_id,  # Using goal_id as plan_id proxy
                signals,
            )
        
        elif action == ReplanningAction.REGENERATE_CURRENT_PLAN:
            # Regenerate plan
            # Get original plan (would need to fetch from storage in real system)
            new_plan = self.scenario_replanner.regenerate_plan(
                None,  # Would pass original plan
                goal,
                current_state,
            )
        
        elif action == ReplanningAction.SWITCH_TO_ALTERNATE_PLAN:
            # Find and switch to alternate
            new_plan = self.scenario_replanner.find_alternate_plan(goal, current_state)[0]
        
        elif action == ReplanningAction.ESCALATE_FOR_REVIEW:
            # Mark for escalation
            pass
        
        # Step 5: Create decision record
        decision = ReplanningDecision(
            id=str(uuid.uuid4())[:8],
            execution_program_id=program.id,
            original_plan_id=program.plan_id,
            action_taken=action,
            new_plan_id=new_plan.id if new_plan else None,
            adjustments_applied=[a.id for a in adjustments],
            reasoning=trigger.reason,
        )
        
        self.decisions.append(decision)
        
        # Mark trigger as resolved
        self.trigger_manager.resolve_trigger(trigger.id, program.id, action)
        
        return decision
    
    def check_and_replan(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
        goal: StrategicGoal,
        current_state: Dict,
    ) -> Optional[ReplanningDecision]:
        """Check if replanning is needed and execute if so."""
        
        # Detect drift
        signals = self.drift_detector.detect_drift(program, tasks, current_state)
        
        # If no significant drift, return None
        if not signals:
            return None
        
        # Check if any signal is high severity
        has_high = any(
            s.severity.value in ["high", "critical"] 
            for s in signals
        )
        
        if not has_high:
            return None
        
        # Run replanning
        return self.run_replanning(program, tasks, goal, current_state)
    
    def get_drift_signals(
        self,
        program_id: str,
    ) -> List[PlanDriftSignal]:
        """Get drift signals for a program."""
        
        return self.drift_detector.get_signals(program_id)
    
    def get_decision_history(
        self,
        program_id: Optional[str] = None,
    ) -> List[ReplanningDecision]:
        """Get replanning decision history."""
        
        if program_id:
            return [d for d in self.decisions if d.execution_program_id == program_id]
        
        return self.decisions
    
    def get_replanning_summary(
        self,
        program_id: str,
    ) -> Dict:
        """Get replanning summary for a program."""
        
        signals = self.drift_detector.get_signals(program_id)
        triggers = self.trigger_manager.get_triggers(program_id)
        decisions = self.get_decision_history(program_id)
        
        return {
            "drift_signals": len(signals),
            "triggers": len(triggers),
            "decisions": len(decisions),
            "last_decision": decisions[-1].action_taken.value if decisions else "none",
        }


# Global service
_replanning_service: Optional[ReplanningService] = None


def get_replanning_service() -> ReplanningService:
    """Get the global replanning service."""
    global _replanning_service
    if _replanning_service is None:
        _replanning_service = ReplanningService()
    return _replanning_service
