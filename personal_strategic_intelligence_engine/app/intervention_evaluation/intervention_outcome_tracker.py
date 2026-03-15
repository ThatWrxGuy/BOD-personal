"""Intervention Outcome Tracker - Tracks all interventions and their outcomes."""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.intervention_evaluation.evaluation_types import (
    InterventionOutcome,
    EvaluationPolicy,
)
from app.intervention.intervention_types import Intervention


class InterventionOutcomeTracker:
    """Tracks outcomes of all interventions."""
    
    def __init__(self, policy: Optional[EvaluationPolicy] = None):
        self.policy = policy or EvaluationPolicy()
        self.outcomes: List[InterventionOutcome] = []
        self.active_interventions: Dict[str, InterventionOutcome] = {}
    
    def record_intervention_start(
        self,
        intervention: Intervention,
        initial_performance: float,
        initial_risk: float,
        initial_momentum: float,
    ) -> str:
        """Record the start of an intervention."""
        
        outcome = InterventionOutcome(
            intervention_id=intervention.intervention_id,
            protocol_name=intervention.intervention_type.value,
            protocol_id=intervention.intervention_type.value,
            target_domain=intervention.target_domain,
            timestamp=datetime.utcnow(),
            initial_performance=initial_performance,
            initial_risk=initial_risk,
            initial_momentum=initial_momentum,
            confidence_score=intervention.confidence_score,
        )
        
        self.active_interventions[intervention.intervention_id] = outcome
        
        return outcome.intervention_id
    
    def record_intervention_result(
        self,
        intervention_id: str,
        final_performance: float,
        final_risk: float,
        final_momentum: float,
    ) -> Optional[InterventionOutcome]:
        """Record the result of an intervention."""
        
        # Find the active intervention
        outcome = self.active_interventions.pop(intervention_id, None)
        
        if not outcome:
            return None
        
        # Calculate changes
        outcome.post_performance = final_performance
        outcome.post_risk = final_risk
        outcome.post_momentum = final_momentum
        
        outcome.performance_change = final_performance - outcome.initial_performance
        outcome.risk_change = final_risk - outcome.initial_risk
        outcome.momentum_change = final_momentum - outcome.initial_momentum
        
        # Determine outcome
        outcome = self._classify_outcome(outcome)
        
        # Add to completed outcomes
        self.outcomes.append(outcome)
        
        return outcome
    
    def _classify_outcome(self, outcome: InterventionOutcome) -> InterventionOutcome:
        """Classify the intervention outcome."""
        
        perf_change = outcome.performance_change
        risk_change = outcome.risk_change
        
        # Success: significant improvement
        if perf_change > 0.5 and risk_change < 0:
            outcome.outcome = "success"
            outcome.recovered = True
        
        # Partial: some improvement
        elif perf_change > 0:
            outcome.outcome = "partial"
        
        # Failure: no improvement or decline
        elif perf_change < -0.3:
            outcome.outcome = "harmful"
        
        else:
            outcome.outcome = "failure"
        
        return outcome
    
    def get_outcomes_for_domain(self, domain: str) -> List[InterventionOutcome]:
        """Get all outcomes for a specific domain."""
        return [o for o in self.outcomes if o.target_domain == domain]
    
    def get_outcomes_for_protocol(self, protocol_id: str) -> List[InterventionOutcome]:
        """Get all outcomes for a specific protocol."""
        return [o for o in self.outcomes if o.protocol_id == protocol_id]
    
    def get_recent_outcomes(self, days: int = 7) -> List[InterventionOutcome]:
        """Get outcomes from recent days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [o for o in self.outcomes if o.timestamp > cutoff]
    
    def get_active_count(self) -> int:
        """Get count of active interventions."""
        return len(self.active_interventions)
    
    def get_total_count(self) -> int:
        """Get total interventions tracked."""
        return len(self.outcomes)
    
    def get_statistics(self) -> Dict:
        """Get basic statistics."""
        
        if not self.outcomes:
            return {
                "total": 0,
                "success": 0,
                "partial": 0,
                "failure": 0,
                "harmful": 0,
            }
        
        outcomes = {}
        for o in self.outcomes:
            outcomes[o.outcome] = outcomes.get(o.outcome, 0) + 1
        
        return {
            "total": len(self.outcomes),
            "success": outcomes.get("success", 0),
            "partial": outcomes.get("partial", 0),
            "failure": outcomes.get("failure", 0),
            "harmful": outcomes.get("harmful", 0),
        }


# Global tracker
_tracker: Optional[InterventionOutcomeTracker] = None


def get_outcome_tracker() -> InterventionOutcomeTracker:
    """Get the global outcome tracker."""
    global _tracker
    if _tracker is None:
        _tracker = InterventionOutcomeTracker()
    return _tracker
