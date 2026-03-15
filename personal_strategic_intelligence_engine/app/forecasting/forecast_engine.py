"""Forecast Engine - Main forecasting engine."""
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from app.forecasting.forecast_types import (
    ForecastCycle,
    ForecastPolicy,
    ForecastStatistics,
    DomainTrend,
    RiskProjection,
)
from app.forecasting.trend_analyzer import TrendAnalyzer, get_trend_analyzer
from app.forecasting.risk_projection import RiskProjector, get_risk_projector
from app.forecasting.goal_probability_engine import GoalProbabilityEngine, get_goal_probability_engine
from app.forecasting.scenario_generator import ScenarioGenerator, get_scenario_generator


class ForecastEngine:
    """Main forecasting engine."""
    
    def __init__(self, policy: Optional[ForecastPolicy] = None):
        self.policy = policy or ForecastPolicy()
        self.trend_analyzer = get_trend_analyzer()
        self.risk_projector = get_risk_projector()
        self.goal_engine = get_goal_probability_engine()
        self.scenario_generator = get_scenario_generator()
        self.cycles: List[ForecastCycle] = []
    
    def add_domain_data(
        self,
        domain: str,
        performance: float,
        risk: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add historical domain data."""
        
        self.trend_analyzer.add_data_point(domain, performance, risk, timestamp)
    
    def register_goal(
        self,
        goal_id: str,
        goal_name: str,
        target_date: date,
        current_progress: float = 0.0,
        target_value: float = 1.0,
        priority: float = 0.5,
    ) -> None:
        """Register a goal for probability calculation."""
        
        self.goal_engine.register_goal(
            goal_id, goal_name, target_date, 
            current_progress, target_value, priority
        )
    
    def run_forecast_cycle(self) -> ForecastCycle:
        """Run a complete forecast cycle."""
        
        cycle_id = str(uuid.uuid4())[:8]
        
        # Get domain names from history
        domain_names = list(self.trend_analyzer.history.keys())
        
        if not domain_names:
            domain_names = ["health", "wealth", "career", "operations", "learning"]
        
        # Analyze trends
        trends = self.trend_analyzer.analyze_all_domains(domain_names)
        
        # Project risks
        risk_inputs = [
            {"name": d.domain, "risk_score": d.current_performance} 
            for d in trends
        ]
        risks = self.risk_projector.project_all_risks(risk_inputs)
        
        # Calculate goal probabilities
        goal_probs = self.goal_engine.calculate_all_probabilities()
        
        # Generate scenarios
        scenarios = self.scenario_generator.generate_scenarios(trends, risks)
        
        # Determine summary items
        highest_risk = [r.domain for r in sorted(risks, key=lambda x: x.probability_of_event, reverse=True)[:3]]
        declining = [t.domain for t in trends if t.trend_direction.value == "declining"]
        at_risk_goals = [g.goal_id for g in goal_probs if g.probability_of_success < 0.5]
        opportunities = [t.domain for t in trends if t.trend_direction.value == "improving"]
        
        cycle = ForecastCycle(
            cycle_id=cycle_id,
            domain_trends=trends,
            risk_projections=risks,
            goal_probabilities=goal_probs,
            scenarios=scenarios,
            highest_risk_domains=highest_risk,
            declining_domains=declining,
            at_risk_goals=at_risk_goals,
            opportunities_identified=opportunities,
        )
        
        self.cycles.append(cycle)
        
        return cycle
    
    def get_trend_report(self) -> Dict[str, Any]:
        """Get domain trends report."""
        
        domain_names = list(self.trend_analyzer.history.keys())
        
        if not domain_names:
            domain_names = ["health", "wealth", "career", "operations", "learning"]
        
        trends = self.trend_analyzer.analyze_all_domains(domain_names)
        
        return {
            "trends": [
                {
                    "domain": t.domain,
                    "current": t.current_performance,
                    "30d": t.projected_performance_30d,
                    "90d": t.projected_performance_90d,
                    "365d": t.projected_performance_365d,
                    "direction": t.trend_direction.value,
                    "confidence": t.trend_confidence,
                }
                for t in trends
            ]
        }
    
    def get_risk_report(self) -> Dict[str, Any]:
        """Get risk projections report."""
        
        domain_names = list(self.trend_analyzer.history.keys())
        
        if not domain_names:
            domain_names = ["health", "wealth", "career", "operations", "learning"]
        
        trends = self.trend_analyzer.analyze_all_domains(domain_names)
        risk_inputs = [{"name": d.domain, "risk_score": d.current_performance} for d in trends]
        risks = self.risk_projector.project_all_risks(risk_inputs)
        
        return {
            "projections": [
                {
                    "domain": r.domain,
                    "current": r.current_risk,
                    "30d": r.projected_risk_30d,
                    "90d": r.projected_risk_90d,
                    "probability": r.probability_of_event,
                    "severity": r.severity.value,
                }
                for r in risks
            ]
        }
    
    def get_goal_report(self) -> Dict[str, Any]:
        """Get goal probabilities report."""
        
        goals = self.goal_engine.calculate_all_probabilities()
        
        return {
            "goals": [
                {
                    "goal_id": g.goal_id,
                    "name": g.goal_name,
                    "progress": g.current_progress,
                    "probability": g.probability_of_success,
                    "expected_months": g.expected_months_to_completion,
                    "confidence": g.confidence,
                    "recommendation": g.recommendation,
                }
                for g in goals
            ]
        }
    
    def get_statistics(self) -> ForecastStatistics:
        """Get forecasting statistics."""
        
        return ForecastStatistics(
            total_cycles=len(self.cycles),
            last_forecast_time=self.cycles[-1].timestamp if self.cycles else None,
        )


# Global engine
_forecast_engine: Optional[ForecastEngine] = None


def get_forecast_engine() -> ForecastEngine:
    """Get the global forecast engine."""
    global _forecast_engine
    if _forecast_engine is None:
        _forecast_engine = ForecastEngine()
    return _forecast_engine
