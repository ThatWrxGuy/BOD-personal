"""Tests for Permission Manager."""
import pytest
from app.execution_engine import (
    PermissionManager,
    ExecutionTask,
    ExecutionPriority,
    PermissionLevel,
    TaskType,
)


class TestPermissionManager:
    """Tests for PermissionManager."""

    def setup_method(self):
        self.manager = PermissionManager()

    def test_high_priority_autonomous(self):
        """Test high priority tasks get autonomous permission."""
        task = ExecutionTask(
            task_id="test_task",
            origin_decision="test",
            description="Important task",
            priority=ExecutionPriority.CRITICAL,
        )
        
        decision = self.manager.evaluate_permission(task)
        
        assert decision.permission_level == PermissionLevel.AUTONOMOUS

    def test_risk_task_approval(self):
        """Test risk tasks require approval."""
        task = ExecutionTask(
            task_id="test_task",
            origin_decision="test",
            description="Execute risk adjustment",
            priority=ExecutionPriority.NORMAL,
        )
        
        decision = self.manager.evaluate_permission(task)
        
        assert decision.permission_level == PermissionLevel.REQUIRES_APPROVAL

    def test_financial_task_approval(self):
        """Test financial tasks require approval."""
        task = ExecutionTask(
            task_id="test_task",
            origin_decision="test",
            description="Rebalance allocation",
            priority=ExecutionPriority.NORMAL,
        )
        
        decision = self.manager.evaluate_permission(task)
        
        assert decision.permission_level == PermissionLevel.REQUIRES_APPROVAL

    def test_monitoring_task_autonomous(self):
        """Test monitoring tasks are autonomous."""
        task = ExecutionTask(
            task_id="test_task",
            origin_decision="test",
            description="Monitor system status",
            priority=ExecutionPriority.LOW,
        )
        
        decision = self.manager.evaluate_permission(task)
        
        assert decision.permission_level == PermissionLevel.AUTONOMOUS

    def test_evaluate_batch(self):
        """Test batch permission evaluation."""
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="test",
                description="Important task",
                priority=ExecutionPriority.HIGH,
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="test",
                description="Risk task",
            ),
        ]
        
        decisions = self.manager.evaluate_batch(tasks)
        
        assert len(decisions) == 2
        assert decisions[0].approved is True
        assert decisions[1].approved is False

    def test_get_permission_summary(self):
        """Test getting permission summary."""
        summary = self.manager.get_permission_summary()
        
        assert summary["total_rules"] > 0
        assert summary["autonomous_rules"] >= 0
        assert summary["approval_rules"] >= 0
