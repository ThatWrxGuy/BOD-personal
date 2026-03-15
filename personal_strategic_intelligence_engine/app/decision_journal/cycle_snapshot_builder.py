"""Cycle snapshot builder for creating decision cycle snapshots."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.decision_journal.journal_models import (
    ConflictSnapshot,
    DecisionCycleSnapshot,
    RecommendationSnapshot,
    SignalSnapshot,
)
from app.optimization.optimization_types import (
    OptimizationCycle,
    OptimizationActionRecommendation,
)
from app.signal_ingestion.signal_models import NormalizedSignal

logger = logging.getLogger(__name__)


class CycleSnapshotBuilder:
    """Builds complete decision-cycle snapshots from the live observation pipeline."""

    def __init__(self):
        self._subsystem_versions = {
            "optimization": "1.0.0",
            "forecasting": "1.0.0",
            "signal_ingestion": "1.0.0",
            "decision_journal": "1.0.0",
        }

    def build_from_optimization_cycle(
        self,
        cycle: OptimizationCycle,
        normalized_signals: Optional[List[NormalizedSignal]] = None,
    ) -> DecisionCycleSnapshot:
        """Build a snapshot from an optimization cycle."""
        
        # Convert signals
        signal_snapshots = []
        if normalized_signals:
            for sig in normalized_signals:
                signal_snapshots.append(self._convert_signal(sig))

        # Convert recommendations
        recommendation_snapshots = []
        for rec in cycle.recommendations:
            recommendation_snapshots.append(self._convert_recommendation(rec))

        # Convert conflicts
        conflict_snapshots = []
        for conflict in cycle.conflict_decisions:
            conflict_snapshots.append(ConflictSnapshot(
                conflict_type=conflict.conflict_type.value if hasattr(conflict.conflict_type, 'value') else str(conflict.conflict_type),
                domains_involved=[d.value if hasattr(d, 'value') else str(d) for d in conflict.domains_involved],
                severity=conflict.severity,
                description=conflict.description,
                resolution=conflict.resolution,
            ))

        # Build confidence summary
        confidence_summary = self._build_confidence_summary(recommendation_snapshots)

        # Build rationale summary
        rationale_summary = self._build_rationale_summary(
            cycle.detected_conditions,
            conflict_snapshots,
            recommendation_snapshots,
        )

        # Create replayable input bundle
        replayable_bundle = {
            "cycle_id": cycle.cycle_id,
            "domain_metrics": [self._serialize_metrics(m) for m in cycle.domain_metrics],
            "detected_conditions": cycle.detected_conditions,
            "tradeoff_count": len(cycle.conflict_decisions),
        }

        return DecisionCycleSnapshot(
            cycle_id=cycle.cycle_id,
            timestamp=cycle.timestamp,
            source_signal_ids=[s.signal_id for s in signal_snapshots],
            normalized_signals=signal_snapshots,
            state_summary=cycle.input_metrics_summary or {},
            detected_conditions=cycle.detected_conditions,
            detected_conflicts=conflict_snapshots,
            recommendations=recommendation_snapshots,
            confidence_summary=confidence_summary,
            rationale_summary=rationale_summary,
            subsystem_versions=self._subsystem_versions,
            replayable_input_bundle=replayable_bundle,
        )

    def build_from_signals_and_recommendations(
        self,
        signals: List[NormalizedSignal],
        recommendations: List[OptimizationActionRecommendation],
        conditions: List[str] = None,
        conflicts: List[Dict[str, Any]] = None,
        state_summary: Dict[str, Any] = None,
    ) -> DecisionCycleSnapshot:
        """Build a snapshot from signals and recommendations (without full optimization cycle)."""
        
        import uuid
        
        cycle_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow()

        # Convert signals
        signal_snapshots = [self._convert_signal(sig) for sig in signals]

        # Convert recommendations
        recommendation_snapshots = [
            self._convert_recommendation(rec) for rec in recommendations
        ]

        # Convert conflicts
        conflict_snapshots = []
        if conflicts:
            for conflict in conflicts:
                conflict_snapshots.append(ConflictSnapshot(
                    conflict_type=conflict.get("type", "unknown"),
                    domains_involved=conflict.get("domains", []),
                    severity=conflict.get("severity", 0.0),
                    description=conflict.get("description", ""),
                    resolution=conflict.get("resolution"),
                ))

        # Build confidence summary
        confidence_summary = self._build_confidence_summary(recommendation_snapshots)

        # Build rationale summary
        rationale_summary = self._build_rationale_summary(
            conditions or [],
            conflict_snapshots,
            recommendation_snapshots,
        )

        # Create replayable bundle
        replayable_bundle = {
            "cycle_id": cycle_id,
            "signal_count": len(signals),
            "conditions": conditions or [],
            "conflict_count": len(conflicts) if conflicts else 0,
        }

        return DecisionCycleSnapshot(
            cycle_id=cycle_id,
            timestamp=timestamp,
            source_signal_ids=[s.signal_id for s in signal_snapshots],
            normalized_signals=signal_snapshots,
            state_summary=state_summary or {},
            detected_conditions=conditions or [],
            detected_conflicts=conflict_snapshots,
            recommendations=recommendation_snapshots,
            confidence_summary=confidence_summary,
            rationale_summary=rationale_summary,
            subsystem_versions=self._subsystem_versions,
            replayable_input_bundle=replayable_bundle,
        )

    def _convert_signal(self, signal: NormalizedSignal) -> SignalSnapshot:
        """Convert a normalized signal to a snapshot."""
        return SignalSnapshot(
            signal_id=signal.signal_id,
            source_id=signal.source_id,
            signal_type=signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
            raw_payload=signal.raw_payload,
            normalized_payload=signal.normalized_payload,
            timestamp=signal.timestamp,
            ingestion_timestamp=signal.ingestion_timestamp,
            freshness_score=signal.freshness_score,
            confidence_score=signal.confidence_score,
        )

    def _convert_recommendation(self, rec: OptimizationActionRecommendation) -> RecommendationSnapshot:
        """Convert a recommendation to a snapshot."""
        return RecommendationSnapshot(
            recommendation_id=f"{rec.target_domain.value}_{rec.action.value}" if hasattr(rec.target_domain, 'value') and hasattr(rec.action, 'value') else f"{rec.target_domain}_{rec.action}",
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
        )

    def _build_confidence_summary(self, recommendations: List[RecommendationSnapshot]) -> Dict[str, Any]:
        """Build a confidence summary from recommendations."""
        if not recommendations:
            return {
                "average_confidence": 0.0,
                "high_confidence_count": 0,
                "low_confidence_count": 0,
            }

        confidences = [r.confidence for r in recommendations]
        avg_confidence = sum(confidences) / len(confidences)

        return {
            "average_confidence": avg_confidence,
            "high_confidence_count": sum(1 for c in confidences if c >= 0.7),
            "low_confidence_count": sum(1 for c in confidences if c < 0.4),
            "total_recommendations": len(recommendations),
        }

    def _build_rationale_summary(
        self,
        conditions: List[str],
        conflicts: List[ConflictSnapshot],
        recommendations: List[RecommendationSnapshot]
    ) -> str:
        """Build a human-readable rationale summary."""
        parts = []

        if conditions:
            parts.append(f"Detected conditions: {', '.join(conditions)}")

        if conflicts:
            conflict_types = set(c.conflict_type for c in conflicts)
            parts.append(f"Detected conflicts: {', '.join(conflict_types)}")

        if recommendations:
            action_counts = {}
            for rec in recommendations:
                action_counts[rec.action] = action_counts.get(rec.action, 0) + 1
            
            action_summary = ", ".join(f"{count} {action}" for action, count in action_counts.items())
            parts.append(f"Generated {len(recommendations)} recommendations ({action_summary})")

        return "; ".join(parts) if parts else "No significant findings"

    def _serialize_metrics(self, metrics) -> Dict[str, Any]:
        """Serialize domain metrics for replay."""
        return {
            "domain": metrics.domain.value if hasattr(metrics.domain, 'value') else str(metrics.domain),
            "performance_score": metrics.performance_score,
            "risk_score": metrics.risk_score,
            "opportunity_score": metrics.opportunity_score,
            "momentum_score": metrics.momentum_score,
            "alignment_score": metrics.alignment_score,
            "resource_allocation": metrics.resource_allocation,
            "strategic_priority": metrics.strategic_priority,
        }


# Global builder instance
_builder: Optional[CycleSnapshotBuilder] = None


def get_cycle_snapshot_builder() -> CycleSnapshotBuilder:
    """Get the global cycle snapshot builder instance."""
    global _builder
    if _builder is None:
        _builder = CycleSnapshotBuilder()
    return _builder
