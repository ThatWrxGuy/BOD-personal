"""Connector Scheduler.

Handles periodic connector execution.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.connectors.connector_models import ConnectorStatus
from app.connectors.connector_registry import get_connector_registry
from app.connectors.connector_health_monitor import get_health_monitor

logger = logging.getLogger(__name__)


class ConnectorScheduler:
    """Scheduler for periodic connector runs."""
    
    def __init__(self):
        self.registry = get_connector_registry()
        self.health_monitor = get_health_monitor()
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._interval = 60  # Check every minute
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            return
        
        self._running = True
        logger.info("Connector scheduler started")
        
        # Start scheduling loop
        asyncio.create_task(self._schedule_loop())
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        
        # Cancel all running tasks
        for name, task in self._tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled connector task: {name}")
        
        self._tasks.clear()
        logger.info("Connector scheduler stopped")
    
    async def schedule_connector(
        self,
        connector_name: str,
        interval_seconds: int,
    ) -> None:
        """Schedule a connector to run at intervals."""
        # Cancel existing task if any
        if connector_name in self._tasks:
            self._tasks[connector_name].cancel()
        
        # Create new periodic task
        task = asyncio.create_task(
            self._run_connector_periodically(connector_name, interval_seconds)
        )
        self._tasks[connector_name] = task
        logger.info(f"Scheduled connector {connector_name} every {interval_seconds}s")
    
    async def unschedule_connector(self, connector_name: str) -> None:
        """Remove a connector from the schedule."""
        if connector_name in self._tasks:
            self._tasks[connector_name].cancel()
            del self._tasks[connector_name]
            logger.info(f"Unscheduled connector: {connector_name}")
    
    async def trigger_now(self, connector_name: str) -> None:
        """Trigger a connector run immediately."""
        from app.connectors.connector_controller import get_connector_controller
        
        controller = get_connector_controller()
        await controller.run_connector(connector_name)
    
    async def _schedule_loop(self) -> None:
        """Main scheduling loop."""
        while self._running:
            try:
                # Get enabled connectors
                connectors = self.registry.get_enabled_connectors()
                
                # Schedule any not already scheduled
                for connector in connectors:
                    if connector.name not in self._tasks:
                        await self.schedule_connector(
                            connector.name,
                            connector.interval_seconds,
                        )
                
                # Remove scheduled tasks for disabled connectors
                scheduled_names = set(self._tasks.keys())
                enabled_names = {c.name for c in connectors}
                
                for name in scheduled_names - enabled_names:
                    await self.unschedule_connector(name)
            
            except Exception as e:
                logger.error(f"Error in schedule loop: {e}")
            
            await asyncio.sleep(self._interval)
    
    async def _run_connector_periodically(
        self,
        connector_name: str,
        interval_seconds: int,
    ) -> None:
        """Run a connector periodically."""
        while self._running:
            try:
                from app.connectors.connector_controller import get_connector_controller
                
                controller = get_connector_controller()
                await controller.run_connector(connector_name)
            
            except Exception as e:
                logger.error(f"Error running connector {connector_name}: {e}")
            
            # Wait for next interval
            await asyncio.sleep(interval_seconds)
    
    def get_scheduled_connectors(self) -> List[str]:
        """Get list of scheduled connector names."""
        return list(self._tasks.keys())
    
    def is_scheduled(self, connector_name: str) -> bool:
        """Check if a connector is scheduled."""
        return connector_name in self._tasks and not self._tasks[connector_name].done()


# Global scheduler instance
_connector_scheduler: Optional[ConnectorScheduler] = None


def get_connector_scheduler() -> ConnectorScheduler:
    """Get the global connector scheduler instance."""
    global _connector_scheduler
    if _connector_scheduler is None:
        _connector_scheduler = ConnectorScheduler()
    return _connector_scheduler
