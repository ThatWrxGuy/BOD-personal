"""Intervention Evaluation Engine - Main engine for evaluating intervention effectiveness."""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from app.intervention_evaluation.evaluation_types import (
    EvaluationCycle,
    EvaluationPolicy,
    EvaluationStatus,
)
from app.intervention_evaluation.intervention_outcome_tracker import (
    InterventionOutcomeTracker,
    get_outcome_tracker,
)
from app.intervention_evaluation.protocol_scorer import ProtocolScorer
from app.intervention_evaluation.effectiveness_analyzer import (
    EffectivenessAnalyzer,
    get_effectiveness_analyzer,
)
from app.intervention_evaluation.threshold_optimizer import (
    ThresholdOptimizer,
    get_threshold_optimizer,
)


class InterventionEvaluationEngine:
    """Main evaluation engine for intervention effectiveness."""
    
    def __init__(self, policy: Optional[EvaluationPolicy] = None):
        self.policy = policy or EvaluationPolicy()
        self.tracker = get_outcome_tracker()
        self.scorer = ProtocolScorer(self.tracker)
        self.analyzer = EffectivenessAnalyzer(self.tracker, self.scorer)
        self.optimizer = get_threshold_optimizer()
        self.cycles: list[EvaluationCycle] = []
    
    def run_evaluation_cycle(self) -> EvaluationCycle:
        """Run a complete evaluation cycle."""
        
        cycle_id = str(uuid.uuid4())[:8]
        
        cycle = EvaluationCycle(
            cycle_id=cycle_id,
            timestamp=datetime.utcnow(),
            status=EvaluationStatus.RUNNING,
        )
        
        # Collect metrics
        cycle.total_interventions_evaluated = self.tracker.get_total_count()
        
        # Analyze overall effectiveness
        overall = self.analyzer.analyze_overall_effectiveness()
        cycle.overall_success_rate = overall.get("overall_success_rate", 0)
        cycle.average_performance_improvement = overall.get("average_performance_improvement", 0)
        cycle.average_risk_reduction = overall.get("average_risk_reduction", 0)
        cycle.average_recovery_time = overall.get("average_recovery_time", 0)
        
        # Score protocols
        protocol_scores = self.scorer.score_all_protocols()
        cycle.total_protocols_evaluated = len(protocol_scores)
        
        # Find protocols requiring review
        for score in protocol_scores:
            if score.requires_review:
                cycle.protocols_requiring_review.append(score.protocol_id)
        
        # Get rankings
        rankings = self.scorer.get_protocol_rankings()
        cycle.top_protocols = rankings.get("top", [])
        cycle.bottom_protocols = rankings.get("bottom", [])
        
        # Get threshold recommendations
        threshold_recs = self.optimizer.get_recommendations()
        cycle.threshold_recommendations = threshold_recs
        
        # Complete cycle
        cycle.status = EvaluationStatus.COMPLETED
        self.cycles.append(cycle)
        
        return cycle
    
    def get_effectiveness_report(self) -> Dict[str, Any]:
        """Get comprehensive effectiveness report."""
        
        overall = self.analyzer.analyze_overall_effectiveness()
        by_domain = self.analyzer.analyze_by_domain()
        trends = self.analyzer.analyze_trends()
        anomalies = self.analyzer.detect_anomalies()
        protocol_scores = self.scorer.score_all_protocols()
        rankings = self.scorer.get_protocol_rankings()
        thresholds = self.optimizer.get_recommendations()
        
        return {
            "overall": overall,
            "by_domain": by_domain,
            "trends": trends,
            "anomalies": anomalies,
            "protocol_scores": [
                {
                    "protocol_id": s.protocol_id,
                    "effectiveness": s.effectiveness_score,
                    "success_rate": s.success_rate,
                }
                for s in protocol_scores
            ],
            "rankings": rankings,
            "threshold_recommendations": thresholds,
        }
    
    def get_protocol_report(self, protocol_id: str) -> Dict[str, Any]:
        """Get report for a specific protocol."""
        
        score = self.scorer.score_protocol(protocol_id)
        
        return {
            "protocol_id": score.protocol_id,
            "protocol_name": score.protocol_name,
            "total_interventions": score.total_interventions,
            "successful_interventions": score.successful_interventions,
            "success_rate": score.success_rate,
            "effectiveness_score": score.effectiveness_score,
            "consistency_score": score.consistency_score,
            "average_performance_improvement": score.average_performance_improvement,
            "average_risk_reduction": score.average_risk_reduction,
            "recovery_rate": score.recovery_rate,
            "requires_review": score.requires_review,
            "review_reason": score.review_reason,
        }
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get all recommendations."""
        
        # Protocol recommendations
        rankings = self.scorer.get_protocol_rankings()
        
        # Threshold recommendations
        thresholds = self.optimizer.get_recommendations()
        
        # Anomalies
        anomalies = self.analyzer.detect_anomalies()
        
        return {
            "protocol_recommendations": {
                "preferred": rankings.get("top", []),
                "avoid": rankings.get("bottom", []),
                "requires_review": rankings.get("requires_review", []),
            },
            "threshold_recommendations": thresholds,
            "anomalies": anomalies,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics."""
        
        return {
            "total_cycles": len(self.cycles),
            "total_interventions_tracked": self.tracker.get_total_count(),
            "total_protocols_evaluated": len(self.scorer.score_all_protocols()),
            "recent_outcomes": self.tracker.get_statistics(),
        }


# Global engine
_evaluation_engine: Optional[InterventionEvaluationEngine] = None


def get_evaluation_engine() -> InterventionEvaluationEngine:
    """Get the global evaluation engine."""
    global _evaluation_engine
    if _evaluation_engine is None:
        _evaluation_engine = InterventionEvaluationEngine()
    return _evaluation_engine
