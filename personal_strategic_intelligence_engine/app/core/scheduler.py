"""Scheduler for recurring board meetings."""
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class BoardScheduler:
    """Scheduler for recurring board meetings."""

    def __init__(self):
        settings = get_settings()
        self.scheduler = AsyncIOScheduler() if settings.scheduler_enabled else None
        self.enabled = settings.scheduler_enabled

    def start(self) -> None:
        """Start the scheduler."""
        if not self.enabled or not self.scheduler:
            logger.info("Scheduler is disabled")
            return

        logger.info("Starting board scheduler")
        self.scheduler.start()

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler:
            logger.info("Shutting down board scheduler")
            self.scheduler.shutdown()

    def schedule_weekly_review(
        self,
        job_func,
        day_of_week: str = "monday",
        hour: int = 9,
        minute: int = 0,
    ) -> Optional[str]:
        """Schedule weekly strategic review."""
        if not self.scheduler:
            logger.warning("Scheduler not enabled")
            return None

        job_id = "weekly_review"
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
        )
        self.scheduler.add_job(
            job_func,
            trigger,
            id=job_id,
            replace_existing=True,
        )
        logger.info(f"Scheduled weekly review for {day_of_week} at {hour}:{minute}")
        return job_id

    def schedule_monthly_review(
        self,
        job_func,
        day: int = 1,
        hour: int = 9,
        minute: int = 0,
    ) -> Optional[str]:
        """Schedule monthly strategic review."""
        if not self.scheduler:
            logger.warning("Scheduler not enabled")
            return None

        job_id = "monthly_review"
        trigger = CronTrigger(
            day=day,
            hour=hour,
            minute=minute,
        )
        self.scheduler.add_job(
            job_func,
            trigger,
            id=job_id,
            replace_existing=True,
        )
        logger.info(f"Scheduled monthly review for day {day} at {hour}:{minute}")
        return job_id

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        if not self.scheduler:
            return False

        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False

    def list_jobs(self) -> list[dict]:
        """List all scheduled jobs."""
        if not self.scheduler:
            return []

        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
            }
            for job in jobs
        ]


# Global scheduler instance
_board_scheduler: Optional[BoardScheduler] = None


def get_board_scheduler() -> BoardScheduler:
    """Get the global board scheduler."""
    global _board_scheduler
    if _board_scheduler is None:
        _board_scheduler = BoardScheduler()
    return _board_scheduler
