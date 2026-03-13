"""Policy stress tester for approval tiers and thresholds.

Tests threshold sensitivity, tier assignment consistency, and detects brittleness.
"""
import random
from typing import Any, Dict, List, Tuple

from app.approval_policy.approval_policy_models import ApprovalTierLevel
from app.governance_simulation.simulation_models import (
    GovernanceSimulationCycle,
    GovernanceSimulationScenario,
    GovernanceSimulationResult,
    TierTransitionEvent,
)


class PolicyStressTester:
    """Stress tester for approval policies and thresholds."""
    
    def __init__(self):
        """Initialize policy stress tester."""
        self.threshold_tests: List[Dict[str, Any]] = []
    
    def test_threshold_sensitivity(
        self,
        scenario: GovernanceSimulationScenario,
        result: GovernanceSimulationResult,
    ) -> Dict[str, Any]:
        """Test how sensitive the system is to threshold changes."""
        # Test different confidence thresholds
        thresholds = [0.3, 0.5, 0.7, 0.9]
        
        results = []
        for threshold in thresholds:
            tier_changes = self._count_tier_changes_at_threshold(
                result.cycles, 
                threshold
            )
            
            results.append({
                "threshold": threshold,
                "tier_changes": tier_changes,
                "stability_score": 1.0 - (tier_changes / max(1, len(result.cycles))),
            })
        
        return {
            "threshold_tests": results,
            "sensitivity_analysis": self._analyze_sensitivity(results),
        }
    
    def _count_tier_changes_at_threshold(
        self,
        cycles: List[GovernanceSimulationCycle],
        confidence_threshold: float,
    ) -> int:
        """Count tier changes at a given confidence threshold."""
        changes = 0
        current_tier = None
        
        for cycle in cycles:
            if not cycle.doctrine_assessment:
                continue
            
            confidence = cycle.doctrine_assessment.get("confidence", 0.5)
            
            # Determine tier based on threshold
            if confidence >= confidence_threshold:
                tier = ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO
            elif confidence >= confidence_threshold - 0.2:
                tier = ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH
            else:
                tier = ApprovalTierLevel.TIER_0_MANUAL_ONLY
            
            if current_tier is not None and tier != current_tier:
                changes += 1
            
            current_tier = tier
        
        return changes
    
    def _analyze_sensitivity(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze threshold sensitivity results."""
        stability_scores = [r["stability_score"] for r in results]
        
        return {
            "min_stability": min(stability_scores),
            "max_stability": max(stability_scores),
            "avg_stability": sum(stability_scores) / len(stability_scores),
            "stability_variance": self._calculate_variance(stability_scores),
        }
    
    def test_tier_assignment_consistency(
        self,
        result: GovernanceSimulationResult,
    ) -> Dict[str, Any]:
        """Test consistency of tier assignments."""
        tiers = [c.current_tier for c in result.cycles if c.current_tier]
        
        if not tiers:
            return {"consistent": True, "details": "No tier data"}
        
        # Count each tier
        tier_counts: Dict[str, int] = {}
        for tier in tiers:
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        # Calculate distribution
        total = len(tiers)
        tier_distribution = {
            tier: count / total 
            for tier, count in tier_counts.items()
        }
        
        # Check for rapid oscillation
        oscillation_rate = self._calculate_oscillation_rate(tiers)
        
        return {
            "tier_counts": tier_counts,
            "tier_distribution": tier_distribution,
            "oscillation_rate": oscillation_rate,
            "consistent": oscillation_rate < 0.3,
        }
    
    def _calculate_oscillation_rate(self, tiers: List[str]) -> float:
        """Calculate rate of tier oscillation."""
        if len(tiers) < 2:
            return 0.0
        
        changes = 0
        for i in range(1, len(tiers)):
            if tiers[i] != tiers[i - 1]:
                changes += 1
        
        return changes / (len(tiers) - 1)
    
    def test_marginal_eligibility(
        self,
        result: GovernanceSimulationResult,
    ) -> Dict[str, Any]:
        """Test behavior at marginal eligibility boundaries."""
        # Find cycles near tier boundaries
        boundary_cycles = []
        
        for i, cycle in enumerate(result.cycles):
            if not cycle.doctrine_assessment:
                continue
            
            confidence = cycle.doctrine_assessment.get("confidence", 0.5)
            
            # Check if near boundaries (0.3, 0.5, 0.7)
            if abs(confidence - 0.3) < 0.05 or \
               abs(confidence - 0.5) < 0.05 or \
               abs(confidence - 0.7) < 0.05:
                boundary_cycles.append({
                    "cycle": i + 1,
                    "confidence": confidence,
                    "tier": cycle.current_tier,
                })
        
        return {
            "boundary_cycles": boundary_cycles,
            "total_boundary_cycles": len(boundary_cycles),
            "boundary_stability": 1.0 - (len(boundary_cycles) / max(1, len(result.cycles))),
        }
    
    def detect_threshold_brittleness(
        self,
        result: GovernanceSimulationResult,
    ) -> Dict[str, Any]:
        """Detect if thresholds are brittle (small changes cause large tier shifts)."""
        # Analyze tier transitions
        transitions = self._extract_tier_transitions(result.cycles)
        
        # Check for rapid up-down transitions
        rapid_transitions = 0
        for i in range(2, len(transitions)):
            if transitions[i-1] != transitions[i-2] and \
               transitions[i] != transitions[i-1]:
                rapid_transitions += 1
        
        brittleness_score = rapid_transitions / max(1, len(transitions) - 2)
        
        return {
            "brittle": brittleness_score > 0.2,
            "brittlness_score": brittleness_score,
            "rapid_transitions": rapid_transitions,
            "recommendation": self._get_brittleness_recommendation(brittleness_score),
        }
    
    def _extract_tier_transitions(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[str]:
        """Extract ordered list of tiers."""
        return [c.current_tier for c in cycles if c.current_tier]
    
    def _get_brittleness_recommendation(self, score: float) -> str:
        """Get recommendation based on brittleness score."""
        if score > 0.4:
            return "Consider widening tier thresholds to reduce brittleness"
        elif score > 0.2:
            return "Monitor tier transitions closely"
        else:
            return "Thresholds appear stable"
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance
    
    def run_full_stress_test(
        self,
        scenario: GovernanceSimulationScenario,
        result: GovernanceSimulationResult,
    ) -> Dict[str, Any]:
        """Run full policy stress test."""
        return {
            "threshold_sensitivity": self.test_threshold_sensitivity(scenario, result),
            "tier_consistency": self.test_tier_assignment_consistency(result),
            "marginal_eligibility": self.test_marginal_eligibility(result),
            "brittleness": self.detect_threshold_brittleness(result),
        }


def run_policy_stress_test(
    scenario: GovernanceSimulationScenario,
    result: GovernanceSimulationResult,
) -> Dict[str, Any]:
    """Convenience function to run policy stress test."""
    tester = PolicyStressTester()
    return tester.run_full_stress_test(scenario, result)
