"""Tests for the State Engine."""
import pytest
from datetime import datetime, timedelta

from app.state_engine import (
    StateEngine,
    StateRepository,
    get_state_engine,
    reset_state_engine,
    StateComponent,
    MemoryTier,
    ExecutionStatus,
)
from app.state_engine.state_models import (
    SystemStateSnapshot,
    OperationalState,
    StrategicState,
    RiskState,
    GoalState,
    ResourceState,
)


class TestStateEngine:
    """Tests for StateEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_state_engine()
        self.engine = StateEngine()

    def test_initialization(self):
        """Test state engine initializes correctly."""
        state = self.engine.initialize_state()
        assert state is not None
        assert state.cycle_id is not None

    def test_get_current_state(self):
        """Test getting current state."""
        self.engine.initialize_state()
        state = self.engine.get_current_state()
        assert state is not None
        assert isinstance(state, SystemStateSnapshot)

    def test_update_operational_state(self):
        """Test updating operational state."""
        self.engine.initialize_state()
        self.engine.update_state(
            StateComponent.OPERATIONAL,
            {"active_priorities": ["health", "wealth"], "execution_status": "running"}
        )
        state = self.engine.get_operational_state()
        assert state.active_priorities == ["health", "wealth"]
        assert state.execution_status == ExecutionStatus.RUNNING

    def test_update_strategic_state(self):
        """Test updating strategic state."""
        self.engine.initialize_state()
        self.engine.update_state(
            StateComponent.STRATEGIC,
            {"confidence_score": 0.8, "strategic_priority": "growth"}
        )
        state = self.engine.get_strategic_state()
        assert state.confidence_score == 0.8
        assert state.strategic_priority == "growth"

    def test_update_risk_state(self):
        """Test updating risk state."""
        self.engine.initialize_state()
        self.engine.update_state(
            StateComponent.RISK,
            {"risk_severity_index": 0.6, "identified_risks": [{"id": "r1"}]}
        )
        state = self.engine.get_risk_state()
        assert state.risk_severity_index == 0.6
        assert len(state.identified_risks) == 1

    def test_update_goal_state(self):
        """Test updating goal state."""
        self.engine.initialize_state()
        self.engine.update_state(
            StateComponent.GOAL,
            {"active_goals": [{"id": "g1", "name": "Test Goal"}]}
        )
        state = self.engine.get_goal_state()
        assert len(state.active_goals) == 1

    def test_update_resource_state(self):
        """Test updating resource state."""
        self.engine.initialize_state()
        self.engine.update_state(
            StateComponent.RESOURCE,
            {"system_capacity": 0.9}
        )
        state = self.engine.get_resource_state()
        assert state.system_capacity == 0.9


class TestTaskManagement:
    """Tests for task management."""

    def setup_method(self):
        reset_state_engine()
        self.engine = StateEngine()
        self.engine.initialize_state()

    def test_add_task(self):
        """Test adding a task."""
        task_id = self.engine.add_task({"name": "Test Task", "priority": 1})
        assert task_id is not None
        tasks = self.engine.get_operational_state().current_tasks
        assert len(tasks) == 1

    def test_complete_task(self):
        """Test completing a task."""
        task_id = self.engine.add_task({"name": "Test Task"})
        result = self.engine.complete_task(task_id)
        assert result is True

    def test_remove_task(self):
        """Test removing a task."""
        task_id = self.engine.add_task({"name": "Test Task"})
        result = self.engine.remove_task(task_id)
        assert result is True


class TestGoalManagement:
    """Tests for goal management."""

    def setup_method(self):
        reset_state_engine()
        self.engine = StateEngine()
        self.engine.initialize_state()

    def test_add_goal(self):
        """Test adding a goal."""
        goal_id = self.engine.add_goal({"name": "Test Goal", "target": 1.0})
        assert goal_id is not None
        goals = self.engine.get_goal_state().active_goals
        assert len(goals) == 1

    def test_update_goal_progress(self):
        """Test updating goal progress."""
        goal_id = self.engine.add_goal({"name": "Test Goal"})
        result = self.engine.update_goal_progress(goal_id, 0.5)
        assert result is True


class TestRiskManagement:
    """Tests for risk management."""

    def setup_method(self):
        reset_state_engine()
        self.engine = StateEngine()
        self.engine.initialize_state()

    def test_add_risk(self):
        """Test adding a risk."""
        risk_id = self.engine.add_risk({"name": "Test Risk", "severity": 0.8})
        assert risk_id is not None

    def test_resolve_risk(self):
        """Test resolving a risk."""
        risk_id = self.engine.add_risk({"name": "Test Risk", "severity": 0.5})
        result = self.engine.resolve_risk(risk_id)
        assert result is True


class TestCycleManagement:
    """Tests for cycle management."""

    def setup_method(self):
        reset_state_engine()
        self.engine = StateEngine()
        self.engine.initialize_state()

    def test_start_cycle(self):
        """Test starting a new cycle."""
        cycle_id = self.engine.start_cycle()
        assert cycle_id is not None
        assert cycle_id == self.engine.get_current_cycle_id()

    def test_complete_cycle(self):
        """Test completing a cycle."""
        self.engine.start_cycle()
        completed_id = self.engine.complete_cycle()
        assert completed_id is not None
        assert self.engine.get_current_cycle_id() is None

    def test_commit_snapshot(self):
        """Test committing a snapshot."""
        self.engine.initialize_state()
        filename = self.engine.commit_cycle_snapshot()
        assert filename is not None


class TestStateSummary:
    """Tests for state summary."""

    def setup_method(self):
        reset_state_engine()
        self.engine = StateEngine()
        self.engine.initialize_state()

    def test_get_state_summary(self):
        """Test getting state summary."""
        summary = self.engine.get_state_summary()
        assert "cycle_id" in summary
        assert "operational" in summary
        assert "strategic" in summary
        assert "goals" in summary
        assert "risks" in summary


class TestStateRepository:
    """Tests for StateRepository."""

    def setup_method(self):
        import tempfile
        import os
        self.temp_dir = tempfile.mkdtemp()
        self.repository = StateRepository(self.temp_dir)

    def test_store_and_retrieve_snapshot(self):
        """Test storing and retrieving snapshots."""
        state = SystemStateSnapshot()
        filename = self.repository.store_snapshot(state)
        assert filename is not None
        
        retrieved = self.repository.get_snapshot(filename)
        assert retrieved is not None

    def test_get_recent_snapshots(self):
        """Test getting recent snapshots."""
        state = SystemStateSnapshot()
        self.repository.store_snapshot(state)
        
        snapshots = self.repository.get_recent_snapshots(limit=5)
        assert len(snapshots) >= 1

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestGetStateEngine:
    """Tests for singleton access."""

    def test_get_state_engine(self):
        """Test getting singleton instance."""
        reset_state_engine()
        engine1 = get_state_engine()
        engine2 = get_state_engine()
        assert engine1 is engine2
