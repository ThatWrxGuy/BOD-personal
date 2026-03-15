"""Planning Service - Central orchestration for strategic planning."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.intelligence.planning.planning_models import (
    StrategicGoal,
    StrategicPlan,
    StrategicPlanPortfolio,
    PlanStatus,
    PlanType,
    TimeHorizon,
    PriorityLevel,
)
from app.intelligence.planning.goal_decomposer import get_goal_decomposer
from app.intelligence.planning.plan_generator import get_plan_generator
from app.intelligence.planning.plan_simulator import get_plan_simulator
from app.intelligence.planning.plan_prioritizer import get_plan_prioritizer
from app.intelligence.planning.plan_monitor import get_plan_monitor


class PlanningService:
    """Central orchestration for strategic planning."""
    
    def __init__(self):
        self.decomposer = get_goal_decomposer()
        self.generator = get_plan_generator()
        self.simulator = get_plan_simulator()
        self.prioritizer = get_plan_prioritizer()
        self.monitor = get_plan_monitor()
        
        # Portfolio
        self.portfolio: Optional[StrategicPlanPortfolio] = None
    
    def create_portfolio(self) -> StrategicPlanPortfolio:
        """Create a new planning portfolio."""
        
        self.portfolio = StrategicPlanPortfolio(
            portfolio_id=str(uuid.uuid4())[:8],
        )
        
        return self.portfolio
    
    def add_goal(self, goal: StrategicGoal) -> StrategicGoal:
        """Add a goal to the portfolio."""
        
        if not self.portfolio:
            self.create_portfolio()
        
        self.portfolio.goals.append(goal)
        self.portfolio.updated_at = datetime.utcnow()
        
        return goal
    
    def create_and_decompose_goal(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        horizon: str = "medium_term",
    ) -> StrategicGoal:
        """Create a goal and decompose it."""
        
        goal = self.decomposer.create_goal(
            title=title,
            description=description,
            priority=priority,
            horizon=horizon,
        )
        
        self.add_goal(goal)
        
        return goal
    
    def generate_plans_for_goal(
        self,
        goal_id: str,
        system_state: Optional[Dict[str, Any]] = None,
    ) -> List[StrategicPlan]:
        """Generate candidate plans for a goal."""
        
        # Find goal
        goal = None
        for g in self.portfolio.goals:
            if g.id == goal_id:
                goal = g
                break
        
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        
        # Decompose goal
        decomposition = self.decomposer.decompose_goal(goal)
        
        # Generate plans
        plans = self.generator.generate_plans(goal, decomposition, system_state)
        
        # Add to portfolio
        self.portfolio.generated_plans.extend(plans)
        self.portfolio.updated_at = datetime.utcnow()
        
        return plans
    
    def simulate_and_evaluate_plans(
        self,
        plan_ids: Optional[List[str]] = None,
    ) -> List:
        """Simulate and evaluate plans."""
        
        # Get plans to evaluate
        if plan_ids:
            plans = [p for p in self.portfolio.generated_plans if p.id in plan_ids]
        else:
            plans = self.portfolio.generated_plans
        
        # Simulate plans
        evaluations = self.simulator.simulate_plans(plans)
        
        # Add to portfolio
        self.portfolio.plan_evaluations.extend(evaluations)
        self.portfolio.updated_at = datetime.utcnow()
        
        return evaluations
    
    def select_best_plan(
        self,
        goal_id: Optional[str] = None,
    ) -> Optional[StrategicPlan]:
        """Select the best plan for a goal."""
        
        # Get plans for goal
        if goal_id:
            plans = [p for p in self.portfolio.generated_plans if p.goal_id == goal_id]
        else:
            plans = self.portfolio.generated_plans
        
        if not plans:
            return None
        
        # Get evaluations
        plan_ids = [p.id for p in plans]
        evaluations = [e for e in self.portfolio.plan_evaluations if e.plan_id in plan_ids]
        
        # Get top plan
        best_plan = self.prioritizer.get_top_plan(plans, evaluations)
        
        if best_plan:
            # Update portfolio
            self.portfolio.selected_plan_id = best_plan.id
            self.portfolio.prioritized_plans = self.prioritizer.prioritized_plans
            
            # Mark as selected
            best_plan.status = PlanStatus.ACTIVE
            best_plan.activated_at = datetime.utcnow()
            
            self.portfolio.active_plans.append(best_plan.id)
            self.portfolio.updated_at = datetime.utcnow()
        
        return best_plan
    
    def generate_full_plan(
        self,
        goal: StrategicGoal,
        system_state: Optional[Dict[str, Any]] = None,
    ) -> StrategicPlan:
        """Generate a complete plan with goal -> decomposition -> simulation -> selection."""
        
        # Add goal
        self.add_goal(goal)
        
        # Generate plans
        plans = self.generate_plans_for_goal(goal.id, system_state)
        
        # Simulate
        self.simulate_and_evaluate_plans()
        
        # Select best
        best_plan = self.select_best_plan(goal.id)
        
        return best_plan
    
    def check_active_plans(
        self,
        current_state: Dict[str, Any],
    ) -> List:
        """Check active plans for needed adjustments."""
        
        active = [p for p in self.portfolio.generated_plans if p.status == PlanStatus.ACTIVE]
        
        signals = self.monitor.check_plans(active, current_state)
        
        self.portfolio.adjustment_signals.extend(signals)
        
        return signals
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get plan recommendations."""
        
        if not self.portfolio or not self.portfolio.generated_plans:
            return {"recommendations": [], "reasoning": []}
        
        plans = self.portfolio.generated_plans
        evaluations = self.portfolio.plan_evaluations
        
        return self.prioritizer.get_recommendations(plans, evaluations)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary."""
        
        if not self.portfolio:
            return {"status": "empty"}
        
        return {
            "portfolio_id": self.portfolio.portfolio_id,
            "goals_count": len(self.portfolio.goals),
            "plans_generated": len(self.portfolio.generated_plans),
            "plans_evaluated": len(self.portfolio.plan_evaluations),
            "active_plans": len(self.portfolio.active_plans),
            "selected_plan": self.portfolio.selected_plan_id,
            "adjustment_signals": len(self.portfolio.adjustment_signals),
        }


# Global service
_planning_service: Optional[PlanningService] = None


def get_planning_service() -> PlanningService:
    """Get the global planning service."""
    global _planning_service
    if _planning_service is None:
        _planning_service = PlanningService()
    return _planning_service
