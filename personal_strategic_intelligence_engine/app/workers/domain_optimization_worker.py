"""Domain Optimization Worker for periodic optimization cycles."""
import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.optimization import get_domain_optimizer
from app.optimization.optimization_logger import get_optimization_logger

logger = logging.getLogger(__name__)


class DomainOptimizationWorker:
    """Worker for periodic domain optimization cycles."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
    
    async def run_optimization_cycle(self) -> dict:
        """Run a single optimization cycle."""
        optimizer = get_domain_optimizer()
        logger = get_optimization_logger()
        
        try:
            # Run the optimization cycle
            cycle = optimizer.run_optimization_cycle()
            
            logger.info(
                f"Optimization cycle {cycle.cycle_id} completed: "
                f"balance={cycle.overall_balance_score:.2f}, "
                f"recommendations={len(cycle.recommendations)}, "
                f"conditions={len(cycle.detected_conditions)}"
            )
            
            return {
                "status": "success",
                "cycle_id": cycle.cycle_id,
                "balance_score": cycle.overall_balance_score,
                "recommendations": len(cycle.recommendations),
                "conditions_detected": len(cycle.detected_conditions),
            }
        except Exception as e:
            logger.error(f"Error in optimization cycle: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def apply_recommendations(self) -> dict:
        """Apply the latest optimization recommendations."""
        optimizer = get_domain_optimizer()
        logger = get_optimization_logger()
        
        try:
            latest_cycle = logger.get_latest_cycle()
            
            if not latest_cycle:
                return {
                    "status": "no_cycle",
                    "message": "No optimization cycle to apply"
                }
            
            result = optimizer.apply_optimization(latest_cycle)
            
            logger.info(
                f"Applied optimization recommendations: "
                f"status={result.get('status')}, "
                f"applied={len(result.get('applied', []))}"
            )
            
            return result
        except Exception as e:
            logger.error(f"Error applying recommendations: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_full_optimization_pass(self) -> dict:
        """Run a complete optimization pass (cycle + apply)."""
        
        # Run the cycle
        cycle_result = await self.run_optimization_cycle()
        
        if cycle_result.get("status") != "success":
            return {
                "cycle": cycle_result,
                "application": {"status": "skipped", "reason": "cycle_failed"}
            }
        
        # Apply recommendations
        apply_result = await self.apply_recommendations()
        
        return {
            "cycle": cycle_result,
            "application": apply_result,
        }
    
    def start(self) -> None:
        """Start the domain optimization scheduler."""
        self.scheduler = AsyncIOScheduler()
        
        # Run optimization cycle every 6 hours
        self.scheduler.add_job(
            self.run_optimization_cycle,
            trigger=IntervalTrigger(hours=6),
            id="domain_optimization_cycle",
            name="Domain Optimization Cycle",
            replace_existing=True,
        )
        
        # Apply recommendations every 6 hours (offset by 1 hour)
        self.scheduler.add_job(
            self.apply_recommendations,
            trigger=IntervalTrigger(hours=6),
            id="apply_optimization_recommendations",
            name="Apply Optimization Recommendations",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Domain optimization worker started")
    
    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Domain optimization worker stopped")
    
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
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None,
                }
                for job in jobs
            ],
        }
    
    def trigger_manual_cycle(self) -> dict:
        """Manually trigger an optimization cycle."""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If in async context, create a task
                future = asyncio.run_coroutine_threadsafe(
                    self.run_optimization_cycle(),
                    loop
                )
                return future.result(timeout=60)
            else:
                return asyncio.run(self.run_optimization_cycle())
        except Exception as e:
            logger.error(f"Error triggering manual cycle: {e}")
            return {"status": "error", "error": str(e)}


# Global worker instance
_domain_optimization_worker: Optional[DomainOptimizationWorker] = None


def get_domain_optimization_worker() -> DomainOptimizationWorker:
    """Get the global domain optimization worker."""
    global _domain_optimization_worker
    if _domain_optimization_worker is None:
        _domain_optimization_worker = DomainOptimizationWorker()
    return _domain_optimization_worker
