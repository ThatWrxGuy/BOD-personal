"""Signal Extractor - Extract meaningful signals from predictive outputs."""
import uuid
from typing import List, Dict, Any, Optional

from app.intelligence.synthesizer.insight_models import (
    StrategicInsight,
    InsightCategory,
    UrgencyLevel,
    PredictionSnapshot,
)


class SignalExtractor:
    """Extracts strategic signals from predictive outputs."""
    
    def __init__(self):
        self.min_confidence = 0.3
    
    def _to_confidence(self, value: float) -> float:
        """Convert 0-10 scale to 0-1 confidence."""
        return min(1.0, max(0.1, value / 10.0))
    
    def extract_from_forecast(
        self,
        forecast_data: PredictionSnapshot,
    ) -> List[StrategicInsight]:
        """Extract insights from forecast engine outputs."""
        
        insights = []
        
        # Analyze domain trends
        for domain, performance in forecast_data.domain_predictions.items():
            if performance < 4.0:
                confidence = self._to_confidence(forecast_data.risk_predictions.get(domain, 5.0))
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.RISK,
                    title=f"{domain.title()} Performance Declining",
                    description=f"Domain {domain} is predicted to perform at {performance:.1f}/10",
                    impact_score=10 - performance,
                    confidence_score=confidence,
                    urgency=UrgencyLevel.HIGH if performance < 3 else UrgencyLevel.MEDIUM,
                    source_engine="forecast",
                    supporting_evidence={"predicted_performance": performance},
                    domains_affected=[domain],
                )
                insights.append(insight)
            elif performance > 7.0:
                confidence = self._to_confidence(forecast_data.risk_predictions.get(domain, 5.0))
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.STRENGTH,
                    title=f"{domain.title()} Performance Strong",
                    description=f"Domain {domain} is predicted to perform at {performance:.1f}/10",
                    impact_score=performance,
                    confidence_score=confidence,
                    urgency=UrgencyLevel.LOW,
                    source_engine="forecast",
                    supporting_evidence={"predicted_performance": performance},
                    domains_affected=[domain],
                )
                insights.append(insight)
        
        # Analyze risks
        for domain, risk in forecast_data.risk_predictions.items():
            if risk > 6.0:
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.RISK,
                    title=f"High Risk in {domain.title()}",
                    description=f"Risk level for {domain} is elevated at {risk:.1f}/10",
                    impact_score=risk,
                    confidence_score=0.8,
                    urgency=UrgencyLevel.HIGH if risk > 7 else UrgencyLevel.MEDIUM,
                    source_engine="forecast",
                    supporting_evidence={"risk_level": risk},
                    domains_affected=[domain],
                )
                insights.append(insight)
        
        # Analyze goals
        for goal_id, probability in forecast_data.goal_probabilities.items():
            if probability < 0.5:
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.FORECAST,
                    title=f"Goal {goal_id} at Risk",
                    description=f"Probability of achieving goal {goal_id} is only {probability:.0%}",
                    impact_score=(1 - probability) * 10,
                    confidence_score=probability,
                    urgency=UrgencyLevel.HIGH if probability < 0.3 else UrgencyLevel.MEDIUM,
                    source_engine="forecast",
                    supporting_evidence={"probability": probability},
                    goals_affected=[goal_id],
                )
                insights.append(insight)
            elif probability > 0.8:
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.OPPORTUNITY,
                    title=f"Goal {goal_id} on Track",
                    description=f"Probability of achieving goal {goal_id} is {probability:.0%}",
                    impact_score=probability * 10,
                    confidence_score=probability,
                    urgency=UrgencyLevel.LOW,
                    source_engine="forecast",
                    supporting_evidence={"probability": probability},
                    goals_affected=[goal_id],
                )
                insights.append(insight)
        
        return insights
    
    def extract_from_simulation(
        self,
        simulation_data: PredictionSnapshot,
    ) -> List[StrategicInsight]:
        """Extract insights from strategy simulation outputs."""
        
        insights = []
        
        # Analyze strategy rankings
        if simulation_data.strategy_rankings:
            # Best strategy
            best_strategy = max(
                simulation_data.strategy_rankings.items(),
                key=lambda x: x[1]
            )
            
            insight = StrategicInsight(
                id=str(uuid.uuid4())[:8],
                category=InsightCategory.SIMULATION,
                title=f"Recommended Strategy: {best_strategy[0]}",
                description=f"Strategy {best_strategy[0]} scored {best_strategy[1]:.2f} in simulation",
                impact_score=best_strategy[1],
                confidence_score=0.7,
                urgency=UrgencyLevel.MEDIUM,
                source_engine="simulation",
                supporting_evidence={
                    "strategy": best_strategy[0],
                    "score": best_strategy[1]
                },
            )
            insights.append(insight)
            
            # Worst strategy
            worst_strategy = min(
                simulation_data.strategy_rankings.items(),
                key=lambda x: x[1]
            )
            
            if worst_strategy[1] < 4.0:
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.WEAKNESS,
                    title=f"Underperforming Strategy: {worst_strategy[0]}",
                    description=f"Strategy {worst_strategy[0]} scored only {worst_strategy[1]:.2f}",
                    impact_score=10 - worst_strategy[1],
                    confidence_score=0.7,
                    urgency=UrgencyLevel.MEDIUM,
                    source_engine="simulation",
                    supporting_evidence={
                        "strategy": worst_strategy[0],
                        "score": worst_strategy[1]
                    },
                )
                insights.append(insight)
        
        return insights
    
    def extract_from_monte_carlo(
        self,
        monte_carlo_data: PredictionSnapshot,
    ) -> List[StrategicInsight]:
        """Extract insights from Monte Carlo stress test outputs."""
        
        # Note: This would normally parse distribution data
        # For now, extract basic insights from available data
        
        insights = []
        
        # Analyze domain volatility (from raw_data if available)
        if monte_carlo_data.raw_data:
            volatility = monte_carlo_data.raw_data.get("volatility", {})
            
            for domain, vol in volatility.items():
                if vol > 0.5:
                    insight = StrategicInsight(
                        id=str(uuid.uuid4())[:8],
                        category=InsightCategory.STRESS_TEST,
                        title=f"High Volatility in {domain.title()}",
                        description=f"Domain {domain} shows high outcome volatility ({vol:.1%})",
                        impact_score=vol * 10,
                        confidence_score=0.8,
                        urgency=UrgencyLevel.HIGH if vol > 0.7 else UrgencyLevel.MEDIUM,
                        source_engine="monte_carlo",
                        supporting_evidence={"volatility": vol},
                        domains_affected=[domain],
                    )
                    insights.append(insight)
        
        # Analyze resilience scores if available
        resilience = monte_carlo_data.raw_data.get("resilience", {})
        
        for strategy, score in resilience.items():
            if score < 0.5:
                insight = StrategicInsight(
                    id=str(uuid.uuid4())[:8],
                    category=InsightCategory.WEAKNESS,
                    title=f"Fragile Strategy: {strategy}",
                    description=f"Strategy {strategy} has low resilience ({score:.1%})",
                    impact_score=(1 - score) * 10,
                    confidence_score=0.8,
                    urgency=UrgencyLevel.HIGH,
                    source_engine="monte_carlo",
                    supporting_evidence={"resilience": score},
                )
                insights.append(insight)
        
        return insights
    
    def extract_all(
        self,
        forecast_data: Optional[PredictionSnapshot] = None,
        simulation_data: Optional[PredictionSnapshot] = None,
        monte_carlo_data: Optional[PredictionSnapshot] = None,
    ) -> List[StrategicInsight]:
        """Extract all signals from all predictive engines."""
        
        all_insights = []
        
        if forecast_data:
            all_insights.extend(self.extract_from_forecast(forecast_data))
        
        if simulation_data:
            all_insights.extend(self.extract_from_simulation(simulation_data))
        
        if monte_carlo_data:
            all_insights.extend(self.extract_from_monte_carlo(monte_carlo_data))
        
        return all_insights


_extractor: Optional[SignalExtractor] = None


def get_signal_extractor() -> SignalExtractor:
    """Get the global signal extractor."""
    global _extractor
    if _extractor is None:
        _extractor = SignalExtractor()
    return _extractor
