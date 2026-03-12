"""Effectiveness Analyzer - Analyzes intervention effectiveness metrics."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.intervention_evaluation.evaluation_types import (
    EvaluationCycle,
    ThresholdAnalysis,
    EvaluationStatus,
)
from app.intervention_evaluation.intervention_outcome_tracker import InterventionOutcomeTracker
from app.intervention_evaluation.protocol_scorer import ProtocolScorer


class EffectivenessAnalyzer:
    """Analyzes intervention effectiveness."""
    
    def __init__(
        self,
        tracker: InterventionOutcomeTracker,
        scorer: ProtocolScorer,
    ):
        self.tracker = tracker
        self.scorer = scorer
    
    def analyze_overall_effectiveness(self) -> Dict[str, Any]:
        """Calculate overall effectiveness metrics."""
        
        outcomes = self.tracker.outcomes
        
        if not outcomes:
            return {
                "total_interventions": 0,
                "overall_success_rate": 0.0,
                "average_performance_improvement": 0.0,
                "average_risk_reduction": 0.0,
                "average_recovery_time": 0.0,
            }
        
        total = len(outcomes)
        
        # Success rate
        success = sum(1 for o in outcomes if o.outcome == "success")
        success_rate = success / total if total > 0 else 0
        
        # Average improvements
        avg_perf = sum(o.performance_change for o in outcomes) / total
        avg_risk = sum(o.risk_change for o in outcomes) / total
        avg_momentum = sum(o.momentum_change for o in outcomes) / total
        
        # Recovery time
        recovery_outcomes = [o for o in outcomes if o.recovered and o.time_to_recovery_days]
        avg_recovery = 0
        if recovery_outcomes:
            avg_recovery = sum(o.time_to_recovery_days for o in recovery_outcomes) / len(recovery_outcomes)
        
        return {
            "total_interventions": total,
            "successful_interventions": success,
            "overall_success_rate": success_rate,
            "average_performance_improvement": avg_perf,
            "average_risk_reduction": avg_risk,
            "average_momentum_change": avg_momentum,
            "average_recovery_time": avg_recovery,
            "recovery_rate": len(recovery_outcomes) / total if total > 0 else 0,
        }
    
    def analyze_by_domain(self) -> Dict[str, Dict[str, Any]]:
        """Analyze effectiveness by domain."""
        
        # Group outcomes by domain
        by_domain: Dict[str, List] = {}
        
        for outcome in self.tracker.outcomes:
            domain = outcome.target_domain
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(outcome)
        
        # Calculate metrics per domain
        results = {}
        
        for domain, outcomes in by_domain.items():
            if not outcomes:
                continue
            
            total = len(outcomes)
            success = sum(1 for o in outcomes if o.outcome == "success")
            
            results[domain] = {
                "total_interventions": total,
                "success_count": success,
                "success_rate": success / total if total > 0 else 0,
                "average_performance_change": sum(o.performance_change for o in outcomes) / total,
                "average_risk_change": sum(o.risk_change for o in outcomes) / total,
            }
        
        return results
    
    def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze recent trends."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [o for o in self.tracker.outcomes if o.timestamp > cutoff]
        
        if not recent:
            return {
                "period_days": days,
                "interventions": 0,
                "trend": "insufficient_data",
            }
        
        # Calculate week-by-week
        weeks = {}
        for outcome in recent:
            week_num = (outcome.timestamp - cutoff).days // 7
            if week_num not in weeks:
                weeks[week_num] = []
            weeks[week_num].append(outcome)
        
        weekly_rates = []
        for week in sorted(weeks.keys()):
            outcomes = weeks[week]
            success = sum(1 for o in outcomes if o.outcome == "success")
            rate = success / len(outcomes) if outcomes else 0
            weekly_rates.append(rate)
        
        # Determine trend
        if len(weekly_rates) < 2:
            trend = "insufficient_data"
        elif weekly_rates[-1] > weekly_rates[0]:
            trend = "improving"
        elif weekly_rates[-1] < weekly_rates[0]:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "period_days": days,
            "interventions": len(recent),
            "weekly_rates": weekly_rates,
            "trend": trend,
        }
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous intervention patterns."""
        
        anomalies = []
        
        # Harmful interventions
        harmful = [o for o in self.tracker.outcomes if o.outcome == "harmful"]
        if harmful:
            anomalies.append({
                "type": "harmful_interventions",
                "count": len(harmful),
                "domains": list(set(o.target_domain for o in harmful)),
                "severity": "high",
            })
        
        # Ineffective protocols
        protocol_scores = self.scorer.score_all_protocols()
        for score in protocol_scores:
            if score.requires_review:
                anomalies.append({
                    "type": "ineffective_protocol",
                    "protocol": score.protocol_id,
                    "reason": score.review_reason,
                    "severity": "medium",
                })
        
        # Domains with multiple failures
        by_domain: Dict[str, int] = {}
        for outcome in self.tracker.outcomes:
            if outcome.outcome == "failure" or outcome.outcome == "harmful":
                by_domain[outcome.target_domain] = by_domain.get(outcome.target_domain, 0) + 1
        
        for domain, count in by_domain.items():
            if count >= 3:
                anomalies.append({
                    "type": "recurring_failures",
                    "domain": domain,
                    "count": count,
                    "severity": "high" if count >= 5 else "medium",
                })
        
        return anomalies


# Global analyzer
_analyzer: Optional[EffectivenessAnalyzer] = None


def get_effectiveness_analyzer() -> EffectivenessAnalyzer:
    """Get the global effectiveness analyzer."""
    global _analyzer
    if _analyzer is None:
        from app.intervention_evaluation.intervention_outcome_tracker import get_outcome_tracker
        tracker = get_outcome_tracker()
        scorer = ProtocolScorer(tracker)
        _analyzer = EffectivenessAnalyzer(tracker, scorer)
    return _analyzer
