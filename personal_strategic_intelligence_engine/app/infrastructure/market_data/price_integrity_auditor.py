"""Price Integrity Auditor - BB-INF-007

Audits and monitors market data integrity.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.infrastructure.market_data.market_data_models import (
    MarketDataIntegrityReport,
    ProviderHealth,
    ProviderStatus,
)

logger = logging.getLogger(__name__)


class PriceIntegrityAuditor:
    """Monitors and audits market data integrity."""
    
    def __init__(self):
        self._requests: List[dict] = []
        self._provider_health: Dict[str, ProviderHealth] = {}
        self._max_requests = 10000  # Keep last 10k requests
    
    def record_request(
        self,
        symbol: str,
        module: str,
        provider: str,
        latency_ms: float,
        approved: bool,
        failure_reason: Optional[str] = None,
        is_fallback: bool = False,
    ) -> None:
        """Record a price request for audit."""
        
        record = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol,
            "module": module,
            "provider": provider,
            "latency_ms": latency_ms,
            "approved": approved,
            "failure_reason": failure_reason,
            "is_fallback": is_fallback,
        }
        
        self._requests.append(record)
        
        # Trim if needed
        if len(self._requests) > self._max_requests:
            self._requests = self._requests[-self._max_requests:]
    
    def record_provider_failure(
        self,
        provider: str,
        error: str,
    ) -> None:
        """Record a provider failure."""
        
        if provider not in self._provider_health:
            self._provider_health[provider] = ProviderHealth(
                provider_name=provider,
                status=ProviderStatus.FAILED,
            )
        
        health = self._provider_health[provider]
        health.failure_count += 1
        health.last_failure = datetime.utcnow()
        health.status = ProviderStatus.FAILED
        
        # Update success rate
        total = health.failure_count + (health.success_rate * 100)  # Approximate
        if total > 0:
            health.success_rate = (total - health.failure_count) / total
    
    def record_provider_success(
        self,
        provider: str,
        latency_ms: float,
    ) -> None:
        """Record a successful provider request."""
        
        if provider not in self._provider_health:
            self._provider_health[provider] = ProviderHealth(
                provider_name=provider,
                status=ProviderStatus.HEALTHY,
            )
        
        health = self._provider_health[provider]
        
        # Update latency
        if health.avg_latency_ms == 0:
            health.avg_latency_ms = latency_ms
        else:
            health.avg_latency_ms = (health.avg_latency_ms * 0.9) + (latency_ms * 0.1)
        
        health.last_success = datetime.utcnow()
        health.failure_count = max(0, health.failure_count - 1)
        
        # Update status
        if health.failure_count == 0:
            health.status = ProviderStatus.HEALTHY
        elif health.failure_count < 3:
            health.status = ProviderStatus.DEGRADED
    
    def generate_report(self) -> MarketDataIntegrityReport:
        """Generate integrity report."""
        
        report = MarketDataIntegrityReport()
        
        if not self._requests:
            return report
        
        # Count stats
        total_requests = len(self._requests)
        valid_live = 0
        stale_blocked = 0
        invalid_rejected = 0
        fallback_blocked = 0
        
        # By symbol
        by_symbol: Dict[str, Dict[str, int]] = {}
        # By module
        by_module: Dict[str, Dict[str, int]] = {}
        
        for req in self._requests:
            symbol = req["symbol"]
            module = req["module"]
            approved = req["approved"]
            failure = req["failure_reason"]
            is_fallback = req["is_fallback"]
            
            # Initialize symbol/module if needed
            if symbol not in by_symbol:
                by_symbol[symbol] = {"requests": 0, "approved": 0, "rejected": 0}
            if module not in by_module:
                by_module[module] = {"requests": 0, "approved": 0, "rejected": 0}
            
            by_symbol[symbol]["requests"] += 1
            by_module[module]["requests"] += 1
            
            if approved:
                valid_live += 1
                by_symbol[symbol]["approved"] += 1
                by_module[module]["approved"] += 1
            else:
                by_symbol[symbol]["rejected"] += 1
                by_module[module]["rejected"] += 1
                
                if failure and "stale" in failure.lower():
                    stale_blocked += 1
                elif is_fallback:
                    fallback_blocked += 1
                else:
                    invalid_rejected += 1
        
        # Set report values
        report.total_requests = total_requests
        report.valid_live_quotes = valid_live
        report.stale_quotes_blocked = stale_blocked
        report.invalid_quotes_rejected = invalid_rejected
        report.fallback_attempts_blocked = fallback_blocked
        report.by_symbol = by_symbol
        report.by_module = by_module
        report.provider_health = self._provider_health
        
        logger.info(f"Generated integrity report: {valid_live}/{total_requests} valid")
        
        return report
    
    def get_recent_failures(self, count: int = 10) -> List[dict]:
        """Get recent failed requests."""
        
        failures = [r for r in self._requests if not r["approved"]]
        return failures[-count:]


# Global instance
_auditor: Optional[PriceIntegrityAuditor] = None


def get_price_integrity_auditor() -> PriceIntegrityAuditor:
    """Get the price integrity auditor."""
    global _auditor
    
    if _auditor is None:
        _auditor = PriceIntegrityAuditor()
    
    return _auditor
