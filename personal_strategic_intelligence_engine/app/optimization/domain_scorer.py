"""Domain Scorer - Calculates performance scores and health metrics for each domain."""
from typing import Optional
from datetime import datetime

from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    DomainCondition,
    DomainConditionResult,
)


class DomainScorer:
    """Calculates scores and health metrics for life domains."""
    
    def __init__(self):
        self._score_history: dict[LifeDomain, list[float]] = {
            domain: [] for domain in LifeDomain
        }
    
    def score_domain(self, metrics: DomainMetrics) -> float:
        """Calculate the composite score for a domain."""
        return metrics.composite_score
    
    def score_all_domains(self, domain_metrics: list[DomainMetrics]) -> dict[LifeDomain, float]:
        """Score all domains and return as dictionary."""
        return {dm.domain: self.score_domain(dm) for dm in domain_metrics}
    
    def detect_domain_condition(
        self,
        metrics: DomainMetrics,
        policy_neglect_threshold: float = 3.5,
        policy_overinvest_threshold: float = 8.0
    ) -> DomainConditionResult:
        """Detect the current condition of a domain."""
        composite = metrics.composite_score
        risk = metrics.risk_score
        opportunity = metrics.opportunity_score
        momentum = metrics.momentum_score
        resource_alloc = metrics.resource_allocation
        
        evidence = []
        condition = DomainCondition.HEALTHY
        severity = 0.0
        
        # Check for neglect (low score + low resources)
        if composite < policy_neglect_threshold and resource_alloc < 20:
            condition = DomainCondition.NEGLECTED
            severity = 1.0 - (composite / policy_neglect_threshold)
            evidence.append(f"Low composite score ({composite:.2f}) with minimal resources ({resource_alloc:.1f}%)")
        
        # Check for overinvestment (high score but diminishing returns)
        elif composite > policy_overinvest_threshold and resource_alloc > 40:
            condition = DomainCondition.OVERINVESTED
            severity = min(1.0, (composite - 7.0) / 2.0)
            evidence.append(f"High score ({composite:.2f}) with heavy resource allocation ({resource_alloc:.1f}%)")
        
        # Check for instability (high momentum variance)
        elif abs(momentum) > 6:
            condition = DomainCondition.UNSTABLE
            severity = abs(momentum) / 10.0
            evidence.append(f"High momentum change ({momentum:.2f}) indicating instability")
        
        # Check for opportunity window (high opportunity + good momentum)
        elif opportunity > 7 and momentum > 3:
            condition = DomainCondition.OPPORTUNITY_WINDOW
            severity = (opportunity - 7) / 3.0
            evidence.append(f"Strong opportunity ({opportunity:.2f}) with positive momentum ({momentum:.2f})")
        
        # Check for risk escalation
        elif risk > 7:
            condition = DomainCondition.RISK_ESCALATION
            severity = (risk - 7) / 3.0
            evidence.append(f"Elevated risk exposure ({risk:.2f})")
        
        # Check for strategic imbalance
        elif composite < 4 and metrics.alignment_score > 7:
            condition = DomainCondition.STRATEGIC_IMBALANCE
            severity = 0.7
            evidence.append(f"Low performance ({composite:.2f}) despite high strategic alignment ({metrics.alignment_score:.2f})")
        
        # Healthy state
        else:
            condition = DomainCondition.HEALTHY
            severity = 0.0
            evidence.append(f"Domain is healthy with balanced metrics")
        
        return DomainConditionResult(
            domain=metrics.domain,
            condition=condition,
            severity=min(1.0, severity),
            evidence=evidence,
            timestamp=datetime.utcnow()
        )
    
    def detect_all_conditions(
        self,
        domain_metrics: list[DomainMetrics],
        policy_neglect_threshold: float = 3.5,
        policy_overinvest_threshold: float = 8.0
    ) -> list[DomainConditionResult]:
        """Detect conditions for all domains."""
        return [
            self.detect_domain_condition(
                dm,
                policy_neglect_threshold,
                policy_overinvest_threshold
            )
            for dm in domain_metrics
        ]
    
    def calculate_domain_health(
        self,
        domain_metrics: list[DomainMetrics]
    ) -> float:
        """Calculate overall domain health (0-10)."""
        if not domain_metrics:
            return 0.0
        
        # Weight by strategic priority (higher priority = more weight)
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dm in domain_metrics:
            # Inverse priority: priority 1 gets weight 10, priority 10 gets weight 1
            weight = 11 - dm.strategic_priority
            weighted_sum += dm.composite_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 5.0
    
    def calculate_balance_score(
        self,
        domain_metrics: list[DomainMetrics]
    ) -> float:
        """Calculate how balanced the domains are (0-10)."""
        if not domain_metrics:
            return 0.0
        
        scores = [dm.composite_score for dm in domain_metrics]
        
        # Calculate standard deviation
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to balance score (lower deviation = higher balance)
        # Max std_dev of 10 gives score of 0, std_dev of 0 gives score of 10
        balance = max(0, 10 - std_dev)
        
        return balance
    
    def calculate_opportunity_potential(
        self,
        domain_metrics: list[DomainMetrics]
    ) -> list[tuple[LifeDomain, float]]:
        """Calculate opportunity potential for each domain."""
        potentials = []
        
        for dm in domain_metrics:
            # Opportunity potential = opportunity score * momentum (positive momentum boosts)
            potential = dm.opportunity_score
            if dm.momentum_score > 0:
                potential *= (1 + dm.momentum_score / 10)
            potentials.append((dm.domain, min(10.0, potential)))
        
        return sorted(potentials, key=lambda x: x[1], reverse=True)
    
    def identify_domains_needing_attention(
        self,
        domain_metrics: list[DomainMetrics],
        policy_neglect_threshold: float = 3.5
    ) -> list[LifeDomain]:
        """Identify domains that need immediate attention."""
        needs_attention = []
        
        for dm in domain_metrics:
            if dm.composite_score < policy_neglect_threshold:
                needs_attention.append(dm.domain)
            elif dm.risk_score > 7:
                needs_attention.append(dm.domain)
            elif dm.momentum_score < -5:
                needs_attention.append(dm.domain)
        
        return needs_attention
    
    def normalize_scores(
        self,
        domain_metrics: list[DomainMetrics]
    ) -> list[DomainMetrics]:
        """Normalize all domain scores to ensure consistency."""
        if not domain_metrics:
            return []
        
        # Ensure all scores are within bounds
        normalized = []
        for dm in domain_metrics:
            normalized_dm = DomainMetrics(
                domain=dm.domain,
                performance_score=max(0, min(10, dm.performance_score)),
                risk_score=max(0, min(10, dm.risk_score)),
                opportunity_score=max(0, min(10, dm.opportunity_score)),
                momentum_score=max(-10, min(10, dm.momentum_score)),
                alignment_score=max(0, min(10, dm.alignment_score)),
                resource_allocation=max(0, min(100, dm.resource_allocation)),
                strategic_priority=max(1, min(10, dm.strategic_priority)),
            )
            normalized.append(normalized_dm)
        
        return normalized
    
    def record_score_history(
        self,
        domain: LifeDomain,
        score: float
    ) -> None:
        """Record a score for historical tracking."""
        if domain in self._score_history:
            self._score_history[domain].append(score)
            # Keep only last 100 scores
            if len(self._score_history[domain]) > 100:
                self._score_history[domain] = self._score_history[domain][-100:]
    
    def get_score_trend(
        self,
        domain: LifeDomain,
        window: int = 10
    ) -> float:
        """Get the score trend for a domain over recent cycles."""
        if domain not in self._score_history or not self._score_history[domain]:
            return 0.0
        
        recent = self._score_history[domain][-window:]
        if len(recent) < 2:
            return 0.0
        
        # Calculate simple trend
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        
        return (sum(second_half) / len(second_half)) - (sum(first_half) / len(first_half))
    
    def get_detailed_domain_report(
        self,
        metrics: DomainMetrics
    ) -> dict:
        """Generate a detailed report for a single domain."""
        condition = self.detect_domain_condition(metrics)
        
        return {
            "domain": metrics.domain.value,
            "composite_score": round(metrics.composite_score, 2),
            "health_status": metrics.health_status,
            "condition": condition.condition.value,
            "condition_severity": round(condition.severity, 2),
            "condition_evidence": condition.evidence,
            "metrics": {
                "performance": round(metrics.performance_score, 2),
                "risk": round(metrics.risk_score, 2),
                "opportunity": round(metrics.opportunity_score, 2),
                "momentum": round(metrics.momentum_score, 2),
                "alignment": round(metrics.alignment_score, 2),
                "resource_allocation": round(metrics.resource_allocation, 1),
                "strategic_priority": metrics.strategic_priority,
            },
            "recommendations": self._generate_domain_recommendations(metrics, condition),
        }
    
    def _generate_domain_recommendations(
        self,
        metrics: DomainMetrics,
        condition: DomainConditionResult
    ) -> list[str]:
        """Generate recommendations based on domain condition."""
        recommendations = []
        
        if condition.condition == DomainCondition.NEGLECTED:
            recommendations.append(f"Increase resource allocation to {metrics.domain.value}")
            recommendations.append("Review and reset domain goals")
        
        elif condition.condition == DomainCondition.OVERINVESTED:
            recommendations.append("Consider reallocating resources to other domains")
            recommendations.append("Focus on maintenance rather than expansion")
        
        elif condition.condition == DomainCondition.UNSTABLE:
            recommendations.append("Stabilize domain with consistent actions")
            recommendations.append("Review what's causing the volatility")
        
        elif condition.condition == DomainCondition.OPPORTUNITY_WINDOW:
            recommendations.append("Capitalize on current opportunity")
            recommendations.append("Increase focus temporarily")
        
        elif condition.condition == DomainCondition.RISK_ESCALATION:
            recommendations.append("Implement risk mitigation measures")
            recommendations.append("Review threat sources")
        
        elif condition.condition == DomainCondition.STRATEGIC_IMBALANCE:
            recommendations.append("Address execution blockers")
            recommendations.append("Realign domain with strategic goals")
        
        return recommendations


# Global scorer instance
_domain_scorer: Optional[DomainScorer] = None


def get_domain_scorer() -> DomainScorer:
    """Get the global domain scorer."""
    global _domain_scorer
    if _domain_scorer is None:
        _domain_scorer = DomainScorer()
    return _domain_scorer
