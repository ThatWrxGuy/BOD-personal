"""Threshold Optimizer - Analyzes and optimizes trigger thresholds."""
from typing import List, Dict, Any, Optional

from app.intervention_evaluation.evaluation_types import ThresholdAnalysis
from app.intervention_evaluation.intervention_outcome_tracker import InterventionOutcomeTracker
from app.intervention.intervention_types import TriggerType


class ThresholdOptimizer:
    """Optimizes trigger thresholds based on intervention outcomes."""
    
    def __init__(self, tracker: InterventionOutcomeTracker):
        self.tracker = tracker
    
    def analyze_threshold(self, trigger_type: str) -> ThresholdAnalysis:
        """Analyze a specific trigger type."""
        
        # Get all outcomes for this trigger
        outcomes = self.tracker.get_recent_outcomes(90)  # Last 90 days
        
        if not outcomes:
            return ThresholdAnalysis(
                trigger_type=trigger_type,
                threshold_value=0.5,
                times_triggered=0,
            )
        
        # Analyze patterns
        times_triggered = len(outcomes)
        
        # Determine usefulness based on outcomes
        successful = sum(1 for o in outcomes if o.outcome == "success")
        useful = successful / times_triggered if times_triggered > 0 else 0
        
        useless = times_triggered - successful
        
        # Calculate recommendation
        recommendation = None
        confidence = 0.5
        
        if times_triggered >= 10:
            if useful < 0.3:
                recommendation = "INCREASE_THRESHOLD"
                confidence = 0.8
            elif useful > 0.7:
                recommendation = "DECREASE_THRESHOLD"
                confidence = 0.6
            else:
                recommendation = "MAINTAIN"
                confidence = 0.7
        
        return ThresholdAnalysis(
            trigger_type=trigger_type,
            threshold_value=0.5,  # Default
            times_triggered=times_triggered,
            useful_triggers=successful,
            useless_triggers=useless,
            success_rate=useful,
            recommended_adjustment=recommendation,
            confidence=confidence,
        )
    
    def analyze_all_thresholds(self) -> List[ThresholdAnalysis]:
        """Analyze all trigger types."""
        
        # Get all trigger types
        trigger_types = [
            "domain_performance_collapse",
            "risk_escalation",
            "priority_oscillation",
            "sustained_imbalance",
            "excessive_alerts",
            "execution_overload",
            "resource_starvation",
            "strategic_drift",
        ]
        
        return [self.analyze_threshold(t) for t in trigger_types]
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get threshold optimization recommendations."""
        
        analyses = self.analyze_all_thresholds()
        
        recommendations = []
        
        for analysis in analyses:
            if analysis.recommended_adjustment and analysis.recommended_adjustment != "MAINTAIN":
                recommendations.append({
                    "trigger_type": analysis.trigger_type,
                    "current_threshold": analysis.threshold_value,
                    "recommendation": analysis.recommended_adjustment,
                    "confidence": analysis.confidence,
                    "reason": f"Success rate: {analysis.success_rate:.1%}",
                })
        
        return recommendations


# Global optimizer
_optimizer: Optional[ThresholdOptimizer] = None


def get_threshold_optimizer() -> ThresholdOptimizer:
    """Get the global threshold optimizer."""
    global _optimizer
    if _optimizer is None:
        from app.intervention_evaluation.intervention_outcome_tracker import get_outcome_tracker
        tracker = get_outcome_tracker()
        _optimizer = ThresholdOptimizer(tracker)
    return _optimizer
