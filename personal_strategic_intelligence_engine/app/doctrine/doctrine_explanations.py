"""Doctrine explanation engine for audit and inspection."""
import logging
from typing import Any, Dict, List, Optional

from app.doctrine.doctrine_models import (
    DoctrineAssessment,
    DoctrineConflict,
    DoctrineRecommendation,
)

logger = logging.getLogger(__name__)


class DoctrineExplainer:
    """Generates structured explanations for doctrine evaluations."""

    def explain_assessment(self, assessment: DoctrineAssessment) -> Dict[str, Any]:
        """Generate detailed explanation for a doctrine assessment."""
        
        explanation = {
            "summary": assessment.evaluation_summary,
            "alignment": {
                "level": assessment.alignment_score.level.value,
                "score": assessment.alignment_score.score,
                "confidence": assessment.alignment_score.confidence,
            },
            "rules_applied": [],
            "conflicts": [],
            "risk_flags": assessment.risk_flags,
            "recommendations": [],
            "why_triggered": [],
            "why_not_triggered": [],
        }
        
        # Explain each rule
        for rule_id in assessment.policy_rules_applied:
            rule_explanation = self._explain_rule(rule_id, assessment)
            explanation["rules_applied"].append(rule_explanation)
        
        # Explain conflicts
        for conflict in assessment.doctrine_conflicts:
            conflict_explanation = self._explain_conflict(conflict)
            explanation["conflicts"].append(conflict_explanation)
        
        # Explain recommendations
        for rec in assessment.recommended_adjustments:
            rec_explanation = self._explain_recommendation(rec)
            explanation["recommendations"].append(rec_explanation)
        
        # Add why triggered / not triggered
        explanation["why_triggered"] = self._get_triggered_reasons(assessment)
        explanation["why_not_triggered"] = self._get_not_triggered_reasons(assessment)
        
        return explanation

    def _explain_rule(self, rule_id: str, assessment: DoctrineAssessment) -> Dict[str, Any]:
        """Explain a specific rule's evaluation."""
        
        # Get rule result from factors
        score = assessment.alignment_score.factors.get(rule_id, 0.0)
        
        # Determine trigger status
        is_triggered = assessment.alignment_score.level.value in [
            "misaligned", "requires_review"
        ]
        
        return {
            "rule_id": rule_id,
            "contribution": score,
            "triggered": is_triggered,
            "impact": "high" if abs(score) > 0.3 else "medium" if abs(score) > 0.1 else "low",
        }

    def _explain_conflict(self, conflict: DoctrineConflict) -> Dict[str, Any]:
        """Explain a doctrine conflict."""
        
        return {
            "type": conflict.conflict_type,
            "severity": conflict.severity,
            "description": conflict.description,
            "rules_involved": conflict.rules_involved,
            "resolution": conflict.resolution_suggestion or "Manual review required",
            "requires_attention": conflict.severity > 0.5,
        }

    def _explain_recommendation(self, rec: DoctrineRecommendation) -> Dict[str, Any]:
        """Explain a doctrine recommendation."""
        
        return {
            "type": rec.adjustment_type,
            "target": rec.target,
            "adjustment": rec.adjustment,
            "rationale": rec.rationale,
            "priority": rec.priority,
            "actionable": rec.adjustment_type in ["priority_adjustment", "policy_adjustment"],
        }

    def _get_triggered_reasons(self, assessment: DoctrineAssessment) -> List[str]:
        """Get reasons why rules were triggered."""
        reasons = []
        
        for conflict in assessment.doctrine_conflicts:
            if conflict.severity > 0.7:
                reasons.append(
                    f"High severity conflict in {conflict.conflict_type}: "
                    f"{conflict.description}"
                )
        
        for flag in assessment.risk_flags[:3]:  # Limit to top 3
            reasons.append(f"Risk flag: {flag}")
        
        return reasons

    def _get_not_triggered_reasons(self, assessment: DoctrineAssessment) -> List[str]:
        """Get reasons why rules were not triggered."""
        reasons = []
        
        if assessment.alignment_score.level.value == "aligned":
            reasons.append("All policy rules satisfied")
            reasons.append("No high-severity conflicts detected")
            reasons.append("Recommendations within acceptable thresholds")
        
        return reasons

    def generate_audit_report(self, assessment: DoctrineAssessment) -> str:
        """Generate human-readable audit report."""
        
        lines = []
        
        lines.append("=" * 60)
        lines.append("DOCTRINE EVALUATION AUDIT REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"Cycle ID: {assessment.cycle_id}")
        lines.append(f"Timestamp: {assessment.timestamp}")
        lines.append(f"Doctrine Version: {assessment.doctrine_version}")
        lines.append("")
        
        lines.append("ALIGNMENT ASSESSMENT")
        lines.append("-" * 40)
        lines.append(f"Level: {assessment.alignment_score.level.value}")
        lines.append(f"Score: {assessment.alignment_score.score:.3f}")
        lines.append(f"Confidence: {assessment.alignment_score.confidence:.3f}")
        lines.append("")
        
        if assessment.doctrine_conflicts:
            lines.append("CONFLICTS DETECTED")
            lines.append("-" * 40)
            for conflict in assessment.doctrine_conflicts:
                lines.append(f"  - {conflict.conflict_type}: {conflict.description}")
                lines.append(f"    Severity: {conflict.severity:.2f}")
            lines.append("")
        
        if assessment.risk_flags:
            lines.append("RISK FLAGS")
            lines.append("-" * 40)
            for flag in assessment.risk_flags:
                lines.append(f"  - {flag}")
            lines.append("")
        
        if assessment.recommended_adjustments:
            lines.append("RECOMMENDED ADJUSTMENTS")
            lines.append("-" * 40)
            for rec in assessment.recommended_adjustments:
                lines.append(f"  - {rec.adjustment_type}: {rec.rationale}")
            lines.append("")
        
        lines.append("POLICY RULES APPLIED")
        lines.append("-" * 40)
        for rule_id in assessment.policy_rules_applied:
            lines.append(f"  - {rule_id}")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append(assessment.evaluation_summary)
        lines.append("=" * 60)
        
        return "\n".join(lines)

    def explain_for_replay(self, assessment: DoctrineAssessment) -> Dict[str, Any]:
        """Generate explanation suitable for replay inspection."""
        
        return {
            "replay_compatible": True,
            "deterministic": True,
            "inputs_used": {
                "signals": assessment.signals_considered,
                "journal_events": assessment.journal_events_referenced,
                "learning_feedback": assessment.learning_feedback_used,
                "rules": assessment.policy_rules_applied,
            },
            "version": assessment.doctrine_version,
            "audit_trail": {
                "rules_applied": len(assessment.policy_rules_applied),
                "conflicts_found": len(assessment.doctrine_conflicts),
                "risk_flags_raised": len(assessment.risk_flags),
            }
        }


# Global explainer instance
_explainer: Optional[DoctrineExplainer] = None


def get_doctrine_explainer() -> DoctrineExplainer:
    """Get the global doctrine explainer instance."""
    global _explainer
    if _explainer is None:
        _explainer = DoctrineExplainer()
    return _explainer
