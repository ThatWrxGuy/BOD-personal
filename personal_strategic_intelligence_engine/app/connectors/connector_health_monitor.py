"""Connector Health Monitor.

Tracks connector reliability and performance metrics.
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.connectors.connector_models import (
    ConnectorHealth,
    ConnectorStatus,
)
from app.connectors.connector_store import get_connector_store


class ConnectorHealthMonitor:
    """Monitor for connector health metrics."""
    
    def __init__(self):
        self.store = get_connector_store()
        self._metrics: Dict[str, Dict] = {}
    
    def record_run_start(self, connector_name: str) -> None:
        """Record the start of a connector run."""
        if connector_name not in self._metrics:
            self._init_metrics(connector_name)
        
        self._metrics[connector_name]["current_run_start"] = time.time()
        self._metrics[connector_name]["run_count"] += 1
    
    def record_run_complete(
        self,
        connector_name: str,
        signals_count: int,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Record the completion of a connector run."""
        if connector_name not in self._metrics:
            self._init_metrics(connector_name)
        
        metrics = self._metrics[connector_name]
        
        # Calculate duration
        if "current_run_start" in metrics:
            duration_ms = (time.time() - metrics["current_run_start"]) * 1000
            metrics["last_duration_ms"] = duration_ms
            
            # Update average latency
            total_runs = metrics.get("successful_runs", 0) + metrics.get("failed_runs", 0)
            if total_runs > 0:
                avg_latency = metrics.get("avg_latency_ms", 0.0)
                metrics["avg_latency_ms"] = (avg_latency * total_runs + duration_ms) / (total_runs + 1)
            else:
                metrics["avg_latency_ms"] = duration_ms
        
        # Update success/failure counts
        if success:
            metrics["successful_runs"] = metrics.get("successful_runs", 0) + 1
            metrics["consecutive_failures"] = 0
            metrics["last_success"] = datetime.utcnow()
        else:
            metrics["failed_runs"] = metrics.get("failed_runs", 0) + 1
            metrics["consecutive_failures"] = metrics.get("consecutive_failures", 0) + 1
            metrics["last_error"] = error
        
        # Update signal counts
        metrics["total_signals"] = metrics.get("total_signals", 0) + signals_count
        metrics["last_signal_count"] = signals_count
        
        # Determine status
        if not success:
            status = ConnectorStatus.ERROR
        elif metrics.get("consecutive_failures", 0) > 3:
            status = ConnectorStatus.ERROR
        else:
            status = ConnectorStatus.ACTIVE
        
        # Persist health
        health = self._build_health(connector_name, status)
        self.store.save_health(health)
    
    def get_health(self, connector_name: str) -> Optional[ConnectorHealth]:
        """Get health metrics for a connector."""
        # First try to get from store
        health = self.store.get_health(connector_name)
        
        if health:
            return health
        
        # If not in store, create from metrics
        if connector_name in self._metrics:
            return self._build_health(connector_name, ConnectorStatus.ACTIVE)
        
        return None
    
    def get_all_health(self) -> List[ConnectorHealth]:
        """Get health for all connectors."""
        return self.store.get_all_health()
    
    def get_uptime_percentage(self, connector_name: str) -> float:
        """Calculate uptime percentage for a connector."""
        health = self.get_health(connector_name)
        if not health or health.total_runs == 0:
            return 0.0
        
        return (health.successful_runs / health.total_runs) * 100
    
    def is_healthy(self, connector_name: str) -> bool:
        """Check if a connector is healthy."""
        health = self.get_health(connector_name)
        if not health:
            return False
        
        # Check for recent errors
        if health.status == ConnectorStatus.ERROR:
            return False
        
        # Check consecutive failures
        if health.consecutive_failures > 3:
            return False
        
        # Check if we have recent successful runs
        if health.last_success:
            time_since_success = datetime.utcnow() - health.last_success
            if time_since_success > timedelta(hours=24):
                return False
        
        return True
    
    def _init_metrics(self, connector_name: str) -> None:
        """Initialize metrics for a connector."""
        self._metrics[connector_name] = {
            "run_count": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_signals": 0,
            "avg_latency_ms": 0.0,
            "last_duration_ms": 0.0,
            "consecutive_failures": 0,
            "last_error": None,
            "last_success": None,
        }
    
    def _build_health(
        self,
        connector_name: str,
        status: ConnectorStatus,
    ) -> ConnectorHealth:
        """Build a ConnectorHealth object from metrics."""
        metrics = self._metrics.get(connector_name, {})
        
        health = ConnectorHealth(
            connector_name=connector_name,
            status=status,
            total_runs=metrics.get("run_count", 0),
            successful_runs=metrics.get("successful_runs", 0),
            failed_runs=metrics.get("failed_runs", 0),
            signals_produced=metrics.get("total_signals", 0),
            last_signal_count=metrics.get("last_signal_count", 0),
            avg_latency_ms=metrics.get("avg_latency_ms", 0.0),
            last_latency_ms=metrics.get("last_duration_ms", 0.0),
            last_error=metrics.get("last_error"),
            consecutive_failures=metrics.get("consecutive_failures", 0),
            last_success=metrics.get("last_success"),
            last_check=datetime.utcnow(),
        )
        
        return health


# Global health monitor instance
_health_monitor: Optional[ConnectorHealthMonitor] = None


def get_health_monitor() -> ConnectorHealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = ConnectorHealthMonitor()
    return _health_monitor
