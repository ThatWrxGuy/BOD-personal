"""Promotion Engine.

Promotes successful variants into Alpha Engine or research registry.
"""

from typing import Optional
from dataclasses import dataclass

from app.intelligence.autonomous_strategy_lab.lab_models import (
    StrategyVariant, VariantStatus, PromotionDecision, DecisionType, VariantPerformance
)


class PromotionEngine:
    """Promotes successful variants."""
    
    def __init__(self):
        self.decisions = []
    
    def evaluate_promotion(
        self,
        variant: StrategyVariant,
        performance: VariantPerformance,
    ) -> PromotionDecision:
        """Evaluate whether to promote a variant."""
        
        # Check criteria
        if performance.sample_size < 30:
            decision = PromotionDecision(
                variant_id=variant.id,
                decision=DecisionType.NEEDS_REVIEW,
                rationale="Insufficient sample size",
                destination="research",
                approval_required=True,
            )
        elif performance.expectancy <= 0:
            decision = PromotionDecision(
                variant_id=variant.id,
                decision=DecisionType.REJECTED,
                rationale="Negative expectancy",
                destination="rejected",
                approval_required=False,
            )
        elif performance.stability_score < 0.5:
            decision = PromotionDecision(
                variant_id=variant.id,
                decision=DecisionType.NEEDS_REVIEW,
                rationale="Low stability score",
                destination="research",
                approval_required=True,
            )
        elif performance.degradation_risk > 0.5:
            decision = PromotionDecision(
                variant_id=variant.id,
                decision=DecisionType.NEEDS_REVIEW,
                rationale="High degradation risk",
                destination="research",
                approval_required=True,
            )
        else:
            # Check if governance approval needed
            approval_required = performance.expectancy > 30 or performance.stability_score < 0.7
            
            decision = PromotionDecision(
                variant_id=variant.id,
                decision=DecisionType.PROMOTED,
                rationale="Meets all promotion criteria",
                destination="alpha_registry" if approval_required else "active_research",
                approval_required=approval_required,
            )
        
        self.decisions.append(decision)
        return decision
    
    def get_pending_decisions(self) -> list:
        """Get decisions pending approval."""
        
        return [d for d in self.decisions if d.approval_required]


def create_engine() -> PromotionEngine:
    """Create promotion engine."""
    return PromotionEngine()
