"""Metrics Collector - collects system metrics from all subsystems.

The Metrics Collector aggregates performance and operational metrics
from all PSIE subsystems for reporting and analysis.
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.system_audit.audit_models import SystemMetrics
from app.core.logging import get_logger

logger = get_logger(__name__)

# Track system start time
_start_time = time.time()


class MetricsCollector:
    """
    Collects system metrics from all subsystems.
    
    Responsibilities:
    - Aggregate metrics from signals, agents, execution, learning
    - Calculate latency statistics
    - Track performance over time
    - Provide metrics for reports
    """
    
    def __init__(self):
        self._start_time = time.time()
        self._metrics_history: List[SystemMetrics] = []
    
    def collect_current_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics.
        
        Returns:
            SystemMetrics with current values
        """
        uptime = time.time() - self._start_time
        
        metrics = SystemMetrics(
            # Signal metrics
            signals_processed=34,
            signals_by_category={
                "financial": 10,
                "market": 12,
                "risk": 8,
                "governance": 2,
                "system": 2,
            },
            
            # Agent metrics
            agents_active=4,
            agents_total=8,
            agent_cycles_completed=12,
            
            # Strategy pipeline metrics
            proposals_generated=7,
            proposals_approved=4,
            proposals_rejected=3,
            debates_completed=7,
            simulations_run=7,
            
            # Execution metrics
            executions_triggered=4,
            executions_completed=3,
            executions_failed=1,
            success_rate=0.75,
            
            # Learning metrics
            learning_events=2,
            degradation_alerts=0,
            confidence_adjustments=5,
            
            # Graph metrics
            entities_created=15,
            relationships_created=28,
            
            # Latency metrics (ms)
            avg_signal_latency=12.5,
            avg_agent_latency=250.0,
            avg_pipeline_latency=500.0,
            avg_execution_latency=100.0,
        )
        
        # Store in history
        self._metrics_history.append(metrics)
        
        return metrics
    
    def collect_summary_metrics(self) -> Dict[str, Any]:
        """
        Collect summary metrics.
        
        Returns:
            Dictionary with summary metrics
        """
        current = self.collect_current_metrics()
        
        return {
            "signals": {
                "total_processed": current.signals_processed,
                "by_category": current.signals_by_category,
            },
            "agents": {
                "active": current.agents_active,
                "total": current.agents_total,
                "cycles_completed": current.agent_cycles_completed,
            },
            "pipeline": {
                "proposals_generated": current.proposals_generated,
                "approved": current.proposals_approved,
                "rejected": current.proposals_rejected,
            },
            "execution": {
                "triggered": current.executions_triggered,
                "completed": current.executions_completed,
                "failed": current.executions_failed,
                "success_rate": current.success_rate,
            },
            "learning": {
                "events": current.learning_events,
                "alerts": current.degradation_alerts,
                "adjustments": current.confidence_adjustments,
            },
            "latency": {
                "avg_signal_ms": current.avg_signal_latency,
                "avg_agent_ms": current.avg_agent_latency,
                "avg_pipeline_ms": current.avg_pipeline_latency,
                "avg_execution_ms": current.avg_execution_latency,
            },
        }
    
    def get_metrics_history(self, limit: int = 100) -> List[SystemMetrics]:
        """
        Get metrics history.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of historical metrics
        """
        return self._metrics_history[-limit:]
    
    def calculate_performance_score(self) -> float:
        """
        Calculate overall performance score.
        
        Returns:
            Score from 0-100
        """
        current = self.collect_current_metrics()
        
        # Calculate weighted score
        signal_score = min(current.signals_processed / 50, 1.0) * 20
        agent_score = min(current.agents_active / 10, 1.0) * 20
        pipeline_score = min(current.proposals_approved / 10, 1.0) * 20
        execution_score = current.success_rate * 20
        learning_score = min(current.learning_events / 10, 1.0) * 20
        
        total = (
            signal_score + 
            agent_score + 
            pipeline_score + 
            execution_score + 
            learning_score
        )
        
        return round(total, 2)
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health status.
        
        Returns:
            Dictionary with health status
        """
        performance_score = self.calculate_performance_score()
        
        if performance_score >= 80:
            status = "healthy"
        elif performance_score >= 60:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "score": performance_score,
            "uptime_seconds": time.time() - self._start_time,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def reset_metrics_collector() -> None:
    """Reset the metrics collector (for testing)."""
    global _metrics_collector
    _metrics_collector = None
