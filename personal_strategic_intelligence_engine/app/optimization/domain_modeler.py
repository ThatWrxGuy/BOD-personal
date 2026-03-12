"""Domain Modeler - Constructs structured representations of life domains."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    DomainDataInput,
)

logger = logging.getLogger(__name__)


class DomainModeler:
    """Constructs and manages life domain models."""
    
    def __init__(self):
        self._domain_cache: dict[LifeDomain, DomainMetrics] = {}
        self._last_update: Optional[datetime] = None
    
    def create_domain_metrics(
        self,
        domain: LifeDomain,
        data: DomainDataInput,
        strategic_priority: int = 5
    ) -> DomainMetrics:
        """Create domain metrics from input data."""
        
        # Calculate performance score (0-10)
        performance = self._calculate_performance_score(data)
        
        # Calculate risk score (0-10)
        risk = self._calculate_risk_score(data)
        
        # Calculate opportunity score (0-10)
        opportunity = self._calculate_opportunity_score(data)
        
        # Calculate momentum score (-10 to 10)
        momentum = self._calculate_momentum_score(data)
        
        # Calculate alignment score (0-10)
        alignment = self._calculate_alignment_score(data)
        
        # Calculate resource allocation (0-100%)
        resources = self._calculate_resource_allocation(data)
        
        metrics = DomainMetrics(
            domain=domain,
            performance_score=performance,
            risk_score=risk,
            opportunity_score=opportunity,
            momentum_score=momentum,
            alignment_score=alignment,
            resource_allocation=resources,
            strategic_priority=strategic_priority,
        )
        
        self._domain_cache[domain] = metrics
        self._last_update = datetime.utcnow()
        
        return metrics
    
    def _calculate_performance_score(self, data: DomainDataInput) -> float:
        """Calculate performance score from input data."""
        score = 5.0  # Base score
        
        # Goal progress contribution
        if data.goal_progress > 0:
            score += data.goal_progress * 3
        
        # Task completion contribution
        score += data.task_completion_rate * 2
        
        # Quality indicators
        if data.quality_indicators:
            avg_quality = sum(data.quality_indicators) / len(data.quality_indicators)
            score += avg_quality * 2
        
        return min(10.0, max(0.0, score))
    
    def _calculate_risk_score(self, data: DomainDataInput) -> float:
        """Calculate risk score from input data."""
        score = 2.0  # Base low risk
        
        # Threat indicators
        if data.threat_indicators:
            avg_threat = sum(data.threat_indicators) / len(data.threat_indicators)
            score += avg_threat * 5
        
        # Vulnerability contribution
        score += data.vulnerability_score * 3
        
        return min(10.0, max(0.0, score))
    
    def _calculate_opportunity_score(self, data: DomainDataInput) -> float:
        """Calculate opportunity score from input data."""
        score = 3.0  # Base score
        
        # Opportunity indicators
        if data.opportunity_indicators:
            avg_opp = sum(data.opportunity_indicators) / len(data.opportunity_indicators)
            score += avg_opp * 4
        
        # Market timing contribution
        score += data.market_timing * 3
        
        return min(10.0, max(0.0, score))
    
    def _calculate_momentum_score(self, data: DomainDataInput) -> float:
        """Calculate momentum score from input data."""
        # Recent progress and trend direction averaged
        momentum = (data.recent_progress * 5) + (data.trend_direction * 5)
        return min(10.0, max(-10.0, momentum))
    
    def _calculate_alignment_score(self, data: DomainDataInput) -> float:
        """Calculate alignment score from input data."""
        score = 5.0
        
        # Strategic alignment
        score += data.strategic_alignment * 3
        
        # Goal alignment
        score += data.goal_alignment * 2
        
        return min(10.0, max(0.0, score))
    
    def _calculate_resource_allocation(self, data: DomainDataInput) -> float:
        """Calculate resource allocation percentage."""
        # Time-based calculation normalized
        time_weight = min(data.time_invested_hours / 40, 1.0) * 50  # Max 50 points for time
        energy_weight = data.energy_invested * 30  # Max 30 points for energy
        financial_weight = min(data.financial_investment / 1000, 1.0) * 20  # Max 20 for financial
        
        return min(100.0, time_weight + energy_weight + financial_weight)
    
    def create_default_domain_metrics(
        self,
        domain: LifeDomain,
        strategic_priority: int = 5
    ) -> DomainMetrics:
        """Create default domain metrics when no data is available."""
        return DomainMetrics(
            domain=domain,
            performance_score=5.0,
            risk_score=3.0,
            opportunity_score=5.0,
            momentum_score=0.0,
            alignment_score=5.0,
            resource_allocation=12.5,  # Equal split for 8 domains
            strategic_priority=strategic_priority,
        )
    
    def get_all_domain_metrics(self) -> list[DomainMetrics]:
        """Get all cached domain metrics."""
        if not self._domain_cache:
            # Initialize with defaults
            self._initialize_default_domains()
        return list(self._domain_cache.values())
    
    def get_domain_metrics(self, domain: LifeDomain) -> DomainMetrics:
        """Get metrics for a specific domain."""
        if domain not in self._domain_cache:
            self._domain_cache[domain] = self.create_default_domain_metrics(domain)
        return self._domain_cache[domain]
    
    def update_domain_metrics(
        self,
        domain: LifeDomain,
        data: DomainDataInput
    ) -> DomainMetrics:
        """Update existing domain metrics with new data."""
        current = self.get_domain_metrics(domain)
        return self.create_domain_metrics(
            domain=domain,
            data=data,
            strategic_priority=current.strategic_priority
        )
    
    def _initialize_default_domains(self) -> None:
        """Initialize all domains with default metrics."""
        priorities = {
            LifeDomain.HEALTH: 1,
            LifeDomain.WEALTH: 2,
            LifeDomain.CAREER: 3,
            LifeDomain.LEARNING: 4,
            LifeDomain.RELATIONSHIPS: 5,
            LifeDomain.PERSONAL_DEVELOPMENT: 6,
            LifeDomain.OPERATIONS: 7,
            LifeDomain.STRATEGIC_PROJECTS: 8,
        }
        
        for domain in LifeDomain:
            self._domain_cache[domain] = self.create_default_domain_metrics(
                domain=domain,
                strategic_priority=priorities.get(domain, 5)
            )
    
    def reset_domain(self, domain: LifeDomain) -> None:
        """Reset a domain to default metrics."""
        if domain in self._domain_cache:
            del self._domain_cache[domain]
    
    def reset_all_domains(self) -> None:
        """Reset all domains to defaults."""
        self._domain_cache.clear()
        self._initialize_default_domains()
    
    def get_cache_status(self) -> dict:
        """Get the current cache status."""
        return {
            "cached_domains": len(self._domain_cache),
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "domains": [d.value for d in self._domain_cache.keys()],
        }


# Global modeler instance
_domain_modeler: Optional[DomainModeler] = None


def get_domain_modeler() -> DomainModeler:
    """Get the global domain modeler."""
    global _domain_modeler
    if _domain_modeler is None:
        _domain_modeler = DomainModeler()
    return _domain_modeler
