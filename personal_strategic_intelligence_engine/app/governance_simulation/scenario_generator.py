"""Scenario generator for governance stress testing.

Generates various types of stress scenarios to test governance stability.
"""
import hashlib
import random
from datetime import datetime
from typing import List, Optional

from app.governance_simulation.simulation_models import (
    GovernanceSimulationScenario,
    ScenarioType,
    SignalPattern,
)


# Default domains for signal generation
DEFAULT_DOMAINS = ["finance", "health", "operations", "strategy", "risk", "legacy"]

# Signal categories per domain
SIGNAL_CATEGORIES = {
    "finance": ["market_update", "portfolio_change", "budget_alert", "cashflow_update"],
    "health": ["vital_sign", "activity_update", "sleep_quality", "nutrition_update"],
    "operations": ["task_completion", "workflow_status", "resource_update", "bottleneck_detected"],
    "strategy": ["goal_progress", "milestone_achieved", "pivot_needed", "opportunity_identified"],
    "risk": ["threat_detected", "vulnerability_identified", "contingency_triggered", "mitigation_needed"],
    "legacy": ["maintenance_due", "deprecation_warning", "migration_ready", "archive_status"],
}


class ScenarioGenerator:
    """Generator for governance stress scenarios."""
    
    def __init__(self, random_seed: Optional[int] = None):
        """Initialize scenario generator with optional seed."""
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
    
    def generate_scenario(self, scenario_type: ScenarioType) -> GovernanceSimulationScenario:
        """Generate a scenario configuration based on type."""
        scenario_configs = {
            ScenarioType.STEADY_STATE: self._steady_state_config,
            ScenarioType.NOISY_SIGNAL: self._noisy_signal_config,
            ScenarioType.HIGH_VOLATILITY: self._high_volatility_config,
            ScenarioType.CONFLICTING_DOMAIN: self._conflicting_domain_config,
            ScenarioType.SIGNAL_RELIABILITY_DEGRADATION: self._reliability_degradation_config,
            ScenarioType.CONFIDENCE_SHOCK: self._confidence_shock_config,
            ScenarioType.RECOVERY: self._recovery_config,
            ScenarioType.ADVERSARIAL_POLICY_PRESSURE: self._adversarial_policy_config,
        }
        
        config_generator = scenario_configs.get(
            scenario_type, 
            self._steady_state_config
        )
        return config_generator()
    
    def _steady_state_config(self) -> GovernanceSimulationScenario:
        """Generate steady-state scenario with minimal noise."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.STEADY_STATE,
            name="Steady State Governance",
            description="Normal operating conditions with stable signals",
            cycle_count=100,
            signal_count_per_cycle=5,
            signal_noise_level=0.05,
            signal_volatility=0.05,
            signal_conflict_rate=0.02,
            domain_count=4,
            conflicting_domain_weight=0.0,
            execution_intent_rate=0.3,
            auto_approval_enabled=False,
        )
    
    def _noisy_signal_config(self) -> GovernanceSimulationScenario:
        """Generate noisy signal scenario."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.NOISY_SIGNAL,
            name="Noisy Signal Environment",
            description="High noise environment with unreliable signals",
            cycle_count=100,
            signal_count_per_cycle=10,
            signal_noise_level=0.7,
            signal_volatility=0.3,
            signal_conflict_rate=0.3,
            domain_count=5,
            conflicting_domain_weight=0.2,
            execution_intent_rate=0.4,
            auto_approval_enabled=False,
        )
    
    def _high_volatility_config(self) -> GovernanceSimulationScenario:
        """Generate high volatility scenario."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.HIGH_VOLATILITY,
            name="High Volatility Environment",
            description="Rapidly changing signal patterns",
            cycle_count=100,
            signal_count_per_cycle=8,
            signal_noise_level=0.3,
            signal_volatility=0.9,
            signal_conflict_rate=0.4,
            domain_count=6,
            conflicting_domain_weight=0.3,
            execution_intent_rate=0.5,
            auto_approval_enabled=False,
        )
    
    def _conflicting_domain_config(self) -> GovernanceSimulationScenario:
        """Generate conflicting domain scenario."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.CONFLICTING_DOMAIN,
            name="Conflicting Domain Signals",
            description="Conflicting signals from different domains",
            cycle_count=100,
            signal_count_per_cycle=6,
            signal_noise_level=0.2,
            signal_volatility=0.4,
            signal_conflict_rate=0.6,
            domain_count=6,
            conflicting_domain_weight=0.8,
            execution_intent_rate=0.35,
            auto_approval_enabled=False,
        )
    
    def _reliability_degradation_config(self) -> GovernanceSimulationScenario:
        """Generate signal reliability degradation scenario."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.SIGNAL_RELIABILITY_DEGRADATION,
            name="Signal Reliability Degradation",
            description="Progressive degradation of signal reliability",
            cycle_count=100,
            signal_count_per_cycle=7,
            signal_noise_level=0.4,
            signal_volatility=0.5,
            signal_conflict_rate=0.3,
            domain_count=4,
            conflicting_domain_weight=0.2,
            reliability_degradation_rate=0.02,
            execution_intent_rate=0.3,
            auto_approval_enabled=False,
        )
    
    def _confidence_shock_config(self) -> GovernanceSimulationScenario:
        """Generate confidence shock scenario."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.CONFIDENCE_SHOCK,
            name="Confidence Shock",
            description="Sudden changes in confidence levels",
            cycle_count=100,
            signal_count_per_cycle=5,
            signal_noise_level=0.2,
            signal_volatility=0.3,
            signal_conflict_rate=0.2,
            domain_count=4,
            confidence_shock_magnitude=0.8,
            execution_intent_rate=0.3,
            auto_approval_enabled=False,
        )
    
    def _recovery_config(self) -> GovernanceSimulationScenario:
        """Generate recovery scenario after stress."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.RECOVERY,
            name="Recovery Scenario",
            description="System recovering from stress condition",
            cycle_count=100,
            signal_count_per_cycle=5,
            signal_noise_level=0.15,
            signal_volatility=0.2,
            signal_conflict_rate=0.1,
            domain_count=4,
            execution_intent_rate=0.3,
            auto_approval_enabled=False,
        )
    
    def _adversarial_policy_config(self) -> GovernanceSimulationScenario:
        """Generate adversarial policy pressure scenario."""
        return GovernanceSimulationScenario(
            scenario_type=ScenarioType.ADVERSARIAL_POLICY_PRESSURE,
            name="Adversarial Policy Pressure",
            description="Intentional pressure on governance policy boundaries",
            cycle_count=100,
            signal_count_per_cycle=8,
            signal_noise_level=0.5,
            signal_volatility=0.6,
            signal_conflict_rate=0.5,
            domain_count=6,
            conflicting_domain_weight=0.6,
            execution_intent_rate=0.7,
            auto_approval_enabled=False,
        )
    
    def generate_signals(
        self,
        scenario: GovernanceSimulationScenario,
        cycle_number: int,
    ) -> List[SignalPattern]:
        """Generate signals for a given cycle based on scenario configuration."""
        signals = []
        
        # Calculate reliability degradation over time
        reliability_base = 1.0 - (cycle_number * scenario.reliability_degradation_rate)
        reliability_base = max(reliability_base, 0.1)
        
        # Calculate noise based on cycle for gradual changes
        cycle_noise_factor = min(1.0, cycle_number / 50)  # Gradual increase
        
        for i in range(scenario.signal_count_per_cycle):
            # Select domain with bias toward conflicting domains
            domain = self._select_domain(scenario, cycle_number)
            
            # Select category
            category = random.choice(SIGNAL_CATEGORIES.get(domain, ["generic"]))
            
            # Generate magnitude with volatility
            base_magnitude = random.uniform(-1.0, 1.0)
            if scenario.signal_volatility > 0:
                volatility_impact = random.gauss(0, scenario.signal_volatility)
                magnitude = base_magnitude + volatility_impact
                magnitude = max(-1.0, min(1.0, magnitude))
            else:
                magnitude = base_magnitude
            
            # Add noise
            noise = random.gauss(0, scenario.signal_noise_level * cycle_noise_factor)
            magnitude += noise
            magnitude = max(-1.0, min(1.0, magnitude))
            
            # Calculate reliability
            reliability = reliability_base - (scenario.signal_noise_level * cycle_noise_factor)
            reliability = max(0.1, min(1.0, reliability))
            
            # Create signal pattern
            signal = SignalPattern(
                pattern_id=f"signal_{cycle_number}_{i}_{domain}_{category}",
                domain=domain,
                category=category,
                magnitude=magnitude,
                reliability=reliability,
                timestamp=datetime.utcnow(),
            )
            signals.append(signal)
        
        # Add conflicting signals if configured
        if scenario.signal_conflict_rate > 0 and random.random() < scenario.signal_conflict_rate:
            conflicting_signal = self._generate_conflicting_signal(
                signals, 
                scenario,
                cycle_number
            )
            if conflicting_signal:
                signals.append(conflicting_signal)
        
        return signals
    
    def _select_domain(
        self, 
        scenario: GovernanceSimulationScenario, 
        cycle_number: int
    ) -> str:
        """Select a domain for signal generation."""
        if scenario.conflicting_domain_weight > 0 and random.random() < scenario.conflicting_domain_weight:
            # Prefer conflicting domains
            return random.choice(DEFAULT_DOMAINS[:scenario.domain_count])
        return random.choice(DEFAULT_DOMAINS[:max(1, scenario.domain_count)])
    
    def _generate_conflicting_signal(
        self,
        existing_signals: List[SignalPattern],
        scenario: GovernanceSimulationScenario,
        cycle_number: int,
    ) -> Optional[SignalPattern]:
        """Generate a signal that conflicts with existing signals."""
        if not existing_signals:
            return None
        
        # Find a domain that conflicts
        existing_domains = set(s.domain for s in existing_signals)
        conflicting_domains = [d for d in DEFAULT_DOMAINS if d not in existing_domains]
        
        if not conflicting_domains:
            return None
        
        domain = random.choice(conflicting_domains)
        category = random.choice(SIGNAL_CATEGORIES.get(domain, ["generic"]))
        
        # Magnitude opposite to existing average
        avg_magnitude = sum(s.magnitude for s in existing_signals) / len(existing_signals)
        magnitude = -avg_magnitude + random.uniform(-0.3, 0.3)
        magnitude = max(-1.0, min(1.0, magnitude))
        
        return SignalPattern(
            pattern_id=f"conflict_{cycle_number}_{domain}_{category}",
            domain=domain,
            category=category,
            magnitude=magnitude,
            reliability=0.7,
            timestamp=datetime.utcnow(),
        )
    
    def generate_confidence_shock(
        self,
        scenario: GovernanceSimulationScenario,
        cycle_number: int,
    ) -> float:
        """Generate confidence shock value for a cycle."""
        if scenario.confidence_shock_magnitude > 0:
            # Trigger shocks at specific intervals
            shock_cycle = cycle_number % 20
            if shock_cycle < 3:  # 3 consecutive cycles of shock
                return scenario.confidence_shock_magnitude * random.uniform(-1, 1)
        return 0.0
    
    def get_scenario_for_testing(self) -> GovernanceSimulationScenario:
        """Get a default scenario for testing purposes."""
        return self._steady_state_config()
    
    def get_all_scenario_types(self) -> List[ScenarioType]:
        """Get list of all available scenario types."""
        return list(ScenarioType)


def create_scenario_generator(seed: Optional[int] = None) -> ScenarioGenerator:
    """Factory function to create a scenario generator."""
    return ScenarioGenerator(random_seed=seed)
