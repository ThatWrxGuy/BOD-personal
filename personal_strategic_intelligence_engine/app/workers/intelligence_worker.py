"""Intelligence Worker for periodic intelligence updates."""
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import AsyncSessionLocal
from app.intelligence.intelligence_service import IntelligenceService
from app.core.logging import get_logger

logger = get_logger(__name__)


class IntelligenceWorker:
    """Worker for periodic intelligence updates."""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None

    async def run_trend_analysis(self) -> dict:
        """Run trend analysis."""
        async with AsyncSessionLocal() as session:
            service = IntelligenceService(session)
            try:
                trends = await service.detect_trends()
                logger.info(f"Trend analysis complete: {len(trends.get('signal_trends', []))} trends")
                return {"status": "success", "trends": trends}
            except Exception as e:
                logger.error(f"Error in trend analysis: {e}")
                return {"status": "error", "error": str(e)}

    async def run_forecasting(self) -> dict:
        """Run forecast generation."""
        async with AsyncSessionLocal() as session:
            service = IntelligenceService(session)
            try:
                forecasts = await service.generate_forecasts()
                logger.info(f"Forecasting complete: {len(forecasts)} forecasts")
                return {"status": "success", "forecasts_generated": len(forecasts)}
            except Exception as e:
                logger.error(f"Error in forecasting: {e}")
                return {"status": "error", "error": str(e)}

    async def run_risk_projection(self) -> dict:
        """Run risk projection."""
        async with AsyncSessionLocal() as session:
            service = IntelligenceService(session)
            try:
                risks = await service.calculate_risk_projections()
                logger.info(f"Risk projection complete: {len(risks)} risks identified")
                return {"status": "success", "risks_identified": len(risks)}
            except Exception as e:
                logger.error(f"Error in risk projection: {e}")
                return {"status": "error", "error": str(e)}

    async def run_goal_probability(self) -> dict:
        """Run goal probability calculation."""
        async with AsyncSessionLocal() as session:
            service = IntelligenceService(session)
            try:
                probabilities = await service.evaluate_goal_probabilities()
                logger.info(f"Goal probability complete: {len(probabilities)} goals evaluated")
                return {"status": "success", "goals_evaluated": len(probabilities)}
            except Exception as e:
                logger.error(f"Error in goal probability: {e}")
                return {"status": "error", "error": str(e)}

    async def run_full_intelligence_cycle(self) -> dict:
        """Run a complete intelligence cycle."""
        results = {
            "trends": {},
            "forecasts": {},
            "risks": {},
            "probabilities": {},
        }
        
        try:
            results["trends"] = await self.run_trend_analysis()
        except Exception as e:
            logger.error(f"Error in trends: {e}")
        
        try:
            results["forecasts"] = await self.run_forecasting()
        except Exception as e:
            logger.error(f"Error in forecasts: {e}")
        
        try:
            results["risks"] = await self.run_risk_projection()
        except Exception as e:
            logger.error(f"Error in risks: {e}")
        
        try:
            results["probabilities"] = await self.run_goal_probability()
        except Exception as e:
            logger.error(f"Error in probabilities: {e}")
        
        logger.info(f"Intelligence cycle complete: {results}")
        return results

    def start(self) -> None:
        """Start the intelligence scheduler."""
        self.scheduler = AsyncIOScheduler()
        
        # Trend analysis every 6 hours
        self.scheduler.add_job(
            self.run_trend_analysis,
            trigger=IntervalTrigger(hours=6),
            id="trend_analysis",
            replace_existing=True,
        )
        
        # Forecast generation daily
        self.scheduler.add_job(
            self.run_forecasting,
            trigger=IntervalTrigger(hours=24),
            id="forecasting",
            replace_existing=True,
        )
        
        # Risk projection every 12 hours
        self.scheduler.add_job(
            self.run_risk_projection,
            trigger=IntervalTrigger(hours=12),
            id="risk_projection",
            replace_existing=True,
        )
        
        # Goal probability calculation daily
        self.scheduler.add_job(
            self.run_goal_probability,
            trigger=IntervalTrigger(hours=24),
            id="goal_probability",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Intelligence worker started")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Intelligence worker stopped")

    def get_status(self) -> dict:
        """Get worker status."""
        if not self.scheduler:
            return {"running": False, "jobs": []}
        
        jobs = self.scheduler.get_jobs()
        return {
            "running": True,
            "jobs": [
                {
                    "id": job.id,
                    "next_run": str(job.next_run_time) if job.next_run_time else None,
                }
                for job in jobs
            ],
        }


# Global worker instance
_intelligence_worker: Optional[IntelligenceWorker] = None


def get_intelligence_worker() -> IntelligenceWorker:
    """Get the global intelligence worker."""
    global _intelligence_worker
    if _intelligence_worker is None:
        _intelligence_worker = IntelligenceWorker()
    return _intelligence_worker
