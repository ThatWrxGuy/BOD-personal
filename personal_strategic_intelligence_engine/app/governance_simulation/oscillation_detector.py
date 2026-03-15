"""Oscillation detector for governance simulations.

Detects recommendation and policy oscillations in governance behavior.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.governance_simulation.simulation_models import (
    GovernanceSimulationCycle,
    OscillationEvent,
    OscillationType,
)


class OscillationDetector:
    """Detector for recommendation and policy oscillations."""
    
    def __init__(self, min_reversals: int = 2, severity_threshold: float = 0.3):
        """Initialize oscillation detector.
        
        Args:
            min_reversals: Minimum reversals to trigger oscillation detection
            severity_threshold: Threshold for severity classification
        """
        self.min_reversals = min_reversals
        self.severity_threshold = severity_threshold
    
    def detect_all_oscillations(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[OscillationEvent]:
        """Detect all types of oscillations in simulation cycles."""
        events = []
        
        # Detect different oscillation types
        events.extend(self.detect_recommendation_reversals(cycles))
        events.extend(self.detect_priority_flapping(cycles))
        events.extend(self.detect_confidence_swings(cycles))
        events.extend(self.detect_policy_alternation(cycles))
        
        return events
    
    def detect_recommendation_reversals(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[OscillationEvent]:
        """Detect repeated recommendation reversals."""
        if len(cycles) < 3:
            return []
        
        events = []
        
        # Track domains with recommendations
        domain_history: Dict[str, List[bool]] = {}
        
        for cycle in cycles:
            domains_with_recs = set(rec.get("domain") for rec in cycle.recommendations)
            
            for domain in domains_with_recs:
                if domain not in domain_history:
                    domain_history[domain] = []
                domain_history[domain].append(True)
        
        # Check for domains that appear and disappear repeatedly
        for domain, history in domain_history.items():
            if len(history) < 3:
                continue
            
            reversals = self._count_reversals(history)
            
            if reversals >= self.min_reversals:
                # Find cycle range
                start_cycle = 1
                end_cycle = len(history)
                
                # Calculate amplitude
                present_count = sum(1 for h in history if h)
                amplitude = present_count / len(history)
                
                event = OscillationEvent(
                    oscillation_type=OscillationType.RECOMMENDATION_REVERSAL,
                    cycle_range=(start_cycle, end_cycle),
                    description=f"Domain '{domain}' repeatedly added and removed from recommendations",
                    affected_elements=[domain],
                    reversal_count=reversals,
                    severity=self._classify_severity(reversals, amplitude),
                    amplitude=amplitude,
                )
                events.append(event)
        
        return events
    
    def detect_priority_flapping(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[OscillationEvent]:
        """Detect priority flapping (rapid priority changes)."""
        if len(cycles) < 3:
            return []
        
        events = []
        
        # Track priorities across cycles
        priorities_by_domain: Dict[str, List[float]] = {}
        
        for cycle in cycles:
            for rec in cycle.recommendations:
                domain = rec.get("domain", "unknown")
                priority = rec.get("priority", 0.5)
                
                if domain not in priorities_by_domain:
                    priorities_by_domain[domain] = []
                priorities_by_domain[domain].append(priority)
        
        # Check for priority oscillation
        for domain, priorities in priorities_by_domain.items():
            if len(priorities) < 3:
                continue
            
            reversals = self._count_reversals(
                [p > 0.5 for p in priorities]
            )
            
            if reversals >= self.min_reversals:
                # Calculate amplitude (range of priorities)
                amplitude = max(priorities) - min(priorities)
                
                event = OscillationEvent(
                    oscillation_type=OscillationType.PRIORITY_FLAPPING,
                    cycle_range=(1, len(priorities)),
                    description=f"Priority for domain '{domain}' oscillating rapidly",
                    affected_elements=[domain],
                    reversal_count=reversals,
                    severity=self._classify_severity(reversals, amplitude),
                    amplitude=amplitude,
                )
                events.append(event)
        
        return events
    
    def detect_confidence_swings(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[OscillationEvent]:
        """Detect confidence level swings."""
        if len(cycles) < 3:
            return []
        
        confidence_values = []
        
        for cycle in cycles:
            if cycle.doctrine_assessment:
                conf = cycle.doctrine_assessment.get("confidence", 0.5)
                confidence_values.append(conf)
        
        if len(confidence_values) < 3:
            return []
        
        # Detect reversals in confidence direction
        directions = []
        for i in range(1, len(confidence_values)):
            if confidence_values[i] > confidence_values[i-1]:
                directions.append(1)
            elif confidence_values[i] < confidence_values[i-1]:
                directions.append(-1)
            else:
                directions.append(0)
        
        reversals = self._count_reversals([d != 0 for d in directions])
        
        if reversals >= self.min_reversals:
            # Calculate amplitude
            amplitude = max(confidence_values) - min(confidence_values)
            
            event = OscillationEvent(
                oscillation_type=OscillationType.CONFIDENCE_SWING,
                cycle_range=(1, len(confidence_values)),
                description="Confidence level swinging up and down",
                affected_elements=["confidence"],
                reversal_count=reversals,
                severity=self._classify_severity(reversals, amplitude),
                amplitude=amplitude,
            )
            return [event]
        
        return []
    
    def detect_policy_alternation(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[OscillationEvent]:
        """Detect policy/state alternation."""
        if len(cycles) < 3:
            return []
        
        tiers = [cycle.current_tier for cycle in cycles if cycle.current_tier]
        
        if len(tiers) < 3:
            return []
        
        # Count tier transitions
        transitions = 0
        for i in range(1, len(tiers)):
            if tiers[i] != tiers[i - 1]:
                transitions += 1
        
        if transitions >= self.min_reversals:
            event = OscillationEvent(
                oscillation_type=OscillationType.POLICY_STATE_ALTERNATION,
                cycle_range=(1, len(tiers)),
                description="Approval tier changing repeatedly",
                affected_elements=tiers,
                reversal_count=transitions,
                severity=self._classify_severity(transitions, 1.0),
                amplitude=1.0,
            )
            return [event]
        
        return []
    
    def _count_reversals(self, values: List[bool]) -> int:
        """Count reversals in a boolean sequence."""
        if len(values) < 2:
            return 0
        
        reversals = 0
        for i in range(1, len(values)):
            if values[i] != values[i - 1]:
                reversals += 1
        
        return reversals
    
    def _classify_severity(self, reversal_count: int, amplitude: float) -> str:
        """Classify oscillation severity."""
        # High reversals and high amplitude = critical
        if reversal_count >= 5 and amplitude > 0.7:
            return "critical"
        # Moderate reversals or amplitude = high
        elif reversal_count >= 3 or amplitude > 0.5:
            return "high"
        # Low reversals = medium
        elif reversal_count >= 2:
            return "medium"
        else:
            return "low"


def detect_oscillations(
    cycles: List[GovernanceSimulationCycle],
    min_reversals: int = 2,
) -> List[OscillationEvent]:
    """Convenience function to detect oscillations."""
    detector = OscillationDetector(min_reversals=min_reversals)
    return detector.detect_all_oscillations(cycles)
