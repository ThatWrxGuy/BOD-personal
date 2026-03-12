"""Protocol Scorer - Scores effectiveness of intervention protocols."""
from typing import List, Dict, Optional
from datetime import datetime

from app.intervention_evaluation.evaluation_types import (
    ProtocolEffectiveness,
    InterventionOutcome,
)
from app.intervention_evaluation.intervention_outcome_tracker import InterventionOutcomeTracker


class ProtocolScorer:
    """Scores effectiveness of intervention protocols."""
    
    def __init__(self, tracker: InterventionOutcomeTracker):
        self.tracker = tracker
    
    def score_protocol(self, protocol_id: str) -> ProtocolEffectiveness:
        """Calculate effectiveness scores for a protocol."""
        
        outcomes = self.tracker.get_outcomes_for_protocol(protocol_id)
        
        if not outcomes:
            return ProtocolEffectiveness(
                protocol_id=protocol_id,
                protocol_name=protocol_id,
            )
        
        # Calculate counts
        total = len(outcomes)
        successful = sum(1 for o in outcomes if o.outcome == "success")
        failed = sum(1 for o in outcomes if o.outcome == "failure")
        partial = sum(1 for o in outcomes if o.outcome == "partial")
        
        # Calculate averages
        avg_perf = sum(o.performance_change for o in outcomes) / total
        avg_risk = sum(o.risk_change for o in outcomes) / total
        avg_momentum = sum(o.momentum_change for o in outcomes) / total
        
        # Calculate success rate
        success_rate = successful / total if total > 0 else 0
        
        # Calculate effectiveness score
        effectiveness = self._calculate_effectiveness(
            avg_perf, avg_risk, success_rate
        )
        
        # Calculate consistency
        consistency = self._calculate_consistency(outcomes)
        
        # Calculate recovery metrics
        recovered = sum(1 for o in outcomes if o.recovered)
        recovery_rate = recovered / total if total > 0 else 0
        
        avg_recovery = 0
        recovery_outcomes = [o for o in outcomes if o.recovered]
        if recovery_outcomes:
            avg_recovery = sum(
                (o.time_to_recovery_days or 0) for o in recovery_outcomes
            ) / len(recovery_outcomes)
        
        # Determine if requires review
        requires_review = False
        review_reason = None
        
        if total >= 5:
            if success_rate < 0.3:
                requires_review = True
                review_reason = f"Low success rate: {success_rate:.1%}"
            elif effectiveness < 0.3:
                requires_review = True
                review_reason = f"Low effectiveness: {effectiveness:.2f}"
            elif consistency < 0.3:
                requires_review = True
                review_reason = f"Inconsistent results: {consistency:.2f}"
        
        return ProtocolEffectiveness(
            protocol_id=protocol_id,
            protocol_name=protocol_id,
            total_interventions=total,
            successful_interventions=successful,
            failed_interventions=failed,
            partial_interventions=partial,
            average_performance_improvement=avg_perf,
            average_risk_reduction=avg_risk,
            average_momentum_change=avg_momentum,
            success_rate=success_rate,
            effectiveness_score=effectiveness,
            consistency_score=consistency,
            average_recovery_time_days=avg_recovery,
            recovery_rate=recovery_rate,
            requires_review=requires_review,
            review_reason=review_reason,
        )
    
    def _calculate_effectiveness(
        self,
        avg_perf: float,
        avg_risk: float,
        success_rate: float,
    ) -> float:
        """Calculate overall effectiveness score."""
        
        # Weight factors
        perf_weight = 0.4
        risk_weight = 0.3
        success_weight = 0.3
        
        # Normalize performance (-1 to +1 range typically)
        perf_score = max(0, min(1, (avg_perf + 1) / 2))
        
        # Risk reduction is positive (negative change is good)
        risk_score = max(0, min(1, 1 - abs(avg_risk)))
        
        return (
            perf_score * perf_weight +
            risk_score * risk_weight +
            success_rate * success_weight
        )
    
    def _calculate_consistency(self, outcomes: List[InterventionOutcome]) -> float:
        """Calculate consistency of outcomes."""
        
        if len(outcomes) < 2:
            return 1.0
        
        # Calculate variance in performance changes
        perf_changes = [o.performance_change for o in outcomes]
        avg = sum(perf_changes) / len(perf_changes)
        variance = sum((p - avg) ** 2 for p in perf_changes) / len(perf_changes)
        
        # Convert to consistency score (low variance = high consistency)
        # Variance of 0 = 1.0, variance of 4 = 0.0
        consistency = max(0, 1 - (variance ** 0.5) / 2)
        
        return consistency
    
    def score_all_protocols(self) -> List[ProtocolEffectiveness]:
        """Score all protocols."""
        
        # Get unique protocol IDs
        protocol_ids = set()
        for outcome in self.tracker.outcomes:
            protocol_ids.add(outcome.protocol_id)
        
        # Score each protocol
        scores = []
        for pid in protocol_ids:
            score = self.score_protocol(pid)
            scores.append(score)
        
        # Sort by effectiveness
        scores.sort(key=lambda x: x.effectiveness_score, reverse=True)
        
        return scores
    
    def get_protocol_rankings(self) -> Dict:
        """Get protocol rankings."""
        
        scores = self.score_all_protocols()
        
        if not scores:
            return {
                "top": [],
                "bottom": [],
                "requires_review": [],
            }
        
        top = [
            {"protocol_id": s.protocol_id, "score": s.effectiveness_score}
            for s in scores[:3]
        ]
        
        bottom = [
            {"protocol_id": s.protocol_id, "score": s.effectiveness_score}
            for s in scores[-3:]
        ]
        
        review = [
            {"protocol_id": s.protocol_id, "reason": s.review_reason}
            for s in scores if s.requires_review
        ]
        
        return {
            "top": top,
            "bottom": bottom,
            "requires_review": review,
        }
