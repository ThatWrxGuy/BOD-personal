"""Constraint Engine.

Prevents invalid or dangerous variants.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from app.intelligence.autonomous_strategy_lab.lab_models import StrategyVariant


@dataclass
class ConstraintViolation:
    """Constraint violation details."""
    rule: str
    severity: str
    message: str


class ConstraintEngine:
    """Validates variants against constraints."""
    
    def __init__(self):
        self.violations = []
    
    def validate_variant(self, variant: StrategyVariant) -> List[ConstraintViolation]:
        """Validate a variant against all constraints."""
        
        violations = []
        
        # Check for required parameters
        if not variant.parameters:
            violations.append(ConstraintViolation(
                rule="required_parameters",
                severity="critical",
                message="Variant has no parameters",
            ))
        
        # Check for invalid parameter combinations
        violations.extend(self._check_parameter_combinations(variant))
        
        # Check for unsupported signals
        violations.extend(self._check_signal_dependencies(variant))
        
        # Check for risk profile
        violations.extend(self._check_risk_profile(variant))
        
        # Store violations
        self.violations.extend(violations)
        
        return violations
    
    def _check_parameter_combinations(self, variant: StrategyVariant) -> List[ConstraintViolation]:
        """Check for invalid parameter combinations."""
        
        violations = []
        params = variant.parameters
        
        # Check hold time vs confirmation
        if "hold_time_minutes" in params and "confirmation_bars" in params:
            if params["hold_time_minutes"] < params["confirmation_bars"]:
                violations.append(ConstraintViolation(
                    rule="parameter_timing",
                    severity="high",
                    message="Hold time should exceed confirmation bars duration",
                ))
        
        # Check delta target range
        if "delta_target" in params:
            delta = params["delta_target"]
            if delta < 0.1 or delta > 0.6:
                violations.append(ConstraintViolation(
                    rule="delta_range",
                    severity="medium",
                    message=f"Delta target {delta} outside recommended range",
                ))
        
        return violations
    
    def _check_signal_dependencies(self, variant: StrategyVariant) -> List[ConstraintViolation]:
        """Check signal dependencies."""
        
        violations = []
        
        # This would check against available signals
        # For now, just a placeholder
        
        return violations
    
    def _check_risk_profile(self, variant: StrategyVariant) -> List[ConstraintViolation]:
        """Check risk profile constraints."""
        
        violations = []
        
        # High risk strategies need more validation
        if "risk_profile" in variant.parameters:
            if variant.parameters["risk_profile"] == "extreme":
                violations.append(ConstraintViolation(
                    rule="extreme_risk",
                    severity="critical",
                    message="Extreme risk profiles require governance approval",
                ))
        
        return violations
    
    def is_valid(self, variant: StrategyVariant) -> bool:
        """Check if variant is valid."""
        
        violations = self.validate_variant(variant)
        
        # Critical violations make invalid
        critical = [v for v in violations if v.severity == "critical"]
        
        return len(critical) == 0
    
    def get_violations_summary(self) -> Dict:
        """Get summary of violations."""
        
        return {
            "total_violations": len(self.violations),
            "by_severity": {
                "critical": len([v for v in self.violations if v.severity == "critical"]),
                "high": len([v for v in self.violations if v.severity == "high"]),
                "medium": len([v for v in self.violations if v.severity == "medium"]),
            },
        }


def create_engine() -> ConstraintEngine:
    """Create constraint engine."""
    return ConstraintEngine()
