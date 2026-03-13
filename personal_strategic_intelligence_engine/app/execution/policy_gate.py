"""Policy gate - validates execution against system policies."""
import logging
from typing import List

from app.execution.execution_models import (
    ExecutionIntent,
    PolicyGateResult,
)

logger = logging.getLogger(__name__)


class PolicyGate:
    """Validates execution against system policies."""

    def __init__(self):
        # Policy rules that must be satisfied
        self._policy_rules = [
            "execution_mode_check",
            "intent_validation",
            "parameter_safety",
        ]

    def validate(self, intent: ExecutionIntent) -> PolicyGateResult:
        """
        Validate execution intent against policy rules.
        
        Args:
            intent: The execution intent to validate
            
        Returns:
            PolicyGateResult with pass/fail status
        """
        violations = []
        rules_checked = []
        
        # Check 1: Execution mode must be enabled
        from app.execution.execution_models import EXECUTION_MODE
        if EXECUTION_MODE.value == "disabled":
            violations.append("Execution mode is disabled")
        else:
            rules_checked.append("execution_mode_check")
        
        # Check 2: Intent must have valid domain
        if not intent.domain or intent.domain == "unknown":
            violations.append("Invalid or missing domain")
        else:
            rules_checked.append("intent_validation")
        
        # Check 3: Parameters must be safe
        param_violations = self._check_parameter_safety(intent)
        if param_violations:
            violations.extend(param_violations)
        else:
            rules_checked.append("parameter_safety")
        
        # Determine pass/fail
        passed = len(violations) == 0
        
        result = PolicyGateResult(
            passed=passed,
            policy_rules_checked=rules_checked,
            violations=violations,
        )
        
        if not passed:
            logger.warning(f"Policy gate rejected intent {intent.intent_id}: {violations}")
        
        return result

    def _check_parameter_safety(self, intent: ExecutionIntent) -> List[str]:
        """Check if parameters are safe for execution."""
        violations = []
        
        # Check for dangerous parameter values
        dangerous_keys = {"password", "secret", "token", "api_key", "credential"}
        
        for key in intent.parameters:
            if any(dangerous in key.lower() for dangerous in dangerous_keys):
                violations.append(f"Parameter '{key}' contains sensitive data")
        
        # Check for excessively large parameter values
        for key, value in intent.parameters.items():
            if isinstance(value, str) and len(value) > 10000:
                violations.append(f"Parameter '{key}' exceeds maximum length")
            if isinstance(value, (list, dict)) and len(str(value)) > 50000:
                violations.append(f"Parameter '{key}' is excessively large")
        
        return violations


# Global gate instance
_gate: "PolicyGate" = None


def get_policy_gate() -> PolicyGate:
    """Get the global policy gate instance."""
    global _gate
    if _gate is None:
        _gate = PolicyGate()
    return _gate
