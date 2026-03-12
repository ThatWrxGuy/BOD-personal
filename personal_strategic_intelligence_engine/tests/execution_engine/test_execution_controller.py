"""Tests for Execution Controller."""
import pytest
from app.execution_engine import (
    ExecutionController,
    ExecutionTask,
    ExecutionWorkflow,
    ExecutionPriority,
    PermissionLevel,
    ExecutionStatus,
)


class TestExecutionController:
    """Tests for ExecutionController."""

    def setup_method(self):
        self.controller = ExecutionController()

    def test_create_workflow_from_decision(self):
        """Test creating workflow from decision."""
        workflow = self.controller.create_workflow_from_decision(
            decision_summary="Rebalance financial allocation",
            decision_id="test_decision",
        )
        
        assert workflow is not None
        assert workflow.origin_decision == "test_decision"
        assert len(workflow.tasks) > 0

    def test_execute_task(self):
        """Test executing a single task."""
        task = ExecutionTask(
            task_id="test_task",
            origin_decision="test",
            description="Test task",
        )
        
        result = self.controller.execute_task(task)
        
        assert result is not None
        assert result.task_id == "test_task"

    def test_execute_workflow(self):
        """Test executing a workflow."""
        # Create a simple workflow
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
                priority=ExecutionPriority.NORMAL,
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="dec1",
                description="Task 2",
                priority=ExecutionPriority.NORMAL,
            ),
        ]
        
        workflow = self.controller.workflow_planner.create_workflow(
            tasks=tasks,
            origin_decision="dec1",
        )
        
        result = self.controller.execute_workflow(workflow)
        
        assert result is not None
        assert result.workflow_id == workflow.workflow_id

    def test_get_execution_summary(self):
        """Test getting execution summary."""
        summary = self.controller.get_execution_summary()
        
        assert summary is not None
        assert hasattr(summary, "total_tasks")

    def test_permission_check(self):
        """Test permission evaluation."""
        task = ExecutionTask(
            task_id="test_task",
            origin_decision="test",
            description="Execute risk adjustment",
        )
        
        permission = self.controller.permission_manager.evaluate_permission(task)
        
        assert permission is not None
