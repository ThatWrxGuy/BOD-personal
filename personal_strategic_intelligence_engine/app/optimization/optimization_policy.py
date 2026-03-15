"""Optimization Policy - Defines optimization constraints, rules, and safeguards."""
from typing import Optional
from datetime import datetime, timedelta

from app.optimization.optimization_types import (
    LifeDomain,
    OptimizationPolicy,
    OptimizationAction,
    OptimizationActionRecommendation,
    DomainMetrics,
    DomainConditionResult,
    TradeoffDecision,
)


class OptimizationPolicyEngine:
    """Enforces policy constraints on optimization decisions."""
    
    def __init__(self, policy: Optional[OptimizationPolicy] = None):
        self._policy = policy or OptimizationPolicy()
        self._last_adjustments: dict[LifeDomain, datetime] = {}
        self._action_cooldown: dict[LifeDomain, datetime] = {}
    
    @property
    def policy(self) -> OptimizationPolicy:
        """Get current policy."""
        return self._policy
    
    def update_policy(self, policy: OptimizationPolicy) -> None:
        """Update the optimization policy."""
        self._policy = policy
    
    def can_adjust_domain(self, domain: LifeDomain) -> bool:
        """Check if a domain can be adjusted (respects cooldown)."""
        if domain not in self._action_cooldown:
            return True
        
        cooldown_end = self._action_cooldown[domain] + timedelta(
            hours=self._policy.recovery_period_hours
        )
        return datetime.utcnow() >= cooldown_end
    
    def record_domain_adjustment(self, domain: LifeDomain) -> None:
        """Record when a domain was last adjusted."""
        self._last_adjustments[domain] = datetime.utcnow()
        self._action_cooldown[domain] = datetime.utcnow()
    
    def get_adjustment_cooldown_remaining(self, domain: LifeDomain) -> float:
        """Get remaining cooldown hours for domain adjustment."""
        if domain not in self._action_cooldown:
            return 0.0
        
        cooldown_end = self._action_cooldown[domain] + timedelta(
            hours=self._policy.recovery_period_hours
        )
        remaining = (cooldown_end - datetime.utcnow()).total_seconds() / 3600
        return max(0.0, remaining)
    
    def validate_action(
        self,
        action: OptimizationAction,
        target_domain: LifeDomain,
        current_metrics: DomainMetrics,
        conditions: list[DomainConditionResult]
    ) -> tuple[bool, str]:
        """Validate if an action is allowed under current policy."""
        
        # Check domain cooldown
        if not self.can_adjust_domain(target_domain):
            remaining = self.get_adjustment_cooldown_remaining(target_domain)
            return False, f"Domain {target_domain.value} is in cooldown period ({remaining:.1f}h remaining)"
        
        # Check if action would violate min/max score constraints
        if action == OptimizationAction.INCREASE_PRIORITY:
            if current_metrics.composite_score >= self._policy.max_domain_score:
                return False, f"Domain {target_domain.value} already at max score"
        
        elif action == OptimizationAction.DECREASE_PRIORITY:
            if current_metrics.composite_score <= self._policy.min_domain_score:
                return False, f"Domain {target_domain.value} already at min score"
        
        # Check daily shift limit
        today_adjustments = sum(
            1 for dt in self._last_adjustments.values()
            if dt.date() == datetime.utcnow().date()
        )
        if today_adjustments >= self._policy.max_daily_domain_shifts:
            return False, f"Daily adjustment limit reached ({self._policy.max_daily_domain_shifts})"
        
        # Check for critical domains (health should never be neglected)
        if target_domain == LifeDomain.HEALTH:
            condition = next(
                (c for c in conditions if c.domain == LifeDomain.HEALTH),
                None
            )
            if condition and condition.condition.value in ["neglected", "critical"]:
                return False, "Health domain cannot be neglected - safety constraint"
        
        return True, "Action validated"
    
    def apply_policy_to_recommendation(
        self,
        recommendation: OptimizationActionRecommendation,
        current_metrics: DomainMetrics,
        conditions: list[DomainConditionResult]
    ) -> OptimizationActionRecommendation:
        """Apply policy constraints to a recommendation."""
        
        is_valid, reason = self.validate_action(
            recommendation.action,
            recommendation.target_domain,
            current_metrics,
            conditions
        )
        
        if not is_valid:
            # Convert to maintain status quo if invalid
            return OptimizationActionRecommendation(
                action=OptimizationAction.MAINTAIN_STATUS_QUO,
                target_domain=recommendation.target_domain,
                priority=recommendation.priority,
                reasoning=f"Original action blocked by policy: {reason}",
                expected_impact=0.0,
                confidence=0.0,
                policy_constraints_respected=True,
            )
        
        return OptimizationActionRecommendation(
            **recommendation.model_dump(),
            policy_constraints_respected=True,
        )
    
    def apply_policy_to_tradeoff(
        self,
        tradeoff: TradeoffDecision,
        all_metrics: list[DomainMetrics]
    ) -> TradeoffDecision:
        """Apply policy constraints to a tradeoff decision."""
        
        # Ensure critical domains aren't severely impacted
        critical_domains = {LifeDomain.HEALTH, LifeDomain.WEALTH}
        
        if tradeoff.loser in critical_domains:
            # Check if the impact would violate policy
            loser_metrics = next(
                (m for m in all_metrics if m.domain == tradeoff.loser),
                None
            )
            if loser_metrics and loser_metrics.composite_score < self._policy.min_domain_score:
                # Override the tradeoff to protect critical domain
                return TradeoffDecision(
                    tradeoff_type=tradeoff.tradeoff_type,
                    domains_involved=tradeoff.domains_involved,
                    winner=tradeoff.loser,  # Flip the decision
                    loser=tradeoff.winner,
                    reasoning=f"Policy protection: {tradeoff.loser.value} below minimum threshold",
                    long_term_value_impact=tradeoff.long_term_value_impact * -0.5,
                    risk_mitigation_score=1.0,
                    sustainability_score=1.0,
                    energy_impact=0.0,
                )
        
        return tradeoff
    
    def calculate_risk_tolerance_factor(self) -> float:
        """Calculate the risk tolerance factor based on policy."""
        tolerance_map = {
            "conservative": 0.3,
            "moderate": 0.5,
            "aggressive": 0.8,
        }
        return tolerance_map.get(self._policy.risk_tolerance, 0.5)
    
    def get_weighted_objective(
        self,
        sustainability_score: float,
        long_term_score: float,
        energy_score: float
    ) -> float:
        """Calculate weighted objective value based on policy weights."""
        return (
            sustainability_score * self._policy.sustainability_weight +
            long_term_score * self._policy.long_term_weight +
            energy_score * self._policy.energy_constraint_factor
        )
    
    def should_auto_rebalance(self) -> bool:
        """Check if automatic rebalancing is enabled."""
        return self._policy.enable_automatic_rebalancing
    
    def get_policy_status(self) -> dict:
        """Get current policy status."""
        return {
            "policy": self._policy.model_dump(),
            "cooldowns": {
                domain.value: self.get_adjustment_cooldown_remaining(domain)
                for domain in LifeDomain
            },
            "recent_adjustments": {
                domain.value: dt.isoformat()
                for domain, dt in self._last_adjustments.items()
            },
        }
    
    def reset_cooldowns(self) -> None:
        """Reset all cooldowns (for testing)."""
        self._action_cooldown.clear()
        self._last_adjustments.clear()


# Global policy engine instance
_policy_engine: Optional[OptimizationPolicyEngine] = None


def get_optimization_policy_engine() -> OptimizationPolicyEngine:
    """Get the global policy engine."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = OptimizationPolicyEngine()
    return _policy_engine
