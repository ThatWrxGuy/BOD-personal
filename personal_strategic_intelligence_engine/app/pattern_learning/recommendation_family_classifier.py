"""Recommendation Family Classifier.

Groups recommendations into strategy families.
"""
from typing import Any, Dict, List, Optional

from app.pattern_learning.pattern_models import (
    RecommendationFamily,
    StrategyFamily,
)


class RecommendationFamilyClassifier:
    """Classifies recommendations into strategy families."""
    
    # Mapping from action types to strategy families
    FAMILY_MAPPINGS = {
        # Defensive stabilization
        "reduce_commitments": StrategyFamily.DEFENSIVE_STABILIZATION,
        "reduce_scope": StrategyFamily.DEFENSIVE_STABILIZATION,
        "decrease_workload": StrategyFamily.DEFENSIVE_STABILIZATION,
        "scale_back": StrategyFamily.DEFENSIVE_STABILIZATION,
        
        # Productivity focus
        "increase_output": StrategyFamily.PRODUCTIVITY_FOCUS,
        "boost_efficiency": StrategyFamily.PRODUCTIVITY_FOCUS,
        "accelerate_delivery": StrategyFamily.PRODUCTIVITY_FOCUS,
        
        # Financial stabilization
        "increase_savings": StrategyFamily.FINANCIAL_STABILIZATION,
        "reduce_expenses": StrategyFamily.FINANCIAL_STABILIZATION,
        "improve_cashflow": StrategyFamily.FINANCIAL_STABILIZATION,
        "budget_optimization": StrategyFamily.FINANCIAL_STABILIZATION,
        
        # Health recovery
        "increase_sleep": StrategyFamily.HEALTH_RECOVERY,
        "schedule_recovery": StrategyFamily.HEALTH_RECOVERY,
        "reduce_stress": StrategyFamily.HEALTH_RECOVERY,
        "exercise_more": StrategyFamily.HEALTH_RECOVERY,
        
        # Focus prioritization
        "prioritize_goals": StrategyFamily.FOCUS_PRIORITIZATION,
        "focus_on_core": StrategyFamily.FOCUS_PRIORITIZATION,
        "eliminate_distractions": StrategyFamily.FOCUS_PRIORITIZATION,
        
        # Risk mitigation
        "hedge_risk": StrategyFamily.RISK_MITIGATION,
        "diversify": StrategyFamily.RISK_MITIGATION,
        "add_contingency": StrategyFamily.RISK_MITIGATION,
        
        # Resource optimization
        "optimize_schedule": StrategyFamily.RESOURCE_OPTIMIZATION,
        "reallocate_resources": StrategyFamily.RESOURCE_OPTIMIZATION,
        "improve_time_management": StrategyFamily.RESOURCE_OPTIMIZATION,
    }
    
    # Family descriptions
    FAMILY_DESCRIPTIONS = {
        StrategyFamily.DEFENSIVE_STABILIZATION: "Reduce scope/workload to stabilize",
        StrategyFamily.PRODUCTIVITY_FOCUS: "Increase output and efficiency",
        StrategyFamily.FINANCIAL_STABILIZATION: "Improve financial position",
        StrategyFamily.HEALTH_RECOVERY: "Restore health and energy",
        StrategyFamily.FOCUS_PRIORITIZATION: "Focus on key priorities",
        StrategyFamily.RISK_MITIGATION: "Reduce exposure to risks",
        StrategyFamily.RESOURCE_OPTIMIZATION: "Optimize resource allocation",
        StrategyFamily.EXPLORATION: "Try new approaches",
    }
    
    def __init__(self):
        self._families: Dict[StrategyFamily, RecommendationFamily] = {}
        self._initialize_families()
    
    def _initialize_families(self) -> None:
        """Initialize strategy families."""
        for family in StrategyFamily:
            self._families[family] = RecommendationFamily(
                family_id=f"family_{family.value}",
                family_name=family.value.replace("_", " ").title(),
                strategy_family=family,
                recommendation_types=self._get_types_for_family(family),
                domain=self._infer_domain(family),
            )
    
    def _get_types_for_family(self, family: StrategyFamily) -> List[str]:
        """Get recommendation types for a family."""
        return [
            k for k, v in self.FAMILY_MAPPINGS.items()
            if v == family
        ]
    
    def _infer_domain(self, family: StrategyFamily) -> str:
        """Infer primary domain for a family."""
        domain_mapping = {
            StrategyFamily.DEFENSIVE_STABILIZATION: "tasks",
            StrategyFamily.PRODUCTIVITY_FOCUS: "tasks",
            StrategyFamily.FINANCIAL_STABILIZATION: "finance",
            StrategyFamily.HEALTH_RECOVERY: "health",
            StrategyFamily.FOCUS_PRIORITIZATION: "strategy",
            StrategyFamily.RISK_MITIGATION: "risk",
            StrategyFamily.RESOURCE_OPTIMIZATION: "calendar",
            StrategyFamily.EXPLORATION: "general",
        }
        return domain_mapping.get(family, "general")
    
    def classify(self, action_type: str) -> StrategyFamily:
        """Classify a recommendation into a strategy family."""
        
        action_lower = action_type.lower()
        
        # Try direct mapping
        for key, family in self.FAMILY_MAPPINGS.items():
            if key in action_lower:
                return family
        
        # Default to exploration
        return StrategyFamily.EXPLORATION
    
    def get_family(self, family: StrategyFamily) -> RecommendationFamily:
        """Get a strategy family."""
        return self._families.get(family)
    
    def get_all_families(self) -> List[RecommendationFamily]:
        """Get all strategy families."""
        return list(self._families.values())
    
    def get_family_by_action(self, action_type: str) -> RecommendationFamily:
        """Get the family for an action type."""
        family = self.classify(action_type)
        return self._families.get(family)
    
    def update_family_statistics(
        self,
        family: StrategyFamily,
        success: bool,
    ) -> None:
        """Update statistics for a family."""
        
        if family not in self._families:
            return
        
        self._families[family].total_attempts += 1
        
        if success:
            self._families[family].success_count += 1
        else:
            self._families[family].failure_count += 1
        
        # Update success rate
        total = self._families[family].total_attempts
        successes = self._families[family].success_count
        self._families[family].success_rate = successes / total if total > 0 else 0.0


# Global classifier instance
_recommendation_family_classifier: Optional[RecommendationFamilyClassifier] = None


def get_recommendation_family_classifier() -> RecommendationFamilyClassifier:
    """Get the global recommendation family classifier instance."""
    global _recommendation_family_classifier
    if _recommendation_family_classifier is None:
        _recommendation_family_classifier = RecommendationFamilyClassifier()
    return _recommendation_family_classifier
