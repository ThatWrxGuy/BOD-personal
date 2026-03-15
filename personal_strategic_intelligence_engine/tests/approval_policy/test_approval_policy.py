"""Tests for the Approval Policy Layer."""
import pytest

from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    EligibilityStatus,
    PolicyTransitionType,
)
from app.approval_policy.approval_policy_controller import ApprovalPolicyController
from app.approval_policy.approval_tier_classifier import ApprovalTierClassifier
from app.approval_policy.policy_thresholds import PolicyThresholds
from app.approval_policy.auto_execution_guard import AutoExecutionGuard
from app.approval_policy.tier_registry import TierRegistry
from app.approval_policy.policy_transition_analyzer import PolicyTransitionAnalyzer


class TestApprovalTierLevels:
    """Tests for approval tier levels."""

    def test_tier_values(self):
        """Test tier level enum values."""
        assert ApprovalTierLevel.TIER_0_MANUAL_ONLY.value == "tier_0_manual_only"
        assert ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH.value == "tier_1_manual_fast_path"
        assert ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO.value == "tier_2_conditional_auto"
        assert ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO.value == "tier_3_system_safe_auto"


class TestPolicyThresholds:
    """Tests for policy thresholds."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        thresholds = PolicyThresholds()
        
        assert thresholds.min_execution_samples == 10
        assert thresholds.min_success_rate == 0.90
        assert thresholds.min_confidence == 0.85
        assert thresholds.max_risk_score == 0.30

    def test_custom_thresholds(self):
        """Test custom threshold values."""
        thresholds = PolicyThresholds(custom_thresholds={"min_execution_samples": 5})
        
        assert thresholds.min_execution_samples == 5

    def test_meets_auto_eligibility(self):
        """Test auto eligibility check."""
        thresholds = PolicyThresholds()
        
        meets, blockers = thresholds.meets_auto_eligibility(
            execution_count=15,
            success_rate=0.95,
            confidence=0.90,
            risk_score=0.20,
        )
        
        assert meets is True
        assert len(blockers) == 0


class TestApprovalTierClassifier:
    """Tests for approval tier classifier."""

    def test_classify_adjust_priority(self):
        """Test classifying adjust_priority action."""
        classifier = ApprovalTierClassifier()
        
        eligibility = classifier.classify(
            action_type="adjust_priority",
            domain="health",
        )
        
        assert eligibility.current_tier == ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH

    def test_classify_generate_insight(self):
        """Test classifying generate_insight action."""
        classifier = ApprovalTierClassifier()
        
        eligibility = classifier.classify(
            action_type="generate_insight",
            domain="health",
        )
        
        assert eligibility.current_tier == ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO

    def test_classify_allocate_resource(self):
        """Test classifying allocate_resource action."""
        classifier = ApprovalTierClassifier()
        
        eligibility = classifier.classify(
            action_type="allocate_resource",
            domain="health",
        )
        
        assert eligibility.current_tier == ApprovalTierLevel.TIER_0_MANUAL_ONLY


class TestAutoExecutionGuard:
    """Tests for auto-execution guard."""

    def test_guard_blocks_when_disabled(self):
        """Test guard blocks when auto-execution is disabled."""
        guard = AutoExecutionGuard()
        
        eligibility = guard.check_eligibility(
            action_type="adjust_priority",
            domain="health",
            execution_count=20,
            success_rate=0.95,
            confidence=0.90,
            risk_score=0.10,
            doctrine_aligned=True,
        )
        
        # Should be blocked because AUTO_EXECUTION_ENABLED = False
        assert eligibility.allowed is False

    def test_guard_requires_reversibility(self):
        """Test guard requires reversible actions."""
        guard = AutoExecutionGuard()
        
        # With auto-execution enabled, check reversibility
        # This tests the logic path
        from app.approval_policy import approval_policy_models
        original = approval_policy_models.AUTO_EXECUTION_ENABLED
        approval_policy_models.AUTO_EXECUTION_ENABLED = True
        
        try:
            eligibility = guard.check_eligibility(
                action_type="allocate_resource",  # Not fully reversible
                domain="health",
                execution_count=20,
                success_rate=0.95,
                confidence=0.90,
                risk_score=0.10,
                doctrine_aligned=True,
            )
            
            # Should fail due to reversibility
            assert eligibility.allowed is False
        finally:
            approval_policy_models.AUTO_EXECUTION_ENABLED = original


class TestTierRegistry:
    """Tests for tier registry."""

    def test_register_tier(self):
        """Test registering a tier."""
        registry = TierRegistry()
        
        rule = registry.register(
            action_type="test_action",
            domain="health",
            tier=ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
            justification="Test justification",
        )
        
        assert rule.action_type == "test_action"
        assert rule.tier == ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH

    def test_get_tier(self):
        """Test getting a tier."""
        registry = TierRegistry()
        
        registry.register(
            action_type="test_action",
            domain="health",
            tier=ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO,
        )
        
        rule = registry.get("test_action", "health")
        
        assert rule is not None
        assert rule.tier == ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO


class TestPolicyTransitionAnalyzer:
    """Tests for policy transition analyzer."""

    def test_analyze_no_change(self):
        """Test analyzing with no change needed."""
        analyzer = PolicyTransitionAnalyzer()
        
        event = analyzer.analyze(
            action_type="adjust_priority",
            domain="health",
            current_tier=ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
            execution_count=5,
            success_rate=0.60,
        )
        
        # Should not upgrade due to low success rate
        assert event.transition_type in [PolicyTransitionType.NO_CHANGE, PolicyTransitionType.DOWNGRADE]

    def test_analyze_upgrade_candidate(self):
        """Test analyzing with upgrade potential."""
        analyzer = PolicyTransitionAnalyzer()
        
        event = analyzer.analyze(
            action_type="adjust_priority",
            domain="health",
            current_tier=ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
            execution_count=15,
            success_rate=0.95,
        )
        
        # Should recommend upgrade
        assert event.to_tier in [
            ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO,
            ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO,
        ]


class TestApprovalPolicyController:
    """Tests for approval policy controller."""

    def test_classify_tier(self):
        """Test tier classification."""
        controller = ApprovalPolicyController()
        
        eligibility = controller.classify_tier(
            action_type="adjust_priority",
            domain="health",
        )
        
        assert eligibility.current_tier is not None

    def test_check_auto_execution(self):
        """Test auto-execution check."""
        controller = ApprovalPolicyController()
        
        eligibility = controller.check_auto_execution(
            action_type="adjust_priority",
            domain="health",
            execution_count=20,
            success_rate=0.95,
            confidence=0.90,
            risk_score=0.10,
        )
        
        # Should be blocked due to AUTO_EXECUTION_ENABLED = False
        assert eligibility.allowed is False

    def test_get_statistics(self):
        """Test getting statistics."""
        controller = ApprovalPolicyController()
        
        stats = controller.get_statistics()
        
        assert "auto_execution_enabled" in stats
        assert stats["auto_execution_enabled"] is False


class TestSafetyEnforcement:
    """Tests for safety enforcement."""

    def test_auto_execution_disabled(self):
        """Verify auto-execution is disabled."""
        from app.approval_policy import approval_policy_models
        assert approval_policy_models.AUTO_EXECUTION_ENABLED is False
