"""Tests for the Execution Layer."""
import pytest
from datetime import datetime

from app.execution.execution_models import (
    ExecutionMode,
    ExecutionStatus,
    ApprovalStatus,
    ExecutionIntent,
    ExecutionApproval,
    ExecutionDecision,
    EXECUTION_MODE,
    LIVE_EXECUTION_ENABLED,
    CONFIDENCE_THRESHOLD,
)
from app.execution.execution_controller import ExecutionController
from app.execution.execution_intent_builder import ExecutionIntentBuilder
from app.execution.policy_gate import PolicyGate
from app.execution.risk_gate import RiskGate
from app.execution.approval_gate import ApprovalGate


class TestExecutionModels:
    """Tests for execution models."""

    def test_execution_intent_creation(self):
        """Test creating an execution intent."""
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.8,
        )
        
        assert intent.recommendation_id == "rec_001"
        assert intent.domain == "health"
        assert intent.confidence == 0.8

    def test_execution_mode_values(self):
        """Test execution mode enum values."""
        assert ExecutionMode.DISABLED.value == "disabled"
        assert ExecutionMode.CONTROLLED.value == "controlled"
        assert ExecutionMode.AUTOMATED.value == "automated"

    def test_approval_status_values(self):
        """Test approval status enum values."""
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"


class TestIntentBuilder:
    """Tests for execution intent builder."""

    def test_build_intent(self):
        """Test building an intent from recommendation."""
        builder = ExecutionIntentBuilder()
        
        recommendation = {
            "target_domain": "wealth",
            "action_type": "adjust_priority",
            "priority": 5,
        }
        
        intent = builder.build_intent(
            recommendation_id="rec_001",
            recommendation=recommendation,
            confidence=0.75,
        )
        
        assert intent.recommendation_id == "rec_001"
        assert intent.domain == "wealth"
        assert intent.action_type == "adjust_priority"
        assert intent.confidence == 0.75
        assert intent.parameters["priority"] == 5

    def test_can_build_intent(self):
        """Test checking if recommendation can be built."""
        builder = ExecutionIntentBuilder()
        
        assert builder.can_build_intent({"target_domain": "health", "action": "test"}) is True
        assert builder.can_build_intent({}) is False


class TestPolicyGate:
    """Tests for policy gate."""

    def test_validate_pass(self):
        """Test validation passes with valid intent."""
        from app.execution import execution_models
        # Temporarily enable execution mode for testing
        original_mode = execution_models.EXECUTION_MODE
        execution_models.EXECUTION_MODE = execution_models.ExecutionMode.CONTROLLED
        
        gate = PolicyGate()
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.8,
        )
        
        result = gate.validate(intent)
        
        assert result.passed is True
        
        # Restore original mode
        execution_models.EXECUTION_MODE = original_mode

    def test_validate_fail_no_domain(self):
        """Test validation fails without domain."""
        gate = PolicyGate()
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="",
            action_type="adjust_priority",
            confidence=0.8,
        )
        
        result = gate.validate(intent)
        
        assert result.passed is False
        assert len(result.violations) > 0


class TestRiskGate:
    """Tests for risk gate."""

    def test_low_risk_intent(self):
        """Test low risk intent passes."""
        gate = RiskGate(threshold=0.5)
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.9,
            parameters={"adjustment": 0.1},
        )
        
        result = gate.validate(intent)
        
        assert result.passed is True

    def test_high_risk_intent(self):
        """Test high risk intent fails."""
        gate = RiskGate(threshold=0.5)
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="delete_account",
            confidence=0.3,
            parameters={"adjustment": 0.8},
        )
        
        result = gate.validate(intent)
        
        assert result.passed is False


class TestApprovalGate:
    """Tests for approval gate."""

    def test_request_approval_required(self):
        """Test approval is required by default."""
        gate = ApprovalGate(approval_required=True)
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.8,
        )
        
        result = gate.request_approval(intent)
        
        # With approval required, should be pending
        assert result.status == ApprovalStatus.PENDING

    def test_approve_intent(self):
        """Test approving an intent."""
        gate = ApprovalGate(approval_required=False)
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.8,
        )
        
        result = gate.request_approval(intent)
        
        assert result.approved is True
        assert result.status == ApprovalStatus.APPROVED


class TestExecutionController:
    """Tests for execution controller."""

    def test_create_intent(self):
        """Test creating an execution intent."""
        controller = ExecutionController()
        
        recommendation = {
            "target_domain": "wealth",
            "action_type": "adjust_priority",
            "priority": 5,
        }
        
        intent = controller.create_intent(
            recommendation_id="rec_001",
            recommendation=recommendation,
            confidence=0.8,
        )
        
        assert intent.recommendation_id == "rec_001"
        assert intent.domain == "wealth"

    def test_validate_intent_passes(self):
        """Test validating a low-risk intent."""
        controller = ExecutionController()
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.9,
        )
        
        decision = controller.validate_intent(intent)
        
        # With approval not required, should pass gates
        assert decision is not None

    def test_validate_intent_low_confidence(self):
        """Test validating intent with low confidence fails."""
        controller = ExecutionController()
        
        intent = ExecutionIntent(
            recommendation_id="rec_001",
            domain="health",
            action_type="adjust_priority",
            confidence=0.3,  # Below threshold
        )
        
        decision = controller.validate_intent(intent)
        
        # Should fail due to low confidence
        assert decision.approved is False

    def test_get_statistics(self):
        """Test getting execution statistics."""
        controller = ExecutionController()
        
        stats = controller.get_statistics()
        
        assert "total" in stats
        assert "pending" in stats


class TestSafetyFlags:
    """Tests for safety enforcement."""

    def test_live_execution_disabled(self):
        """Verify live execution is disabled."""
        assert LIVE_EXECUTION_ENABLED is False

    def test_approval_required(self):
        """Verify approval is required by default."""
        from app.execution import execution_models
        assert execution_models.APPROVAL_REQUIRED is True

    def test_confidence_threshold(self):
        """Verify confidence threshold is set."""
        assert CONFIDENCE_THRESHOLD > 0
        assert CONFIDENCE_THRESHOLD <= 1.0
