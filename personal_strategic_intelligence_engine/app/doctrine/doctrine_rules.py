"""Doctrine rule definitions and rule structures."""
import logging
from typing import Any, Dict, List, Optional

from app.doctrine.doctrine_models import (
    PolicyRule,
    PolicyRuleType,
    AlignmentScore,
    AlignmentLevel,
    DecisionContext,
    LIVE_EXECUTION_ENABLED,
)

logger = logging.getLogger(__name__)


class DoctrineRule:
    """Base class for doctrine rules."""

    def __init__(self, rule: PolicyRule):
        self.rule = rule
        self.rule_id = rule.rule_id
        self.rule_type = rule.rule_type

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate the rule against decision context."""
        raise NotImplementedError("Subclasses must implement evaluate()")

    def get_name(self) -> str:
        """Get rule name."""
        return self.rule.name

    def is_enabled(self) -> bool:
        """Check if rule is enabled."""
        return self.rule.enabled


class RiskManagementRule(DoctrineRule):
    """Rule for risk management evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate risk management alignment."""
        
        # Check optimization output for risk signals
        opt_output = context.optimization_output
        risk_score = opt_output.get("risk_score", 0.5)
        
        # Check for high-risk recommendations
        high_risk_recs = 0
        for rec in context.candidate_recommendations:
            if rec.get("risk_factors"):
                high_risk_recs += 1
        
        # Determine alignment
        if risk_score > 0.7 or high_risk_recs > 2:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.5
            explanation = f"High risk detected: score={risk_score}, high_risk_recs={high_risk_recs}"
        elif risk_score > 0.5 or high_risk_recs > 0:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"Moderate risk: score={risk_score}"
        else:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = "Risk levels acceptable"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "risk_score": risk_score,
                "high_risk_recommendations": high_risk_recs,
            }
        }


class CapitalAllocationRule(DoctrineRule):
    """Rule for capital/resource allocation evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate capital allocation alignment."""
        
        state = context.state_snapshot
        opt_output = context.optimization_output
        
        # Get resource allocations
        allocations = opt_output.get("resource_allocation", {})
        
        # Check if any domain exceeds reasonable allocation
        violations = []
        total = sum(allocations.values()) if allocations else 0
        
        if total > 100:
            violations.append("Total allocation exceeds 100%")
        
        for domain, alloc in allocations.items():
            if alloc > 40:
                violations.append(f"{domain} allocation too high: {alloc}%")
        
        if violations:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.3
            explanation = f"Allocation violations: {', '.join(violations)}"
        else:
            level = AlignmentLevel.ALIGNED
            score = 0.4
            explanation = "Capital allocation within bounds"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "total_allocation": total,
                "violations": violations,
            }
        }


class SignalReliabilityRule(DoctrineRule):
    """Rule for signal reliability evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate signal reliability alignment."""
        
        signals = context.signals
        
        if not signals:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.2
            explanation = "No signals available for evaluation"
            return {
                "rule_id": self.rule_id,
                "score": score,
                "level": level,
                "explanation": explanation,
                "factors": {"signal_count": 0}
            }
        
        # Check signal freshness and confidence
        low_confidence = 0
        stale_signals = 0
        
        for sig in signals:
            conf = sig.get("confidence_score", 0.5)
            fresh = sig.get("freshness_score", 0.5)
            
            if conf < 0.4:
                low_confidence += 1
            if fresh < 0.3:
                stale_signals += 1
        
        total = len(signals)
        
        if low_confidence > total * 0.5 or stale_signals > total * 0.3:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.4
            explanation = f"Low signal reliability: {low_confidence} low conf, {stale_signals} stale"
        elif low_confidence > 0 or stale_signals > 0:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"Some reliability concerns: {low_confidence} low conf"
        else:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = "Signal reliability acceptable"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "signal_count": total,
                "low_confidence": low_confidence,
                "stale_signals": stale_signals,
            }
        }


class ConfidenceThresholdRule(DoctrineRule):
    """Rule for confidence threshold evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate confidence threshold alignment."""
        
        opt_output = context.optimization_output
        learning = context.learning_feedback
        
        # Get confidence from optimization
        conf_score = opt_output.get("confidence", 0.5)
        
        # Check if learning has adjusted confidence
        adjusted = learning.get("confidence_adjustment", 0.0)
        final_conf = max(0.0, min(1.0, conf_score + adjusted))
        
        threshold = self.rule.threshold
        
        if final_conf < threshold:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.5 * (threshold - final_conf)
            explanation = f"Confidence {final_conf:.2f} below threshold {threshold}"
        elif final_conf < threshold + 0.1:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"Confidence {final_conf:.2f} near threshold"
        else:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = f"Confidence {final_conf:.2f} acceptable"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "base_confidence": conf_score,
                "adjusted_confidence": final_conf,
                "threshold": threshold,
                "adjustment": adjusted,
            }
        }


class StrategicAlignmentRule(DoctrineRule):
    """Rule for strategic alignment evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate strategic alignment."""
        
        state = context.state_snapshot
        opt_output = context.optimization_output
        learning = context.learning_feedback
        
        # Check if recommendations align with strategic priorities
        priorities = state.get("strategic_priorities", {})
        
        recs = context.candidate_recommendations
        aligned_recs = 0
        
        for rec in recs:
            domain = rec.get("target_domain", "")
            priority = rec.get("priority", 5)
            
            # Higher priority domain should have higher priority recommendations
            domain_priority = priorities.get(domain, 3)
            
            if priority <= domain_priority:
                aligned_recs += 1
        
        total = len(recs) if recs else 1
        alignment_ratio = aligned_recs / total
        
        if alignment_ratio >= 0.7:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = f"Strategic alignment good: {aligned_recs}/{total} aligned"
        elif alignment_ratio >= 0.4:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"Partial alignment: {aligned_recs}/{total}"
        else:
            level = AlignmentLevel.MISALIGNED
            score = -0.3
            explanation = f"Low strategic alignment: {aligned_recs}/{total}"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "total_recommendations": total,
                "aligned_recommendations": aligned_recs,
                "alignment_ratio": alignment_ratio,
            }
        }


class ConflictResolutionRule(DoctrineRule):
    """Rule for conflict resolution evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate conflict resolution."""
        
        journal = context.journal_history
        opt_output = context.optimization_output
        
        # Check for unresolved conflicts
        conflicts = opt_output.get("conflicts", [])
        
        if not conflicts:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = "No conflicts to resolve"
            return {
                "rule_id": self.rule_id,
                "score": score,
                "level": level,
                "explanation": explanation,
                "factors": {"conflict_count": 0}
            }
        
        # Check conflict severity
        high_severity = sum(1 for c in conflicts if c.get("severity", 0) > 0.7)
        
        if high_severity > 0:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.4
            explanation = f"{high_severity} high-severity conflicts detected"
        else:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"{len(conflicts)} conflicts detected, moderate severity"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "conflict_count": len(conflicts),
                "high_severity": high_severity,
            }
        }


class ConfidenceThresholdRule(DoctrineRule):
    """Rule for confidence threshold evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate confidence threshold alignment."""
        
        opt_output = context.optimization_output
        learning = context.learning_feedback
        
        # Get confidence from optimization
        conf_score = opt_output.get("confidence", 0.5)
        
        # Check if learning has adjusted confidence
        adjusted = learning.get("confidence_adjustment", 0.0)
        final_conf = max(0.0, min(1.0, conf_score + adjusted))
        
        threshold = self.rule.threshold
        
        if final_conf < threshold:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.5 * (threshold - final_conf)
            explanation = f"Confidence {final_conf:.2f} below threshold {threshold}"
        elif final_conf < threshold + 0.1:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"Confidence {final_conf:.2f} near threshold"
        else:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = f"Confidence {final_conf:.2f} acceptable"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "base_confidence": conf_score,
                "adjusted_confidence": final_conf,
                "threshold": threshold,
                "adjustment": adjusted,
            }
        }


class StrategicAlignmentRule(DoctrineRule):
    """Rule for strategic alignment evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate strategic alignment."""
        
        state = context.state_snapshot
        recs = context.candidate_recommendations
        
        # Check if recommendations align with strategic priorities
        priorities = state.get("strategic_priorities", {})
        aligned_recs = 0
        
        for rec in recs:
            domain = rec.get("target_domain", "")
            priority = rec.get("priority", 5)
            
            # Higher priority domain should have higher priority recommendations
            domain_priority = priorities.get(domain, 3)
            
            if priority <= domain_priority:
                aligned_recs += 1
        
        total = len(recs) if recs else 1
        alignment_ratio = aligned_recs / total
        
        if alignment_ratio >= 0.7:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = f"Strategic alignment good: {aligned_recs}/{total} aligned"
        elif alignment_ratio >= 0.4:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"Partial alignment: {aligned_recs}/{total}"
        else:
            level = AlignmentLevel.MISALIGNED
            score = -0.3
            explanation = f"Low strategic alignment: {aligned_recs}/{total}"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "total_recommendations": total,
                "aligned_recommendations": aligned_recs,
                "alignment_ratio": alignment_ratio,
            }
        }


class ConflictResolutionRule(DoctrineRule):
    """Rule for conflict resolution evaluation."""

    def evaluate(self, context: DecisionContext) -> Dict[str, Any]:
        """Evaluate conflict resolution."""
        
        opt_output = context.optimization_output
        
        # Check for unresolved conflicts
        conflicts = opt_output.get("conflicts", [])
        
        if not conflicts:
            level = AlignmentLevel.ALIGNED
            score = 0.5
            explanation = "No conflicts to resolve"
            return {
                "rule_id": self.rule_id,
                "score": score,
                "level": level,
                "explanation": explanation,
                "factors": {"conflict_count": 0}
            }
        
        # Check conflict severity
        high_severity = sum(1 for c in conflicts if c.get("severity", 0) > 0.7)
        
        if high_severity > 0:
            level = AlignmentLevel.REQUIRES_REVIEW
            score = -0.4
            explanation = f"{high_severity} high-severity conflicts detected"
        else:
            level = AlignmentLevel.NEUTRAL
            score = 0.0
            explanation = f"{len(conflicts)} conflicts detected, moderate severity"
        
        return {
            "rule_id": self.rule_id,
            "score": score,
            "level": level,
            "explanation": explanation,
            "factors": {
                "conflict_count": len(conflicts),
                "high_severity": high_severity,
            }
        }


# Rule factory functions
def create_default_rules() -> List[DoctrineRule]:
    """Create default doctrine rules."""
    
    rules = [
        # Risk Management
        RiskManagementRule(PolicyRule(
            rule_id="risk_mgmt_001",
            rule_type=PolicyRuleType.RISK_MANAGEMENT,
            name="Risk Threshold",
            description="Ensure risk levels are within acceptable bounds",
            weight=1.2,
            threshold=0.5,
            priority=1,
        )),
        
        # Capital Allocation
        CapitalAllocationRule(PolicyRule(
            rule_id="capital_001",
            rule_type=PolicyRuleType.CAPITAL_ALLOCATION,
            name="Capital Distribution",
            description="Ensure capital allocation is balanced",
            weight=1.0,
            threshold=0.4,
            priority=2,
        )),
        
        # Signal Reliability
        SignalReliabilityRule(PolicyRule(
            rule_id="signal_rel_001",
            rule_type=PolicyRuleType.SIGNAL_RELIABILITY,
            name="Signal Quality",
            description="Ensure input signals are reliable",
            weight=0.9,
            threshold=0.3,
            priority=1,
        )),
        
        # Confidence Threshold
        ConfidenceThresholdRule(PolicyRule(
            rule_id="conf_thresh_001",
            rule_type=PolicyRuleType.CONFIDENCE_THRESHOLD,
            name="Minimum Confidence",
            description="Ensure recommendation confidence meets minimum",
            weight=1.1,
            threshold=0.5,
            priority=1,
        )),
        
        # Strategic Alignment
        StrategicAlignmentRule(PolicyRule(
            rule_id="strat_align_001",
            rule_type=PolicyRuleType.STRATEGIC_ALIGNMENT,
            name="Strategic Fit",
            description="Ensure recommendations align with strategy",
            weight=1.0,
            threshold=0.5,
            priority=2,
        )),
        
        # Conflict Resolution
        ConflictResolutionRule(PolicyRule(
            rule_id="conflict_001",
            rule_type=PolicyRuleType.CONFLICT_RESOLUTION,
            name="Conflict Handling",
            description="Ensure conflicts are properly resolved",
            weight=0.8,
            threshold=0.5,
            priority=3,
        )),
    ]
    
    return rules
