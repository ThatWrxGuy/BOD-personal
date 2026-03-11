"""Intelligence Service for unified intelligence operations."""
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.trend_analyzer import TrendAnalyzer, get_trend_analyzer
from app.intelligence.forecasting_engine import ForecastingEngine, get_forecasting_engine
from app.intelligence.scenario_simulator import ScenarioSimulator, get_scenario_simulator
from app.intelligence.risk_projection_engine import RiskProjectionEngine, get_risk_projection_engine
from app.intelligence.goal_probability_model import GoalProbabilityModel, get_goal_probability_model
from app.core.logging import get_logger

logger = get_logger(__name__)


class IntelligenceService:
    """Unified interface for all intelligence functions."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.trend_analyzer = TrendAnalyzer(session)
        self.forecasting_engine = ForecastingEngine(session)
        self.scenario_simulator = ScenarioSimulator(session)
        self.risk_engine = RiskProjectionEngine(session)
        self.goal_probability = GoalProbabilityModel(session)

    async def detect_trends(self, days: int = 30) -> dict:
        """Detect trends in historical data."""
        return await self.trend_analyzer.get_comprehensive_trends(days=days)

    async def generate_forecasts(self, days_ahead: int = 30) -> list:
        """Generate forecasts from historical data."""
        return await self.forecasting_engine.generate_all_forecasts(days_ahead)

    async def run_scenario_simulation(
        self,
        scenario_type: str,
        parameters: dict = None,
    ):
        """Run a scenario simulation."""
        if scenario_type == "savings_increase":
            return await self.scenario_simulator.simulate_savings_increase(
                parameters.get("increase_percentage", 20) if parameters else 20
            )
        elif scenario_type == "expense_reduction":
            return await self.scenario_simulator.simulate_expense_reduction(
                parameters.get("reduction_percentage", 15) if parameters else 15
            )
        elif scenario_type == "workload_change":
            return await self.scenario_simulator.simulate_workload_change(
                parameters.get("change_percentage", -20) if parameters else -20
            )
        elif scenario_type == "health_activity":
            return await self.scenario_simulator.simulate_health_activity_change(
                parameters.get("activity_change", "increase") if parameters else "increase",
                parameters.get("percentage", 25) if parameters else 25,
            )
        else:
            return await self.scenario_simulator.run_custom_scenario(
                scenario_type,
                parameters or {},
                {},
            )

    async def calculate_risk_projections(self) -> list:
        """Calculate risk projections."""
        return await self.risk_engine.project_all_risks()

    async def evaluate_goal_probabilities(self) -> list:
        """Evaluate probability of goal success."""
        return await self.goal_probability.calculate_all_goal_probabilities()

    async def get_intelligence_dashboard(self) -> dict:
        """Get comprehensive intelligence summary."""
        # Run all analyses
        trends = await self.detect_trends()
        forecasts = await self.generate_forecasts()
        risks = await self.calculate_risk_projections()
        probabilities = await self.goal_probability.calculate_all_goal_probabilities()

        # Summarize
        high_risks = [r for r in risks if r.risk_probability >= 0.7]
        at_risk_goals = [p for p in probabilities if p.probability_of_success < 0.5]

        return {
            "trends": {
                "signal_trends": trends.get("signal_trends", []),
                "anomalies": trends.get("anomalies", []),
            },
            "forecasts": {
                "total": len(forecasts),
                "by_type": {},
            },
            "risks": {
                "total": len(risks),
                "high_priority": len(high_risks),
            },
            "goals": {
                "probabilities_calculated": len(probabilities),
                "at_risk": len(at_risk_goals),
            },
            "generated_at": datetime.utcnow().isoformat(),
        }


async def get_intelligence_service(session: AsyncSession) -> IntelligenceService:
    """Get an intelligence service instance."""
    return IntelligenceService(session)
