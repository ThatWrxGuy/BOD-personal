"""Governance scheduler worker for continuous governance."""
import asyncio
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import AsyncSessionLocal
from app.services.governance_service import GovernanceService
from app.core.logging import get_logger

logger = get_logger(__name__)


class GovernanceSchedulerWorker:
    """Worker for continuous governance operations."""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None

    async def check_scheduled_meetings(self) -> int:
        """Check for and trigger due scheduled meetings."""
        meetings_triggered = 0
        
        async with AsyncSessionLocal() as session:
            service = GovernanceService(session)
            
            try:
                # Initialize schedules if needed
                await service.initialize_governance()
                
                # Get due meetings
                due = await service.get_due_meetings()
                
                for schedule in due:
                    logger.info(f"Triggering scheduled meeting: {schedule.meeting_type}")
                    # In production, this would trigger actual board meetings
                    # For now, we just log and mark as run
                    meetings_triggered += 1
                    
            except Exception as e:
                logger.error(f"Error checking scheduled meetings: {e}")
        
        return meetings_triggered

    async def check_signal_triggers(self) -> int:
        """Check signals and create trigger events."""
        triggers_created = 0
        
        async with AsyncSessionLocal() as session:
            service = GovernanceService(session)
            
            try:
                triggers = await service.check_and_trigger_events()
                triggers_created = len(triggers)
                logger.info(f"Created {triggers_created} trigger events")
                
            except Exception as e:
                logger.error(f"Error checking signal triggers: {e}")
        
        return triggers_created

    async def run_governance_cycle(self) -> dict:
        """Run a complete governance cycle."""
        results = {
            "meetings_triggered": 0,
            "triggers_created": 0,
        }
        
        try:
            results["meetings_triggered"] = await self.check_scheduled_meetings()
            results["triggers_created"] = await self.check_signal_triggers()
            
            logger.info(f"Governance cycle complete: {results}")
            
        except Exception as e:
            logger.error(f"Error in governance cycle: {e}")
        
        return results

    def start(self) -> None:
        """Start the governance scheduler."""
        self.scheduler = AsyncIOScheduler()
        
        # Check scheduled meetings every 15 minutes
        self.scheduler.add_job(
            self.check_scheduled_meetings,
            trigger=IntervalTrigger(minutes=15),
            id="check_scheduled_meetings",
            replace_existing=True,
        )
        
        # Check signal triggers every 5 minutes
        self.scheduler.add_job(
            self.check_signal_triggers,
            trigger=IntervalTrigger(minutes=5),
            id="check_signal_triggers",
            replace_existing=True,
        )
        
        # Run governance cycle every hour
        self.scheduler.add_job(
            self.run_governance_cycle,
            trigger=IntervalTrigger(hours=1),
            id="governance_cycle",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Governance scheduler worker started")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Governance scheduler worker stopped")

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
_governance_worker: Optional[GovernanceSchedulerWorker] = None


def get_governance_worker() -> GovernanceSchedulerWorker:
    """Get the global governance worker."""
    global _governance_worker
    if _governance_worker is None:
        _governance_worker = GovernanceSchedulerWorker()
    return _governance_worker
