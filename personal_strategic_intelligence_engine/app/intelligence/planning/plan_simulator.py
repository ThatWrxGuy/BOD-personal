"""Plan Simulator - Uses simulation engines to evaluate plans."""
import uuid
from typing import List, Dict, Any, Optional

from app.intelligence.planning.planning_models import (
    StrategicPlan,
    PlanEvaluation,
)


class PlanSimulator:
    """Simulates plan outcomes using available engines."""
    
    def __init__(self):
        self.evaluations: Dict[str, PlanEvaluation] = {}
    
    def simulate_plan(
        self,
        plan: StrategicPlan,
        system_state: Optional[Dict[str, Any]] = None,
    ) -> PlanEvaluation:
        """Simulate a single plan and return evaluation."""
        
        # Get base metrics from plan
        reward = plan.reward_score
        risk = plan.risk_score
        confidence = plan.confidence
        
        # Simulate expected return based on plan type
        expected_return = self._calculate_expected_return(plan)
        
        # Calculate probability of success
        probability = self._calculate_probability(plan)
        
        # Calculate resilience score
        resilience = self._calculate_resilience(plan)
        
        # Simulate risk scenarios
        risk_details = self._simulate_risk_scenarios(plan)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            expected_return,
            probability,
            resilience,
            confidence,
        )
        
        evaluation = PlanEvaluation(
            plan_id=plan.id,
            expected_return=expected_return,
            probability_of_success=probability,
            resilience_score=resilience,
            risk_score=risk,
            overall_score=overall_score,
            simulation_details={
                "plan_type": plan.plan_type.value,
                "steps_count": len(plan.steps),
                "risk_scenarios": risk_details,
            },
        )
        
        self.evaluations[plan.id] = evaluation
        
        return evaluation
    
    def simulate_plans(
        self,
        plans: List[StrategicPlan],
        system_state: Optional[Dict[str, Any]] = None,
    ) -> List[PlanEvaluation]:
        """Simulate multiple plans."""
        
        evaluations = []
        
        for plan in plans:
            evaluation = self.simulate_plan(plan, system_state)
            evaluations.append(evaluation)
        
        # Assign ranks
        self._assign_ranks(evaluations)
        
        return evaluations
    
    def _calculate_expected_return(self, plan: StrategicPlan) -> float:
        """Calculate expected return based on plan characteristics."""
        
        base = plan.reward_score
        
        # Adjust for plan type
        type_modifiers = {
            "conservative": 0.7,
            "balanced": 1.0,
            "aggressive": 1.3,
            "resilience": 0.8,
        }
        
        modifier = type_modifiers.get(plan.plan_type.value, 1.0)
        
        # Adjust for steps
        step_modifier = min(1.2, len(plan.steps) / 5.0)
        
        return min(10.0, base * modifier * step_modifier)
    
    def _calculate_probability(self, plan: StrategicPlan) -> float:
        """Calculate probability of success."""
        
        base = plan.confidence
        
        # Higher risk = lower probability
        risk_penalty = (plan.risk_score / 10.0) * 0.3
        
        # More steps = more complexity = lower probability
        complexity_penalty = (len(plan.steps) / 20.0) * 0.1
        
        probability = max(0.1, base - risk_penalty - complexity_penalty)
        
        return probability
    
    def _calculate_resilience(self, plan: StrategicPlan) -> float:
        """Calculate resilience score."""
        
        base = 0.5
        
        # Conservative plans more resilient
        if plan.plan_type.value == "conservative":
            base = 0.8
        elif plan.plan_type.value == "aggressive":
            base = 0.4
        elif plan.plan_type.value == "resilience":
            base = 0.9
        
        # Adjust for duration (longer = less resilient to changes)
        duration_factor = max(0.5, 1.0 - (plan.estimated_duration_days / 365.0) * 0.3)
        
        return min(1.0, base * duration_factor)
    
    def _simulate_risk_scenarios(self, plan: StrategicPlan) -> Dict[str, Any]:
        """Simulate various risk scenarios."""
        
        scenarios = {}
        
        # Market risk
        if "wealth" in plan.title.lower() or "financial" in plan.title.lower():
            scenarios["market_risk"] = {
                "severity": plan.risk_score * 0.1,
                "probability": plan.risk_score / 10.0,
            }
        
        # Execution risk (based on number of steps)
        scenarios["execution_risk"] = {
            "severity": len(plan.steps) * 0.15,
            "probability": min(0.8, len(plan.steps) / 10.0),
        }
        
        # Time risk
        scenarios["time_risk"] = {
            "severity": plan.estimated_duration_days / 100.0,
            "probability": min(0.5, plan.estimated_duration_days / 365.0),
        }
        
        return scenarios
    
    def _calculate_overall_score(
        self,
        expected_return: float,
        probability: float,
        resilience: float,
        confidence: float,
    ) -> float:
        """Calculate overall plan score."""
        
        # Score formula:
        # reward_score * 0.4 + probability * 0.3 + resilience * 0.2 + confidence * 0.1
        
        reward_norm = expected_return / 10.0
        
        score = (
            (reward_norm * 0.4) +
            (probability * 0.3) +
            (resilience * 0.2) +
            (confidence * 0.1)
        )
        
        return score * 10  # Scale to 0-10
    
    def _assign_ranks(self, evaluations: List[PlanEvaluation]) -> None:
        """Assign ranks to evaluations based on overall score."""
        
        sorted_evals = sorted(
            evaluations,
            key=lambda e: e.overall_score,
            reverse=True
        )
        
        for rank, evaluation in enumerate(sorted_evals, 1):
            evaluation.rank = rank
    
    def get_evaluation(self, plan_id: str) -> Optional[PlanEvaluation]:
        """Get evaluation for a specific plan."""
        return self.evaluations.get(plan_id)


_simulator: Optional[PlanSimulator] = None


def get_plan_simulator() -> PlanSimulator:
    """Get the global plan simulator."""
    global _simulator
    if _simulator is None:
        _simulator = PlanSimulator()
    return _simulator
