"""Scenario Simulator for alternative future simulations."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scenario_simulation import ScenarioSimulation
from app.models.goal_progress import GoalProgress
from app.models.strategic_goal import StrategicGoal
from app.core.logging import get_logger

logger = get_logger(__name__)


class ScenarioSimulator:
    """Simulates alternative future scenarios."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def simulate_savings_increase(
        self,
        increase_percentage: float = 20,
    ) -> ScenarioSimulation:
        """Simulate scenario: increase savings rate."""
        scenario_name = "savings_increase"
        description = f"Increase savings rate by {increase_percentage}%"
        
        # Get current goal progress
        from sqlalchemy import select
        result = await self.session.execute(
            select(StrategicGoal).where(
                StrategicGoal.category == "FINANCE",
                StrategicGoal.status == "ACTIVE",
            )
        )
        finance_goals = list(result.scalars().all())
        
        predicted_outcomes = {
            "goal_timeline_change": "reduced by 20-30%",
            "estimated_months_saved": 6,
            "impact_on_goals": [],
        }
        
        for goal in finance_goals:
            if goal.target_value and goal.current_value:
                remaining = goal.target_value - goal.current_value
                # With 20% more savings, timeline reduces
                estimated_reduction = remaining * 0.2
                predicted_outcomes["impact_on_goals"].append({
                    "goal_id": str(goal.id),
                    "goal_title": goal.title,
                    "timeline_reduction_months": estimated_reduction / 1000,  # Simplified
                })
        
        # Estimate confidence
        confidence = 0.6 if len(finance_goals) > 0 else 0.3
        
        simulation = ScenarioSimulation(
            scenario_name=scenario_name,
            description=description,
            parameters={"increase_percentage": increase_percentage},
            predicted_outcomes=predicted_outcomes,
            confidence=confidence,
        )
        
        self.session.add(simulation)
        await self.session.commit()
        await self.session.refresh(simulation)
        
        return simulation

    async def simulate_expense_reduction(
        self,
        reduction_percentage: float = 15,
    ) -> ScenarioSimulation:
        """Simulate scenario: reduce expenses."""
        scenario_name = "expense_reduction"
        description = f"Reduce expenses by {reduction_percentage}%"
        
        predicted_outcomes = {
            "monthly_savings": f"${reduction_percentage * 10}",  # Simplified
            "yearly_impact": f"${reduction_percentage * 120}",
            "goal_impact": "Accelerate financial goals by 15-25%",
        }
        
        simulation = ScenarioSimulation(
            scenario_name=scenario_name,
            description=description,
            parameters={"reduction_percentage": reduction_percentage},
            predicted_outcomes=predicted_outcomes,
            confidence=0.55,
        )
        
        self.session.add(simulation)
        await self.session.commit()
        await self.session.refresh(simulation)
        
        return simulation

    async def simulate_workload_change(
        self,
        change_percentage: float = -20,
    ) -> ScenarioSimulation:
        """Simulate scenario: change in workload."""
        scenario_name = "workload_change"
        direction = "reduce" if change_percentage < 0 else "increase"
        description = f"{direction.capitalize()} workload by {abs(change_percentage)}%"
        
        predicted_outcomes = {
            "health_impact": "positive" if change_percentage < 0 else "negative",
            "productivity_change": f"{abs(change_percentage) * 0.5}% estimated",
            "timeline_impact": "extended by 10-15%" if change_percentage > 0 else "reduced by 15-20%",
        }
        
        if change_percentage < 0:
            predicted_outcomes["burnout_risk"] = "reduced"
        else:
            predicted_outcomes["burnout_risk"] = "increased"
        
        simulation = ScenarioSimulation(
            scenario_name=scenario_name,
            description=description,
            parameters={"change_percentage": change_percentage},
            predicted_outcomes=predicted_outcomes,
            confidence=0.5,
        )
        
        self.session.add(simulation)
        await self.session.commit()
        await self.session.refresh(simulation)
        
        return simulation

    async def simulate_health_activity_change(
        self,
        activity_change: str = "increase",
        percentage: float = 25,
    ) -> ScenarioSimulation:
        """Simulate scenario: change in health activity."""
        scenario_name = f"health_{activity_change}"
        description = f"{activity_change.capitalize()} health activity by {percentage}%"
        
        predicted_outcomes = {
            "fitness_improvement": f"{percentage * 0.5}%" if activity_change == "increase" else f"-{percentage * 0.3}%",
            "energy_levels": "improved" if activity_change == "increase" else "reduced",
            "productivity_impact": "positive" if activity_change == "increase" else "negative",
        }
        
        simulation = ScenarioSimulation(
            scenario_name=scenario_name,
            description=description,
            parameters={"activity_change": activity_change, "percentage": percentage},
            predicted_outcomes=predicted_outcomes,
            confidence=0.55,
        )
        
        self.session.add(simulation)
        await self.session.commit()
        await self.session.refresh(simulation)
        
        return simulation

    async def run_custom_scenario(
        self,
        scenario_name: str,
        parameters: dict,
        predicted_outcomes: dict,
    ) -> ScenarioSimulation:
        """Run a custom scenario simulation."""
        simulation = ScenarioSimulation(
            scenario_name=scenario_name,
            description=parameters.get("description", "Custom scenario"),
            parameters=parameters,
            predicted_outcomes=predicted_outcomes,
            confidence=0.5,  # Default for custom scenarios
        )
        
        self.session.add(simulation)
        await self.session.commit()
        await self.session.refresh(simulation)
        
        return simulation

    async def compare_scenarios(
        self,
        scenario_ids: list[uuid.UUID],
    ) -> dict:
        """Compare multiple scenarios."""
        scenarios = []
        for sid in scenario_ids:
            scenario = await self.session.get(ScenarioSimulation, sid)
            if scenario:
                scenarios.append(scenario)
        
        if not scenarios:
            return {"error": "No scenarios found"}
        
        comparison = {
            "scenarios": [
                {
                    "name": s.scenario_name,
                    "description": s.description,
                    "confidence": s.confidence,
                    "outcomes": s.predicted_outcomes,
                }
                for s in scenarios
            ],
        }
        
        return comparison


async def get_scenario_simulator(session: AsyncSession) -> ScenarioSimulator:
    """Get a scenario simulator instance."""
    return ScenarioSimulator(session)
