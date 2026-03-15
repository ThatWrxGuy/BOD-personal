"""Plan Generator - Generates candidate plans for achieving goals."""
import uuid
from typing import List, Dict, Any, Optional

from app.intelligence.planning.planning_models import (
    StrategicGoal,
    StrategicPlan,
    PlanStep,
    GoalDecomposition,
    PlanType,
    TimeHorizon,
)


class PlanGenerator:
    """Generates multiple candidate plans for achieving goals."""
    
    def __init__(self):
        self.generated_plans: List[StrategicPlan] = []
    
    def generate_plans(
        self,
        goal: StrategicGoal,
        decomposition: GoalDecomposition,
        system_state: Optional[Dict[str, Any]] = None,
    ) -> List[StrategicPlan]:
        """Generate multiple candidate plans for a goal."""
        
        plans = []
        
        # Generate each plan type
        plans.append(self._generate_conservative_plan(goal, decomposition))
        plans.append(self._generate_balanced_plan(goal, decomposition))
        plans.append(self._generate_aggressive_plan(goal, decomposition))
        plans.append(self._generate_resilience_plan(goal, decomposition))
        
        self.generated_plans.extend(plans)
        
        return plans
    
    def _generate_conservative_plan(
        self,
        goal: StrategicGoal,
        decomposition: GoalDecomposition,
    ) -> StrategicPlan:
        """Generate a conservative (low-risk) plan."""
        
        steps = self._create_steps(decomposition.milestones, "conservative")
        
        plan = StrategicPlan(
            id=str(uuid.uuid4())[:8],
            goal_id=goal.id,
            plan_type=PlanType.CONSERVATIVE,
            title=f"Conservative: {goal.title}",
            description="Low-risk approach prioritizing stability over speed",
            expected_outcome="Steady progress with minimal downside",
            reward_score=5.0,
            risk_score=2.0,
            confidence=0.85,
            time_horizon=TimeHorizon.LONG_TERM,
            estimated_duration_days=decomposition.estimated_duration_days * 1.5,
            steps=steps,
        )
        
        return plan
    
    def _generate_balanced_plan(
        self,
        goal: StrategicGoal,
        decomposition: GoalDecomposition,
    ) -> StrategicPlan:
        """Generate a balanced plan."""
        
        steps = self._create_steps(decomposition.milestones, "balanced")
        
        plan = StrategicPlan(
            id=str(uuid.uuid4())[:8],
            goal_id=goal.id,
            plan_type=PlanType.BALANCED,
            title=f"Balanced: {goal.title}",
            description="Moderate risk-reward approach",
            expected_outcome="Good progress with acceptable risk",
            reward_score=7.0,
            risk_score=4.0,
            confidence=0.70,
            time_horizon=TimeHorizon.MEDIUM_TERM,
            estimated_duration_days=decomposition.estimated_duration_days,
            steps=steps,
        )
        
        return plan
    
    def _generate_aggressive_plan(
        self,
        goal: StrategicGoal,
        decomposition: GoalDecomposition,
    ) -> StrategicPlan:
        """Generate an aggressive (high-reward) plan."""
        
        steps = self._create_steps(decomposition.milestones, "aggressive")
        
        plan = StrategicPlan(
            id=str(uuid.uuid4())[:8],
            goal_id=goal.id,
            plan_type=PlanType.AGGRESSIVE,
            title=f"Aggressive: {goal.title}",
            description="High-reward approach with elevated risk",
            expected_outcome="Maximum progress in shortest time",
            reward_score=9.0,
            risk_score=7.0,
            confidence=0.55,
            time_horizon=TimeHorizon.SHORT_TERM,
            estimated_duration_days=decomposition.estimated_duration_days * 0.6,
            steps=steps,
        )
        
        return plan
    
    def _generate_resilience_plan(
        self,
        goal: StrategicGoal,
        decomposition: GoalDecomposition,
    ) -> StrategicPlan:
        """Generate a resilience-focused plan."""
        
        steps = self._create_steps(decomposition.milestones, "resilience")
        
        plan = StrategicPlan(
            id=str(uuid.uuid4())[:8],
            goal_id=goal.id,
            plan_type=PlanType.RESILIENCE,
            title=f"Resilience: {goal.title}",
            description="Focus on building capacity to handle disruptions",
            expected_outcome="Strong foundation with high adaptability",
            reward_score=6.0,
            risk_score=3.0,
            confidence=0.80,
            time_horizon=TimeHorizon.MEDIUM_TERM,
            estimated_duration_days=decomposition.estimated_duration_days * 1.2,
            steps=steps,
        )
        
        return plan
    
    def _create_steps(
        self,
        milestones: List[str],
        approach: str,
    ) -> List[PlanStep]:
        """Create plan steps from milestones based on approach."""
        
        steps = []
        
        # Duration modifier based on approach
        duration_map = {
            "conservative": 14,
            "balanced": 7,
            "aggressive": 3,
            "resilience": 10,
        }
        
        duration = duration_map.get(approach, 7)
        
        for i, milestone in enumerate(milestones):
            step = PlanStep(
                step_id=str(uuid.uuid4())[:8],
                sequence=i + 1,
                action=f"Execute: {milestone}",
                description=f"Work towards: {milestone}",
                expected_result=milestone,
                expected_impact=self._get_impact(approach),
                estimated_duration_days=duration,
            )
            steps.append(step)
        
        return steps
    
    def _get_impact(self, approach: str) -> float:
        """Get expected impact based on approach."""
        impact_map = {
            "conservative": 1.5,
            "balanced": 2.0,
            "aggressive": 2.5,
            "resilience": 1.8,
        }
        return impact_map.get(approach, 2.0)
    
    def get_plan(self, plan_id: str) -> Optional[StrategicPlan]:
        """Get a specific plan."""
        for plan in self.generated_plans:
            if plan.id == plan_id:
                return plan
        return None


_generator: Optional[PlanGenerator] = None


def get_plan_generator() -> PlanGenerator:
    """Get the global plan generator."""
    global _generator
    if _generator is None:
        _generator = PlanGenerator()
    return _generator
