"""Outcome Evaluator - Evaluates outcomes of strategic decisions."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.intelligence.learning.learning_models import (
    OutcomeEvaluation,
    DecisionRecord,
    OutcomeStatus,
)


class OutcomeEvaluator:
    """Evaluates outcomes of strategic decisions."""
    
    def __init__(self):
        self.evaluations: List[OutcomeEvaluation] = []
    
    def evaluate_decision(
        self,
        decision: DecisionRecord,
        current_domain_state: Dict[str, float],
        current_risk_state: Dict[str, float],
        goal_progress: Optional[Dict[str, float]] = None,
    ) -> OutcomeEvaluation:
        """Evaluate the outcome of a decision."""
        
        # Calculate time elapsed
        time_elapsed = (datetime.utcnow() - decision.timestamp).days
        
        # Compare expected vs actual domain changes
        expected_vs_actual = self._compare_states(
            decision.domain_state,
            current_domain_state,
        )
        
        # Calculate performance change
        perf_change = self._calculate_performance_change(
            decision.domain_state,
            current_domain_state,
        )
        
        # Calculate risk change
        risk_change = self._calculate_risk_change(
            decision.risk_state,
            current_risk_state,
        )
        
        # Calculate goal progress
        goal_change = 0.0
        if goal_progress:
            # Simplified - would need more complex logic
            goal_change = sum(goal_progress.values()) / len(goal_progress) if goal_progress else 0.0
        
        # Determine outcome status and success score
        outcome_status, success_score = self._determine_outcome(
            perf_change,
            risk_change,
            goal_change,
            expected_vs_actual,
        )
        
        # Calculate deviation from expected
        deviation = self._calculate_deviation(
            expected_vs_actual,
            decision.expected_outcome,
        )
        
        evaluation = OutcomeEvaluation(
            evaluation_id=str(uuid.uuid4())[:8],
            decision_id=decision.decision_id,
            decision_timestamp=decision.timestamp,
            time_elapsed_days=time_elapsed,
            outcome_status=outcome_status,
            success_score=success_score,
            expected_vs_actual=expected_vs_actual,
            goal_progress_change=goal_change,
            risk_change=risk_change,
            performance_change=perf_change,
            deviation_from_expected=deviation,
            deviation_description=self._generate_deviation_description(
                expected_vs_actual, outcome_status
            ),
        )
        
        self.evaluations.append(evaluation)
        
        return evaluation
    
    def _compare_states(
        self,
        expected: Dict[str, float],
        actual: Dict[str, float],
    ) -> Dict[str, float]:
        """Compare expected vs actual domain states."""
        
        comparison = {}
        
        # All domains from both
        all_domains = set(expected.keys()) | set(actual.keys())
        
        for domain in all_domains:
            exp = expected.get(domain, 5.0)
            act = actual.get(domain, 5.0)
            comparison[domain] = act - exp  # Positive = exceeded, negative = under
        
        return comparison
    
    def _calculate_performance_change(
        self,
        before: Dict[str, float],
        after: Dict[str, float],
    ) -> float:
        """Calculate overall performance change."""
        
        if not before:
            return 0.0
        
        before_avg = sum(before.values()) / len(before)
        after_avg = sum(after.values()) / len(after) if after else before_avg
        
        return after_avg - before_avg
    
    def _calculate_risk_change(
        self,
        before: Dict[str, float],
        after: Dict[str, float],
    ) -> float:
        """Calculate risk change (negative = improved)."""
        
        if not before:
            return 0.0
        
        before_avg = sum(before.values()) / len(before)
        after_avg = sum(after.values()) / len(after) if after else before_avg
        
        # Risk decreased = positive outcome
        return before_avg - after_avg
    
    def _determine_outcome(
        self,
        perf_change: float,
        risk_change: float,
        goal_change: float,
        state_comparison: Dict[str, float],
    ) -> tuple[OutcomeStatus, float]:
        """Determine outcome status and success score."""
        
        # Score based on multiple factors
        score = 0.5  # Base score
        
        # Performance contribution
        if perf_change > 0.5:
            score += 0.2
        elif perf_change < -0.5:
            score -= 0.2
        
        # Risk contribution (risk decrease = positive)
        if risk_change > 0.5:
            score += 0.2
        elif risk_change < -0.5:
            score -= 0.2
        
        # Goal contribution
        if goal_change > 0:
            score += 0.1
        elif goal_change < 0:
            score -= 0.1
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        # Determine status
        if score >= 0.8:
            status = OutcomeStatus.SUCCESS
        elif score >= 0.5:
            status = OutcomeStatus.PARTIAL_SUCCESS
        elif score >= 0.3:
            status = OutcomeStatus.INCONCLUSIVE
        else:
            status = OutcomeStatus.FAILURE
        
        return status, score
    
    def _calculate_deviation(
        self,
        state_comparison: Dict[str, float],
        expected_outcome: str,
    ) -> float:
        """Calculate deviation from expected outcome."""
        
        if not state_comparison:
            return 0.0
        
        # Calculate average deviation
        deviations = [abs(v) for v in state_comparison.values()]
        avg_deviation = sum(deviations) / len(deviations) if deviations else 0.0
        
        # Normalize to 0-1 scale
        return min(1.0, avg_deviation / 5.0)
    
    def _generate_deviation_description(
        self,
        state_comparison: Dict[str, float],
        status: OutcomeStatus,
    ) -> str:
        """Generate human-readable deviation description."""
        
        if status == OutcomeStatus.SUCCESS:
            return "Outcomes exceeded expectations"
        elif status == OutcomeStatus.PARTIAL_SUCCESS:
            return "Outcomes partially met expectations"
        elif status == OutcomeStatus.FAILURE:
            return "Outcomes did not meet expectations"
        else:
            return "Outcomes were inconclusive"
    
    def get_evaluation(self, evaluation_id: str) -> Optional[OutcomeEvaluation]:
        """Get a specific evaluation."""
        
        for eval in self.evaluations:
            if eval.evaluation_id == evaluation_id:
                return eval
        
        return None
    
    def get_evaluations_for_decision(
        self,
        decision_id: str,
    ) -> List[OutcomeEvaluation]:
        """Get all evaluations for a specific decision."""
        
        return [
            e for e in self.evaluations
            if e.decision_id == decision_id
        ]
    
    def get_recent_evaluations(
        self,
        days: int = 30,
    ) -> List[OutcomeEvaluation]:
        """Get recent evaluations."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return [
            e for e in self.evaluations
            if e.evaluation_timestamp > cutoff
        ]
    
    def get_success_rate(
        self,
        strategy_type: Optional[str] = None,
    ) -> float:
        """Calculate success rate from evaluations."""
        
        if not self.evaluations:
            return 0.0
        
        relevant = self.evaluations
        if strategy_type:
            relevant = [
                e for e in relevant
                # Would need to join with decision to get strategy type
            ]
        
        if not relevant:
            return 0.0
        
        successes = sum(
            1 for e in relevant
            if e.outcome_status in [OutcomeStatus.SUCCESS, OutcomeStatus.PARTIAL_SUCCESS]
        )
        
        return successes / len(relevant)


_evaluator: Optional[OutcomeEvaluator] = None


def get_outcome_evaluator() -> OutcomeEvaluator:
    """Get the global outcome evaluator."""
    global _evaluator
    if _evaluator is None:
        _evaluator = OutcomeEvaluator()
    return _evaluator
