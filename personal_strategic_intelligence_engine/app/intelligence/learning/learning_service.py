"""Learning Service - Main orchestration for meta-cognitive learning."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.intelligence.learning.learning_models import (
    LearningReport,
    LearningPolicy,
    StrategyType,
)
from app.intelligence.learning.decision_tracker import (
    DecisionTracker,
    get_decision_tracker,
)
from app.intelligence.learning.outcome_evaluator import (
    OutcomeEvaluator,
    get_outcome_evaluator,
)
from app.intelligence.learning.strategy_effectiveness import (
    StrategyEffectivenessAnalyzer,
    get_strategy_effectiveness_analyzer,
)
from app.intelligence.learning.doctrine_updater import (
    DoctrineUpdater,
    get_doctrine_updater,
)


class LearningService:
    """Main orchestration for meta-cognitive learning."""
    
    def __init__(self, policy: Optional[LearningPolicy] = None):
        self.policy = policy or LearningPolicy()
        self.tracker = get_decision_tracker()
        self.evaluator = get_outcome_evaluator()
        self.effectiveness_analyzer = get_strategy_effectiveness_analyzer()
        self.doctrine_updater = get_doctrine_updater()
        
        # History
        self.reports: List[LearningReport] = []
    
    def track_decision(
        self,
        recommendation_id: str,
        strategy_type: StrategyType,
        action: str,
        expected_outcome: str,
        confidence: float,
        priority_score: float,
        domain_state: Dict[str, float],
        risk_state: Optional[Dict[str, float]] = None,
    ):
        """Track a new strategic decision."""
        
        return self.tracker.track_decision(
            recommendation_id=recommendation_id,
            strategy_type=strategy_type,
            action=action,
            expected_outcome=expected_outcome,
            confidence=confidence,
            priority_score=priority_score,
            domain_state=domain_state,
            risk_state=risk_state,
        )
    
    def run_learning_cycle(
        self,
        current_domain_state: Optional[Dict[str, float]] = None,
        current_risk_state: Optional[Dict[str, float]] = None,
    ) -> LearningReport:
        """Run a complete learning cycle."""
        
        # Step 1: Get decisions ready for evaluation
        decisions = self.tracker.get_decisions_for_evaluation(
            self.policy.evaluation_delay_days
        )
        
        # Step 2: Evaluate outcomes
        evaluations = self._evaluate_decisions(
            decisions,
            current_domain_state or {},
            current_risk_state or {},
        )
        
        # Step 3: Analyze effectiveness
        decision_mapping = {d.decision_id: d.strategy_type for d in decisions}
        effectiveness = self.effectiveness_analyzer.analyze_effectiveness(
            evaluations,
            decision_mapping,
        )
        
        # Step 4: Update doctrine
        doctrine_updates = self.doctrine_updater.update_doctrine(effectiveness)
        
        # Step 5: Generate report
        report = self._generate_report(
            evaluations,
            effectiveness,
            doctrine_updates,
        )
        
        self.reports.append(report)
        
        return report
    
    def _evaluate_decisions(
        self,
        decisions,
        current_domain_state: Dict[str, float],
        current_risk_state: Dict[str, float],
    ):
        """Evaluate outcomes for decisions."""
        
        evaluations = []
        
        for decision in decisions:
            evaluation = self.evaluator.evaluate_decision(
                decision=decision,
                current_domain_state=current_domain_state,
                current_risk_state=current_risk_state,
            )
            
            # Mark decision as evaluated
            self.tracker.mark_evaluated(
                decision.decision_id,
                evaluation.evaluation_id,
            )
            
            evaluations.append(evaluation)
        
        return evaluations
    
    def _generate_report(
        self,
        evaluations,
        effectiveness,
        doctrine_updates,
    ) -> LearningReport:
        """Generate a learning report."""
        
        # Count successes/failures
        successful = sum(
            1 for e in evaluations
            if e.outcome_status.value in ["success", "partial_success"]
        )
        failed = sum(
            1 for e in evaluations
            if e.outcome_status.value == "failure"
        )
        
        # Get strategy recommendations
        strategy_recs = self.effectiveness_analyzer.get_recommendations()
        
        # Get failing strategies
        failing = self.effectiveness_analyzer.get_failing_strategies()
        
        # Calculate confidence
        confidence = 0.5
        if evaluations:
            confidence = sum(e.success_score for e in evaluations) / len(evaluations)
        
        report = LearningReport(
            report_id=str(uuid.uuid4())[:8],
            timestamp=datetime.utcnow(),
            decisions_evaluated=len(evaluations),
            successful_decisions=successful,
            failed_decisions=failed,
            strategy_effectiveness={
                k.value: v for k, v in effectiveness.items()
            },
            doctrine_updates=doctrine_updates,
            successful_strategies=[s.value for s in self.effectiveness_analyzer.get_top_strategies()],
            failing_strategies=[s.value for s in failing],
            emerging_patterns=strategy_recs,
            recommended_doctrine_changes=[
                f"Update {u.parameter_name}: {u.old_value:.2f} → {u.new_value:.2f}"
                for u in doctrine_updates
            ],
            evaluation_period_days=self.policy.evaluation_delay_days,
            confidence=confidence,
        )
        
        return report
    
    def get_latest_report(self) -> Optional[LearningReport]:
        """Get the most recent learning report."""
        
        if self.reports:
            return self.reports[-1]
        return None
    
    def get_report_history(
        self,
        limit: int = 10,
    ) -> List[LearningReport]:
        """Get recent learning reports."""
        
        return self.reports[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics."""
        
        return {
            "total_decisions_tracked": len(self.tracker.decisions),
            "total_evaluations": len(self.evaluator.evaluations),
            "total_reports": len(self.reports),
            "total_doctrine_updates": len(self.doctrine_updater.updates),
        }
    
    def get_current_doctrine(self) -> Dict[str, float]:
        """Get current doctrine weights."""
        
        return self.doctrine_updater.get_current_doctrine()
    
    def get_effectiveness_summary(self) -> Dict[str, Any]:
        """Get strategy effectiveness summary."""
        
        effectiveness = self.effectiveness_analyzer.get_all_effectiveness()
        
        return {
            strategy.value: {
                "success_rate": metrics.success_rate,
                "total_decisions": metrics.total_decisions,
                "average_impact": metrics.average_impact,
            }
            for strategy, metrics in effectiveness.items()
            if metrics.total_decisions > 0
        }


# Global service
_learning_service: Optional[LearningService] = None


def get_learning_service() -> LearningService:
    """Get the global learning service."""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service
