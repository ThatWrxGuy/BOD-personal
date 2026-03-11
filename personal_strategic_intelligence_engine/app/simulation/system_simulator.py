"""System Simulator for orchestrating the full simulation."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation_run import SimulationRun, AuditReport
from app.simulation.scenario_builder import ScenarioBuilder, get_scenario_builder
from app.simulation.data_seed_generator import DataSeedGenerator, get_data_seed_generator
from app.simulation.metrics_collector import MetricsCollector, get_metrics_collector
from app.simulation.timeline_runner import TimelineRunner, get_timeline_runner
from app.simulation.audit_evaluator import AuditEvaluator, get_audit_evaluator
from app.simulation.report_builder import ReportBuilder, get_report_builder
from app.core.logging import get_logger

logger = get_logger(__name__)


class SystemSimulator:
    """Orchestrates the full system simulation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def run_simulation(
        self,
        scenario_type: str = "mixed_life_pressure",
        simulated_days: int = 14,
        seed: Optional[int] = None,
    ) -> SimulationRun:
        """Run a full system simulation."""
        
        # Create simulation run record
        run = SimulationRun(
            name=f"Simulation-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            scenario_type=scenario_type.upper(),
            status="RUNNING",
            start_time=datetime.utcnow(),
            simulated_days=simulated_days,
            seed_config={"seed": seed, "scenario_type": scenario_type},
        )
        
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        
        logger.info(f"Starting simulation run {run.id}")
        
        try:
            # Build scenario
            builder = get_scenario_builder()
            scenario = builder.get_scenario(scenario_type)
            
            # Seed data
            seed_generator = get_data_seed_generator(self.session)
            await seed_generator.seed_all(scenario)
            
            # Initialize metrics collector
            metrics = get_metrics_collector(self.session, run.id)
            
            # Record simulation start
            await metrics.record_event(
                event_type="ALERT",
                title="Simulation Started",
                description=f"Running {scenario_type} scenario for {simulated_days} days",
                component="system_simulator",
                severity="MEDIUM",
                metadata={"scenario": scenario_type, "days": simulated_days},
            )
            
            # Run timeline
            timeline_runner = get_timeline_runner(self.session, metrics)
            timeline_result = await timeline_runner.run_full_timeline(scenario, simulated_days)
            
            # Run evaluation
            evaluator = get_audit_evaluator(metrics)
            report_builder = get_report_builder(evaluator, metrics)
            
            # Generate report
            report_data = report_builder.build_report(
                simulation_name=scenario.get("name", scenario_type),
                scenario_description=scenario.get("description", ""),
                simulated_days=simulated_days,
            )
            
            # Save audit report
            audit_report = AuditReport(
                simulation_run_id=run.id,
                executive_summary=report_data.get("executive_summary"),
                system_readiness_score=report_data.get("system_readiness_score", 0),
                component_scores=report_data.get("component_scores", {}),
                strengths=report_data.get("strengths", []),
                weaknesses=report_data.get("weaknesses", []),
                failures=report_data.get("failures", []),
                recommendations=report_data.get("recommendations", []),
                report_text=str(report_data),
            )
            
            self.session.add(audit_report)
            
            # Update run status
            run.status = "COMPLETED"
            run.end_time = datetime.utcnow()
            run.summary = f"Processed {timeline_result['total_days']} days, score: {report_data['system_readiness_score']}/100"
            
            await self.session.commit()
            
            logger.info(f"Simulation {run.id} completed with score {report_data['system_readiness_score']}/100")
            
            return run
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            
            run.status = "FAILED"
            run.end_time = datetime.utcnow()
            run.summary = f"Failed: {str(e)}"
            
            await self.session.commit()
            
            raise

    async def get_simulation_run(self, run_id: uuid.UUID) -> Optional[SimulationRun]:
        """Get a simulation run by ID."""
        return await self.session.get(SimulationRun, run_id)

    async def list_simulation_runs(self) -> list[SimulationRun]:
        """List all simulation runs."""
        from sqlalchemy import select
        result = await self.session.execute(
            select(SimulationRun).order_by(SimulationRun.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_audit_report(self, run_id: uuid.UUID) -> Optional[AuditReport]:
        """Get the audit report for a simulation run."""
        from sqlalchemy import select
        result = await self.session.execute(
            select(AuditReport).where(AuditReport.simulation_run_id == run_id)
        )
        return result.scalar_one_or_none()


async def get_system_simulator(session: AsyncSession) -> SystemSimulator:
    """Get a system simulator instance."""
    return SystemSimulator(session)
