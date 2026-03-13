"""Doctrine conflict detector for governance simulations.

Detects and analyzes doctrine behavior inconsistencies across cycles.
"""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.governance_simulation.simulation_models import (
    ConflictSeverity,
    DoctrineConflictEvent,
    GovernanceSimulationCycle,
    ScenarioType,
)


class DoctrineConflictDetector:
    """Detector for doctrine conflicts and inconsistencies."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """Initialize doctrine conflict detector.
        
        Args:
            similarity_threshold: Threshold for considering contexts similar
        """
        self.similarity_threshold = similarity_threshold
        self.previous_assessments: List[Dict[str, Any]] = []
    
    def detect_conflicts(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[DoctrineConflictEvent]:
        """Detect doctrine conflicts across simulation cycles."""
        events = []
        
        # First pass: detect explicit conflicts in assessments
        events.extend(self._detect_explicit_conflicts(cycles))
        
        # Second pass: detect contextual inconsistencies
        events.extend(self._detect_contextual_inconsistencies(cycles))
        
        # Third pass: detect rule instability
        events.extend(self._detect_rule_instability(cycles))
        
        return events
    
    def _detect_explicit_conflicts(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[DoctrineConflictEvent]:
        """Detect explicit conflicts reported in doctrine assessments."""
        events = []
        
        for cycle in cycles:
            if not cycle.doctrine_assessment:
                continue
            
            conflicts = cycle.doctrine_assessment.get("doctrine_conflicts", [])
            
            for conflict in conflicts:
                event = DoctrineConflictEvent(
                    cycle_number=cycle.cycle_number,
                    conflict_type=conflict.get("conflict_type", "unknown"),
                    rules_involved=conflict.get("rules_involved", []),
                    severity=self._parse_severity(conflict.get("severity", "low")),
                    context_hash=self._hash_context(cycle),
                    description=conflict.get("description", ""),
                )
                events.append(event)
        
        return events
    
    def _detect_contextual_inconsistencies(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[DoctrineConflictEvent]:
        """Detect when similar contexts produce different doctrine results."""
        events = []
        
        # Group cycles by context similarity
        context_groups: Dict[str, List[GovernanceSimulationCycle]] = {}
        
        for cycle in cycles:
            if not cycle.doctrine_assessment:
                continue
            
            # Create context signature
            context_sig = self._create_context_signature(cycle)
            
            if context_sig not in context_groups:
                context_groups[context_sig] = []
            context_groups[context_sig].append(cycle)
        
        # Check each group for inconsistencies
        for context_sig, group_cycles in context_groups.items():
            if len(group_cycles) < 2:
                continue
            
            # Get alignment scores
            scores = [
                c.doctrine_assessment.get("alignment_score", 0.0)
                for c in group_cycles
                if c.doctrine_assessment
            ]
            
            if len(scores) < 2:
                continue
            
            # Calculate variance
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            
            # If variance is high, flag as inconsistency
            if variance > 0.1:  # Threshold for significant difference
                severity = ConflictSeverity.MEDIUM
                if variance > 0.3:
                    severity = ConflictSeverity.HIGH
                
                event = DoctrineConflictEvent(
                    cycle_number=group_cycles[0].cycle_number,
                    conflict_type="contextual_inconsistency",
                    rules_involved=["doctrine_evaluation"],
                    severity=severity,
                    context_hash=context_sig,
                    previous_result_hash=self._hash_assessment(group_cycles[-1].doctrine_assessment) if group_cycles[-1].doctrine_assessment else None,
                    description=f"Similar contexts produced different alignment scores (variance: {variance:.3f})",
                )
                events.append(event)
        
        return events
    
    def _detect_rule_instability(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[DoctrineConflictEvent]:
        """Detect instability in rule application across cycles."""
        events = []
        
        # Track rules applied over time
        rules_history: List[List[str]] = []
        
        for cycle in cycles:
            if cycle.doctrine_assessment:
                rules = cycle.doctrine_assessment.get("rules_applied", [])
                rules_history.append(rules)
        
        if len(rules_history) < 3:
            return events
        
        # Check for rule changes
        for i in range(1, len(rules_history)):
            prev_rules = set(rules_history[i - 1])
            curr_rules = set(rules_history[i])
            
            # Check if rules changed significantly
            if prev_rules and curr_rules:
                common = len(prev_rules & curr_rules)
                total = len(prev_rules | curr_rules)
                
                if total > 0:
                    similarity = common / total
                    
                    # If similarity is low, flag as instability
                    if similarity < 0.5:
                        # This is normal during stress scenarios
                        # Only flag if it's not an adversarial scenario
                        # (adversarial scenarios are expected to cause instability)
                        
                        # For now, we'll flag all but with lower severity
                        severity = ConflictSeverity.LOW
                        if similarity < 0.3:
                            severity = ConflictSeverity.MEDIUM
                        
                        event = DoctrineConflictEvent(
                            cycle_number=i + 1,
                            conflict_type="rule_instability",
                            rules_involved=list(curr_rules),
                            severity=severity,
                            context_hash=f"rules_{i}",
                            description=f"Rule set changed significantly (similarity: {similarity:.2f})",
                        )
                        events.append(event)
        
        return events
    
    def _create_context_signature(self, cycle: GovernanceSimulationCycle) -> str:
        """Create a signature for the cycle context."""
        # Use domain states to create context
        if not cycle.state_snapshot:
            return "default"
        
        domains = cycle.state_snapshot.get("domains", {})
        
        # Create simplified state representation
        state_repr = {}
        for domain, state in domains.items():
            state_repr[domain] = {
                "perf": round(state.get("performance", 0.5), 2),
                "risk": round(state.get("risk", 0.3), 2),
            }
        
        return self._hash_dict(state_repr)
    
    def _hash_context(self, cycle: GovernanceSimulationCycle) -> str:
        """Hash the cycle context."""
        return self._create_context_signature(cycle)
    
    def _hash_assessment(self, assessment: Optional[Dict[str, Any]]) -> Optional[str]:
        """Hash a doctrine assessment."""
        if not assessment:
            return None
        
        # Create deterministic string
        score = assessment.get("alignment_score", 0)
        level = assessment.get("alignment_level", "neutral")
        confidence = assessment.get("confidence", 0.5)
        
        return hashlib.sha256(
            f"{score}:{level}:{confidence}".encode()
        ).hexdigest()[:16]
    
    def _hash_dict(self, data: Dict[str, Any]) -> str:
        """Hash a dictionary."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def _parse_severity(self, severity_str: str) -> ConflictSeverity:
        """Parse severity string to enum."""
        severity_map = {
            "low": ConflictSeverity.LOW,
            "medium": ConflictSeverity.MEDIUM,
            "high": ConflictSeverity.HIGH,
            "critical": ConflictSeverity.CRITICAL,
        }
        return severity_map.get(severity_str.lower(), ConflictSeverity.LOW)


def detect_doctrine_conflicts(
    cycles: List[GovernanceSimulationCycle],
) -> List[DoctrineConflictEvent]:
    """Convenience function to detect doctrine conflicts."""
    detector = DoctrineConflictDetector()
    return detector.detect_conflicts(cycles)
