"""Scenario Replanner - Performs deeper replanning when adjustments are insufficient."""
import uuid
from typing import List, Dict, Optional

from app.intelligence.planning.planning_models import StrategicPlan, StrategicGoal, PlanType
from app.intelligence.planning.goal_decomposer import get_goal_decomposer
from app.intelligence.planning.plan_generator import get_plan_generator
from app.intelligence.planning.plan_simulator import get_plan_simulator


class ScenarioReplanner:
    """Performs deeper replanning when local adjustments are insufficient."""
    
    def __init__(self):
        self.decomposer = get_goal_decomposer()
        self.generator = get_plan_generator()
        self.simulator = get_plan_simulator()
        
        self.regenerated_plans: Dict[str, StrategicPlan] = {}
    
    def regenerate_plan(
        self,
        original_plan: StrategicPlan,
        goal: StrategicGoal,
        current_state: Dict,
    ) -> StrategicPlan:
        """Regenerate a plan under new assumptions."""
        
        # Get decomposition
        decomposition = self.decomposer.decompose_goal(goal)
        
        # Determine new plan type based on current state
        new_type = self._determine_plan_type(original_plan, current_state)
        
        # Generate new plan
        plans = self.generator.generate_plans(goal, decomposition, current_state)
        
        # Find matching plan type
        new_plan = None
        for plan in plans:
            if plan.plan_type == new_type:
                new_plan = plan
                break
        
        if not new_plan:
            new_plan = plans[0]  # Default to first
        
        # Store
        self.regenerated_plans[new_plan.id] = new_plan
        
        return new_plan
    
    def _determine_plan_type(
        self,
        original_plan: StrategicPlan,
        current_state: Dict,
    ) -> PlanType:
        """Determine what plan type to switch to."""
        
        # Check risk level
        risk = current_state.get("overall_risk", 5.0)
        
        # Check for opportunities
        opportunities = current_state.get("opportunities", [])
        
        # Current type
        current_type = original_plan.plan_type
        
        # If aggressive plan and risk increased, switch to conservative
        if current_type == PlanType.AGGRESSIVE and risk > 7.0:
            return PlanType.CONSERVATIVE
        
        # If conservative and opportunity emerged, switch to balanced
        if current_type == PlanType.CONSERVATIVE and opportunities:
            return PlanType.BALANCED
        
        # If risk is high, prefer resilience
        if risk > 6.0:
            return PlanType.RESILIENCE
        
        # Default to balanced
        return PlanType.BALANCED
    
    def find_alternate_plan(
        self,
        goal: StrategicGoal,
        current_state: Dict,
    ) -> List[StrategicPlan]:
        """Find alternate plans for a goal."""
        
        decomposition = self.decomposer.decompose_goal(goal)
        plans = self.generator.generate_plans(goal, decomposition, current_state)
        
        return plans
    
    def simulate_plan(
        self,
        plan: StrategicPlan,
        current_state: Dict,
    ) -> Dict:
        """Simulate a regenerated plan."""
        
        evaluation = self.simulator.simulate_plan(plan, current_state)
        
        return {
            "plan_id": plan.id,
            "plan_type": plan.plan_type.value,
            "score": evaluation.overall_score,
            "probability": evaluation.probability_of_success,
            "risk": evaluation.risk_score,
        }
    
    def get_regenerated_plan(
        self,
        plan_id: str,
    ) -> Optional[StrategicPlan]:
        """Get a regenerated plan."""
        
        return self.regenerated_plans.get(plan_id)


_replanner: Optional[ScenarioReplanner] = None


def get_scenario_replanner() -> ScenarioReplanner:
    """Get the global scenario replanner."""
    global _replanner
    if _replanner is None:
        _replanner = ScenarioReplanner()
    return _replanner
