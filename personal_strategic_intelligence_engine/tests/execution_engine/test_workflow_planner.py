"""Tests for Workflow Planner."""
import pytest
from app.execution_engine import (
    WorkflowPlanner,
    ExecutionTask,
    ExecutionPriority,
    PermissionLevel,
    ExecutionStatus,
    TaskType,
)


class TestWorkflowPlanner:
    """Tests for WorkflowPlanner."""

    def setup_method(self):
        self.planner = WorkflowPlanner()

    def test_create_workflow(self):
        """Test creating a workflow."""
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="dec1",
                description="Task 2",
                dependencies=["task1"],
            ),
        ]
        
        workflow = self.planner.create_workflow(
            tasks=tasks,
            origin_decision="dec1",
        )
        
        assert workflow.origin_decision == "dec1"
        assert len(workflow.tasks) == 2

    def test_priority_inheritance(self):
        """Test priority inheritance."""
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
                priority=ExecutionPriority.LOW,
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="dec1",
                description="Task 2",
                priority=ExecutionPriority.CRITICAL,
            ),
        ]
        
        workflow = self.planner.create_workflow(tasks=tasks, origin_decision="dec1")
        
        assert workflow.priority == ExecutionPriority.CRITICAL

    def test_execution_order_resolution(self):
        """Test execution order based on dependencies."""
        tasks = [
            ExecutionTask(
                task_id="task3",
                origin_decision="dec1",
                description="Task 3",
                dependencies=["task2"],
            ),
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="dec1",
                description="Task 2",
                dependencies=["task1"],
            ),
        ]
        
        workflow = self.planner.create_workflow(tasks=tasks, origin_decision="dec1")
        
        # task1 should come before task2, task2 before task3
        order = workflow.execution_order
        assert order.index("task1") < order.index("task2")
        assert order.index("task2") < order.index("task3")

    def test_detect_circular_dependencies(self):
        """Test circular dependency detection."""
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
                dependencies=["task2"],
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="dec1",
                description="Task 2",
                dependencies=["task1"],
            ),
        ]
        
        has_cycle = self.planner.detect_circular_dependencies(tasks)
        assert has_cycle is True

    def test_identify_parallel_tasks(self):
        """Test identifying parallel tasks."""
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
            ),
            ExecutionTask(
                task_id="task2",
                origin_decision="dec1",
                description="Task 2",
            ),
            ExecutionTask(
                task_id="task3",
                origin_decision="dec1",
                description="Task 3",
                dependencies=["task1"],
            ),
        ]
        
        parallel_groups = self.planner.identify_parallel_tasks(tasks)
        
        # First group should have task1 and task2
        assert "task1" in parallel_groups[0]
        assert "task2" in parallel_groups[0]
        # Second group should have task3
        assert "task3" in parallel_groups[1]

    def test_validate_workflow(self):
        """Test workflow validation."""
        tasks = [
            ExecutionTask(
                task_id="task1",
                origin_decision="dec1",
                description="Task 1",
            ),
        ]
        
        workflow = self.planner.create_workflow(tasks=tasks, origin_decision="dec1")
        
        validation = self.planner.validate_workflow(workflow)
        
        assert validation["is_valid"] is True
        assert len(validation["issues"]) == 0
