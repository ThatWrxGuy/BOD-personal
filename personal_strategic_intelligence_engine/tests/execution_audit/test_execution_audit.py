"""Tests for the Execution Audit Layer."""
import pytest
from datetime import datetime

from app.execution_audit.outcome_models import (
    OutcomeCategory,
    ReversibilityLevel,
    ApprovalPolicyLevel,
    ExecutionOutcomeSnapshot,
    ExecutionReliabilityScore,
)
from app.execution_audit.execution_audit_controller import ExecutionAuditController
from app.execution_audit.outcome_tracker import OutcomeTracker
from app.execution_audit.outcome_evaluator import OutcomeEvaluator
from app.execution_audit.reversibility_classifier import ReversibilityClassifier
from app.execution_audit.execution_reliability_analyzer import ExecutionReliabilityAnalyzer
from app.execution_audit.approval_policy_advisor import ApprovalPolicyAdvisor


class TestOutcomeModels:
    """Tests for outcome models."""

    def test_outcome_category_values(self):
        """Test outcome category enum values."""
        assert OutcomeCategory.IMPROVEMENT.value == "improvement"
        assert OutcomeCategory.NO_CHANGE.value == "no_change"
        assert OutcomeCategory.DETERIORATION.value == "deterioration"
        assert OutcomeCategory.MIXED.value == "mixed"

    def test_reversibility_level_values(self):
        """Test reversibility level enum values."""
        assert ReversibilityLevel.FULLY_REVERSIBLE.value == "fully_reversible"
        assert ReversibilityLevel.PARTIALLY_REVERSIBLE.value == "partially_reversible"
        assert ReversibilityLevel.IRREVERSIBLE.value == "irreversible"

    def test_approval_policy_level_values(self):
        """Test approval policy level enum values."""
        assert ApprovalPolicyLevel.MANUAL_ONLY.value == "manual_only"
        assert ApprovalPolicyLevel.ELIGIBLE_FOR_AUTO.value == "eligible_for_auto"


class TestOutcomeTracker:
    """Tests for outcome tracker."""

    def test_capture_outcome(self):
        """Test capturing an outcome."""
        tracker = OutcomeTracker()
        
        snapshot = tracker.capture_outcome(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
            pre_execution_state={"priority": 3},
            post_execution_state={"priority": 5},
        )
        
        assert snapshot.execution_id == "exec_001"
        assert snapshot.action_type == "adjust_priority"
        assert snapshot.pre_execution_state["priority"] == 3

    def test_get_snapshot(self):
        """Test getting a snapshot."""
        tracker = OutcomeTracker()
        
        snapshot = tracker.capture_outcome(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
        )
        
        retrieved = tracker.get_snapshot(snapshot.snapshot_id)
        assert retrieved is not None
        assert retrieved.execution_id == "exec_001"

    def test_get_statistics(self):
        """Test getting tracker statistics."""
        tracker = OutcomeTracker()
        
        tracker.capture_outcome(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
        )
        
        stats = tracker.get_statistics()
        assert stats["total_snapshots"] == 1


class TestOutcomeEvaluator:
    """Tests for outcome evaluator."""

    def test_evaluate_improvement(self):
        """Test evaluating an improvement outcome."""
        evaluator = OutcomeEvaluator()
        
        snapshot = ExecutionOutcomeSnapshot(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
            pre_execution_state={"score": 50},
            post_execution_state={"score": 75},
        )
        
        evaluation = evaluator.evaluate(snapshot)
        
        assert evaluation.category in [OutcomeCategory.IMPROVEMENT, OutcomeCategory.MIXED]

    def test_evaluate_no_change(self):
        """Test evaluating no change outcome."""
        evaluator = OutcomeEvaluator()
        
        snapshot = ExecutionOutcomeSnapshot(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
            pre_execution_state={"score": 50},
            post_execution_state={"score": 50},
        )
        
        evaluation = evaluator.evaluate(snapshot)
        
        assert evaluation.score == 0.0

    def test_evaluate_error(self):
        """Test evaluating an error outcome."""
        evaluator = OutcomeEvaluator()
        
        snapshot = ExecutionOutcomeSnapshot(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
            error_message="Execution failed",
        )
        
        evaluation = evaluator.evaluate(snapshot)
        
        assert evaluation.category == OutcomeCategory.ERROR


class TestReversibilityClassifier:
    """Tests for reversibility classifier."""

    def test_classify_fully_reversible(self):
        """Test classifying fully reversible action."""
        classifier = ReversibilityClassifier()
        
        result = classifier.classify("adjust_priority", "health")
        
        assert result.reversibility == ReversibilityLevel.FULLY_REVERSIBLE

    def test_classify_unknown(self):
        """Test classifying unknown action."""
        classifier = ReversibilityClassifier()
        
        result = classifier.classify("unknown_action", "health")
        
        assert result.reversibility == ReversibilityLevel.UNKNOWN

    def test_set_custom_rule(self):
        """Test setting custom reversibility rule."""
        classifier = ReversibilityClassifier()
        
        classifier.set_rule("test_action", ReversibilityLevel.IRREVERSIBLE)
        
        result = classifier.classify("test_action", "health")
        
        assert result.reversibility == ReversibilityLevel.IRREVERSIBLE


class TestReliabilityAnalyzer:
    """Tests for reliability analyzer."""

    def test_analyze(self):
        """Test analyzing reliability."""
        analyzer = ExecutionReliabilityAnalyzer(min_samples=2)
        
        snapshots = [
            ExecutionOutcomeSnapshot(
                execution_id=f"exec_{i}",
                recommendation_id=f"rec_{i}",
                action_type="adjust_priority",
                domain="health",
            )
            for i in range(3)
        ]
        
        scores = analyzer.analyze(snapshots)
        
        assert len(scores) > 0
        assert scores[0].action_type == "adjust_priority"

    def test_is_reliable(self):
        """Test checking reliability."""
        analyzer = ExecutionReliabilityAnalyzer(min_samples=2)
        
        # Add some snapshots
        snapshots = [
            ExecutionOutcomeSnapshot(
                execution_id=f"exec_{i}",
                recommendation_id=f"rec_{i}",
                action_type="adjust_priority",
                domain="health",
            )
            for i in range(5)
        ]
        
        analyzer.analyze(snapshots)
        
        # Without enough outcome evaluations and with success_rate=1.0
        # (all treated as successful in this simplified implementation),
        # and with enough samples, it should be reliable
        # Note: current implementation treats all as successful by default
        result = analyzer.is_reliable("adjust_priority", "health")
        
        # With 5 samples and 100% success rate, should be reliable
        assert result is True


class TestApprovalPolicyAdvisor:
    """Tests for approval policy advisor."""

    def test_recommend_policy(self):
        """Test recommending policy."""
        advisor = ApprovalPolicyAdvisor()
        
        # Without reliability data
        recommendation = advisor.recommend_policy("adjust_priority", "health")
        
        assert recommendation.action_type == "adjust_priority"
        assert recommendation.current_level == ApprovalPolicyLevel.MANUAL_ONLY
        assert recommendation.recommended_level == ApprovalPolicyLevel.MANUAL_ONLY


class TestExecutionAuditController:
    """Tests for execution audit controller."""

    def test_capture_outcome(self):
        """Test capturing outcome through controller."""
        controller = ExecutionAuditController()
        
        snapshot = controller.capture_outcome(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
            pre_execution_state={"priority": 3},
            post_execution_state={"priority": 5},
        )
        
        assert snapshot.execution_id == "exec_001"

    def test_classify_reversibility(self):
        """Test classifying reversibility."""
        controller = ExecutionAuditController()
        
        result = controller.classify_reversibility("adjust_priority", "health")
        
        assert result.reversibility == ReversibilityLevel.FULLY_REVERSIBLE

    def test_get_statistics(self):
        """Test getting statistics."""
        controller = ExecutionAuditController()
        
        controller.capture_outcome(
            execution_id="exec_001",
            recommendation_id="rec_001",
            action_type="adjust_priority",
            domain="health",
        )
        
        stats = controller.get_statistics()
        
        assert "tracker" in stats
        assert "reliability" in stats


class TestSafetyEnforcement:
    """Tests for safety enforcement in audit subsystem."""

    def test_live_execution_still_disabled(self):
        """Verify live execution is still disabled."""
        from app.execution_audit import outcome_models
        assert outcome_models.LIVE_EXECUTION_ENABLED is False
