"""Execution feedback analyzer for governance simulations.

Analyzes execution-intent and outcome feedback under simulation conditions.
"""
from typing import Any, Dict, List

from app.governance_simulation.simulation_models import (
    GovernanceSimulationCycle,
    GovernanceSimulationScenario,
)


class ExecutionFeedbackAnalyzer:
    """Analyzer for execution feedback in simulations."""
    
    def __init__(self):
        """Initialize execution feedback analyzer."""
        pass
    
    def analyze_execution_pressure(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Analyze execution pressure vs signal severity."""
        if not cycles:
            return {"pressure_score": 0.0, "analysis": "No cycles"}
        
        # Calculate execution intent rate per cycle
        intent_rates = []
        for cycle in cycles:
            num_intents = len(cycle.execution_intents)
            intent_rates.append(num_intents)
        
        avg_intents = sum(intent_rates) / len(intent_rates)
        
        # Calculate pressure based on rate
        pressure_score = min(avg_intents / 5.0, 1.0)  # Normalize to 0-1
        
        # Identify cycles with high pressure
        high_pressure_cycles = [
            i + 1 for i, rate in enumerate(intent_rates) 
            if rate > avg_intents * 2
        ]
        
        return {
            "pressure_score": pressure_score,
            "avg_intents_per_cycle": avg_intents,
            "max_intents": max(intent_rates),
            "min_intents": min(intent_rates),
            "high_pressure_cycles": high_pressure_cycles,
            "total_intents": sum(intent_rates),
        }
    
    def detect_overproduction(
        self,
        cycles: List[GovernanceSimulationCycle],
        threshold: int = 10,
    ) -> Dict[str, Any]:
        """Detect overproduction of execution intents from minor signals."""
        overproduction_events = []
        
        for cycle in cycles:
            # Get signal count
            signal_count = len(cycle.signals)
            
            # Get execution intent count
            intent_count = len(cycle.execution_intents)
            
            # Check ratio
            if signal_count > 0:
                ratio = intent_count / signal_count
                
                if ratio > threshold:
                    overproduction_events.append({
                        "cycle": cycle.cycle_number,
                        "signal_count": signal_count,
                        "intent_count": intent_count,
                        "ratio": ratio,
                    })
        
        return {
            "overproduction_detected": len(overproduction_events) > 0,
            "event_count": len(overproduction_events),
            "events": overproduction_events,
            "overproduction_ratio": len(overproduction_events) / max(1, len(cycles)),
        }
    
    def detect_learning_overreaction(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Detect learning overreaction to outcomes."""
        if len(cycles) < 2:
            return {"overreaction_detected": False}
        
        # Track confidence changes
        confidence_changes = []
        
        for i in range(1, len(cycles)):
            prev_conf = cycles[i-1].doctrine_assessment.get("confidence", 0.5) if cycles[i-1].doctrine_assessment else 0.5
            curr_conf = cycles[i].doctrine_assessment.get("confidence", 0.5) if cycles[i].doctrine_assessment else 0.5
            
            change = abs(curr_conf - prev_conf)
            confidence_changes.append(change)
        
        if not confidence_changes:
            return {"overreaction_detected": False}
        
        # Calculate statistics
        avg_change = sum(confidence_changes) / len(confidence_changes)
        max_change = max(confidence_changes)
        
        # Detect overreaction (large sudden changes)
        overreaction_threshold = 0.2  # 20% change in one cycle
        overreaction_cycles = [
            i + 2 for i, change in enumerate(confidence_changes)
            if change > overreaction_threshold
        ]
        
        return {
            "overreaction_detected": len(overreaction_cycles) > 0,
            "avg_confidence_change": avg_change,
            "max_confidence_change": max_change,
            "overreaction_cycles": overreaction_cycles,
            "overreaction_count": len(overreaction_cycles),
        }
    
    def assess_audit_quality(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Assess quality of audit/reliability signals."""
        # Check if execution outcomes are being recorded
        cycles_with_outcomes = sum(
            1 for cycle in cycles 
            if cycle.execution_outcome is not None
        )
        
        # Check if learning updates are happening
        cycles_with_learning = sum(
            1 for cycle in cycles 
            if cycle.learning_update and cycle.learning_update.get("confidence_updated", False)
        )
        
        total_cycles = len(cycles)
        
        return {
            "outcome_recording_rate": cycles_with_outcomes / max(1, total_cycles),
            "learning_update_rate": cycles_with_learning / max(1, total_cycles),
            "cycles_with_outcomes": cycles_with_outcomes,
            "cycles_with_learning": cycles_with_learning,
            "quality_score": (
                (cycles_with_outcomes / max(1, total_cycles)) * 0.5 +
                (cycles_with_learning / max(1, total_cycles)) * 0.5
            ),
        }
    
    def analyze_execution_domain_distribution(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Analyze distribution of execution intents across domains."""
        domain_counts: Dict[str, int] = {}
        
        for cycle in cycles:
            for intent in cycle.execution_intents:
                domain = intent.get("domain", "unknown")
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        if not domain_counts:
            return {"distribution": {}, "balanced": True}
        
        # Calculate distribution metrics
        total = sum(domain_counts.values())
        distribution = {
            domain: count / total 
            for domain, count in domain_counts.items()
        }
        
        # Check balance (no domain should dominate)
        max_share = max(distribution.values())
        balanced = max_share < 0.6  # No single domain > 60%
        
        return {
            "distribution": distribution,
            "balanced": balanced,
            "dominant_domain": max(domain_counts, key=domain_counts.get) if domain_counts else None,
            "domain_count": len(domain_counts),
        }
    
    def run_full_analysis(
        self,
        scenario: GovernanceSimulationScenario,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Run complete execution feedback analysis."""
        return {
            "execution_pressure": self.analyze_execution_pressure(cycles),
            "overproduction": self.detect_overproduction(cycles),
            "learning_overreaction": self.detect_learning_overreaction(cycles),
            "audit_quality": self.assess_audit_quality(cycles),
            "domain_distribution": self.analyze_execution_domain_distribution(cycles),
        }


def analyze_execution_feedback(
    scenario: GovernanceSimulationScenario,
    cycles: List[GovernanceSimulationCycle],
) -> Dict[str, Any]:
    """Convenience function to analyze execution feedback."""
    analyzer = ExecutionFeedbackAnalyzer()
    return analyzer.run_full_analysis(scenario, cycles)
