"""Planning-simulation validation pipeline.

This module ensures strategic plans are validated through simulation before governance review.
"""
import uuid
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


class PlanSimulationValidator:
    """Validates strategic plans through simulation before governance."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def validate_plan(
        self,
        plan_id: uuid.UUID,
        plan_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run simulation validation on a strategic plan."""
        
        logger.info(f"Validating plan {plan_id} through simulation")
        
        # Import simulation engine
        from app.simulation_engine import get_simulation_core
        
        simulation_engine = await get_simulation_engine(self.session)
        
        # Determine decision type from plan
        decision_type = self._extract_decision_type(plan_data)
        
        # Run simulation
        simulation = await simulation_engine.run_simulation(
            decision_type=decision_type,
            decision_description=plan_data.get("title", "Strategic Plan Validation"),
            decision_params=plan_data.get("parameters", {}),
            time_horizon_days=plan_data.get("time_horizon_days", 90),
            domain=plan_data.get("domain", "strategic"),
            decision_id=plan_id,
        )
        
        # Extract validation results
        scenarios = await simulation_engine.get_simulation_scenarios(simulation.id)
        
        # Calculate risk score
        risk_scores = [s.risk_score for s in scenarios if s.risk_score]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.5
        
        # Determine if plan is validated
        is_validated = avg_risk < 0.7  # Threshold
        
        validation_result = {
            "simulation_id": str(simulation.id),
            "simulation_status": simulation.status,
            "scenarios_generated": simulation.scenarios_generated,
            "recommended_scenario": simulation.recommended_scenario,
            "average_risk_score": avg_risk,
            "is_validated": is_validated,
            "risk_level": "low" if avg_risk < 0.3 else "medium" if avg_risk < 0.6 else "high",
        }
        
        if not is_validated:
            validation_result["warning"] = "Plan has elevated risk - review recommended before approval"
        
        logger.info(f"Plan {plan_id} validation complete: validated={is_validated}, risk={avg_risk}")
        
        return validation_result
    
    def _extract_decision_type(self, plan_data: Dict[str, Any]) -> str:
        """Extract decision type from plan data."""
        
        title = plan_data.get("title", "").lower()
        description = plan_data.get("description", "").lower()
        
        text = title + " " + description
        
        if "invest" in text:
            return "investment"
        elif "spend" in text or "budget" in text:
            return "spending"
        elif "work" in text or "hour" in text:
            return "workload"
        elif "expense" in text:
            return "expense"
        elif "goal" in text:
            return "goal_timeline"
        else:
            return "generic"


async def get_plan_simulation_validator(session: AsyncSession) -> PlanSimulationValidator:
    """Get plan simulation validator instance."""
    return PlanSimulationValidator(session)
