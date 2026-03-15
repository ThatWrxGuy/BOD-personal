"""Monitoring and Metrics - Track platform health and retrieval quality.

Tracks:
- Source hit rate
- Stale data rate
- Citation coverage
- Connector health
- Denied request count
- Retrieval latency
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class PlatformMetrics:
    """Platform health and retrieval quality metrics."""
    
    def __init__(self):
        # Retrieval metrics
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.denied_requests: int = 0
        self.total_latency_ms: float = 0.0
        
        # Source metrics
        self.source_hits: Dict[str, int] = defaultdict(int)
        self.source_errors: Dict[str, int] = defaultdict(int)
        self.source_latency: Dict[str, List[float]] = defaultdict(list)
        
        # Data freshness metrics
        self.stale_data_count: int = 0
        self.fresh_data_count: int = 0
        
        # Connector metrics
        self.connector_health: Dict[str, str] = {}
        
        # Denied requests
        self.denial_reasons: Dict[str, int] = defaultdict(int)
    
    def record_request(
        self,
        success: bool,
        latency_ms: float,
        sources: List[str],
    ):
        """Record a retrieval request."""
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        
        if success:
            self.successful_requests += 1
        else:
            self.denied_requests += 1
        
        for source in sources:
            self.source_hits[source] += 1
            self.source_latency[source].append(latency_ms)
    
    def record_denial(self, reason: str):
        """Record a denied request."""
        self.denied_requests += 1
        self.denial_reasons[reason] += 1
    
    def record_stale_data(self, is_stale: bool):
        """Record data freshness."""
        if is_stale:
            self.stale_data_count += 1
        else:
            self.fresh_data_count += 1
    
    def record_connector_health(self, connector_id: str, status: str):
        """Record connector health status."""
        self.connector_health[connector_id] = status
    
    def get_hit_rate(self, source_id: Optional[str] = None) -> float:
        """Get source hit rate."""
        if source_id:
            return self.source_hits.get(source_id, 0) / max(self.total_requests, 1)
        
        total_hits = sum(self.source_hits.values())
        return total_hits / max(self.total_requests, 1)
    
    def get_stale_rate(self) -> float:
        """Get stale data rate."""
        total = self.stale_data_count + self.fresh_data_count
        return self.stale_data_count / max(total, 1)
    
    def get_avg_latency(self, source_id: Optional[str] = None) -> float:
        """Get average retrieval latency."""
        if source_id:
            latencies = self.source_latency.get(source_id, [])
            return sum(latencies) / max(len(latencies), 1)
        
        return self.total_latency_ms / max(self.total_requests, 1)
    
    def get_denial_rate(self) -> float:
        """Get denied request rate."""
        return self.denied_requests / max(self.total_requests, 1)
    
    def get_top_sources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most used sources."""
        sorted_sources = sorted(
            self.source_hits.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "source_id": source_id,
                "hit_count": hit_count,
                "avg_latency_ms": self.get_avg_latency(source_id),
            }
            for source_id, hit_count in sorted_sources[:limit]
        ]
    
    def get_connectors_status(self) -> Dict[str, Any]:
        """Get connector health status."""
        total = len(self.connector_health)
        healthy = sum(1 for s in self.connector_health.values() if s == "healthy")
        
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": total - healthy,
            "connectors": self.connector_health,
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "requests": {
                "total": self.total_requests,
                "successful": self.successful_requests,
                "denied": self.denied_requests,
                "success_rate": self.successful_requests / max(self.total_requests, 1),
                "denial_rate": self.get_denial_rate(),
            },
            "latency": {
                "avg_ms": self.get_avg_latency(),
            },
            "sources": {
                "total_unique": len(self.source_hits),
                "hit_rate": self.get_hit_rate(),
            },
            "freshness": {
                "stale_count": self.stale_data_count,
                "fresh_count": self.fresh_data_count,
                "stale_rate": self.get_stale_rate(),
            },
            "denials": dict(self.denial_reasons),
        }
    
    def reset(self):
        """Reset all metrics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.denied_requests = 0
        self.total_latency_ms = 0.0
        self.source_hits.clear()
        self.source_errors.clear()
        self.source_latency.clear()
        self.stale_data_count = 0
        self.fresh_data_count = 0
        self.connector_health.clear()
        self.denial_reasons.clear()


class HumanReviewReport:
    """Human-readable review reports."""
    
    def __init__(self, metrics: PlatformMetrics):
        self.metrics = metrics
    
    def generate_dashboard(self) -> str:
        """Generate dashboard-style report."""
        summary = self.metrics.get_summary()
        
        report = []
        report.append("=" * 60)
        report.append("DATA PLATFORM HEALTH DASHBOARD")
        report.append("=" * 60)
        report.append("")
        
        # Requests summary
        req = summary["requests"]
        report.append("REQUESTS")
        report.append("-" * 40)
        report.append(f"  Total Requests:      {req['total']:,}")
        report.append(f"  Successful:         {req['successful']:,}")
        report.append(f"  Denied:             {req['denied']:,}")
        report.append(f"  Success Rate:       {req['success_rate']*100:.1f}%")
        report.append(f"  Denial Rate:        {req['denial_rate']*100:.1f}%")
        report.append("")
        
        # Latency
        report.append("LATENCY")
        report.append("-" * 40)
        report.append(f"  Average:            {summary['latency']['avg_ms']:.2f}ms")
        report.append("")
        
        # Sources
        src = summary["sources"]
        report.append("TOP SOURCES (by usage)")
        report.append("-" * 40)
        for source in self.metrics.get_top_sources(5):
            report.append(f"  {source['source_id']:<30} {source['hit_count']:>6} hits  {source['avg_latency_ms']:>8.2f}ms")
        report.append("")
        
        # Freshness
        frh = summary["freshness"]
        report.append("DATA FRESHNESS")
        report.append("-" * 40)
        report.append(f"  Fresh Records:      {frh['fresh_count']:,}")
        report.append(f"  Stale Records:      {frh['stale_count']:,}")
        report.append(f"  Stale Rate:        {frh['stale_rate']*100:.1f}%")
        report.append("")
        
        # Connectors
        conn = self.metrics.get_connectors_status()
        report.append("CONNECTORS")
        report.append("-" * 40)
        report.append(f"  Healthy:           {conn['healthy']}/{conn['total']}")
        report.append("")
        
        # Denials
        if summary["denials"]:
            report.append("DENIAL REASONS")
            report.append("-" * 40)
            for reason, count in summary["denials"].items():
                report.append(f"  {reason:<40} {count:>6}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Singleton
_metrics: Optional[PlatformMetrics] = None


def get_platform_metrics() -> PlatformMetrics:
    """Get platform metrics singleton."""
    global _metrics
    if _metrics is None:
        _metrics = PlatformMetrics()
    return _metrics
