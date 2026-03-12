"""Tradeoff Engine - Evaluates tradeoffs when competing domains require attention."""
from typing import Optional
from datetime import datetime

from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    TradeoffDecision,
    TradeoffType,
    OptimizationPolicy,
)


class TradeoffEngine:
    """Evaluates tradeoffs between competing domain priorities."""
    
    def __init__(self):
        self._tradeoff_history: list[TradeoffDecision] = []
        self._active_conflicts: list[dict] = []
    
    def detect_conflicts(
        self,
        domain_metrics: list[DomainMetrics]
    ) -> list[dict]:
        """Detect potential conflicts between domains."""
        conflicts = []
        
        # Group domains by resource allocation
        high_resource = [dm for dm in domain_metrics if dm.resource_allocation > 35]
        low_resource = [dm for dm in domain_metrics if dm.resource_allocation < 15]
        
        # Check for resource imbalance
        if len(high_resource) > 3 and len(low_resource) > 2:
            conflicts.append({
                "type": "resource_imbalance",
                "description": f"Multiple domains over-allocated ({len(high_resource)}) vs under-allocated ({len(low_resource)})",
                "high_resource": [dm.domain for dm in high_resource],
                "low_resource": [dm.domain for dm in low_resource],
            })
        
        # Check for conflicting priorities
        for i, dm1 in enumerate(domain_metrics):
            for dm2 in domain_metrics[i+1:]:
                # High alignment but opposite momentum
                if (dm1.alignment_score > 7 and dm2.alignment_score > 7 and
                    dm1.momentum_score * dm2.momentum_score < 0):
                    conflicts.append({
                        "type": "momentum_conflict",
                        "description": f"Strategic alignment but opposite momentum",
                        "domains": [dm1.domain, dm2.domain],
                    })
                
                # One high risk, other high opportunity
                if dm1.risk_score > 7 and dm2.opportunity_score > 7:
                    conflicts.append({
                        "type": "risk_opportunity_tradeoff",
                        "description": "Risk mitigation vs opportunity capture",
                        "domains": [dm1.domain, dm2.domain],
                    })
        
        self._active_conflicts = conflicts
        return conflicts
    
    def resolve_tradeoff(
        self,
        domain_a: LifeDomain,
        domain_b: LifeDomain,
        metrics_a: DomainMetrics,
        metrics_b: DomainMetrics,
        policy: OptimizationPolicy
    ) -> TradeoffDecision:
        """Resolve a tradeoff between two domains."""
        
        # Determine tradeoff type
        tradeoff_type = self._classify_tradeoff(domain_a, domain_b)
        
        # Calculate scores for each domain
        score_a = self._calculate_domain_value(metrics_a, policy)
        score_b = self._calculate_domain_value(metrics_b, policy)
        
        # Determine winner and loser
        if score_a > score_b:
            winner = domain_a
            loser = domain_b
        else:
            winner = domain_b
            loser = domain_a
        
        # Calculate decision metrics
        long_term_impact = self._calculate_long_term_impact(
            winner, loser, metrics_a, metrics_b
        )
        risk_mitigation = self._calculate_risk_mitigation(
            winner, loser, metrics_a, metrics_b
        )
        sustainability = self._calculate_sustainability(
            winner, loser, metrics_a, metrics_b
        )
        energy_impact = self._calculate_energy_impact(
            winner, loser, metrics_a, metrics_b
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            tradeoff_type, winner, loser,
            score_a, score_b,
            long_term_impact, risk_mitigation, sustainability
        )
        
        decision = TradeoffDecision(
            tradeoff_type=tradeoff_type,
            domains_involved=[domain_a, domain_b],
            winner=winner,
            loser=loser,
            reasoning=reasoning,
            long_term_value_impact=long_term_impact,
            risk_mitigation_score=risk_mitigation,
            sustainability_score=sustainability,
            energy_impact=energy_impact,
            timestamp=datetime.utcnow()
        )
        
        self._tradeoff_history.append(decision)
        return decision
    
    def _classify_tradeoff(
        self,
        domain_a: LifeDomain,
        domain_b: LifeDomain
    ) -> TradeoffType:
        """Classify the type of tradeoff."""
        domain_pair = {domain_a, domain_b}
        
        if LifeDomain.CAREER in domain_pair and LifeDomain.HEALTH in domain_pair:
            return TradeoffType.CAREER_VS_HEALTH
        elif LifeDomain.WEALTH in domain_pair and LifeDomain.LEARNING in domain_pair:
            return TradeoffType.INCOME_VS_LEARNING
        elif LifeDomain.STRATEGIC_PROJECTS in domain_pair and LifeDomain.OPERATIONS in domain_pair:
            return TradeoffType.STRATEGIC_VS_OPERATIONAL
        elif LifeDomain.RELATIONSHIPS in domain_pair and LifeDomain.CAREER in domain_pair:
            return TradeoffType.RELATIONSHIPS_VS_WORKLOAD
        elif LifeDomain.WEALTH in domain_pair and LifeDomain.LEARNING in domain_pair:
            return TradeoffType.WEALTH_VS_TIME
        elif LifeDomain.PERSONAL_DEVELOPMENT in domain_pair and LifeDomain.CAREER in domain_pair:
            return TradeoffType.DEVELOPMENT_VS_EXECUTION
        else:
            # Generic tradeoff based on priority
            return TradeoffType.STRATEGIC_VS_OPERATIONAL
    
    def _calculate_domain_value(
        self,
        metrics: DomainMetrics,
        policy: OptimizationPolicy
    ) -> float:
        """Calculate the strategic value of a domain."""
        # Composite value considering policy weights
        value = (
            metrics.composite_score * 0.25 +
            metrics.opportunity_score * 0.20 *
                (1 if policy.risk_tolerance == "aggressive" else 0.8) +
            metrics.alignment_score * 0.25 +
            metrics.momentum_score * 0.10 +
            (10 - metrics.risk_score) * 0.20
        )
        
        # Boost for strategic priority
        value += (11 - metrics.strategic_priority) * 0.05
        
        return value
    
    def _calculate_long_term_impact(
        self,
        winner: LifeDomain,
        loser: LifeDomain,
        metrics_a: DomainMetrics,
        metrics_b: DomainMetrics
    ) -> float:
        """Calculate long-term value impact."""
        winner_metrics = metrics_a if metrics_a.domain == winner else metrics_b
        loser_metrics = metrics_a if metrics_a.domain == loser else metrics_b
        
        # Positive if winner has higher alignment and opportunity
        impact = (
            (winner_metrics.alignment_score - loser_metrics.alignment_score) * 0.1 +
            (winner_metrics.opportunity_score - loser_metrics.opportunity_score) * 0.1
        )
        
        return max(-1, min(1, impact))
    
    def _calculate_risk_mitigation(
        self,
        winner: LifeDomain,
        loser: LifeDomain,
        metrics_a: DomainMetrics,
        metrics_b: DomainMetrics
    ) -> float:
        """Calculate risk mitigation score."""
        winner_metrics = metrics_a if metrics_a.domain == winner else metrics_b
        loser_metrics = metrics_a if metrics_a.domain == loser else metrics_b
        
        # Higher if winner has lower risk
        return (10 - winner_metrics.risk_score) / 10
    
    def _calculate_sustainability(
        self,
        winner: LifeDomain,
        loser: LifeDomain,
        metrics_a: DomainMetrics,
        metrics_b: DomainMetrics
    ) -> float:
        """Calculate sustainability score."""
        winner_metrics = metrics_a if metrics_a.domain == winner else metrics_b
        loser_metrics = metrics_a if metrics_a.domain == loser else metrics_b
        
        # Higher if winner has positive momentum
        momentum_factor = 0.5 + (winner_metrics.momentum_score / 20)
        return max(0, min(1, momentum_factor))
    
    def _calculate_energy_impact(
        self,
        winner: LifeDomain,
        loser: LifeDomain,
        metrics_a: DomainMetrics,
        metrics_b: DomainMetrics
    ) -> float:
        """Calculate energy impact."""
        winner_metrics = metrics_a if metrics_a.domain == winner else metrics_b
        loser_metrics = metrics_a if metrics_a.domain == loser else metrics_b
        
        # Negative if winner requires high energy
        impact = -(winner_metrics.resource_allocation - loser_metrics.resource_allocation) / 100
        return max(-1, min(1, impact))
    
    def _generate_reasoning(
        self,
        tradeoff_type: TradeoffType,
        winner: LifeDomain,
        loser: LifeDomain,
        score_a: float,
        score_b: float,
        long_term_impact: float,
        risk_mitigation: float,
        sustainability: float
    ) -> str:
        """Generate reasoning for the tradeoff decision."""
        
        reasons = []
        
        # Score difference
        diff = abs(score_a - score_b)
        if diff > 1.0:
            reasons.append(f"significant score advantage ({diff:.2f})")
        
        # Long-term impact
        if long_term_impact > 0.2:
            reasons.append("strong long-term value creation")
        elif long_term_impact < -0.2:
            reasons.append("potential long-term value erosion")
        
        # Risk consideration
        if risk_mitigation > 0.7:
            reasons.append("favorable risk profile")
        
        # Sustainability
        if sustainability > 0.7:
            reasons.append("sustainable momentum")
        
        if not reasons:
            reasons.append("balanced tradeoffs")
        
        return (
            f"{winner.value.title()} prioritized over {loser.value.title()} due to: "
            f"{'; '.join(reasons)}. "
            f"Tradeoff type: {tradeoff_type.value}"
        )
    
    def resolve_all_tradeoffs(
        self,
        domain_metrics: list[DomainMetrics],
        policy: OptimizationPolicy
    ) -> list[TradeoffDecision]:
        """Resolve all detected tradeoffs."""
        decisions = []
        
        # Get all domain pairs
        for i, dm1 in enumerate(domain_metrics):
            for dm2 in domain_metrics[i+1:]:
                # Only process if there's significant difference
                if abs(dm1.composite_score - dm2.composite_score) > 1.0:
                    decision = self.resolve_tradeoff(
                        dm1.domain,
                        dm2.domain,
                        dm1,
                        dm2,
                        policy
                    )
                    decisions.append(decision)
        
        return decisions
    
    def get_active_tradeoffs(self) -> list[TradeoffType]:
        """Get currently active tradeoff types."""
        # Return unique tradeoff types from history
        return list(set(d.tradeoff_type for d in self._tradeoff_history[-10:]))
    
    def get_tradeoff_history(
        self,
        limit: int = 20
    ) -> list[TradeoffDecision]:
        """Get recent tradeoff history."""
        return self._tradeoff_history[-limit:]
    
    def get_tradeoff_statistics(self) -> dict:
        """Get tradeoff statistics."""
        if not self._tradeoff_history:
            return {
                "total_decisions": 0,
                "by_type": {},
                "win_distribution": {},
            }
        
        by_type = {}
        win_distribution = {}
        
        for decision in self._tradeoff_history:
            # Count by type
            ttype = decision.tradeoff_type.value
            by_type[ttype] = by_type.get(ttype, 0) + 1
            
            # Count wins
            if decision.winner:
                win_domain = decision.winner.value
                win_distribution[win_domain] = win_distribution.get(win_domain, 0) + 1
        
        return {
            "total_decisions": len(self._tradeoff_history),
            "by_type": by_type,
            "win_distribution": win_distribution,
        }
    
    def clear_history(self) -> None:
        """Clear tradeoff history (for testing)."""
        self._tradeoff_history.clear()
        self._active_conflicts.clear()


# Global tradeoff engine instance
_tradeoff_engine: Optional[TradeoffEngine] = None


def get_tradeoff_engine() -> TradeoffEngine:
    """Get the global tradeoff engine."""
    global _tradeoff_engine
    if _tradeoff_engine is None:
        _tradeoff_engine = TradeoffEngine()
    return _tradeoff_engine
