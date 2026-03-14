"""Simulation Scheduler.

Schedules periodic simulation runs.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading

from app.intelligence.strategy_simulation.simulation_models import (
    SimulationResult,
)


class SimulationScheduler:
    """Schedules and manages simulation runs."""
    
    def __init__(self):
        self.last_weekly_run: Optional[datetime] = None
        self.last_monthly_run: Optional[datetime] = None
        self.scheduled_simulations: List[Dict] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start the scheduler."""
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
    
    def _run_scheduler(self) -> None:
        """Run scheduler loop."""
        import time
        while self.running:
            self._check_and_run_schedules()
            time.sleep(3600)  # Check every hour
    
    def _check_and_run_schedules(self) -> None:
        """Check and run scheduled simulations."""
        now = datetime.now()
        
        # Weekly simulation run
        if self.last_weekly_run is None or (now - self.last_weekly_run).days >= 7:
            self._run_weekly_simulation()
            self.last_weekly_run = now
        
        # Monthly large-scale discovery run
        if self.last_monthly_run is None or (now - self.last_monthly_run).days >= 30:
            self._run_monthly_discovery()
            self.last_monthly_run = now
    
    def _run_weekly_simulation(self) -> None:
        """Run weekly strategy simulation."""
        print("[SimulationScheduler] Running weekly strategy simulation...")
        # In production, would trigger actual simulation
    
    def _run_monthly_discovery(self) -> None:
        """Run monthly discovery run."""
        print("[SimulationScheduler] Running monthly strategy discovery...")
        # In production, would trigger actual discovery
    
    def schedule_simulation(
        self,
        strategy_id: str,
        scheduled_time: datetime,
    ) -> str:
        """Schedule a simulation."""
        import uuid
        schedule_id = str(uuid.uuid4())
        self.scheduled_simulations.append({
            "schedule_id": schedule_id,
            "strategy_id": strategy_id,
            "scheduled_time": scheduled_time,
            "status": "pending",
        })
        return schedule_id
    
    def cancel_simulation(self, schedule_id: str) -> bool:
        """Cancel a scheduled simulation."""
        for sim in self.scheduled_simulations:
            if sim["schedule_id"] == schedule_id:
                sim["status"] = "cancelled"
                return True
        return False
    
    def get_schedule_status(self) -> Dict:
        """Get schedule status."""
        return {
            "last_weekly_run": self.last_weekly_run.isoformat() if self.last_weekly_run else None,
            "last_monthly_run": self.last_monthly_run.isoformat() if self.last_monthly_run else None,
            "scheduled_count": len(self.scheduled_simulations),
            "running": self.running,
        }


# Global scheduler
_scheduler: Optional[SimulationScheduler] = None


def get_scheduler() -> SimulationScheduler:
    """Get global scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SimulationScheduler()
    return _scheduler


def start_scheduler() -> None:
    """Start global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler() -> None:
    """Stop global scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()
