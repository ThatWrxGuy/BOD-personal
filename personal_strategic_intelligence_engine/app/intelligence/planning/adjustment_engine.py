"""Adjustment Engine - Generates tactical modifications to plans."""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.intelligence.planning.planning_models import StrategicPlan, PlanStep
from app.intelligence.planning.replanning_models import (
    PlanAdjustment,
    AdjustmentType,
)


class AdjustmentEngine:
    """Generates tactical adjustments to plans without full regeneration."""
    
    def __init__(self):
        self.adjustments: Dict[str, List[PlanAdjustment]] = {}
    
    def generate_adjustments(
        self,
        plan: StrategicPlan,
        drift_signals: List,
    ) -> List[PlanAdjustment]:
        """Generate adjustments based on drift signals."""
        
        adjustments = []
        
        # Analyze drift to determine adjustment type
        for signal in drift_signals:
            if signal.drift_type.value == "schedule_drift":
                adj = self._handle_schedule_drift(plan, signal)
            elif signal.drift_type.value == "performance_drift":
                adj = self._handle_performance_drift(plan, signal)
            elif signal.drift_type.value == "risk_drift":
                adj = self._handle_risk_drift(plan, signal)
            else:
                continue
            
            if adj:
                adjustments.append(adj)
        
        # Store
        if plan.id not in self.adjustments:
            self.adjustments[plan.id] = []
        
        self.adjustments[plan.id].extend(adjustments)
        
        return adjustments
    
    def _handle_schedule_drift(self, plan: StrategicPlan, signal) -> Optional[PlanAdjustment]:
        """Handle schedule drift by accelerating or deferring."""
        
        # Accelerate critical tasks
        adjustment = PlanAdjustment(
            id=str(uuid.uuid4())[:8],
            plan_id=plan.id,
            adjustment_type=AdjustmentType.ACCELERATE_STEP,
            description=f"Accelerate execution to address schedule drift",
            affected_steps=[plan.steps[0].step_id] if plan.steps else [],
            recommended_action="Accelerate critical path tasks",
            timeline_change={},  # Would add negative days
        )
        
        return adjustment
    
    def _handle_performance_drift(self, plan: StrategicPlan, signal) -> Optional[PlanAdjustment]:
        """Handle performance drift by replacing or removing failing steps."""
        
        if signal.impacted_tasks:
            # Replace failing steps
            adjustment = PlanAdjustment(
                id=str(uuid.uuid4())[:8],
                plan_id=plan.id,
                adjustment_type=AdjustmentType.REPLACE_STEP,
                description=f"Replace failing steps to improve performance",
                affected_steps=signal.impacted_tasks[:1],
                recommended_action="Replace underperforming steps",
            )
            return adjustment
        
        return None
    
    def _handle_risk_drift(self, plan: StrategicPlan, signal) -> Optional[PlanAdjustment]:
        """Handle risk drift by reordering or deferring."""
        
        # Switch to lower-risk steps
        adjustment = PlanAdjustment(
            id=str(uuid.uuid4())[:8],
            plan_id=plan.id,
            adjustment_type=AdjustmentType.REORDER_STEPS,
            description="Reorder to reduce risk exposure",
            affected_steps=[s.step_id for s in plan.steps[-2:]] if len(plan.steps) > 1 else [],
            recommended_action="Defer high-risk steps",
            risk_delta=-1.0,  # Reduce risk
        )
        
        return adjustment
    
    def apply_adjustment(
        self,
        plan: StrategicPlan,
        adjustment: PlanAdjustment,
    ) -> StrategicPlan:
        """Apply an adjustment to a plan."""
        
        if adjustment.adjustment_type == AdjustmentType.DEFER_STEP:
            # Defer affected steps
            for step in plan.steps:
                if step.step_id in adjustment.affected_steps:
                    if step.due_at:
                        step.due_at = step.due_at + timedelta(days=7)
        
        elif adjustment.adjustment_type == AdjustmentType.REMOVE_STEP:
            # Remove steps
            plan.steps = [s for s in plan.steps if s.step_id not in adjustment.affected_steps]
        
        elif adjustment.adjustment_type == AdjustmentType.REORDER_STEPS:
            # Reorder - in a real system would change sequence
            pass
        
        return plan
    
    def get_adjustments(
        self,
        plan_id: str,
    ) -> List[PlanAdjustment]:
        """Get adjustments for a plan."""
        
        return self.adjustments.get(plan_id, [])


_adjustment_engine: Optional[AdjustmentEngine] = None


def get_adjustment_engine() -> AdjustmentEngine:
    """Get the global adjustment engine."""
    global _adjustment_engine
    if _adjustment_engine is None:
        _adjustment_engine = AdjustmentEngine()
    return _adjustment_engine
