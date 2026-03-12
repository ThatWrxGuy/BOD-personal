"""Decision Model - Models strategic decisions for simulation."""
import uuid
from typing import List, Dict, Any

from app.strategy_simulation.simulation_types import (
    StrategyDecision,
    StrategyType,
)


class DecisionModel:
    """Models strategic decisions for simulation."""
    
    def __init__(self):
        self.decision_templates = self._create_templates()
    
    def _create_templates(self) -> Dict[str, StrategyDecision]:
        """Create decision templates."""
        
        templates = {}
        
        # 1. Focus shift to learning
        templates["focus_learning"] = StrategyDecision(
            decision_id="focus_learning",
            name="Focus on Learning",
            description="Shift resources to learning domain for skill development",
            strategy_type=StrategyType.FOCUS_SHIFT,
            affected_domains=["learning", "career"],
            resource_changes={"learning": 5.0, "career": 2.0, "wealth": -3.0, "operations": -2.0},
            expected_outcome="Improved career prospects through skill development",
            priority=0.7,
        )
        
        # 2. Focus on wealth
        templates["focus_wealth"] = StrategyDecision(
            decision_id="focus_wealth",
            name="Focus on Wealth Building",
            description="Prioritize wealth accumulation and financial growth",
            strategy_type=StrategyType.FOCUS_SHIFT,
            affected_domains=["wealth", "operations"],
            resource_changes={"wealth": 6.0, "operations": -2.0, "health": -2.0, "relationships": -2.0},
            expected_outcome="Increased financial security",
            priority=0.8,
        )
        
        # 3. Balance strategy
        templates["balance"] = StrategyDecision(
            decision_id="balance",
            name="Balanced Approach",
            description="Maintain balanced focus across all domains",
            strategy_type=StrategyType.FOCUS_SHIFT,
            affected_domains=["health", "wealth", "career", "relationships"],
            resource_changes={"health": 1.0, "wealth": 1.0, "career": 1.0, "relationships": 1.0},
            expected_outcome="Sustainable progress across all domains",
            priority=0.6,
        )
        
        # 4. Health focus
        templates["focus_health"] = StrategyDecision(
            decision_id="focus_health",
            name="Prioritize Health",
            description="Focus on health and wellness improvements",
            strategy_type=StrategyType.FOCUS_SHIFT,
            affected_domains=["health", "personal_development"],
            resource_changes={"health": 6.0, "personal_development": 2.0, "career": -3.0, "wealth": -3.0},
            expected_outcome="Improved energy and wellbeing",
            priority=0.9,
        )
        
        # 5. Career advancement
        templates["focus_career"] = StrategyDecision(
            decision_id="focus_career",
            name="Career Advancement",
            description="Focus on career growth and professional development",
            strategy_type=StrategyType.FOCUS_SHIFT,
            affected_domains=["career", "learning"],
            resource_changes={"career": 5.0, "learning": 3.0, "relationships": -4.0, "operations": -2.0},
            expected_outcome="Career progression and higher income potential",
            priority=0.75,
        )
        
        # 6. Operations efficiency
        templates["improve_operations"] = StrategyDecision(
            decision_id="improve_operations",
            name="Operational Excellence",
            description="Improve operational efficiency and reduce overhead",
            strategy_type=StrategyType.RESOURCE_REALLOCATION,
            affected_domains=["operations", "wealth"],
            resource_changes={"operations": 4.0, "wealth": 2.0, "strategic_projects": -3.0, "learning": -3.0},
            expected_outcome="Better resource utilization and cost savings",
            priority=0.65,
        )
        
        # 7. Risk mitigation
        templates["mitigate_risk"] = StrategyDecision(
            decision_id="mitigate_risk",
            name="Risk Mitigation",
            description="Focus on reducing high-priority risks",
            strategy_type=StrategyType.RISK_MITIGATION,
            affected_domains=["wealth", "health", "operations"],
            resource_changes={"wealth": -2.0, "health": -2.0, "operations": 2.0},
            expected_outcome="Reduced risk exposure",
            priority=0.85,
        )
        
        return templates
    
    def get_all_strategies(self) -> List[StrategyDecision]:
        """Get all available strategy templates."""
        return list(self.decision_templates.values())
    
    def get_strategy(self, decision_id: str) -> StrategyDecision:
        """Get a specific strategy."""
        return self.decision_templates.get(decision_id)
    
    def create_custom_strategy(
        self,
        name: str,
        description: str,
        affected_domains: List[str],
        resource_changes: Dict[str, float],
        strategy_type: StrategyType = StrategyType.FOCUS_SHIFT,
    ) -> StrategyDecision:
        """Create a custom strategy decision."""
        
        return StrategyDecision(
            decision_id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            strategy_type=strategy_type,
            affected_domains=affected_domains,
            resource_changes=resource_changes,
            expected_outcome="Custom strategic decision",
            priority=0.5,
        )


# Global model
_decision_model: DecisionModel = None


def get_decision_model() -> DecisionModel:
    """Get the global decision model."""
    global _decision_model
    if _decision_model is None:
        _decision_model = DecisionModel()
    return _decision_model
