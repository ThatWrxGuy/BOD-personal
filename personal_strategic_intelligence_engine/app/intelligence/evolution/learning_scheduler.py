"""Learning Scheduler.

Schedules and runs periodic learning tasks.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
import schedule
import time
import threading

from app.intelligence.evolution.evolution_models import LearningSchedule


class LearningScheduler:
    """Schedules periodic learning tasks."""
    
    def __init__(self):
        self.schedule = LearningSchedule()
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
        """Run the scheduler loop."""
        while self.running:
            self._check_and_run_tasks()
            time.sleep(60)  # Check every minute
    
    def _check_and_run_tasks(self) -> None:
        """Check and run scheduled tasks."""
        now = datetime.now()
        
        # Daily tasks
        if self.schedule.last_daily_run is None or (now - self.schedule.last_daily_run).days >= 1:
            self._run_daily_tasks()
            self.schedule.last_daily_run = now
        
        # Weekly tasks
        if self.schedule.last_weekly_run is None or (now - self.schedule.last_weekly_run).days >= 7:
            self._run_weekly_tasks()
            self.schedule.last_weekly_run = now
        
        # Monthly tasks
        if self.schedule.last_monthly_run is None or (now - self.schedule.last_monthly_run).days >= 30:
            self._run_monthly_tasks()
            self.schedule.last_monthly_run = now
    
    def _run_daily_tasks(self) -> None:
        """Run daily learning tasks."""
        for task in self.schedule.daily_tasks:
            if task == "signal_performance":
                print(f"[Scheduler] Running daily task: {task}")
                # In production, would trigger signal performance update
    
    def _run_weekly_tasks(self) -> None:
        """Run weekly learning tasks."""
        for task in self.schedule.weekly_tasks:
            if task == "feature_recalculation":
                print(f"[Scheduler] Running weekly task: {task}")
                # In production, would trigger feature importance recalculation
    
    def _run_monthly_tasks(self) -> None:
        """Run monthly learning tasks."""
        for task in self.schedule.monthly_tasks:
            if task == "strategy_optimization":
                print(f"[Scheduler] Running monthly task: {task}")
                # In production, would trigger strategy optimization
    
    def add_daily_task(self, task_name: str) -> None:
        """Add a daily task."""
        if task_name not in self.schedule.daily_tasks:
            self.schedule.daily_tasks.append(task_name)
    
    def add_weekly_task(self, task_name: str) -> None:
        """Add a weekly task."""
        if task_name not in self.schedule.weekly_tasks:
            self.schedule.weekly_tasks.append(task_name)
    
    def add_monthly_task(self, task_name: str) -> None:
        """Add a monthly task."""
        if task_name not in self.schedule.monthly_tasks:
            self.schedule.monthly_tasks.append(task_name)
    
    def get_schedule_status(self) -> Dict:
        """Get current schedule status."""
        return {
            "daily_tasks": self.schedule.daily_tasks,
            "weekly_tasks": self.schedule.weekly_tasks,
            "monthly_tasks": self.schedule.monthly_tasks,
            "last_daily_run": self.schedule.last_daily_run.isoformat() if self.schedule.last_daily_run else None,
            "last_weekly_run": self.schedule.last_weekly_run.isoformat() if self.schedule.last_weekly_run else None,
            "last_monthly_run": self.schedule.last_monthly_run.isoformat() if self.schedule.last_monthly_run else None,
            "running": self.running,
        }


# Global scheduler instance
_scheduler: Optional[LearningScheduler] = None


def get_scheduler() -> LearningScheduler:
    """Get global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = LearningScheduler()
    return _scheduler


def start_scheduler() -> None:
    """Start the global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler() -> None:
    """Stop the global scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()
