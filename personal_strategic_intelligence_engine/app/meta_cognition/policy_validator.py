"""Policy validation engine."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.meta_cognition.meta_types import (
    PolicyComplianceStatus,
    ContradictionSeverity,
)
from app.meta_cognition.meta_models import PolicyRule


class PolicyValidator:
    """Validates strategic decisions against policies and doctrine.
    
    Checks include:
    - risk threshold violations
    - doctrine contradictions
    - prohibited strategy patterns
    """
    
    def __init__(self):
        self._policy_rules: Dict[str, PolicyRule] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default policy rules."""
        
        # Risk threshold policies
        self.add_policy_rule(PolicyRule(
            rule_id="risk_max_drawdown",
            name="Maximum Drawdown Limit",
            description="Do not exceed maximum drawdown threshold",
            rule_type="risk_threshold",
            condition={"max_drawdown": 0.25},
            severity=ContradictionSeverity.CRITICAL,
        ))
        
        self.add_policy_rule(PolicyRule(
            rule_id="risk_concentration",
            name="Risk Concentration Limit",
            description="Avoid excessive concentration in single asset/domain",
            rule_type="risk_threshold",
            condition={"max_concentration": 0.40},
            severity=ContradictionSeverity.HIGH,
        ))
        
        # Doctrine contradiction policies
        self.add_policy_rule(PolicyRule(
            rule_id="doctrine_alignment",
            name="Doctrine Alignment",
            description="Decisions should align with established doctrine",
            rule_type="doctrine_contradiction",
            condition={"min_doctrine_alignment": 0.5},
            severity=ContradictionSeverity.MEDIUM,
        ))
        
        # Prohibited patterns
        self.add_policy_rule(PolicyRule(
            rule_id="prohibited_overtrading",
            name="Overtrading Prohibition",
            description="Avoid excessive trading activity",
            rule_type="prohibited_pattern",
            condition={"max_trades_per_cycle": 10},
            severity=ContradictionSeverity.MEDIUM,
        ))
        
        self.add_policy_rule(PolicyRule(
            rule_id="prohibited_leverage",
            name="Leverage Limit",
            description="Avoid excessive leverage",
            rule_type="prohibited_pattern",
            condition={"max_leverage": 2.0},
            severity=ContradictionSeverity.CRITICAL,
        ))
    
    def add_policy_rule(self, rule: PolicyRule):
        """Add a policy rule."""
        self._policy_rules[rule.rule_id] = rule
    
    def remove_policy_rule(self, rule_id: str) -> bool:
        """Remove a policy rule."""
        if rule_id in self._policy_rules:
            del self._policy_rules[rule_id]
            return True
        return False
    
    def get_policy_rule(self, rule_id: str) -> Optional[PolicyRule]:
        """Get a policy rule."""
        return self._policy_rules.get(rule_id)
    
    def get_all_rules(self) -> List[PolicyRule]:
        """Get all policy rules."""
        return list(self._policy_rules.values())
    
    def validate_decision(
        self,
        decision: Dict[str, Any],
        doctrine_alignment: float = 0.5,
    ) -> tuple[PolicyComplianceStatus, List[Dict[str, Any]]]:
        """Validate a decision against all policies.
        
        Args:
            decision: The decision to validate
            doctrine_alignment: Alignment with doctrine (0-1)
            
        Returns:
            Tuple of (compliance_status, violations)
        """
        violations = []
        
        # Check each policy rule
        for rule in self._policy_rules.values():
            if not rule.is_active:
                continue
            
            violation = self._check_rule(rule, decision, doctrine_alignment)
            if violation:
                violations.append(violation)
        
        # Determine overall status
        if not violations:
            status = PolicyComplianceStatus.COMPLIANT
        elif any(v.get("severity") == "critical" for v in violations):
            status = PolicyComplianceStatus.VIOLATION
        elif any(v.get("severity") in ["high", "critical"] for v in violations):
            status = PolicyComplianceStatus.VIOLATION
        elif violations:
            status = PolicyComplianceStatus.WARNING
        else:
            status = PolicyComplianceStatus.COMPLIANT
        
        return status, violations
    
    def _check_rule(
        self,
        rule: PolicyRule,
        decision: Dict[str, Any],
        doctrine_alignment: float,
    ) -> Optional[Dict[str, Any]]:
        """Check a single policy rule."""
        
        if rule.rule_type == "risk_threshold":
            return self._check_risk_threshold(rule, decision)
        elif rule.rule_type == "doctrine_contradiction":
            return self._check_doctrine_contradiction(rule, doctrine_alignment)
        elif rule.rule_type == "prohibited_pattern":
            return self._check_prohibited_pattern(rule, decision)
        
        return None
    
    def _check_risk_threshold(
        self,
        rule: PolicyRule,
        decision: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Check risk threshold violations."""
        
        condition = rule.condition
        
        # Check max drawdown
        if "max_drawdown" in condition:
            current_drawdown = decision.get("expected_drawdown", 0.0)
            if current_drawdown > condition["max_drawdown"]:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "severity": rule.severity.value,
                    "message": f"Expected drawdown {current_drawdown:.1%} exceeds limit {condition['max_drawdown']:.1%}",
                    "current_value": current_drawdown,
                    "threshold": condition["max_drawdown"],
                }
        
        # Check concentration
        if "max_concentration" in condition:
            concentration = decision.get("concentration", 0.0)
            if concentration > condition["max_concentration"]:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "severity": rule.severity.value,
                    "message": f"Concentration {concentration:.1%} exceeds limit {condition['max_concentration']:.1%}",
                    "current_value": concentration,
                    "threshold": condition["max_concentration"],
                }
        
        return None
    
    def _check_doctrine_contradiction(
        self,
        rule: PolicyRule,
        doctrine_alignment: float,
    ) -> Optional[Dict[str, Any]]:
        """Check doctrine alignment violations."""
        
        min_alignment = rule.condition.get("min_doctrine_alignment", 0.5)
        
        if doctrine_alignment < min_alignment:
            return {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "severity": rule.severity.value,
                "message": f"Doctrine alignment {doctrine_alignment:.1%} below minimum {min_alignment:.1%}",
                "current_value": doctrine_alignment,
                "minimum": min_alignment,
            }
        
        return None
    
    def _check_prohibited_pattern(
        self,
        rule: PolicyRule,
        decision: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Check prohibited pattern violations."""
        
        condition = rule.condition
        
        # Check trading frequency
        if "max_trades_per_cycle" in condition:
            trades = decision.get("planned_trades", 0)
            if trades > condition["max_trades_per_cycle"]:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "severity": rule.severity.value,
                    "message": f"Planned trades {trades} exceeds limit {condition['max_trades_per_cycle']}",
                    "current_value": trades,
                    "limit": condition["max_trades_per_cycle"],
                }
        
        # Check leverage
        if "max_leverage" in condition:
            leverage = decision.get("leverage", 1.0)
            if leverage > condition["max_leverage"]:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "severity": rule.severity.value,
                    "message": f"Leverage {leverage:.1f}x exceeds limit {condition['max_leverage']:.1f}x",
                    "current_value": leverage,
                    "limit": condition["max_leverage"],
                }
        
        return None
    
    def validate_risk_only(
        self,
        risk_metrics: Dict[str, Any],
    ) -> tuple[PolicyComplianceStatus, List[Dict[str, Any]]]:
        """Validate risk metrics only.
        
        Args:
            risk_metrics: Dictionary of risk metrics
            
        Returns:
            Tuple of (compliance_status, violations)
        """
        # Create a synthetic decision from risk metrics
        decision = {
            "expected_drawdown": risk_metrics.get("drawdown", 0.0),
            "concentration": risk_metrics.get("concentration", 0.0),
            "leverage": risk_metrics.get("leverage", 1.0),
        }
        
        return self.validate_decision(decision, doctrine_alignment=0.5)
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of all policies."""
        return {
            "total_rules": len(self._policy_rules),
            "active_rules": sum(1 for r in self._policy_rules.values() if r.is_active),
            "rules_by_type": self._count_rules_by_type(),
            "rules_by_severity": self._count_rules_by_severity(),
        }
    
    def _count_rules_by_type(self) -> Dict[str, int]:
        """Count rules by type."""
        counts = {}
        for rule in self._policy_rules.values():
            counts[rule.rule_type] = counts.get(rule.rule_type, 0) + 1
        return counts
    
    def _count_rules_by_severity(self) -> Dict[str, int]:
        """Count rules by severity."""
        counts = {}
        for rule in self._policy_rules.values():
            counts[rule.severity.value] = counts.get(rule.severity.value, 0) + 1
        return counts
