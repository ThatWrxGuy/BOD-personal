"""Replay engine for safely replaying historical decision cycles."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.decision_journal.journal_models import (
    AuditComparisonResult,
    DecisionCycleSnapshot,
    DriftClassification,
    ReplayRequest,
    ReplayResult,
    ReplayStatus,
    RecommendationSnapshot,
    LIVE_EXECUTION_ENABLED,
    REPLAY_MODE,
)
from app.decision_journal.journal_store import get_journal_store
from app.optimization.optimization_types import LifeDomain

logger = logging.getLogger(__name__)


class ReplayEngine:
    """Replays historical decision cycles using stored snapshots."""

    def __init__(self):
        self.store = get_journal_store()

    def replay_cycle(
        self,
        request: ReplayRequest,
        compare_outputs: bool = True
    ) -> ReplayResult:
        """Replay a historical decision cycle."""
        
        # Enforce replay mode safety
        if not REPLAY_MODE:
            return ReplayResult(
                original_cycle_id=request.cycle_id,
                replay_timestamp=datetime.utcnow(),
                status=ReplayStatus.FAILED,
                error_message="Replay mode is not enabled",
            )

        start_time = datetime.utcnow()

        # Get original cycle
        original_cycle = self.store.get_cycle(request.cycle_id)
        if not original_cycle:
            return ReplayResult(
                original_cycle_id=request.cycle_id,
                replay_timestamp=datetime.utcnow(),
                status=ReplayStatus.FAILED,
                error_message=f"Cycle {request.cycle_id} not found",
            )

        try:
            # Get replayable input bundle
            replay_bundle = original_cycle.replayable_input_bundle
            
            # Run the optimization with the stored inputs
            replayed_recommendations = self._run_optimization_replay(
                replay_bundle,
                original_cycle
            )

            # Compare outputs if requested
            if compare_outputs:
                comparison = self._compare_outputs(
                    original_cycle.recommendations,
                    replayed_recommendations,
                    original_cycle.detected_conflicts,
                )
                
                drift = self._classify_drift(
                    comparison.confidence_differences,
                    comparison.conflict_differences,
                    comparison.priority_differences,
                )
                
                drift_classification = drift
            else:
                comparison = AuditComparisonResult(
                    cycle_id=request.cycle_id,
                    compared_timestamp=datetime.utcnow(),
                )
                drift_classification = DriftClassification.NONE

            # Calculate latency
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            return ReplayResult(
                original_cycle_id=request.cycle_id,
                replay_timestamp=datetime.utcnow(),
                status=ReplayStatus.COMPLETED,
                replayed_recommendations=replayed_recommendations,
                original_recommendations=original_cycle.recommendations,
                confidence_deltas=comparison.confidence_differences,
                conflict_deltas=comparison.conflict_differences,
                divergences=comparison.priority_differences,
                drift_classification=drift_classification,
                processing_latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Replay failed: {e}")
            return ReplayResult(
                original_cycle_id=request.cycle_id,
                replay_timestamp=datetime.utcnow(),
                status=ReplayStatus.FAILED,
                error_message=str(e),
            )

    def _run_optimization_replay(
        self,
        replay_bundle: Dict[str, Any],
        original_cycle: DecisionCycleSnapshot
    ) -> List[RecommendationSnapshot]:
        """Run optimization with replay inputs."""
        
        # Import here to avoid circular imports
        from app.optimization.domain_optimizer import DomainOptimizer
        from app.optimization.optimization_types import DomainMetrics, LifeDomain
        
        try:
            # Try to reconstruct domain metrics from the bundle
            domain_metrics = []
            
            if "domain_metrics" in replay_bundle:
                for m in replay_bundle["domain_metrics"]:
                    domain_metrics.append(DomainMetrics(
                        domain=LifeDomain(m.get("domain", "health")),
                        performance_score=m.get("performance_score", 5.0),
                        risk_score=m.get("risk_score", 5.0),
                        opportunity_score=m.get("opportunity_score", 5.0),
                        momentum_score=m.get("momentum_score", 0.0),
                        alignment_score=m.get("alignment_score", 5.0),
                        resource_allocation=m.get("resource_allocation", 20.0),
                        strategic_priority=m.get("strategic_priority", 1),
                    ))
            
            # If we have signals, convert them to metrics
            if not domain_metrics and original_cycle.normalized_signals:
                for sig in original_cycle.normalized_signals:
                    domain = self._infer_domain_from_signal(sig)
                    if domain:
                        np = sig.normalized_payload
                        domain_metrics.append(DomainMetrics(
                            domain=domain,
                            performance_score=np.get("performance_score", 5.0),
                            risk_score=np.get("risk_score", 5.0),
                            opportunity_score=np.get("opportunity_score", 5.0),
                            momentum_score=np.get("momentum_score", 0.0),
                            alignment_score=np.get("alignment_score", 5.0),
                            resource_allocation=np.get("resource_allocation", 20.0),
                            strategic_priority=1,
                        ))
            
            # If still no metrics, use defaults
            if not domain_metrics:
                domain_metrics = self._get_default_metrics()
            
            # Run optimization
            optimizer = DomainOptimizer()
            cycle = optimizer.run_optimization_cycle(domain_metrics)
            
            # Convert recommendations to snapshots
            recommendations = []
            for rec in cycle.recommendations:
                recommendations.append(RecommendationSnapshot(
                    recommendation_id=f"{rec.target_domain.value}_{rec.action.value}" if hasattr(rec.target_domain, 'value') else f"{rec.target_domain}_{rec.action}",
                    action=rec.action.value if hasattr(rec.action, 'value') else str(rec.action),
                    target_domain=rec.target_domain.value if hasattr(rec.target_domain, 'value') else str(rec.target_domain),
                    priority=rec.priority,
                    reasoning=rec.reasoning,
                    expected_impact=rec.expected_impact,
                    confidence=rec.confidence,
                    urgency=rec.urgency if hasattr(rec, 'urgency') else "medium",
                    suggested_next_steps=rec.suggested_next_steps if hasattr(rec, 'suggested_next_steps') else [],
                    evidence_chain=rec.evidence_chain if hasattr(rec, 'evidence_chain') else {},
                    risk_factors=rec.risk_factors if hasattr(rec, 'risk_factors') else [],
                    confidence_factors=rec.confidence_factors if hasattr(rec, 'confidence_factors') else {},
                    policy_constraints_respected=rec.policy_constraints_respected if hasattr(rec, 'policy_constraints_respected') else True,
                    is_blocked=rec.action.value == "maintain_status_quo" if hasattr(rec.action, 'value') else False,
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization replay failed: {e}")
            # Return empty recommendations on failure
            return []

    def _infer_domain_from_signal(self, signal) -> LifeDomain:
        """Infer domain from signal type."""
        type_to_domain = {
            "health": LifeDomain.HEALTH,
            "wealth": LifeDomain.WEALTH,
            "career": LifeDomain.CAREER,
            "relationships": LifeDomain.RELATIONSHIPS,
            "learning": LifeDomain.LEARNING,
        }
        
        signal_type = signal.signal_type.lower()
        return type_to_domain.get(signal_type)

    def _get_default_metrics(self) -> List:
        """Get default metrics for replay."""
        from app.optimization.optimization_types import DomainMetrics, LifeDomain
        
        return [
            DomainMetrics(
                domain=LifeDomain.HEALTH,
                performance_score=5.0, risk_score=5.0, opportunity_score=5.0,
                momentum_score=0.0, alignment_score=5.0,
                resource_allocation=20.0, strategic_priority=1,
            ),
            DomainMetrics(
                domain=LifeDomain.WEALTH,
                performance_score=5.0, risk_score=5.0, opportunity_score=5.0,
                momentum_score=0.0, alignment_score=5.0,
                resource_allocation=20.0, strategic_priority=2,
            ),
        ]

    def _compare_outputs(
        self,
        original: List[RecommendationSnapshot],
        replayed: List[RecommendationSnapshot],
        original_conflicts: List
    ) -> AuditComparisonResult:
        """Compare original and replayed outputs."""
        
        comparison = AuditComparisonResult(
            cycle_id="",
            compared_timestamp=datetime.utcnow(),
        )
        
        # Compare recommendation counts
        comparison.recommendation_count_delta = len(replayed) - len(original)
        
        # Compare confidences
        orig_conf = {r.target_domain: r.confidence for r in original}
        repl_conf = {r.target_domain: r.confidence for r in replayed}
        
        for domain in set(list(orig_conf.keys()) + list(repl_conf.keys())):
            orig_c = orig_conf.get(domain, 0)
            repl_c = repl_conf.get(domain, 0)
            delta = repl_c - orig_c
            
            if abs(delta) > 0.1:
                comparison.confidence_differences.append({
                    "domain": domain,
                    "original": orig_c,
                    "replayed": repl_c,
                    "delta": delta,
                })
        
        # Compare priorities
        orig_pri = {r.target_domain: r.priority for r in original}
        repl_pri = {r.target_domain: r.priority for r in replayed}
        
        for domain in set(list(orig_pri.keys()) + list(repl_pri.keys())):
            orig_p = orig_pri.get(domain, 0)
            repl_p = repl_pri.get(domain, 0)
            
            if orig_p != repl_p:
                comparison.priority_differences.append({
                    "domain": domain,
                    "original": orig_p,
                    "replayed": repl_p,
                })
        
        return comparison

    def _classify_drift(
        self,
        confidence_diffs: List[Dict],
        conflict_diffs: List,
        priority_diffs: List[Dict]
    ) -> DriftClassification:
        """Classify the level of behavioral drift."""
        
        # Count significant differences
        sig_confidence = sum(1 for d in confidence_diffs if abs(d.get("delta", 0)) > 0.2)
        sig_priority = len(priority_diffs)
        
        if sig_confidence == 0 and sig_priority == 0:
            return DriftClassification.NONE
        elif sig_confidence <= 1 and sig_priority <= 1:
            return DriftClassification.MINOR
        elif sig_confidence <= 2 and sig_priority <= 2:
            return DriftClassification.MODERATE
        else:
            return DriftClassification.SIGNIFICANT


# Global engine instance
_engine: Optional[ReplayEngine] = None


def get_replay_engine() -> ReplayEngine:
    """Get the global replay engine instance."""
    global _engine
    if _engine is None:
        _engine = ReplayEngine()
    return _engine
