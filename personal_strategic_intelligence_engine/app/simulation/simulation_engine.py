"""Simulation engine for strategic decision simulation."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.simulation.simulation_types import (
    SimulationRun,
    SimulationScenario,
    SimulationResult,
    SimulationStatus,
)
from app.simulation.scenario_generator import get_scenario_generator
from app.simulation.outcome_modeler import get_outcome_modeler
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class SimulationEngine:
    """Main simulation engine."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def run_simulation(
        self,
        decision_type: str,
        decision_description: Optional[str] = None,
        decision_params: Optional[Dict[str, Any]] = None,
        time_horizon_days: int = 90,
        domain: str = "financial",
        decision_id: Optional[uuid.UUID] = None,
    ) -> SimulationRun:
        """Run a simulation."""
        
        logger.info(f"Starting simulation for {decision_type}")
        
        # Create simulation run
        simulation = SimulationRun(
            decision_id=decision_id,
            decision_type=decision_type,
            decision_description=decision_description,
            time_horizon_days=time_horizon_days,
            domain=domain,
            status=SimulationStatus.RUNNING,
            started_at=datetime.utcnow(),
            current_step="initializing",
        )
        
        self.session.add(simulation)
        await self.session.commit()
        await self.session.refresh(simulation)
        
        try:
            # Publish event
            await self._publish_event(simulation, "started")
            
            # Generate scenarios
            simulation.current_step = "generating_scenarios"
            await self.session.commit()
            
            generator = await get_scenario_generator()
            scenarios_data = await generator.generate_scenarios(
                decision_type,
                decision_params or {},
                time_horizon_days,
            )
            
            # Create scenario records
            scenarios = []
            for scenario_data in scenarios_data:
                scenario = SimulationScenario(
                    simulation_id=simulation.id,
                    scenario_name=scenario_data["scenario_name"],
                    scenario_type=scenario_data.get("scenario_type", "baseline"),
                    parameters=scenario_data.get("parameters", {}),
                )
                self.session.add(scenario)
                scenarios.append(scenario)
            
            await self.session.commit()
            
            simulation.scenarios_generated = len(scenarios)
            
            # Publish event
            await self._publish_event(simulation, "scenarios_generated")
            
            # Model outcomes for each scenario
            simulation.current_step = "modeling_outcomes"
            await self.session.commit()
            
            modeler = await get_outcome_modeler()
            
            for scenario in scenarios:
                outcome = await modeler.model_outcomes(
                    decision_type,
                    {"parameters": scenario.parameters},
                    time_horizon_days,
                )
                
                # Update scenario with results
                scenario.expected_outcome = outcome
                scenario.projected_value = outcome.get("projected_value", 0)
                scenario.confidence_score = outcome.get("confidence", 0.5)
                scenario.risk_score = outcome.get("risk_score", 0.5)
                scenario.risk_factors = outcome.get("key_factors", [])
                
                # Create result record
                result = SimulationResult(
                    simulation_id=simulation.id,
                    scenario_id=scenario.id,
                    outcome_type=outcome.get("domain", "general"),
                    expected_value=outcome.get("projected_value", 0),
                    confidence_score=outcome.get("confidence", 0.5),
                    risk_level=outcome.get("risk_score", 0.5),
                    risk_factors=outcome.get("key_factors", []),
                    details=outcome,
                )
                self.session.add(result)
            
            await self.session.commit()
            
            # Determine recommended scenario
            recommended = self._determine_recommended_scenario(scenarios)
            simulation.recommended_scenario = recommended.get("scenario_name") if recommended else None
            simulation.overall_risk_level = recommended.get("risk_level", "medium") if recommended else "medium"
            
            # Complete simulation
            simulation.status = SimulationStatus.COMPLETED
            simulation.completed_at = datetime.utcnow()
            simulation.current_step = "completed"
            
            await self.session.commit()
            
            # Publish event
            await self._publish_event(simulation, "completed")
            
            # Track metrics
            increment("simulations_completed", domain=MetricDomain.SYSTEM)
            
            logger.info(f"Simulation completed: {simulation.id}")
            
            return simulation
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            simulation.status = SimulationStatus.FAILED
            simulation.error_message = str(e)
            simulation.completed_at = datetime.utcnow()
            await self.session.commit()
            raise
    
    def _determine_recommended_scenario(
        self,
        scenarios: List[SimulationScenario],
    ) -> Optional[Dict[str, Any]]:
        """Determine the recommended scenario."""
        
        if not scenarios:
            return None
        
        # Score each scenario: higher is better
        # Consider: risk score (lower is better), projected value (higher is better)
        
        best_scenario = None
        best_score = float('-inf')
        
        for scenario in scenarios:
            risk = scenario.risk_score or 0.5
            value = scenario.projected_value or 0
            
            # Score: high value, low risk
            score = value - (risk * 1000)
            
            if score > best_score:
                best_score = score
                best_scenario = {
                    "scenario_name": scenario.scenario_name,
                    "scenario_type": scenario.scenario_type,
                    "risk_level": "low" if risk < 0.3 else "medium" if risk < 0.6 else "high",
                    "projected_value": value,
                    "risk_score": risk,
                }
        
        return best_scenario
    
    async def _publish_event(
        self,
        simulation: SimulationRun,
        event_suffix: str,
    ) -> None:
        """Publish simulation event."""
        
        event_bus = get_event_bus(self.session)
        
        await event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={
                    "simulation_id": str(simulation.id),
                    "decision_type": simulation.decision_type,
                    "event": event_suffix,
                },
                source_module="simulation_engine",
            )
        )
    
    async def get_simulation(
        self,
        simulation_id: uuid.UUID,
    ) -> Optional[SimulationRun]:
        """Get a simulation run."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(SimulationRun).where(SimulationRun.id == simulation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_simulations(
        self,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[SimulationRun]:
        """Get simulation runs."""
        
        from sqlalchemy import select, desc
        
        query = select(SimulationRun).order_by(desc(SimulationRun.created_at)).limit(limit)
        
        if status:
            query = query.where(SimulationRun.status == status)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_simulation_scenarios(
        self,
        simulation_id: uuid.UUID,
    ) -> List[SimulationScenario]:
        """Get scenarios for a simulation."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(SimulationScenario)
            .where(SimulationScenario.simulation_id == simulation_id)
        )
        return list(result.scalars().all())
    
    async def get_simulation_results(
        self,
        simulation_id: uuid.UUID,
    ) -> List[SimulationResult]:
        """Get results for a simulation."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(SimulationResult)
            .where(SimulationResult.simulation_id == simulation_id)
        )
        return list(result.scalars().all())


async def get_simulation_engine(session: AsyncSession) -> SimulationEngine:
    """Get simulation engine instance."""
    return SimulationEngine(session)
