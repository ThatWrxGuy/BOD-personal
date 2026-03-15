"""Plan Monitor - Monitors active plans and triggers adjustments."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.intelligence.planning.planning_models import (
    StrategicPlan,
    PlanStatus,
    PlanAdjustmentSignal,
    PriorityLevel,
)


class PlanMonitor:
    """Monitors active plans and triggers adjustments when needed."""
    
    def __init__(self):
        self.signals: List[PlanAdjustmentSignal] = []
        self.plan_progress: Dict[str, float] = {}  # plan_id -> progress 0-1
    
    def check_plan(
        self,
        plan: StrategicPlan,
        current_state: Dict[str, Any],
    ) -> List[PlanAdjustmentSignal]:
        """Check if a plan needs adjustment."""
        
        signals = []
        
        # Check if plan is active
        if plan.status != PlanStatus.ACTIVE:
            return signals
        
        # Check progress
        progress = self.plan_progress.get(plan.id, 0.0)
        
        # Check for various triggers
        signals.extend(self._check_risk_triggers(plan, current_state))
        signals.extend(self._check_progress_triggers(plan, progress))
        signals.extend(self._check_opportunity_triggers(plan, current_state))
        
        self.signals.extend(signals)
        
        return signals
    
    def check_plans(
        self,
        plans: List[StrategicPlan],
        current_state: Dict[str, Any],
    ) -> List[PlanAdjustmentSignal]:
        """Check multiple plans for adjustments."""
        
        all_signals = []
        
        for plan in plans:
            signals = self.check_plan(plan, current_state)
            all_signals.extend(signals)
        
        return all_signals
    
    def _check_risk_triggers(
        self,
        plan: StrategicPlan,
        current_state: Dict[str, Any],
    ) -> List[PlanAdjustmentSignal]:
        """Check for risk-related triggers."""
        
        signals = []
        
        # Check risk spikes
        risk_level = current_state.get("overall_risk", 5.0)
        
        if risk_level > 8.0:
            signal = PlanAdjustmentSignal(
                signal_id=str(uuid.uuid4())[:8],
                plan_id=plan.id,
                trigger_type="risk_spike",
                description=f"Risk level elevated to {risk_level}/10",
                severity=PriorityLevel.HIGH,
                recommended_action="pause",
            )
            signals.append(signal)
        
        # Check domain-specific risks
        domain_risks = current_state.get("domain_risks", {})
        
        for domain, risk in domain_risks.items():
            if risk > 7.0 and domain in plan.title.lower():
                signal = PlanAdjustmentSignal(
                    signal_id=str(uuid.uuid4())[:8],
                    plan_id=plan.id,
                    trigger_type="risk_spike",
                    description=f"Domain {domain} risk elevated to {risk}/10",
                    severity=PriorityLevel.HIGH,
                    recommended_action="replan",
                )
                signals.append(signal)
        
        return signals
    
    def _check_progress_triggers(
        self,
        plan: StrategicPlan,
        progress: float,
    ) -> List[PlanAdjustmentSignal]:
        """Check for progress-related triggers."""
        
        signals = []
        
        # Check if progress is lagging (less than expected for time elapsed)
        # Simplified: assume progress should be proportional to time
        
        # No progress for too long
        if progress < 0.1 and len(self.signals) > 5:
            signal = PlanAdjustmentSignal(
                signal_id=str(uuid.uuid4())[:8],
                plan_id=plan.id,
                trigger_type="goal_failure",
                description="Minimal progress detected",
                severity=PriorityLevel.MEDIUM,
                recommended_action="replan",
            )
            signals.append(signal)
        
        return signals
    
    def _check_opportunity_triggers(
        self,
        plan: StrategicPlan,
        current_state: Dict[str, Any],
    ) -> List[PlanAdjustmentSignal]:
        """Check for new opportunities."""
        
        signals = []
        
        # Check for new opportunities
        opportunities = current_state.get("opportunities", [])
        
        if opportunities:
            signal = PlanAdjustmentSignal(
                signal_id=str(uuid.uuid4())[:8],
                plan_id=plan.id,
                trigger_type="opportunity",
                description=f"New opportunity detected: {opportunities[0]}",
                severity=PriorityLevel.MEDIUM,
                recommended_action="continue",
            )
            signals.append(signal)
        
        return signals
    
    def update_progress(self, plan_id: str, progress: float) -> None:
        """Update progress for a plan."""
        self.plan_progress[plan_id] = max(0.0, min(1.0, progress))
    
    def get_signals(
        self,
        plan_id: Optional[str] = None,
    ) -> List[PlanAdjustmentSignal]:
        """Get adjustment signals."""
        
        if plan_id:
            return [s for s in self.signals if s.plan_id == plan_id]
        
        return self.signals
    
    def get_active_signals(self) -> List[PlanAdjustmentSignal]:
        """Get unaddressed signals."""
        return [s for s in self.signals if s.severity in [PriorityLevel.HIGH, PriorityLevel.CRITICAL]]


_monitor: Optional[PlanMonitor] = None


def get_plan_monitor() -> PlanMonitor:
    """Get the global plan monitor."""
    global _monitor
    if _monitor is None:
        _monitor = PlanMonitor()
    return _monitor
