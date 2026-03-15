"""Research Registry.

Tracks all strategy templates, variants, experiments, and statuses.
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.intelligence.autonomous_strategy_lab.lab_models import (
    StrategyVariant, VariantStatus, ExperimentRun, PromotionDecision
)


class ResearchRegistry:
    """Registry for research tracking."""
    
    def __init__(self):
        self.variants: Dict[str, StrategyVariant] = {}
        self.experiments: Dict[str, ExperimentRun] = {}
        self.promotions: Dict[str, PromotionDecision] = {}
    
    def register_variant(self, variant: StrategyVariant) -> None:
        """Register a variant."""
        self.variants[variant.id] = variant
    
    def register_experiment(self, experiment: ExperimentRun) -> None:
        """Register an experiment."""
        self.experiments[experiment.id] = experiment
    
    def record_promotion(self, decision: PromotionDecision) -> None:
        """Record a promotion decision."""
        self.promotions[decision.variant_id] = decision
    
    def get_variant(self, variant_id: str) -> Optional[StrategyVariant]:
        """Get variant by ID."""
        return self.variants.get(variant_id)
    
    def list_variants(self, status: Optional[VariantStatus] = None) -> List[StrategyVariant]:
        """List variants, optionally filtered by status."""
        if status:
            return [v for v in self.variants.values() if v.status == status]
        return list(self.variants.values())
    
    def get_summary(self) -> Dict:
        """Get registry summary."""
        
        status_counts = {}
        for v in self.variants.values():
            status = v.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_variants": len(self.variants),
            "total_experiments": len(self.experiments),
            "total_promotions": len(self.promotions),
            "by_status": status_counts,
        }


# Global registry
_registry = None

def get_registry() -> ResearchRegistry:
    """Get global research registry."""
    global _registry
    if _registry is None:
        _registry = ResearchRegistry()
    return _registry
