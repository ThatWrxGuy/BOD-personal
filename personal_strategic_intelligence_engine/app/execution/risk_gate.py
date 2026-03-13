"""Risk gate - evaluates risk conditions for execution."""
import logging
from typing import List, Optional

from app.execution.execution_models import (
    ExecutionIntent,
    RiskGateResult,
    RISK_THRESHOLD,
)

logger = logging.getLogger(__name__)


class RiskGate:
    """Evaluates risk conditions for execution."""

    def __init__(self, threshold: float = RISK_THRESHOLD):
        self._threshold = threshold
        
        # Risk factors to check
        self._high_risk_actions = {
            "delete",
            "remove",
            "revoke",
            "suspend",
            "terminate",
        }
        
        self._medium_risk_actions = {
            "modify",
            "update",
            "change",
            "adjust",
        }

    def validate(self, intent: ExecutionIntent, additional_risk: float = 0.0) -> RiskGateResult:
        """
        Validate execution intent against risk thresholds.
        
        Args:
            intent: The execution intent to validate
            additional_risk: Additional risk score from external sources
            
        Returns:
            RiskGateResult with risk assessment
        """
        risk_flags = []
        
        # Calculate base risk from action type
        action_risk = self._calculate_action_risk(intent.action_type)
        risk_flags.extend(action_risk["flags"])
        
        # Calculate risk from parameters
        param_risk = self._calculate_parameter_risk(intent.parameters)
        risk_flags.extend(param_risk["flags"])
        
        # Add confidence-based risk (lower confidence = higher risk)
        confidence_risk = self._calculate_confidence_risk(intent.confidence)
        risk_flags.extend(confidence_risk["flags"])
        
        # Add additional risk
        if additional_risk > 0:
            risk_flags.append(f"external_risk: {additional_risk}")
        
        # Calculate total risk score
        total_risk = min(1.0, action_risk["score"] + param_risk["score"] + 
                        confidence_risk["score"] + additional_risk)
        
        # Determine if passed
        passed = total_risk <= self._threshold
        
        # Determine risk level
        if total_risk > 0.7:
            risk_level = "critical"
        elif total_risk > 0.5:
            risk_level = "high"
        elif total_risk > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        result = RiskGateResult(
            passed=passed,
            risk_level=risk_level,
            risk_score=total_risk,
            risk_flags=risk_flags,
            threshold=self._threshold,
        )
        
        if not passed:
            logger.warning(f"Risk gate blocked intent {intent.intent_id}: risk={total_risk:.2f} > threshold={self._threshold}")
        
        return result

    def _calculate_action_risk(self, action_type: str) -> dict:
        """Calculate risk from action type."""
        flags = []
        score = 0.0
        
        action_lower = action_type.lower()
        
        # Check for high-risk actions
        for high_risk in self._high_risk_actions:
            if high_risk in action_lower:
                flags.append(f"high_risk_action: {action_type}")
                score = 0.5
                break
        
        # Check for medium-risk actions if not high-risk
        if not flags:
            for med_risk in self._medium_risk_actions:
                if med_risk in action_lower:
                    flags.append(f"medium_risk_action: {action_type}")
                    score = 0.25
                    break
        
        return {"flags": flags, "score": score}

    def _calculate_parameter_risk(self, parameters: dict) -> dict:
        """Calculate risk from parameters."""
        flags = []
        score = 0.0
        
        # Check for aggressive parameters
        if "adjustment" in parameters:
            adj = parameters["adjustment"]
            if isinstance(adj, (int, float)):
                if abs(adj) > 0.5:
                    flags.append(f"large_adjustment: {adj}")
                    score += 0.2
                elif abs(adj) > 0.3:
                    flags.append(f"moderate_adjustment: {adj}")
                    score += 0.1
        
        # Check for resource overallocation
        if "resource_allocation" in parameters:
            alloc = parameters["resource_allocation"]
            if isinstance(alloc, dict):
                total = sum(alloc.values()) if alloc else 0
                if total > 100:
                    flags.append(f"over_allocation: {total}%")
                    score += 0.3
                elif total > 80:
                    flags.append(f"high_allocation: {total}%")
                    score += 0.15
        
        return {"flags": flags, "score": score}

    def _calculate_confidence_risk(self, confidence: float) -> dict:
        """Calculate risk from confidence level."""
        flags = []
        score = 0.0
        
        if confidence < 0.5:
            flags.append(f"low_confidence: {confidence}")
            score = 0.3
        elif confidence < 0.7:
            flags.append(f"moderate_confidence: {confidence}")
            score = 0.1
        
        return {"flags": flags, "score": score}

    def set_threshold(self, threshold: float):
        """Update the risk threshold."""
        self._threshold = max(0.0, min(1.0, threshold))


# Global gate instance
_gate: Optional["RiskGate"] = None


def get_risk_gate() -> RiskGate:
    """Get the global risk gate instance."""
    global _gate
    if _gate is None:
        _gate = RiskGate()
    return _gate
