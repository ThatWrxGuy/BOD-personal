"""Saturation analyzer for governance simulations.

Measures and detects governance overload conditions.
"""
from typing import Any, Dict, List

from app.governance_simulation.simulation_models import (
    GovernanceSimulationCycle,
    SaturationEvent,
)


class SaturationAnalyzer:
    """Analyzer for governance saturation/overload conditions."""
    
    def __init__(
        self,
        recommendation_capacity: int = 10,
        approval_queue_capacity: int = 20,
        doctrine_flag_capacity: int = 5,
    ):
        """Initialize saturation analyzer.
        
        Args:
            recommendation_capacity: Max recommendations per cycle before overload
            approval_queue_capacity: Max pending approvals before overload
            doctrine_flag_capacity: Max risk flags per cycle before overload
        """
        self.recommendation_capacity = recommendation_capacity
        self.approval_queue_capacity = approval_queue_capacity
        self.doctrine_flag_capacity = doctrine_flag_capacity
    
    def detect_saturation(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[SaturationEvent]:
        """Detect all saturation events in simulation cycles."""
        events = []
        
        # Detect different saturation types
        events.extend(self._detect_recommendation_overload(cycles))
        events.extend(self._detect_approval_queue_saturation(cycles))
        events.extend(self._detect_doctrine_flag_excess(cycles))
        
        return events
    
    def _detect_recommendation_overload(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[SaturationEvent]:
        """Detect recommendation queue saturation."""
        events = []
        
        for cycle in cycles:
            rec_count = len(cycle.recommendations)
            overload_ratio = rec_count / self.recommendation_capacity
            
            if overload_ratio >= 1.0:
                event = SaturationEvent(
                    cycle_number=cycle.cycle_number,
                    saturation_type="recommendation_overload",
                    current_load=rec_count,
                    capacity=self.recommendation_capacity,
                    overload_ratio=overload_ratio,
                    affected_count=rec_count,
                    description=f"Recommendation queue overloaded: {rec_count} recommendations (capacity: {self.recommendation_capacity})",
                )
                events.append(event)
            elif overload_ratio >= 0.7:
                # Warning level
                event = SaturationEvent(
                    cycle_number=cycle.cycle_number,
                    saturation_type="recommendation_warning",
                    current_load=rec_count,
                    capacity=self.recommendation_capacity,
                    overload_ratio=overload_ratio,
                    affected_count=rec_count,
                    description=f"Recommendation queue approaching capacity: {rec_count}/{self.recommendation_capacity}",
                )
                events.append(event)
        
        return events
    
    def _detect_approval_queue_saturation(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[SaturationEvent]:
        """Detect approval queue saturation."""
        events = []
        
        for cycle in cycles:
            # Count intents requiring approval
            pending_count = sum(
                1 for intent in cycle.execution_intents
                if intent.get("requires_approval", False) and not intent.get("approved", False)
            )
            
            overload_ratio = pending_count / self.approval_queue_capacity
            
            if overload_ratio >= 1.0:
                event = SaturationEvent(
                    cycle_number=cycle.cycle_number,
                    saturation_type="approval_queue",
                    current_load=pending_count,
                    capacity=self.approval_queue_capacity,
                    overload_ratio=overload_ratio,
                    affected_count=pending_count,
                    description=f"Approval queue overloaded: {pending_count} pending approvals (capacity: {self.approval_queue_capacity})",
                )
                events.append(event)
        
        return events
    
    def _detect_doctrine_flag_excess(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> List[SaturationEvent]:
        """Detect excess doctrine/risk flags."""
        events = []
        
        for cycle in cycles:
            if not cycle.doctrine_assessment:
                continue
            
            flag_count = len(cycle.doctrine_assessment.get("risk_flags", []))
            overload_ratio = flag_count / self.doctrine_flag_capacity
            
            if overload_ratio >= 1.0:
                event = SaturationEvent(
                    cycle_number=cycle.cycle_number,
                    saturation_type="doctrine_flag_excess",
                    current_load=flag_count,
                    capacity=self.doctrine_flag_capacity,
                    overload_ratio=overload_ratio,
                    affected_count=flag_count,
                    description=f"Risk flag overload: {flag_count} flags (capacity: {self.doctrine_flag_capacity})",
                )
                events.append(event)
        
        return events
    
    def compute_saturation_metrics(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Compute overall saturation metrics."""
        if not cycles:
            return {
                "avg_recommendations_per_cycle": 0,
                "avg_risk_flags_per_cycle": 0,
                "saturation_rate": 0,
            }
        
        # Calculate averages
        total_recs = sum(len(c.recommendations) for c in cycles)
        total_flags = sum(
            len(c.doctrine_assessment.get("risk_flags", [])) 
            if c.doctrine_assessment else 0 
            for c in cycles
        )
        
        avg_recs = total_recs / len(cycles)
        avg_flags = total_flags / len(cycles)
        
        # Calculate saturation rate
        saturated_cycles = sum(
            1 for c in cycles
            if len(c.recommendations) >= self.recommendation_capacity or
            (c.doctrine_assessment and 
             len(c.doctrine_assessment.get("risk_flags", [])) >= self.doctrine_flag_capacity)
        )
        
        saturation_rate = saturated_cycles / len(cycles)
        
        return {
            "avg_recommendations_per_cycle": avg_recs,
            "avg_risk_flags_per_cycle": avg_flags,
            "saturation_rate": saturation_rate,
            "saturated_cycles": saturated_cycles,
            "total_cycles": len(cycles),
        }
    
    def estimate_operator_burden(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Estimate manual review burden on operators."""
        if not cycles:
            return {"burden_level": "none", "estimated_hours_per_100_cycles": 0}
        
        # Estimate manual actions required
        manual_actions = 0
        
        for cycle in cycles:
            # Count manual approvals needed
            manual_approvals = sum(
                1 for intent in cycle.execution_intents
                if intent.get("requires_approval", False)
            )
            
            # Count recommendations requiring review
            review_count = len(cycle.recommendations)
            
            manual_actions += manual_approvals + review_count
        
        # Estimate burden (rough heuristic: 5 min per action)
        avg_actions_per_cycle = manual_actions / len(cycles)
        hours_per_100_cycles = (avg_actions_per_cycle * 100 * 5) / 60
        
        # Classify burden level
        if hours_per_100_cycles > 10:
            burden_level = "high"
        elif hours_per_100_cycles > 5:
            burden_level = "moderate"
        elif hours_per_100_cycles > 1:
            burden_level = "low"
        else:
            burden_level = "minimal"
        
        return {
            "burden_level": burden_level,
            "estimated_hours_per_100_cycles": hours_per_100_cycles,
            "avg_actions_per_cycle": avg_actions_per_cycle,
            "total_manual_actions": manual_actions,
        }
    
    def run_full_saturation_analysis(
        self,
        cycles: List[GovernanceSimulationCycle],
    ) -> Dict[str, Any]:
        """Run complete saturation analysis."""
        events = self.detect_saturation(cycles)
        metrics = self.compute_saturation_metrics(cycles)
        burden = self.estimate_operator_burden(cycles)
        
        return {
            "saturation_events": events,
            "metrics": metrics,
            "operator_burden": burden,
            "recommendations": self._generate_recommendations(events, metrics, burden),
        }
    
    def _generate_recommendations(
        self,
        events: List[SaturationEvent],
        metrics: Dict[str, Any],
        burden: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check saturation rate
        if metrics.get("saturation_rate", 0) > 0.3:
            recommendations.append(
                "High saturation rate detected. Consider increasing governance capacity or optimizing thresholds."
            )
        
        # Check burden level
        if burden.get("burden_level") == "high":
            recommendations.append(
                "High operator burden detected. Consider automating more approvals or reducing recommendation volume."
            )
        
        # Check recommendation overload
        if metrics.get("avg_recommendations_per_cycle", 0) > 7:
            recommendations.append(
                "High recommendation volume. Consider implementing priority filtering."
            )
        
        if not recommendations:
            recommendations.append("Governance load within acceptable parameters.")
        
        return recommendations


def analyze_saturation(
    cycles: List[GovernanceSimulationCycle],
) -> Dict[str, Any]:
    """Convenience function to analyze saturation."""
    analyzer = SaturationAnalyzer()
    return analyzer.run_full_saturation_analysis(cycles)
