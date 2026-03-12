"""Enhanced Simulation Engine - Complete engine for strategic scenario simulation."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.strategy_simulation.simulation_types import (
    SimulationCycle,
    SimulationPolicy,
    SimulationStatus,
    ScenarioType,
    StrategyDecision,
    CandidateStrategy,
    SimulatedOutcome,
    StrategyScore,
    ScenarioEnvironment,
    StrategyComparison,
    SimulationRecommendation,
    StrategyType,
)
from app.strategy_simulation.decision_model import DecisionModel, get_decision_model
from app.strategy_simulation.outcome_simulator import OutcomeSimulator, get_outcome_simulator
from app.strategy_simulation.strategy_comparator import StrategyComparator, get_strategy_comparator
from app.strategy_simulation.simulation_logger import get_simulation_logger


class EnhancedSimulationEngine:
    """Enhanced simulation engine for strategic scenarios."""
    
    def __init__(self, policy: Optional[SimulationPolicy] = None):
        self.policy = policy or SimulationPolicy()
        self.decision_model = get_decision_model()
        self.outcome_simulator = get_outcome_simulator()
        self.comparator = get_strategy_comparator()
        self.logger = get_simulation_logger()
        self.cycles: List[SimulationCycle] = []
    
    def run_simulation_cycle(
        self,
        current_domains: Dict[str, float],
        current_risks: Optional[Dict[str, float]] = None,
        strategies: Optional[List[CandidateStrategy]] = None,
    ) -> SimulationCycle:
        """Run a complete simulation cycle."""
        
        cycle_id = str(uuid.uuid4())[:8]
        
        if current_risks is None:
            current_risks = {d: 5.0 for d in current_domains}
        
        # Start logging
        self.logger.log_simulation_start(cycle_id, current_domains, len(strategies or []))
        
        # Create cycle
        cycle = SimulationCycle(
            cycle_id=cycle_id,
            timestamp=datetime.utcnow(),
            status=SimulationStatus.RUNNING,
            current_domains=current_domains,
            current_risks=current_risks,
        )
        
        # Generate candidate strategies
        if strategies is None:
            strategies = self._generate_candidate_strategies()
        
        strategies = strategies[:self.policy.max_candidate_strategies]
        cycle.candidate_strategies = strategies
        
        # Generate scenario environments
        scenarios = self._create_scenario_environments()
        cycle.scenarios = scenarios
        
        # Get time horizons
        horizons = self.policy.time_horizons
        
        # Simulate baseline (no change)
        baseline_outcome = self._simulate_baseline(
            current_domains, horizons[0], scenarios[0]
        )
        
        # Simulate each strategy in each scenario
        all_outcomes = []
        
        for strategy in strategies:
            for scenario in scenarios[:self.policy.max_scenarios_per_strategy]:
                outcome = self._simulate_strategy(
                    strategy, current_domains, horizons[0], scenario
                )
                all_outcomes.append(outcome)
        
        cycle.outcomes = all_outcomes
        
        # Calculate strategy scores
        scores = self._calculate_strategy_scores(strategies, all_outcomes, scenarios)
        cycle.scores = scores
        
        # Compare strategies
        comparison = self._compare_strategies(
            baseline_outcome, strategies, all_outcomes, scores
        )
        cycle.comparison = comparison
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            comparison, strategies, current_domains
        )
        cycle.recommendation = recommendation
        
        # Set summary
        cycle.best_strategy = comparison.recommended_strategy
        cycle.execution_recommended = (
            comparison.recommended_strategy is not None and
            cycle.confidence_level >= self.policy.min_confidence_threshold
        )
        cycle.confidence_level = self._calculate_confidence(scores)
        cycle.status = SimulationStatus.COMPLETED
        
        # Log completion
        self.logger.log_simulation_complete(
            cycle_id,
            cycle.best_strategy or "",
            cycle.execution_recommended,
            cycle.confidence_level
        )
        
        self.cycles.append(cycle)
        
        return cycle
    
    def _generate_candidate_strategies(self) -> List[CandidateStrategy]:
        """Generate candidate strategies from decision model."""
        
        decisions = self.decision_model.get_all_strategies()
        
        strategies = []
        for decision in decisions:
            strategy = CandidateStrategy(
                strategy_id=decision.decision_id,
                strategy_name=decision.name,
                description=decision.description,
                strategy_type=decision.strategy_type,
                affected_domains=decision.affected_domains,
                total_resource_changes=decision.resource_changes,
                expected_outcome=decision.expected_outcome,
                priority=decision.priority,
            )
            strategies.append(strategy)
        
        return strategies
    
    def _create_scenario_environments(self) -> List[ScenarioEnvironment]:
        """Create scenario environments for stress testing."""
        
        return [
            # 1. Baseline
            ScenarioEnvironment(
                scenario_id="baseline",
                scenario_type=ScenarioType.BASELINE_ENVIRONMENT,
                name="Baseline Environment",
                description="Normal operating conditions",
                external_pressure_level=0.5,
                opportunity_density=0.5,
                disruption_frequency=0.2,
                volatility_level=0.3,
                domain_modifiers={},
                probability=0.40,
            ),
            # 2. Economic Stress
            ScenarioEnvironment(
                scenario_id="economic_stress",
                scenario_type=ScenarioType.ECONOMIC_STRESS,
                name="Economic Stress",
                description="Challenging economic conditions",
                external_pressure_level=0.8,
                opportunity_density=0.3,
                disruption_frequency=0.6,
                volatility_level=0.8,
                domain_modifiers={"wealth": -0.3, "career": -0.2},
                probability=0.20,
            ),
            # 3. Unexpected Opportunity
            ScenarioEnvironment(
                scenario_id="opportunity",
                scenario_type=ScenarioType.UNEXPECTED_OPPORTUNITY,
                name="Unexpected Opportunity",
                description="Major opportunity emerges",
                external_pressure_level=0.3,
                opportunity_density=0.9,
                disruption_frequency=0.3,
                volatility_level=0.4,
                domain_modifiers={"career": 0.3, "wealth": 0.2},
                probability=0.15,
            ),
            # 4. Execution Overload
            ScenarioEnvironment(
                scenario_id="execution_overload",
                scenario_type=ScenarioType.EXECUTION_OVERLOAD,
                name="Execution Overload",
                description="Too many initiatives, capacity strain",
                external_pressure_level=0.6,
                opportunity_density=0.5,
                disruption_frequency=0.7,
                volatility_level=0.5,
                domain_modifiers={"operations": -0.3, "health": -0.2},
                probability=0.15,
            ),
            # 5. Health Disruption
            ScenarioEnvironment(
                scenario_id="health_disruption",
                scenario_type=ScenarioType.HEALTH_DISRUPTION,
                name="Health Disruption",
                description="Health challenge emerges",
                external_pressure_level=0.5,
                opportunity_density=0.4,
                disruption_frequency=0.8,
                volatility_level=0.4,
                domain_modifiers={"health": -0.5, "operations": -0.2, "wealth": -0.1},
                probability=0.10,
            ),
        ]
    
    def _simulate_baseline(
        self,
        current_domains: Dict[str, float],
        days: int,
        environment: ScenarioEnvironment,
    ) -> SimulatedOutcome:
        """Simulate baseline (continue current approach)."""
        
        baseline_strategy = StrategyDecision(
            decision_id="baseline",
            name="Continue Current Approach",
            description="No strategic change",
            strategy_type=StrategyType.FOCUS_SHIFT,
            resource_changes={},
            priority=0.5,
        )
        
        return self.outcome_simulator.simulate_outcome(
            baseline_strategy, current_domains, days, environment
        )
    
    def _simulate_strategy(
        self,
        strategy: CandidateStrategy,
        current_domains: Dict[str, float],
        days: int,
        environment: ScenarioEnvironment,
    ) -> SimulatedOutcome:
        """Simulate a strategy in a scenario."""
        
        # Convert to StrategyDecision
        decision = StrategyDecision(
            decision_id=strategy.strategy_id,
            name=strategy.strategy_name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            affected_domains=strategy.affected_domains,
            resource_changes=strategy.total_resource_changes,
            expected_outcome=strategy.expected_outcome,
            priority=strategy.priority,
        )
        
        outcome = self.outcome_simulator.simulate_outcome(
            decision, current_domains, days, environment
        )
        
        outcome.scenario_type = environment.scenario_type
        
        return outcome
    
    def _calculate_strategy_scores(
        self,
        strategies: List[CandidateStrategy],
        outcomes: List[SimulatedOutcome],
        scenarios: List[ScenarioEnvironment],
    ) -> List[StrategyScore]:
        """Calculate detailed scores for each strategy."""
        
        scores = []
        
        for strategy in strategies:
            # Get outcomes for this strategy
            strategy_outcomes = [
                o for o in outcomes if o.strategy_id == strategy.strategy_id
            ]
            
            if not strategy_outcomes:
                continue
            
            # Calculate metrics
            outcome_scores = [o.overall_score for o in strategy_outcomes]
            avg_score = sum(outcome_scores) / len(outcome_scores)
            
            # Best/worst case
            best_case = max(outcome_scores)
            worst_case = min(outcome_scores)
            
            # Downside risk (how bad is worst case)
            downside = 10 - worst_case
            
            # Expected value
            expected_value = avg_score
            
            # Risk score (based on variance)
            variance = sum((s - avg_score) ** 2 for s in outcome_scores) / len(outcome_scores)
            risk_score = min(1.0, (variance ** 0.5) / 3)
            
            # Resilience (how well it performs in bad scenarios)
            stress_outcomes = [
                o for o in strategy_outcomes 
                if o.scenario_type in [ScenarioType.ECONOMIC_STRESS, ScenarioType.EXECUTION_OVERLOAD]
            ]
            resilience = (
                sum(o.overall_score for o in stress_outcomes) / len(stress_outcomes)
                if stress_outcomes else avg_score
            )
            
            # Balance (domain distribution)
            perf_changes = [o.expected_performance_gain for o in strategy_outcomes]
            balance = 1.0 - (max(perf_changes) - min(perf_changes)) / 10
            
            # Collapse avoidance
            collapse_avoidance = sum(
                1 for o in strategy_outcomes if o.expected_performance_gain > -1.0
            ) / len(strategy_outcomes)
            
            # Goal improvement
            goal_change = 0.0
            if strategy_outcomes and strategy_outcomes[0].goal_probability_change:
                gpc = strategy_outcomes[0].goal_probability_change
                if isinstance(gpc, dict):
                    goal_change = sum(gpc.values()) / len(gpc) if gpc else 0
            
            score = StrategyScore(
                strategy_id=strategy.strategy_id,
                expected_value=expected_value,
                risk_score=risk_score,
                resilience_score=resilience,
                balance_score=balance,
                average_outcome_score=avg_score,
                downside_risk_score=downside,
                best_case_outcome=best_case,
                worst_case_outcome=worst_case,
                collapse_avoidance_score=collapse_avoidance,
                domain_balance_preservation=balance,
                goal_probability_improvement=goal_change,
                expected_interventions=0,
            )
            
            scores.append(score)
        
        return scores
    
    def _compare_strategies(
        self,
        baseline: SimulatedOutcome,
        strategies: List[CandidateStrategy],
        outcomes: List[SimulatedOutcome],
        scores: List[StrategyScore],
    ) -> StrategyComparison:
        """Compare strategies and generate rankings."""
        
        comparison_id = str(uuid.uuid4())[:8]
        
        # Sort by overall score (weighted)
        sorted_scores = sorted(
            scores,
            key=lambda s: (
                s.expected_value * self.policy.expected_value_weight +
                (1 - s.risk_score) * self.policy.risk_weight +
                s.resilience_score * self.policy.resilience_weight +
                s.balance_score * self.policy.balance_weight
            ),
            reverse=True
        )
        
        best = sorted_scores[0] if sorted_scores else None
        worst = sorted_scores[-1] if sorted_scores else None
        
        # Most resilient
        most_resilient = max(scores, key=lambda s: s.resilience_score) if scores else None
        
        # Recommendation
        recommended = best.strategy_id if best else None
        
        # Generate reason
        reason = ""
        if best:
            reason = f"Highest overall score with expected value {best.expected_value:.2f}, "
            reason += f"resilience {best.resilience_score:.2f}, and balance {best.balance_score:.2f}"
        
        comparison = StrategyComparison(
            comparison_id=comparison_id,
            timestamp=datetime.utcnow(),
            baseline_outcome=baseline,
            strategy_outcomes=outcomes,
            strategy_scores=sorted_scores,
            best_strategy=best.strategy_id if best else None,
            worst_strategy=worst.strategy_id if worst else None,
            most_resilient_strategy=most_resilient.strategy_id if most_resilient else None,
            recommended_strategy=recommended,
            recommendation_reason=reason,
        )
        
        return comparison
    
    def _generate_recommendation(
        self,
        comparison: StrategyComparison,
        strategies: List[CandidateStrategy],
        current_domains: Dict[str, float],
    ) -> SimulationRecommendation:
        """Generate final strategy recommendation."""
        
        if not comparison.recommended_strategy:
            return SimulationRecommendation(
                recommended_strategy_id="none",
                strategy_name="No Recommendation",
                reasoning="Insufficient data for recommendation",
            )
        
        # Find recommended strategy
        strategy = next(
            (s for s in strategies if s.strategy_id == comparison.recommended_strategy),
            None
        )
        
        if not strategy:
            return SimulationRecommendation(
                recommended_strategy_id="none",
                strategy_name="Strategy Not Found",
                reasoning="Could not find recommended strategy",
            )
        
        # Find best alternative (second-best)
        scores = comparison.strategy_scores
        alternative = scores[1] if len(scores) > 1 else None
        
        # Expected benefits
        benefits = [
            f"Expected performance gain: +{s.average_outcome_score:.2f}" for s in scores[:1]
        ]
        
        # Expected risks
        risks = [
            f"Downside risk: {s.downside_risk_score:.2f}" if s.downside_risk_score > 3 else "Low risk exposure"
            for s in scores[:1]
        ]
        
        # Projected effects
        projected = {}
        for outcome in comparison.strategy_outcomes:
            if outcome.strategy_id == comparison.recommended_strategy:
                projected = outcome.projected_domains
                break
        
        # Key assumptions
        assumptions = [
            "Current trends continue",
            "External conditions remain stable",
            "Resources available as planned",
        ]
        
        return SimulationRecommendation(
            recommended_strategy_id=strategy.strategy_id,
            strategy_name=strategy.strategy_name,
            reasoning=comparison.recommendation_reason,
            expected_benefits=benefits,
            expected_risks=risks,
            projected_effects=projected,
            alternative_strategy_id=alternative.strategy_id if alternative else None,
            alternative_reason="Alternative if primary conditions worsen",
            key_assumptions=assumptions,
        )
    
    def _calculate_confidence(self, scores: List[StrategyScore]) -> float:
        """Calculate confidence in the recommendation."""
        
        if not scores:
            return 0.0
        
        # Based on score variance
        avg = sum(s.expected_value for s in scores) / len(scores)
        variance = sum((s.expected_value - avg) ** 2 for s in scores) / len(scores)
        
        # Low variance = high confidence
        confidence = 1.0 - min(1.0, (variance ** 0.5) / 3)
        
        # Adjust by number of strategies
        if len(scores) < 3:
            confidence *= 0.7
        
        return confidence
    
    def get_recommendation(self) -> Optional[SimulationRecommendation]:
        """Get the current recommendation."""
        if self.cycles:
            return self.cycles[-1].recommendation
        return None
    
    def get_history(self, limit: int = 10) -> List[SimulationCycle]:
        """Get recent simulation cycles."""
        return self.cycles[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics."""
        
        return {
            "total_cycles": len(self.cycles),
            "strategies_evaluated": sum(len(c.candidate_strategies) for c in self.cycles),
            "recommendations_generated": sum(1 for c in self.cycles if c.recommendation),
        }


# Global engine
_simulation_engine = None


def get_simulation_engine() -> EnhancedSimulationEngine:
    """Get the global simulation engine."""
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = EnhancedSimulationEngine()
    return _simulation_engine
