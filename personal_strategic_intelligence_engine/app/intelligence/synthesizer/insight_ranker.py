"""Insight Ranker - Ranks insights by importance."""
from typing import List

from app.intelligence.synthesizer.insight_models import (
    StrategicInsight,
    UrgencyLevel,
    RiskSeverity,
)


class InsightRanker:
    """Ranks strategic insights by importance."""
    
    # Weights for priority calculation
    IMPACT_WEIGHT = 0.4
    CONFIDENCE_WEIGHT = 0.3
    URGENCY_WEIGHT = 0.2
    RISK_WEIGHT = 0.1
    
    def __init__(self):
        self.urgency_multipliers = {
            UrgencyLevel.LOW: 0.5,
            UrgencyLevel.MEDIUM: 1.0,
            UrgencyLevel.HIGH: 1.5,
            UrgencyLevel.CRITICAL: 2.0,
        }
    
    def calculate_priority_score(self, insight: StrategicInsight) -> float:
        """Calculate priority score for an insight."""
        
        # Normalize impact (0-10 -> 0-1)
        impact_norm = insight.impact_score / 10.0
        
        # Urgency multiplier
        urgency_mult = self.urgency_multipliers.get(insight.urgency, 1.0)
        
        # Calculate score
        priority = (
            (impact_norm * self.IMPACT_WEIGHT) +
            (insight.confidence_score * self.CONFIDENCE_WEIGHT) +
            (urgency_mult * self.URGENCY_WEIGHT / 2.0) +
            (0.5 * self.RISK_WEIGHT)  # Assume medium risk if not specified
        )
        
        # Scale back to 0-10
        return priority * 10
    
    def rank_insights(self, insights: List[StrategicInsight]) -> List[StrategicInsight]:
        """Rank insights by priority score."""
        
        # Calculate priority for each
        for insight in insights:
            insight.priority_score = self.calculate_priority_score(insight)
        
        # Sort by priority (descending)
        ranked = sorted(
            insights,
            key=lambda i: i.priority_score,
            reverse=True
        )
        
        return ranked
    
    def get_top_insights(
        self,
        insights: List[StrategicInsight],
        limit: int = 10,
    ) -> List[StrategicInsight]:
        """Get top N insights by priority."""
        
        ranked = self.rank_insights(insights)
        return ranked[:limit]
    
    def filter_by_category(
        self,
        insights: List[StrategicInsight],
        category: str,
    ) -> List[StrategicInsight]:
        """Filter insights by category."""
        
        return [i for i in insights if i.category.value == category]
    
    def filter_by_urgency(
        self,
        insights: List[StrategicInsight],
        min_urgency: UrgencyLevel,
    ) -> List[StrategicInsight]:
        """Filter insights by minimum urgency level."""
        
        urgency_order = [
            UrgencyLevel.LOW,
            UrgencyLevel.MEDIUM,
            UrgencyLevel.HIGH,
            UrgencyLevel.CRITICAL,
        ]
        
        min_idx = urgency_order.index(min_urgency)
        
        return [
            i for i in insights
            if urgency_order.index(i.urgency) >= min_idx
        ]
    
    def get_critical_insights(
        self,
        insights: List[StrategicInsight],
    ) -> List[StrategicInsight]:
        """Get insights that require immediate attention."""
        
        return self.filter_by_urgency(insights, UrgencyLevel.HIGH)
    
    def get_summary_by_category(
        self,
        insights: List[StrategicInsight],
    ) -> dict:
        """Get summary of insights grouped by category."""
        
        summary = {}
        
        for insight in insights:
            category = insight.category.value
            if category not in summary:
                summary[category] = {
                    "count": 0,
                    "total_priority": 0.0,
                    "avg_confidence": 0.0,
                }
            
            summary[category]["count"] += 1
            summary[category]["total_priority"] += insight.priority_score
        
        # Calculate averages
        for category, data in summary.items():
            if data["count"] > 0:
                data["avg_priority"] = data["total_priority"] / data["count"]
                del data["total_priority"]
        
        return summary


_ranker: InsightRanker = None


def get_insight_ranker() -> InsightRanker:
    """Get the global insight ranker."""
    global _ranker
    if _ranker is None:
        _ranker = InsightRanker()
    return _ranker
