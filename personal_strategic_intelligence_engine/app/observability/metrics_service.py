"""Metrics service for collecting and exposing system metrics."""
import time
from datetime import datetime
from typing import Dict, Optional, Any
from collections import defaultdict

from app.models.observability import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class MetricsService:
    """Central service for metrics collection."""
    
    def __init__(self):
        # In-memory metrics storage
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._timers: Dict[str, float] = {}
    
    def increment(self, metric_name: str, value: float = 1.0, domain: str = MetricDomain.SYSTEM) -> None:
        """Increment a counter metric."""
        key = f"{domain}.{metric_name}"
        self._counters[key] += value
        logger.debug(f"Incremented metric {key} to {self._counters[key]}")
    
    def decrement(self, metric_name: str, value: float = 1.0, domain: str = MetricDomain.SYSTEM) -> None:
        """Decrement a counter metric."""
        key = f"{domain}.{metric_name}"
        self._counters[key] -= value
        logger.debug(f"Decremented metric {key} to {self._counters[key]}")
    
    def set_gauge(self, metric_name: str, value: float, domain: str = MetricDomain.SYSTEM) -> None:
        """Set a gauge metric."""
        key = f"{domain}.{metric_name}"
        self._gauges[key] = value
        logger.debug(f"Set gauge {key} to {value}")
    
    def record_duration(self, metric_name: str, duration_ms: float, domain: str = MetricDomain.SYSTEM) -> None:
        """Record a duration/histogram metric."""
        key = f"{domain}.{metric_name}"
        self._histograms[key].append(duration_ms)
        logger.debug(f"Recorded duration {key}: {duration_ms}ms")
    
    def start_timer(self, metric_name: str) -> None:
        """Start a timer for a metric."""
        self._timers[metric_name] = time.time()
    
    def stop_timer(self, metric_name: str, domain: str = MetricDomain.SYSTEM) -> Optional[float]:
        """Stop a timer and record the duration."""
        if metric_name not in self._timers:
            logger.warning(f"Timer {metric_name} was not started")
            return None
        
        start_time = self._timers.pop(metric_name)
        duration_ms = (time.time() - start_time) * 1000
        self.record_duration(metric_name, duration_ms, domain)
        return duration_ms
    
    def record_status(self, metric_name: str, status: str, domain: str = MetricDomain.SYSTEM) -> None:
        """Record a status change."""
        key = f"{domain}.{metric_name}.{status}"
        self._counters[key] += 1
    
    def get_counter(self, metric_name: str, domain: str = MetricDomain.SYSTEM) -> float:
        """Get a counter value."""
        key = f"{domain}.{metric_name}"
        return self._counters.get(key, 0)
    
    def get_gauge(self, metric_name: str, domain: str = MetricDomain.SYSTEM) -> Optional[float]:
        """Get a gauge value."""
        key = f"{domain}.{metric_name}"
        return self._gauges.get(key)
    
    def get_histogram_stats(self, metric_name: str, domain: str = MetricDomain.SYSTEM) -> Dict[str, float]:
        """Get histogram statistics."""
        key = f"{domain}.{metric_name}"
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)] if count > 1 else sorted_values[0],
            "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[0],
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: self.get_histogram_stats(k.split(".", 1)[1], k.split(".", 1)[0])
                for k in self._histograms.keys()
            },
        }
    
    def get_domain_metrics(self, domain: str) -> Dict[str, Any]:
        """Get metrics for a specific domain."""
        prefix = f"{domain}."
        
        counters = {k.replace(prefix, ""): v for k, v in self._counters.items() if k.startswith(prefix)}
        gauges = {k.replace(prefix, ""): v for k, v in self._gauges.items() if k.startswith(prefix)}
        histograms = {
            k.replace(prefix, ""): self.get_histogram_stats(k.split(".", 1)[1], domain)
            for k in self._histograms.keys() if k.startswith(prefix)
        }
        
        return {
            "counters": counters,
            "gauges": gauges,
            "histograms": histograms,
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()


# Global metrics service
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    """Get the global metrics service."""
    global _metrics_service
    
    if _metrics_service is None:
        _metrics_service = MetricsService()
    
    return _metrics_service


# Convenience functions
def increment(name: str, value: float = 1.0, domain: str = MetricDomain.SYSTEM) -> None:
    """Increment a counter."""
    get_metrics_service().increment(name, value, domain)


def set_gauge(name: str, value: float, domain: str = MetricDomain.SYSTEM) -> None:
    """Set a gauge value."""
    get_metrics_service().set_gauge(name, value, domain)


def record_duration(name: str, duration_ms: float, domain: str = MetricDomain.SYSTEM) -> None:
    """Record a duration."""
    get_metrics_service().record_duration(name, duration_ms, domain)


def start_timer(name: str) -> None:
    """Start a timer."""
    get_metrics_service().start_timer(name)


def stop_timer(name: str, domain: str = MetricDomain.SYSTEM) -> Optional[float]:
    """Stop a timer."""
    return get_metrics_service().stop_timer(name, domain)
