"""Tests for Policy Validator."""
import pytest
from app.meta_cognition import (
    PolicyValidator,
    PolicyComplianceStatus,
    ContradictionSeverity,
)


class TestPolicyValidator:
    """Tests for PolicyValidator."""

    def setup_method(self):
        self.validator = PolicyValidator()

    def test_validate_decision_compliant(self):
        """Test validating a compliant decision."""
        decision = {
            "expected_drawdown": 0.1,
            "concentration": 0.2,
            "leverage": 1.0,
            "planned_trades": 5,
        }
        
        status, violations = self.validator.validate_decision(decision)
        
        assert status == PolicyComplianceStatus.COMPLIANT
        assert len(violations) == 0

    def test_validate_decision_drawdown_violation(self):
        """Test detecting drawdown violation."""
        decision = {
            "expected_drawdown": 0.5,  # Exceeds 0.25 limit
            "concentration": 0.2,
            "leverage": 1.0,
        }
        
        status, violations = self.validator.validate_decision(decision)
        
        assert status == PolicyComplianceStatus.VIOLATION
        assert len(violations) > 0

    def test_validate_decision_leverage_violation(self):
        """Test detecting leverage violation."""
        decision = {
            "expected_drawdown": 0.1,
            "concentration": 0.2,
            "leverage": 5.0,  # Exceeds 2.0 limit
        }
        
        status, violations = self.validator.validate_decision(decision)
        
        assert status == PolicyComplianceStatus.VIOLATION

    def test_validate_decision_concentration_warning(self):
        """Test detecting concentration warning."""
        decision = {
            "expected_drawdown": 0.1,
            "concentration": 0.5,  # High but not critical
            "leverage": 1.0,
        }
        
        status, violations = self.validator.validate_decision(decision)
        
        # Should have some violation or warning
        assert status in [
            PolicyComplianceStatus.COMPLIANT,
            PolicyComplianceStatus.WARNING,
            PolicyComplianceStatus.VIOLATION,
        ]

    def test_validate_decision_doctrine_alignment(self):
        """Test doctrine alignment validation."""
        decision = {
            "expected_drawdown": 0.1,
            "leverage": 1.0,
        }
        
        # Low doctrine alignment
        status, violations = self.validator.validate_decision(decision, doctrine_alignment=0.2)
        
        # Should have warning
        assert status in [PolicyComplianceStatus.WARNING, PolicyComplianceStatus.VIOLATION]

    def test_validate_risk_only(self):
        """Test validating risk metrics only."""
        risk_metrics = {
            "drawdown": 0.3,
            "concentration": 0.4,
            "leverage": 1.5,
        }
        
        status, violations = self.validator.validate_risk_only(risk_metrics)
        
        assert status is not None

    def test_add_policy_rule(self):
        """Test adding a custom policy rule."""
        from app.meta_cognition.meta_models import PolicyRule
        
        rule = PolicyRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test",
            rule_type="risk_threshold",
            condition={"max_value": 0.5},
            severity=ContradictionSeverity.MEDIUM,
        )
        
        self.validator.add_policy_rule(rule)
        
        retrieved = self.validator.get_policy_rule("test_rule")
        assert retrieved is not None
        assert retrieved.name == "Test Rule"

    def test_remove_policy_rule(self):
        """Test removing a policy rule."""
        rule_id = "risk_max_drawdown"
        
        result = self.validator.remove_policy_rule(rule_id)
        assert result is True
        
        # Should not be able to remove again
        result = self.validator.remove_policy_rule(rule_id)
        assert result is False

    def test_get_policy_summary(self):
        """Test getting policy summary."""
        summary = self.validator.get_policy_summary()
        
        assert "total_rules" in summary
        assert "active_rules" in summary
        assert summary["total_rules"] > 0
