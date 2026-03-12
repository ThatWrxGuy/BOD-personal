"""Scenario Generator - Generates potential future scenarios."""
import uuid
from typing import List, Dict, Any
from datetime import date, timedelta

from app.forecasting.forecast_types import (
    FutureScenario,
    DomainTrend,
    RiskProjection,
)


class ScenarioGenerator:
    """Generates potential future scenarios."""
    
    def __init__(self):
        self.scenarios = []
    
    def generate_scenarios(
        self,
        domain_trends: List[DomainTrend],
        risk_projections: List[RiskProjection],
        num_scenarios: int = 4,
    ) -> List[FutureScenario]:
        """Generate potential future scenarios."""
        
        scenarios = []
        
        # 1. Baseline trajectory
        baseline = self._create_baseline_scenario(domain_trends)
        scenarios.append(baseline)
        
        # 2. Accelerated progress
        accelerated = self._create_accelerated_scenario(domain_trends)
        scenarios.append(accelerated)
        
        # 3. Risk escalation
        risk_esc = self._create_risk_escalation_scenario(domain_trends, risk_projections)
        scenarios.append(risk_esc)
        
        # 4. Domain collapse (worst case)
        collapse = self._create_collapse_scenario(domain_trends)
        scenarios.append(collapse)
        
        return scenarios[:num_scenarios]
    
    def _create_baseline_scenario(
        self,
        domain_trends: List[DomainTrend],
    ) -> FutureScenario:
        """Create baseline trajectory scenario."""
        
        states = {}
        
        for trend in domain_trends:
            # Project based on current trajectory
            states[trend.domain] = trend.projected_performance_90d
        
        # Calculate overall risk
        avg_risk = sum(
            trend.projected_performance_90d for trend in domain_trends
        ) / len(domain_trends) if domain_trends else 5.0
        
        return FutureScenario(
            scenario_id=str(uuid.uuid4())[:8],
            scenario_name="Baseline Trajectory",
            probability=0.5,
            domain_states=states,
            key_events=["Continue current approach"],
            overall_risk=10 - avg_risk,
            description="Current trajectory continues with minor variations",
        )
    
    def _create_accelerated_scenario(
        self,
        domain_trends: List[DomainTrend],
    ) -> FutureScenario:
        """Create accelerated progress scenario."""
        
        states = {}
        
        for trend in domain_trends:
            # Project improvement
            projected = min(10, trend.current_performance + 2)
            states[trend.domain] = projected
        
        avg_perf = sum(states.values()) / len(states) if states else 5.0
        
        return FutureScenario(
            scenario_id=str(uuid.uuid4())[:8],
            scenario_name="Accelerated Progress",
            probability=0.2,
            domain_states=states,
            key_events=[
                "Increased resource allocation",
                "Successful interventions",
                "Favorable external conditions",
            ],
            overall_risk=10 - avg_perf,
            description="Goals achieved faster with improved performance across domains",
        )
    
    def _create_risk_escalation_scenario(
        self,
        domain_trends: List[DomainTrend],
        risk_projections: List[RiskProjection],
    ) -> FutureScenario:
        """Create risk escalation scenario."""
        
        states = {}
        
        # Find high risk domains
        high_risk = [r.domain for r in risk_projections if r.probability_of_event > 0.5]
        
        for trend in domain_trends:
            if trend.domain in high_risk:
                # Decline
                states[trend.domain] = max(0, trend.current_performance - 2)
            else:
                states[trend.domain] = trend.projected_performance_90d
        
        avg_perf = sum(states.values()) / len(states) if states else 5.0
        
        return FutureScenario(
            scenario_id=str(uuid.uuid4())[:8],
            scenario_name="Risk Escalation",
            probability=0.2,
            domain_states=states,
            key_events=[
                "Risk events occur in multiple domains",
                "Interventions required",
                "Resource strain",
            ],
            overall_risk=avg_perf,
            description="Multiple risk events materialize, requiring intervention",
        )
    
    def _create_collapse_scenario(
        self,
        domain_trends: List[DomainTrend],
    ) -> FutureScenario:
        """Create worst-case domain collapse scenario."""
        
        states = {}
        
        for trend in domain_trends:
            if trend.trend_direction.value == "declining":
                # Significant decline
                states[trend.domain] = max(0, trend.current_performance - 3)
            else:
                states[trend.domain] = trend.current_performance
        
        avg_perf = sum(states.values()) / len(states) if states else 5.0
        
        return FutureScenario(
            scenario_id=str(uuid.uuid4())[:8],
            scenario_name="Domain Collapse",
            probability=0.1,
            domain_states=states,
            key_events=[
                "Multiple domains fail",
                "System crisis",
                "Emergency interventions needed",
            ],
            overall_risk=avg_perf,
            description="Worst case: critical domains collapse",
        )


# Global generator
_scenario_generator: ScenarioGenerator = None


def get_scenario_generator() -> ScenarioGenerator:
    """Get the global scenario generator."""
    global _scenario_generator
    if _scenario_generator is None:
        _scenario_generator = ScenarioGenerator()
    return _scenario_generator
