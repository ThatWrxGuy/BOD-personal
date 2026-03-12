"""Outcome Simulator - Simulates how decisions affect future states."""
from typing import List, Dict, Any, Optional
import random

from app.strategy_simulation.simulation_types import (
    StrategyDecision,
    SimulatedOutcome,
    EnvironmentScenario,
    ScenarioEnvironment,
)


class OutcomeSimulator:
    """Simulates outcomes of strategic decisions."""
    
    def __init__(self):
        self.default_domains = [
            "health", "wealth", "career", "relationships",
            "learning", "personal_development", "operations", "strategic_projects"
        ]
    
    def simulate_outcome(
        self,
        strategy: StrategyDecision,
        current_domains: Dict[str, float],
        time_horizon_days: int,
        environment: Optional[EnvironmentScenario] = None,
    ) -> SimulatedOutcome:
        """Simulate the outcome of a strategic decision."""
        
        # Apply strategy effects
        projected_domains = self._apply_strategy_effects(
            strategy, current_domains, time_horizon_days
        )
        
        # Apply environment effects
        if environment:
            projected_domains = self._apply_environment_effects(
                environment, projected_domains
            )
        
        # Calculate risk projections
        projected_risk = self._calculate_risk(projected_domains)
        
        # Calculate expected gains
        expected_gain = self._calculate_performance_gain(
            current_domains, projected_domains
        )
        
        # Risk exposure change
        risk_change = self._calculate_risk_change(
            current_domains, projected_domains
        )
        
        # Overall score
        overall_score = self._calculate_overall_score(
            expected_gain, risk_change, strategy.priority
        )
        
        return SimulatedOutcome(
            strategy_id=strategy.decision_id,
            time_horizon_days=time_horizon_days,
            projected_domains=projected_domains,
            projected_risk=projected_risk,
            expected_performance_gain=expected_gain,
            risk_exposure_change=risk_change,
            overall_score=overall_score,
        )
    
    def _apply_strategy_effects(
        self,
        strategy: StrategyDecision,
        current_domains: Dict[str, float],
        days: int,
    ) -> Dict[str, float]:
        """Apply strategy effects to domain states."""
        
        result = current_domains.copy()
        
        # Apply resource changes
        for domain, change in strategy.resource_changes.items():
            if domain in result:
                # Scale effect by time (diminishing over time)
                effect = change * (days / 90) * 0.5
                result[domain] = max(0, min(10, result[domain] + effect))
            else:
                result[domain] = max(0, min(10, 5.0 + change))
        
        # Apply secondary effects (domain interactions)
        result = self._apply_domain_interactions(result, strategy)
        
        return result
    
    def _apply_domain_interactions(
        self,
        domains: Dict[str, float],
        strategy: StrategyDecision,
    ) -> Dict[str, float]:
        """Apply domain interaction effects."""
        
        result = domains.copy()
        
        # Health affects everything positively
        if "health" in result:
            health_boost = result["health"] * 0.1
            for domain in result:
                if domain != "health":
                    result[domain] = min(10, result[domain] + health_boost * 0.1)
        
        # Career affects wealth
        if "career" in result and "wealth" in result:
            wealth_effect = (result["career"] - 5) * 0.15
            result["wealth"] = max(0, min(10, result["wealth"] + wealth_effect))
        
        # Learning affects career
        if "learning" in result and "career" in result:
            career_effect = (result["learning"] - 5) * 0.2
            result["career"] = max(0, min(10, result["career"] + career_effect))
        
        # Operations affects everything negatively when low
        if "operations" in result and result["operations"] < 4:
            penalty = (4 - result["operations"]) * 0.15
            for domain in result:
                if domain != "operations":
                    result[domain] = max(0, result[domain] - penalty)
        
        return result
    
    def _apply_environment_effects(
        self,
        environment,
        domains: Dict[str, float],
    ) -> Dict[str, float]:
        """Apply environmental scenario effects."""
        
        result = domains.copy()
        
        # Try new field names first, fall back to old
        ext_pressure = getattr(environment, 'external_pressure_level', 
                    getattr(environment, 'economic_conditions', 0.5))
        opp_density = getattr(environment, 'opportunity_density',
                    getattr(environment, 'opportunity_availability', 0.5))
        disruption = getattr(environment, 'disruption_frequency', 0.3)
        
        # Economic conditions affect wealth
        if "wealth" in result:
            wealth_effect = (ext_pressure - 0.5) * 2
            result["wealth"] = max(0, min(10, result["wealth"] + wealth_effect))
        
        # Volatility affects wealth negatively  
        volatility = getattr(environment, 'volatility_level',
                   getattr(environment, 'market_volatility', 0.5))
        if "wealth" in result:
            risk_penalty = volatility * 0.5
            result["wealth"] = max(0, result["wealth"] - risk_penalty)
        
        # Health factors
        health_factors = getattr(environment, 'health_factors', 0.5)
        if "health" in result:
            health_effect = (health_factors - 0.5) * 2
            result["health"] = max(0, min(10, result["health"] + health_effect))
        
        # Opportunity availability affects career
        if "career" in result:
            opp_effect = (opp_density - 0.5) * 1.5
            result["career"] = max(0, min(10, result["career"] + opp_effect))
        
        # Apply domain modifiers if present
        if hasattr(environment, 'domain_modifiers'):
            for domain, modifier in environment.domain_modifiers.items():
                if domain in result:
                    result[domain] = max(0, min(10, result[domain] + modifier))
        
        return result
    
    def _calculate_risk(self, domains: Dict[str, float]) -> Dict[str, float]:
        """Calculate risk levels from domain states."""
        
        risk = {}
        
        # Low performance = high risk
        for domain, perf in domains.items():
            if perf < 3:
                risk[domain] = 8.0 - perf
            elif perf < 5:
                risk[domain] = 6.0 - perf * 0.5
            else:
                risk[domain] = 4.0 - perf * 0.3
        
        return risk
    
    def _calculate_performance_gain(
        self,
        before: Dict[str, float],
        after: Dict[str, float],
    ) -> float:
        """Calculate average performance gain."""
        
        gains = []
        
        for domain in before:
            if domain in after:
                gain = after[domain] - before[domain]
                gains.append(gain)
        
        return sum(gains) / len(gains) if gains else 0
    
    def _calculate_risk_change(
        self,
        before: Dict[str, float],
        after: Dict[str, float],
    ) -> float:
        """Calculate change in risk exposure."""
        
        before_risk = self._calculate_risk(before)
        after_risk = self._calculate_risk(after)
        
        before_total = sum(before_risk.values())
        after_total = sum(after_risk.values())
        
        return before_total - after_total  # Positive = risk reduced
    
    def _calculate_overall_score(
        self,
        perf_gain: float,
        risk_change: float,
        priority: float,
    ) -> float:
        """Calculate overall strategy score."""
        
        # Weighted combination
        score = (
            perf_gain * 0.5 +
            risk_change * 0.3 +
            priority * 0.2
        )
        
        return max(0, min(10, 5 + score))
    
    def simulate_multiple_horizons(
        self,
        strategy: StrategyDecision,
        current_domains: Dict[str, float],
        horizons: List[int],
        environment: Optional[EnvironmentScenario] = None,
    ) -> List[SimulatedOutcome]:
        """Simulate outcome at multiple time horizons."""
        
        outcomes = []
        
        for horizon in horizons:
            outcome = self.simulate_outcome(
                strategy, current_domains, horizon, environment
            )
            outcomes.append(outcome)
        
        return outcomes


# Global simulator
_outcome_simulator: Optional[OutcomeSimulator] = None


def get_outcome_simulator() -> OutcomeSimulator:
    """Get the global outcome simulator."""
    global _outcome_simulator
    if _outcome_simulator is None:
        _outcome_simulator = OutcomeSimulator()
    return _outcome_simulator
