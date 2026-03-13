"""Governance Simulator - Core orchestration for governance simulations.

Runs multi-cycle governance simulations with full governance pathway.
"""
import hashlib
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import ApprovalTierLevel
from app.governance_simulation.simulation_models import (
    GovernanceSimulationCycle,
    GovernanceSimulationResult,
    GovernanceSimulationScenario,
    ScenarioType,
    SimulationCyclePhase,
)
from app.governance_simulation.scenario_generator import ScenarioGenerator


class GovernanceSimulator:
    """Core orchestration engine for governance simulations."""
    
    def __init__(
        self,
        scenario: GovernanceSimulationScenario,
        scenario_generator: Optional[ScenarioGenerator] = None,
    ):
        """Initialize governance simulator."""
        self.scenario = scenario
        self.scenario_generator = scenario_generator or ScenarioGenerator(
            random_seed=scenario.random_seed
        )
        
        # State
        self.cycles: List[GovernanceSimulationCycle] = []
        self.current_state: Dict[str, Any] = {}
        self.current_tier = ApprovalTierLevel.TIER_0_MANUAL_ONLY
        self.execution_count = 0
        self.confidence_level = 0.5
        
        # Initialize state
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize simulation state."""
        self.current_state = {
            "domains": {},
            "goals": {},
            "active_recommendations": [],
            "pending_approvals": [],
            "executed_actions": [],
            "learning_history": [],
            "doctrine_confidence": 0.5,
        }
        
        # Initialize domains
        for domain in ["finance", "health", "operations", "strategy", "risk", "legacy"]:
            self.current_state["domains"][domain] = {
                "performance": 0.5,
                "risk": 0.3,
                "reliability": 0.7,
                "last_update": datetime.utcnow().isoformat(),
            }
    
    def run_simulation(self) -> GovernanceSimulationResult:
        """Run complete governance simulation."""
        start_time = time.time()
        
        # Create result object
        result = GovernanceSimulationResult(
            scenario_id=self.scenario.scenario_id,
            scenario_type=self.scenario.scenario_type,
            cycle_count=self.scenario.cycle_count,
            random_seed=self.scenario.random_seed,
            started_at=datetime.utcnow(),
        )
        
        # Run cycles
        for cycle_num in range(1, self.scenario.cycle_count + 1):
            cycle = self._run_cycle(cycle_num)
            self.cycles.append(cycle)
            
            # Update result counts
            result.signals_processed += len(cycle.signals)
            result.recommendations_generated += len(cycle.recommendations)
            result.execution_intents_generated += len(cycle.execution_intents)
            result.cycles.append(cycle)
            
            # Apply state updates
            self._apply_cycle_state(cycle)
        
        # Calculate duration
        result.completed_at = datetime.utcnow()
        result.duration_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _run_cycle(self, cycle_number: int) -> GovernanceSimulationCycle:
        """Run a single governance simulation cycle."""
        cycle_start = time.time()
        
        cycle = GovernanceSimulationCycle(
            cycle_id=f"cycle_{cycle_number}",
            scenario_id=self.scenario.scenario_id,
            cycle_number=cycle_number,
        )
        
        # Phase 1: Signal Ingestion
        phase_start = time.time()
        signals = self.scenario_generator.generate_signals(
            self.scenario, 
            cycle_number
        )
        cycle.signals = signals
        cycle.phase_durations_ms[SimulationCyclePhase.SIGNAL_INGESTION.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 2: State Update
        phase_start = time.time()
        self._update_state(signals, cycle)
        cycle.state_snapshot = self.current_state.copy()
        cycle.phase_durations_ms[SimulationCyclePhase.STATE_UPDATE.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 3: Forecasting
        phase_start = time.time()
        optimization_output = self._run_forecasting(cycle)
        cycle.optimization_output = optimization_output
        cycle.phase_durations_ms[SimulationCyclePhase.FORECASTING.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 4: Doctrine Evaluation
        phase_start = time.time()
        doctrine_assessment = self._run_doctrine_evaluation(cycle)
        cycle.doctrine_assessment = doctrine_assessment
        cycle.phase_durations_ms[SimulationCyclePhase.DOCTRINE_EVALUATION.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 5: Recommendation Generation
        phase_start = time.time()
        recommendations = self._generate_recommendations(cycle)
        cycle.recommendations = recommendations
        cycle.phase_durations_ms[SimulationCyclePhase.RECOMMENDATION_GENERATION.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 6: Execution Intent Formation
        phase_start = time.time()
        execution_intents = self._form_execution_intents(cycle)
        cycle.execution_intents = execution_intents
        cycle.phase_durations_ms[SimulationCyclePhase.EXECUTION_INTENT.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 7: Governance Gates
        phase_start = time.time()
        gate_results = self._run_governance_gates(cycle)
        cycle.governance_gate_results = gate_results
        cycle.phase_durations_ms[SimulationCyclePhase.GOVERNANCE_GATES.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 8: Execution Outcome (simulated)
        phase_start = time.time()
        outcome = self._simulate_execution_outcome(cycle)
        cycle.execution_outcome = outcome
        cycle.phase_durations_ms[SimulationCyclePhase.EXECUTION_OUTCOME.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 9: Learning Update
        phase_start = time.time()
        learning_update = self._run_learning_update(cycle)
        cycle.learning_update = learning_update
        cycle.phase_durations_ms[SimulationCyclePhase.LEARNING_UPDATE.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Phase 10: Approval Policy Reassessment
        phase_start = time.time()
        new_tier = self._reassess_approval_policy(cycle)
        cycle.current_tier = new_tier.value
        self.current_tier = new_tier
        cycle.phase_durations_ms[SimulationCyclePhase.APPROVAL_REASSESSMENT.value] = (
            time.time() - phase_start
        ) * 1000
        
        # Total cycle duration
        cycle.cycle_duration_ms = (time.time() - cycle_start) * 1000
        
        return cycle
    
    def _update_state(
        self,
        signals: List[Any],
        cycle: GovernanceSimulationCycle,
    ) -> None:
        """Update simulation state based on signals."""
        # Process each signal
        for signal in signals:
            domain = signal.domain
            if domain in self.current_state["domains"]:
                # Update domain state
                domain_state = self.current_state["domains"][domain]
                
                # Apply magnitude with decay
                old_performance = domain_state["performance"]
                new_performance = old_performance + (signal.magnitude * 0.1)
                domain_state["performance"] = max(0.0, min(1.0, new_performance))
                
                # Update reliability based on signal reliability
                domain_state["reliability"] = signal.reliability
                
                # Update risk inversely to performance
                domain_state["risk"] = 1.0 - domain_state["performance"]
                
                domain_state["last_update"] = datetime.utcnow().isoformat()
        
        # Apply confidence shock if configured
        confidence_shock = self.scenario_generator.generate_confidence_shock(
            self.scenario,
            cycle.cycle_number
        )
        if confidence_shock != 0:
            self.confidence_level += confidence_shock * 0.2
            self.confidence_level = max(0.0, min(1.0, self.confidence_level))
    
    def _run_forecasting(self, cycle: GovernanceSimulationCycle) -> Dict[str, Any]:
        """Run forecasting/optimization (simulated)."""
        # Simulate forecasting output
        domains = list(self.current_state["domains"].keys())
        
        forecasts = {}
        for domain in domains:
            domain_state = self.current_state["domains"][domain]
            forecasts[domain] = {
                "predicted_performance": domain_state["performance"] + random.uniform(-0.1, 0.1),
                "risk_projection": domain_state["risk"],
                "confidence": self.confidence_level,
                "trend": "stable" if domain_state["performance"] > 0.5 else "declining",
            }
        
        return {
            "forecasts": forecasts,
            "optimization_targets": random.sample(domains, min(2, len(domains))),
            "confidence": self.confidence_level,
        }
    
    def _run_doctrine_evaluation(self, cycle: GovernanceSimulationCycle) -> Dict[str, Any]:
        """Run doctrine evaluation (simulated)."""
        # Calculate alignment based on state
        avg_performance = sum(
            d["performance"] for d in self.current_state["domains"].values()
        ) / len(self.current_state["domains"])
        
        # Base alignment score
        alignment_score = (avg_performance * 2) - 1  # -1 to 1
        alignment_score = max(-1.0, min(1.0, alignment_score))
        
        # Determine alignment level
        if alignment_score > 0.3:
            alignment_level = "aligned"
        elif alignment_score < -0.3:
            alignment_level = "misaligned"
        elif abs(alignment_score) < 0.1:
            alignment_level = "neutral"
        else:
            alignment_level = "requires_review"
        
        # Generate risk flags based on conditions
        risk_flags = []
        if self.current_state["domains"]["risk"]["performance"] > 0.7:
            risk_flags.append("high_risk_domain_active")
        if self.confidence_level < 0.3:
            risk_flags.append("low_confidence")
        
        # Generate doctrine conflicts based on scenario
        conflicts = []
        if self.scenario.scenario_type == ScenarioType.CONFLICTING_DOMAIN:
            conflicts.append({
                "conflict_type": "domain_conflict",
                "severity": "medium",
                "description": "Conflicting signals across domains detected",
            })
        
        return {
            "alignment_score": alignment_score,
            "alignment_level": alignment_level,
            "confidence": self.confidence_level,
            "risk_flags": risk_flags,
            "doctrine_conflicts": conflicts,
            "rules_applied": ["risk_management", "strategic_alignment"],
        }
    
    def _generate_recommendations(self, cycle: GovernanceSimulationCycle) -> List[Dict[str, Any]]:
        """Generate recommendations based on state."""
        recommendations = []
        
        # Generate recommendations for domains below threshold
        for domain, domain_state in self.current_state["domains"].items():
            if domain_state["performance"] < 0.4:
                recommendations.append({
                    "recommendation_id": f"rec_{cycle.cycle_number}_{domain}",
                    "domain": domain,
                    "action_type": "improve_performance",
                    "priority": 1.0 - domain_state["performance"],
                    "confidence": self.confidence_level,
                    "rationale": f"{domain} performance below threshold",
                })
        
        return recommendations
    
    def _form_execution_intents(self, cycle: GovernanceSimulationCycle) -> List[Dict[str, Any]]:
        """Form execution intents from recommendations."""
        intents = []
        
        # Only form intents based on configured rate
        if random.random() > self.scenario.execution_intent_rate:
            return intents
        
        for rec in cycle.recommendations:
            # Form intent with probability based on tier
            if self.current_tier in [
                ApprovalTierLevel.TIER_0_MANUAL_ONLY,
                ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
            ]:
                # Manual tiers: form intent but require approval
                intents.append({
                    "intent_id": f"intent_{cycle.cycle_number}_{rec['domain']}",
                    "recommendation_id": rec["recommendation_id"],
                    "domain": rec["domain"],
                    "action_type": rec["action_type"],
                    "confidence": rec["confidence"] * self.confidence_level,
                    "requires_approval": True,
                    "approved": False,
                })
            elif self.current_tier == ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO:
                # Conditional auto: may auto-approve low-risk
                is_low_risk = random.random() < 0.3
                intents.append({
                    "intent_id": f"intent_{cycle.cycle_number}_{rec['domain']}",
                    "recommendation_id": rec["recommendation_id"],
                    "domain": rec["domain"],
                    "action_type": rec["action_type"],
                    "confidence": rec["confidence"] * self.confidence_level,
                    "requires_approval": not is_low_risk,
                    "approved": is_low_risk,
                })
        
        return intents
    
    def _run_governance_gates(self, cycle: GovernanceSimulationCycle) -> Dict[str, Any]:
        """Run governance gate checks."""
        gate_results = {
            "policy_gate": {
                "passed": True,
                "violations": [],
            },
            "doctrine_gate": {
                "passed": cycle.doctrine_assessment.get("alignment_level") != "misaligned",
                "risk_flags": cycle.doctrine_assessment.get("risk_flags", []),
            },
            "risk_gate": {
                "passed": True,
                "risk_level": "low",
            },
            "approval_gate": {
                "passed": True,
                "required": True,
            },
        }
        
        # Fail gates based on scenario conditions
        if self.scenario.scenario_type == ScenarioType.HIGH_VOLATILITY:
            if random.random() < 0.1:
                gate_results["doctrine_gate"]["passed"] = False
                gate_results["doctrine_gate"]["risk_flags"].append("volatility_breach")
        
        return gate_results
    
    def _simulate_execution_outcome(self, cycle: GovernanceSimulationCycle) -> Dict[str, Any]:
        """Simulate execution outcome (no real execution)."""
        # Simulate outcomes for intents
        executed = []
        failed = []
        
        for intent in cycle.execution_intents:
            if intent.get("approved", False) or random.random() < 0.5:
                # Simulate execution success
                executed.append({
                    "intent_id": intent["intent_id"],
                    "status": "executed",
                    "domain": intent["domain"],
                })
            else:
                failed.append({
                    "intent_id": intent["intent_id"],
                    "status": "rejected",
                    "reason": "approval_required",
                })
        
        return {
            "executed": executed,
            "failed": failed,
            "total_executed": len(executed),
            "total_failed": len(failed),
        }
    
    def _run_learning_update(self, cycle: GovernanceSimulationCycle) -> Dict[str, Any]:
        """Run learning update from cycle."""
        # Update confidence based on outcomes
        outcome = cycle.execution_outcome
        
        if outcome and outcome.get("total_executed", 0) > 0:
            # Positive learning from success
            success_rate = outcome["total_executed"] / (
                outcome["total_executed"] + outcome.get("total_failed", 0)
            )
            
            # Update confidence (bounded)
            confidence_delta = (success_rate - 0.5) * 0.1
            self.confidence_level = max(
                0.1, 
                min(0.9, self.confidence_level + confidence_delta)
            )
        
        return {
            "confidence_updated": True,
            "new_confidence": self.confidence_level,
            "outcomes_learned": outcome.get("total_executed", 0) if outcome else 0,
        }
    
    def _reassess_approval_policy(self, cycle: GovernanceSimulationCycle) -> ApprovalTierLevel:
        """Reassess and potentially change approval tier."""
        # Simple tier reassessment logic
        confidence = self.confidence_level
        
        # Count recent successes
        recent_success_rate = 0.7  # Default assumption
        
        if self.execution_count > 10:
            recent_success_rate = 0.8
        
        # Determine tier
        if confidence > 0.8 and recent_success_rate > 0.9:
            return ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO
        elif confidence > 0.6 and recent_success_rate > 0.7:
            return ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH
        else:
            return ApprovalTierLevel.TIER_0_MANUAL_ONLY
    
    def _apply_cycle_state(self, cycle: GovernanceSimulationCycle) -> None:
        """Apply cycle results to persistent state."""
        # Update execution count
        if cycle.execution_outcome:
            self.execution_count += cycle.execution_outcome.get("total_executed", 0)
        
        # Update doctrine confidence
        self.current_state["doctrine_confidence"] = self.confidence_level
        
        # Add to learning history
        self.current_state["learning_history"].append({
            "cycle": cycle.cycle_number,
            "confidence": self.confidence_level,
            "executed": cycle.execution_outcome.get("total_executed", 0) if cycle.execution_outcome else 0,
        })


def create_governance_simulator(
    scenario: GovernanceSimulationScenario,
    seed: Optional[int] = None,
) -> GovernanceSimulator:
    """Factory function to create a governance simulator."""
    generator = ScenarioGenerator(random_seed=seed or scenario.random_seed)
    return GovernanceSimulator(scenario=scenario, scenario_generator=generator)


def run_governance_simulation(
    scenario_type: ScenarioType,
    cycle_count: int = 100,
    seed: Optional[int] = None,
) -> GovernanceSimulationResult:
    """Convenience function to run a governance simulation."""
    generator = ScenarioGenerator(random_seed=seed)
    scenario = generator.generate_scenario(scenario_type)
    scenario.cycle_count = cycle_count
    
    simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
    return simulator.run_simulation()
