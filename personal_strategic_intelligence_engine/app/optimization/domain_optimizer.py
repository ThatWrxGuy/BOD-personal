"""Domain Optimizer - Determines how resources should shift between domains."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    OptimizationAction,
    OptimizationActionRecommendation,
    DomainConditionResult,
    TradeoffDecision,
    OptimizationCycle,
    OptimizationPolicy,
)
from app.optimization.domain_modeler import get_domain_modeler
from app.optimization.domain_scorer import get_domain_scorer
from app.optimization.tradeoff_engine import get_tradeoff_engine
from app.optimization.optimization_policy import get_optimization_policy_engine
from app.optimization.optimization_logger import get_optimization_logger

logger = logging.getLogger(__name__)


class DomainOptimizer:
    """Main optimizer that determines resource allocation between domains."""
    
    def __init__(self):
        self.modeler = get_domain_modeler()
        self.scorer = get_domain_scorer()
        self.tradeoff_engine = get_tradeoff_engine()
        self.policy_engine = get_optimization_policy_engine()
        self.logger = get_optimization_logger()
    
    def run_optimization_cycle(
        self,
        domain_metrics: Optional[list[DomainMetrics]] = None
    ) -> OptimizationCycle:
        """Run a complete optimization cycle."""
        
        cycle_id = str(uuid.uuid4())[:8]
        
        try:
            # Step 1: Collect domain data
            if domain_metrics is None:
                domain_metrics = self.modeler.get_all_domain_metrics()
            
            # Step 2: Score domains
            scores = self.scorer.score_all_domains(domain_metrics)
            
            # Step 3: Detect domain imbalances
            conditions = self.scorer.detect_all_conditions(
                domain_metrics,
                self.policy_engine.policy.neglect_threshold,
                self.policy_engine.policy.overinvest_threshold
            )
            
            # Step 4: Evaluate tradeoffs
            tradeoffs = self.tradeoff_engine.resolve_all_tradeoffs(
                domain_metrics,
                self.policy_engine.policy
            )
            
            # Step 5: Generate optimization actions
            recommendations = self._generate_recommendations(
                domain_metrics, conditions, tradeoffs
            )
            
            # Step 6: Apply policy constraints
            recommendations = self._apply_policy_constraints(
                recommendations, domain_metrics, conditions
            )
            
            # Step 7: Calculate overall balance
            overall_balance = self.scorer.calculate_balance_score(domain_metrics)
            
            # Step 8: Record cycle
            cycle = OptimizationCycle(
                cycle_id=cycle_id,
                timestamp=datetime.utcnow(),
                domain_metrics=domain_metrics,
                detected_conditions=conditions,
                tradeoff_decisions=tradeoffs,
                recommendations=recommendations,
                overall_balance_score=overall_balance,
                optimization_applied=len(recommendations) > 0,
                execution_status="completed"
            )
            
            self.logger.record_cycle(cycle)
            
            # Log key decisions
            for condition in conditions:
                self.logger.log_condition(condition)
            for tradeoff in tradeoffs:
                self.logger.log_tradeoff(tradeoff)
            for rec in recommendations:
                self.logger.log_recommendation(rec)
            
            return cycle
            
        except Exception as e:
            return OptimizationCycle(
                cycle_id=cycle_id,
                timestamp=datetime.utcnow(),
                domain_metrics=domain_metrics or [],
                detected_conditions=[],
                tradeoff_decisions=[],
                recommendations=[],
                overall_balance_score=0.0,
                optimization_applied=False,
                execution_status="failed",
                error_message=str(e)
            )
    
    def _generate_recommendations(
        self,
        domain_metrics: list[DomainMetrics],
        conditions: list[DomainConditionResult],
        tradeoffs: list[TradeoffDecision]
    ) -> list[OptimizationActionRecommendation]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        # Process each domain condition
        for condition in conditions:
            if condition.condition.value == "neglected":
                rec = self._recommend_neglected_domain(condition)
                if rec:
                    recommendations.append(rec)
            
            elif condition.condition.value == "overinvested":
                rec = self._recommend_overinvested_domain(condition)
                if rec:
                    recommendations.append(rec)
            
            elif condition.condition.value == "opportunity_window":
                rec = self._recommend_opportunity_window(condition)
                if rec:
                    recommendations.append(rec)
            
            elif condition.condition.value == "risk_escalation":
                rec = self._recommend_risk_escalation(condition)
                if rec:
                    recommendations.append(rec)
            
            elif condition.condition.value == "unstable":
                rec = self._recommend_unstable_domain(condition)
                if rec:
                    recommendations.append(rec)
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations[:10]  # Limit to top 10
    
    def _recommend_neglected_domain(
        self,
        condition: DomainConditionResult
    ) -> Optional[OptimizationActionRecommendation]:
        """Recommend action for neglected domain."""
        
        if condition.domain == LifeDomain.HEALTH:
            return OptimizationActionRecommendation(
                action=OptimizationAction.INCREASE_PRIORITY,
                target_domain=condition.domain,
                priority=1,
                reasoning=f"Health domain neglected - immediate recovery needed",
                expected_impact=0.8,
                confidence=0.9,
            )
        
        return OptimizationActionRecommendation(
            action=OptimizationAction.INCREASE_PRIORITY,
            target_domain=condition.domain,
            priority=3,
            reasoning=f"Domain neglected: {condition.evidence[0] if condition.evidence else 'low scores'}",
            expected_impact=0.6,
            confidence=0.7,
        )
    
    def _recommend_overinvested_domain(
        self,
        condition: DomainConditionResult
    ) -> Optional[OptimizationActionRecommendation]:
        """Recommend action for overinvested domain."""
        
        return OptimizationActionRecommendation(
            action=OptimizationAction.DECREASE_PRIORITY,
            target_domain=condition.domain,
            priority=6,
            reasoning=f"Domain overinvested: {condition.evidence[0] if condition.evidence else 'high allocation'}",
            expected_impact=-0.3,
            confidence=0.6,
        )
    
    def _recommend_opportunity_window(
        self,
        condition: DomainConditionResult
    ) -> Optional[OptimizationActionRecommendation]:
        """Recommend action for opportunity window."""
        
        return OptimizationActionRecommendation(
            action=OptimizationAction.ESCALATE_TO_STRATEGIC,
            target_domain=condition.domain,
            priority=2,
            reasoning=f"Opportunity window detected: {condition.evidence[0] if condition.evidence else 'high opportunity'}",
            expected_impact=0.7,
            confidence=0.8,
        )
    
    def _recommend_risk_escalation(
        self,
        condition: DomainConditionResult
    ) -> Optional[OptimizationActionRecommendation]:
        """Recommend action for risk escalation."""
        
        if condition.domain in [LifeDomain.HEALTH, LifeDomain.WEALTH]:
            priority = 1
        else:
            priority = 4
        
        return OptimizationActionRecommendation(
            action=OptimizationAction.TRIGGER_HABIT_INTERVENTION,
            target_domain=condition.domain,
            priority=priority,
            reasoning=f"Risk escalation: {condition.evidence[0] if condition.evidence else 'elevated risk'}",
            expected_impact=0.5,
            confidence=0.7,
        )
    
    def _recommend_unstable_domain(
        self,
        condition: DomainConditionResult
    ) -> Optional[OptimizationActionRecommendation]:
        """Recommend action for unstable domain."""
        
        return OptimizationActionRecommendation(
            action=OptimizationAction.INTRODUCE_RECOVERY,
            target_domain=condition.domain,
            priority=5,
            reasoning=f"Domain unstable: {condition.evidence[0] if condition.evidence else 'high volatility'}",
            expected_impact=0.4,
            confidence=0.5,
        )
    
    def _apply_policy_constraints(
        self,
        recommendations: list[OptimizationActionRecommendation],
        domain_metrics: list[DomainMetrics],
        conditions: list[DomainConditionResult]
    ) -> list[OptimizationActionRecommendation]:
        """Apply policy constraints to recommendations."""
        
        constrained = []
        
        for rec in recommendations:
            metrics = next(
                (m for m in domain_metrics if m.domain == rec.target_domain),
                None
            )
            
            if metrics:
                constrained_rec = self.policy_engine.apply_policy_to_recommendation(
                    rec, metrics, conditions
                )
                constrained.append(constrained_rec)
            else:
                constrained.append(rec)
        
        # Filter out maintain_status_quo if there are better options
        active = [r for r in constrained if r.action != OptimizationAction.MAINTAIN_STATUS_QUO]
        
        if not active and constrained:
            # If all blocked, keep highest priority
            constrained.sort(key=lambda r: r.priority)
            return [constrained[0]]
        
        return active
    
    def apply_optimization(
        self,
        cycle: OptimizationCycle
    ) -> dict:
        """Apply the optimization recommendations."""
        
        if not cycle.optimization_applied:
            return {
                "status": "no_optimization_needed",
                "message": "No recommendations to apply"
            }
        
        applied = []
        failed = []
        
        for rec in cycle.recommendations:
            try:
                # Record the adjustment
                self.policy_engine.record_domain_adjustment(rec.target_domain)
                
                # Update domain model
                metrics = next(
                    (m for m in cycle.domain_metrics if m.domain == rec.target_domain),
                    None
                )
                
                if metrics:
                    # Adjust strategic priority based on action
                    if rec.action == OptimizationAction.INCREASE_PRIORITY:
                        new_priority = max(1, metrics.strategic_priority - 1)
                    elif rec.action == OptimizationAction.DECREASE_PRIORITY:
                        new_priority = min(10, metrics.strategic_priority + 1)
                    else:
                        new_priority = metrics.strategic_priority
                    
                    applied.append({
                        "domain": rec.target_domain.value,
                        "action": rec.action.value,
                        "new_priority": new_priority,
                    })
                    
            except Exception as e:
                failed.append({
                    "domain": rec.target_domain.value,
                    "action": rec.action.value,
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "applied": applied,
            "failed": failed,
        }
    
    def calculate_domain_shifts(
        self,
        current_metrics: list[DomainMetrics],
        target_metrics: list[DomainMetrics]
    ) -> list[dict]:
        """Calculate how resources should shift between domains."""
        shifts = []
        
        current_dict = {m.domain: m for m in current_metrics}
        target_dict = {m.domain: m for m in target_metrics}
        
        for domain in LifeDomain:
            current = current_dict.get(domain)
            target = target_dict.get(domain)
            
            if current and target:
                resource_diff = target.resource_allocation - current.resource_allocation
                priority_diff = target.strategic_priority - current.strategic_priority
                
                if abs(resource_diff) > 1 or abs(priority_diff) > 0:
                    shifts.append({
                        "domain": domain.value,
                        "resource_shift_percent": round(resource_diff, 1),
                        "priority_change": priority_diff,
                        "reasoning": self._generate_shift_reasoning(domain, resource_diff, priority_diff),
                    })
        
        return shifts
    
    def _generate_shift_reasoning(
        self,
        domain: LifeDomain,
        resource_diff: float,
        priority_diff: int
    ) -> str:
        """Generate reasoning for a domain shift."""
        
        if resource_diff > 5:
            return f"Increase resource allocation by {resource_diff:.1f}%"
        elif resource_diff < -5:
            return f"Decrease resource allocation by {abs(resource_diff):.1f}%"
        
        if priority_diff < 0:
            return f"Raise strategic priority by {abs(priority_diff)} levels"
        elif priority_diff > 0:
            return f"Lower strategic priority by {priority_diff} levels"
        
        return "Maintain current allocation"
    
    def get_optimization_summary(self) -> dict:
        """Get summary of current optimization state."""
        
        metrics = self.modeler.get_all_domain_metrics()
        
        if not metrics:
            return {
                "overall_health": 0.0,
                "balance_score": 0.0,
                "domains_needing_attention": [],
                "top_opportunities": [],
                "active_tradeoffs": [],
                "pending_recommendations": 0,
            }
        
        health = self.scorer.calculate_domain_health(metrics)
        balance = self.scorer.calculate_balance_score(metrics)
        
        needs_attention = self.scorer.identify_domains_needing_attention(
            metrics,
            self.policy_engine.policy.neglect_threshold
        )
        
        opportunities = self.scorer.calculate_opportunity_potential(metrics)
        top_opportunities = [opp[0] for opp in opportunities[:3]]
        
        tradeoffs = self.tradeoff_engine.get_active_tradeoffs()
        
        # Get latest cycle recommendations
        latest_cycle = self.logger.get_latest_cycle()
        pending = len(latest_cycle.recommendations) if latest_cycle else 0
        
        return {
            "overall_health": round(health, 2),
            "balance_score": round(balance, 2),
            "domains_needing_attention": [d.value for d in needs_attention],
            "top_opportunities": [d.value for d in top_opportunities],
            "active_tradeoffs": [t.value for t in tradeoffs],
            "pending_recommendations": pending,
            "last_cycle_timestamp": latest_cycle.timestamp.isoformat() if latest_cycle else None,
        }


# Global optimizer instance
_domain_optimizer: Optional[DomainOptimizer] = None


def get_domain_optimizer() -> DomainOptimizer:
    """Get the global domain optimizer."""
    global _domain_optimizer
    if _domain_optimizer is None:
        _domain_optimizer = DomainOptimizer()
    return _domain_optimizer
