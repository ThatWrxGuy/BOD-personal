"""Signal collector worker for scheduled signal collection."""
import asyncio
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.signals.market_signals import MarketSignalCollector
from app.signals.finance_signals import FinanceSignalCollector
from app.signals.health_signals import HealthSignalCollector
from app.signals.macro_signals import MacroSignalCollector
from app.signals.calendar_signals import CalendarSignalCollector
from app.signals.research_signals import ResearchSignalCollector
from app.signals.signal_processor import SignalProcessor
from app.db.session import AsyncSessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)


class SignalCollectorWorker:
    """Worker for collecting signals on a schedule."""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.collectors = [
            MarketSignalCollector(),
            FinanceSignalCollector(),
            HealthSignalCollector(),
            MacroSignalCollector(),
            CalendarSignalCollector(),
            ResearchSignalCollector(),
        ]

    async def collect_signals(self) -> int:
        """Collect signals from all collectors."""
        total_collected = 0
        
        async with AsyncSessionLocal() as session:
            processor = SignalProcessor(session)
            
            for collector in self.collectors:
                try:
                    logger.info(f"Collecting signals from {collector.category}")
                    raw_signals = await collector.collect()
                    
                    if raw_signals:
                        processed = await processor.process_batch(raw_signals)
                        total_collected += len(processed)
                        logger.info(f"Processed {len(processed)} signals from {collector.category}")
                    
                except Exception as e:
                    logger.error(f"Error collecting from {collector.category}: {e}")
        
        return total_collected

    def start(self) -> None:
        """Start the signal collector scheduler."""
        self.scheduler = AsyncIOScheduler()
        
        # Schedule each collector at its specified interval
        for collector in self.collectors:
            interval_seconds = collector.get_interval_seconds()
            self.scheduler.add_job(
                self.collect_signals,
                trigger=IntervalTrigger(seconds=interval_seconds),
                id=f"signal_collector_{collector.category}",
                replace_existing=True,
            )
            logger.info(f"Scheduled {collector.category} collector every {interval_seconds}s")
        
        self.scheduler.start()
        logger.info("Signal collector worker started")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Signal collector worker stopped")

    def get_status(self) -> dict:
        """Get collector status."""
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
            "collectors": [
                {
                    "category": c.category,
                    "interval_seconds": c.get_interval_seconds(),
                }
                for c in self.collectors
            ],
        }


# Global worker instance
_signal_worker: Optional[SignalCollectorWorker] = None


def get_signal_collector_worker() -> SignalCollectorWorker:
    """Get the global signal collector worker."""
    global _signal_worker
    if _signal_worker is None:
        _signal_worker = SignalCollectorWorker()
    return _signal_worker
