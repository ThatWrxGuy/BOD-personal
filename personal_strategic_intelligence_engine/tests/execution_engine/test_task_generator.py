"""Tests for Task Generator."""
import pytest
from app.execution_engine import (
    TaskGenerator,
    ExecutionPriority,
    PermissionLevel,
    TaskType,
)


class TestTaskGenerator:
    """Tests for TaskGenerator."""

    def setup_method(self):
        self.generator = TaskGenerator()

    def test_generate_tasks_allocation(self):
        """Test generating tasks for allocation decision."""
        tasks = self.generator.generate_tasks(
            decision_summary="Rebalance financial allocation",
            decision_id="test_decision",
        )
        
        assert len(tasks) > 0
        assert tasks[0].origin_decision == "test_decision"

    def test_generate_tasks_risk(self):
        """Test generating tasks for risk decision."""
        tasks = self.generator.generate_tasks(
            decision_summary="Implement risk mitigation",
            decision_id="test_decision",
        )
        
        assert len(tasks) > 0

    def test_generate_tasks_growth(self):
        """Test generating tasks for growth decision."""
        tasks = self.generator.generate_tasks(
            decision_summary="Pursue growth opportunities",
            decision_id="test_decision",
        )
        
        assert len(tasks) > 0

    def test_task_dependencies(self):
        """Test task dependencies are set correctly."""
        tasks = self.generator.generate_tasks(
            decision_summary="Rebalance portfolio",
            decision_id="test",
        )
        
        # Later tasks should depend on earlier ones
        for i in range(1, len(tasks)):
            assert tasks[i].dependencies[0] == tasks[i-1].task_id

    def test_generate_single_task(self):
        """Test generating a single task."""
        task = self.generator.generate_single_task(
            description="Test task",
            decision_id="test",
            task_type=TaskType.ANALYSIS,
            priority=ExecutionPriority.HIGH,
            permission_level=PermissionLevel.AUTONOMOUS,
        )
        
        assert task.description == "Test task"
        assert task.task_type == TaskType.ANALYSIS
        assert task.priority == ExecutionPriority.HIGH

    def test_decision_classification(self):
        """Test decision classification."""
        assert self.generator._classify_decision("Rebalance portfolio") == "allocation"
        assert self.generator._classify_decision("Risk mitigation") == "risk"
        assert self.generator._classify_decision("Growth strategy") == "growth"
        assert self.generator._classify_decision("Monitor status") == "maintain"
