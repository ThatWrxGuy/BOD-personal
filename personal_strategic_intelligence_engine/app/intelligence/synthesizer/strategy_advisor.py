"""Strategy Advisor - Converts insights into recommended actions."""
import uuid
from typing import List, Dict, Any, Optional

from app.intelligence.synthesizer.insight_models import (
    StrategicInsight,
    StrategicRecommendation,
    InsightCategory,
    UrgencyLevel,
    RiskSeverity,
)


class StrategyAdvisor:
    """Converts strategic insights into actionable recommendations."""
    
    def __init__(self):
        self.recommendation_templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, Dict]:
        """Initialize recommendation templates."""
        
        return {
            # Risk-based recommendations
            "health_risk": {
                "action": "Prioritize health recovery",
                "outcome": "Improved health domain performance and reduced risk",
                "effort": "medium",
            },
            "wealth_risk": {
                "action": "Increase emergency savings",
                "outcome": "Reduced financial vulnerability",
                "effort": "medium",
            },
            "operations_risk": {
                "action": "Streamline operational processes",
                "outcome": "Improved operational efficiency",
                "effort": "high",
            },
            
            # Opportunity recommendations
            "career_opportunity": {
                "action": "Pursue career advancement opportunity",
                "outcome": "Career growth and increased income potential",
                "effort": "medium",
            },
            "learning_opportunity": {
                "action": "Invest in skill development",
                "outcome": "Enhanced capabilities and career prospects",
                "effort": "medium",
            },
            
            # Goal recommendations
            "goal_declining": {
                "action": "Increase focus on goal-related activities",
                "outcome": "Improved goal completion probability",
                "effort": "low",
            },
            "goal_on_track": {
                "action": "Maintain current trajectory",
                "outcome": "Goal achievement on schedule",
                "effort": "low",
            },
            
            # Strategy recommendations
            "simulation_strategy": {
                "action": "Adopt recommended simulation strategy",
                "outcome": "Optimized resource allocation",
                "effort": "medium",
            },
            
            # Weakness recommendations
            "fragile_strategy": {
                "action": "Diversify strategic approach",
                "outcome": "Reduced strategy vulnerability",
                "effort": "high",
            },
            
            # Default
            "default": {
                "action": "Review and address issue",
                "outcome": "Issue resolution",
                "effort": "medium",
            },
        }
    
    def generate_recommendation(
        self,
        insight: StrategicInsight,
    ) -> StrategicRecommendation:
        """Generate a recommendation for an insight."""
        
        # Map insight category to recommendation template
        template_key = self._get_template_key(insight)
        template = self.recommendation_templates.get(
            template_key,
            self.recommendation_templates["default"]
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(insight)
        
        # Calculate expected impact
        expected_impact = min(10, insight.impact_score * insight.confidence_score)
        
        recommendation = StrategicRecommendation(
            id=str(uuid.uuid4())[:8],
            title=f"Action: {template['action']}",
            description=insight.description,
            recommended_action=template["action"],
            expected_outcome=template["outcome"],
            expected_impact=expected_impact,
            confidence=insight.confidence_score * 0.8,  # Slightly reduced
            risk_level=risk_level,
            source_insight_id=insight.id,
            implementation_effort=template["effort"],
        )
        
        return recommendation
    
    def _get_template_key(self, insight: StrategicInsight) -> str:
        """Map insight to recommendation template key."""
        
        category = insight.category
        
        if category == InsightCategory.RISK:
            # Check domain for specific risk
            if insight.domains_affected:
                domain = insight.domains_affected[0]
                return f"{domain}_risk"
            return "default"
        
        if category == InsightCategory.OPPORTUNITY:
            if insight.domains_affected:
                domain = insight.domains_affected[0]
                return f"{domain}_opportunity"
            return "default"
        
        if category == InsightCategory.FORECAST:
            if "declining" in insight.description.lower():
                return "goal_declining"
            return "goal_on_track"
        
        if category == InsightCategory.SIMULATION:
            return "simulation_strategy"
        
        if category == InsightCategory.WEAKNESS:
            return "fragile_strategy"
        
        return "default"
    
    def _get_risk_level(self, insight: StrategicInsight) -> RiskSeverity:
        """Determine risk level for recommendation."""
        
        if insight.urgency == UrgencyLevel.CRITICAL:
            return RiskSeverity.CRITICAL
        elif insight.urgency == UrgencyLevel.HIGH:
            return RiskSeverity.HIGH
        elif insight.urgency == UrgencyLevel.MEDIUM:
            return RiskSeverity.MEDIUM
        else:
            return RiskSeverity.LOW
    
    def generate_recommendations(
        self,
        insights: List[StrategicInsight],
    ) -> List[StrategicRecommendation]:
        """Generate recommendations for multiple insights."""
        
        recommendations = []
        
        for insight in insights:
            # Skip low-priority insights
            if insight.priority_score < 3.0:
                continue
            
            recommendation = self.generate_recommendation(insight)
            recommendations.append(recommendation)
        
        # Sort by expected impact
        recommendations.sort(key=lambda r: r.expected_impact, reverse=True)
        
        return recommendations
    
    def group_by_domain(
        self,
        recommendations: List[StrategicRecommendation],
    ) -> Dict[str, List[StrategicRecommendation]]:
        """Group recommendations by affected domain."""
        
        grouped = {}
        
        for rec in recommendations:
            # This would need insight to know domain
            # For now, just return single group
            if "domain" not in grouped:
                grouped["general"] = []
            grouped["general"].append(rec)
        
        return grouped


_advisor: Optional[StrategyAdvisor] = None


def get_strategy_advisor() -> StrategyAdvisor:
    """Get the global strategy advisor."""
    global _advisor
    if _advisor is None:
        _advisor = StrategyAdvisor()
    return _advisor
