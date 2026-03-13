"""Tests for the Doctrine Layer."""
import pytest
from datetime import datetime

from app.doctrine.doctrine_models import (
    AlignmentLevel,
    AlignmentScore,
    PolicyRuleType,
    PolicyRule,
    DecisionContext,
    DoctrineAssessment,
    LIVE_EXECUTION_ENABLED,
    DOCTRINE_VERSION,
)
from app.doctrine.doctrine_controller import DoctrineController
from app.doctrine.doctrine_evaluator import DoctrineEvaluator
from app.doctrine.doctrine_registry import DoctrineRegistry
from app.doctrine.doctrine_rules import (
    RiskManagementRule,
    CapitalAllocationRule,
    SignalReliabilityRule,
    create_default_rules,
)
from app.doctrine.doctrine_explanations import DoctrineExplainer


class TestDoctrineModels:
    """Tests for doctrine models."""

    def test_decision_context_creation(self):
        """Test creating a decision context."""
        context = DecisionContext(
            cycle_id="test_001",
            timestamp=datetime.utcnow(),
        )
        
        assert context.cycle_id == "test_001"
        assert context.signals == []

    def test_alignment_level_values(self):
        """Test alignment level enum values."""
        assert AlignmentLevel.ALIGNED.value == "aligned"
        assert AlignmentLevel.MISALIGNED.value == "misaligned"
        assert AlignmentLevel.REQUIRES_REVIEW.value == "requires_review"


class TestDoctrineRegistry:
    """Tests for doctrine registry."""

    def test_registry_initialization(self):
        """Test registry initializes with default rules."""
        registry = DoctrineRegistry()
        
        stats = registry.get_statistics()
        assert stats["total_rules"] >= 6

    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        registry = DoctrineRegistry()
        
        # Get a rule
        rule = registry.get_all_rules()[0]
        original_enabled = rule.is_enabled()
        
        # Disable
        result = registry.disable_rule(rule.rule_id)
        assert result is True
        assert rule.is_enabled() is False
        
        # Re-enable
        result = registry.enable_rule(rule.rule_id)
        assert result is True
        assert rule.is_enabled() is True


class TestDoctrineRules:
    """Tests for doctrine rules."""

    def test_risk_management_rule(self):
        """Test risk management rule evaluation."""
        rule = RiskManagementRule(PolicyRule(
            rule_id="test_001",
            rule_type=PolicyRuleType.RISK_MANAGEMENT,
            name="Test Risk",
            description="Test",
            weight=1.0,
            threshold=0.5,
            priority=1,
        ))
        
        # High risk context
        context = DecisionContext(
            cycle_id="test",
            timestamp=datetime.utcnow(),
            optimization_output={"risk_score": 0.8},
            candidate_recommendations=[
                {"risk_factors": ["factor1"]},
                {"risk_factors": ["factor2"]},
            ],
        )
        
        result = rule.evaluate(context)
        
        assert result["level"] == AlignmentLevel.REQUIRES_REVIEW
        assert result["score"] < 0

    def test_capital_allocation_rule(self):
        """Test capital allocation rule."""
        rule = CapitalAllocationRule(PolicyRule(
            rule_id="test_002",
            rule_type=PolicyRuleType.CAPITAL_ALLOCATION,
            name="Test Capital",
            description="Test",
            weight=1.0,
            threshold=0.4,
            priority=1,
        ))
        
        # Over-allocated context
        context = DecisionContext(
            cycle_id="test",
            timestamp=datetime.utcnow(),
            optimization_output={
                "resource_allocation": {
                    "wealth": 50,
                    "health": 60,
                }
            },
        )
        
        result = rule.evaluate(context)
        
        # Should flag violation
        assert "violations" in result["factors"]

    def test_signal_reliability_rule(self):
        """Test signal reliability rule."""
        rule = SignalReliabilityRule(PolicyRule(
            rule_id="test_003",
            rule_type=PolicyRuleType.SIGNAL_RELIABILITY,
            name="Test Signal",
            description="Test",
            weight=1.0,
            threshold=0.3,
            priority=1,
        ))
        
        # Good signals context
        context = DecisionContext(
            cycle_id="test",
            timestamp=datetime.utcnow(),
            signals=[
                {"signal_id": "sig1", "confidence_score": 0.8, "freshness_score": 0.9},
                {"signal_id": "sig2", "confidence_score": 0.7, "freshness_score": 0.8},
            ],
        )
        
        result = rule.evaluate(context)
        
        assert result["level"] == AlignmentLevel.ALIGNED
        assert result["score"] > 0

    def test_create_default_rules(self):
        """Test creating default rules."""
        rules = create_default_rules()
        
        assert len(rules) >= 6
        
        rule_types = {r.rule_type for r in rules}
        assert PolicyRuleType.RISK_MANAGEMENT in rule_types
        assert PolicyRuleType.CAPITAL_ALLOCATION in rule_types


class TestDoctrineEvaluator:
    """Tests for doctrine evaluator."""

    def test_evaluator_with_empty_context(self):
        """Test evaluation with empty context."""
        evaluator = DoctrineEvaluator()
        
        context = DecisionContext(
            cycle_id="test_empty",
            timestamp=datetime.utcnow(),
        )
        
        assessment = evaluator.evaluate(context)
        
        assert assessment is not None
        assert assessment.cycle_id == "test_empty"

    def test_evaluator_with_signals(self):
        """Test evaluation with signals."""
        evaluator = DoctrineEvaluator()
        
        context = DecisionContext(
            cycle_id="test_signals",
            timestamp=datetime.utcnow(),
            signals=[
                {"signal_id": "sig1", "confidence_score": 0.8, "freshness_score": 0.9},
            ],
            optimization_output={"risk_score": 0.3},
            candidate_recommendations=[],
        )
        
        assessment = evaluator.evaluate(context)
        
        assert assessment.alignment_score is not None

    def test_evaluator_safety(self):
        """Test evaluator safety check."""
        evaluator = DoctrineEvaluator()
        
        # With LIVE_EXECUTION_ENABLED, should return neutral
        # (but our tests run with it disabled)
        context = DecisionContext(
            cycle_id="test_safety",
            timestamp=datetime.utcnow(),
        )
        
        assessment = evaluator.evaluate(context)
        
        assert assessment.doctrine_version == DOCTRINE_VERSION


class TestDoctrineController:
    """Tests for doctrine controller."""

    def test_evaluate_alignment(self):
        """Test full alignment evaluation."""
        controller = DoctrineController()
        
        assessment = controller.evaluate_alignment(
            cycle_id="test_eval_001",
            signals=[
                {"signal_id": "sig1", "confidence_score": 0.8, "freshness_score": 0.9},
            ],
            optimization_output={"risk_score": 0.3},
            candidate_recommendations=[
                {"target_domain": "health", "priority": 1},
            ],
            journal_history=[],  # Must be list
        )
        
        assert assessment.cycle_id == "test_eval_001"
        assert assessment.doctrine_version == DOCTRINE_VERSION
        # Rules may or may not apply depending on context
        assert assessment.alignment_score is not None

    def test_get_explanation(self):
        """Test getting explanation."""
        controller = DoctrineController()
        
        assessment = controller.evaluate_alignment(
            cycle_id="test_explain",
            journal_history=[],  # Must be list
        )
        
        explanation = controller.get_explanation(assessment)
        
        assert "alignment" in explanation
        assert "rules_applied" in explanation


class TestDoctrineExplainer:
    """Tests for doctrine explainer."""

    def test_generate_audit_report(self):
        """Test audit report generation."""
        explainer = DoctrineExplainer()
        
        # Create a test assessment
        assessment = DoctrineAssessment(
            cycle_id="test_audit",
            timestamp=datetime.utcnow(),
            alignment_score=AlignmentScore(
                level=AlignmentLevel.ALIGNED,
                score=0.5,
                confidence=0.8,
            ),
            policy_rules_applied=["rule1", "rule2"],
            confidence_score=0.8,
            evaluation_summary="Test evaluation",
        )
        
        report = explainer.generate_audit_report(assessment)
        
        assert "DOCTRINE EVALUATION AUDIT REPORT" in report
        assert "test_audit" in report


class TestSafetyFlags:
    """Tests for safety enforcement."""

    def test_live_execution_disabled(self):
        """Verify live execution is disabled."""
        assert LIVE_EXECUTION_ENABLED is False

    def test_doctrine_version(self):
        """Verify doctrine version is set."""
        assert DOCTRINE_VERSION is not None
        assert DOCTRINE_VERSION.startswith("1.")
