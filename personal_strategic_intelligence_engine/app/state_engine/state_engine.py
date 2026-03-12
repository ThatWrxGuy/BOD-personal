"""Core State Engine - Single Source of Truth for System State."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.state_engine.state_models import (
    SystemStateSnapshot,
    OperationalState,
    StrategicState,
    RiskState,
    GoalState,
    ResourceState,
    StateUpdate,
)
from app.state_engine.state_types import StateComponent, ExecutionStatus
from app.state_engine.state_repository import StateRepository


class StateEngine:
    """Unified State Engine - Single Source of Truth for System State.
    
    The State Engine maintains the authoritative system state and provides
    read/write access to all intelligence subsystems.
    """
    
    def __init__(self, repository: Optional[StateRepository] = None):
        self.repository = repository or StateRepository()
        
        # Current state
        self._current_state = SystemStateSnapshot()
        self._cycle_count = 0
        self._current_cycle_id: Optional[str] = None
    
    # ============= Initialization =============
    
    def initialize_state(self) -> SystemStateSnapshot:
        """Initialize the system state."""
        self._current_state = SystemStateSnapshot(
            timestamp=datetime.utcnow(),
            cycle_id=self._generate_cycle_id(),
            operational_state=OperationalState(),
            strategic_state=StrategicState(),
            risk_state=RiskState(),
            goal_state=GoalState(),
            resource_state=ResourceState(),
        )
        self._current_cycle_id = self._current_state.cycle_id
        return self._current_state
    
    def _generate_cycle_id(self) -> str:
        """Generate a unique cycle ID."""
        return f"cycle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # ============= State Access =============
    
    def get_current_state(self) -> SystemStateSnapshot:
        """Get the current system state snapshot."""
        return self._current_state
    
    def get_operational_state(self) -> OperationalState:
        """Get current operational state."""
        return self._current_state.operational_state
    
    def get_strategic_state(self) -> StrategicState:
        """Get current strategic state."""
        return self._current_state.strategic_state
    
    def get_risk_state(self) -> RiskState:
        """Get current risk state."""
        return self._current_state.risk_state
    
    def get_goal_state(self) -> GoalState:
        """Get current goal state."""
        return self._current_state.goal_state
    
    def get_resource_state(self) -> ResourceState:
        """Get current resource state."""
        return self._current_state.resource_state
    
    # ============= State Updates =============
    
    def update_state(self, component: StateComponent, data: Dict[str, Any]) -> SystemStateSnapshot:
        """Update a specific state component.
        
        Args:
            component: The component to update (OPERATIONAL, STRATEGIC, RISK, GOAL, RESOURCE)
            data: The data to update
            
        Returns:
            Updated system state snapshot
        """
        self._current_state.timestamp = datetime.utcnow()
        
        if component == StateComponent.OPERATIONAL:
            self._update_operational_state(data)
        elif component == StateComponent.STRATEGIC:
            self._update_strategic_state(data)
        elif component == StateComponent.RISK:
            self._update_risk_state(data)
        elif component == StateComponent.GOAL:
            self._update_goal_state(data)
        elif component == StateComponent.RESOURCE:
            self._update_resource_state(data)
        
        return self._current_state
    
    def _update_operational_state(self, data: Dict[str, Any]):
        """Update operational state."""
        state = self._current_state.operational_state
        
        if "current_tasks" in data:
            state.current_tasks = data["current_tasks"]
        if "active_priorities" in data:
            state.active_priorities = data["active_priorities"]
        if "execution_status" in data:
            state.execution_status = ExecutionStatus(data["execution_status"])
        if "active_cycles" in data:
            state.active_cycles = data["active_cycles"]
        if "completed_cycles" in data:
            state.completed_cycles = data["completed_cycles"]
    
    def _update_strategic_state(self, data: Dict[str, Any]):
        """Update strategic state."""
        state = self._current_state.strategic_state
        
        if "active_strategies" in data:
            state.active_strategies = data["active_strategies"]
        if "forecast_summary" in data:
            state.forecast_summary = data["forecast_summary"]
        if "simulation_summary" in data:
            state.simulation_summary = data["simulation_summary"]
        if "confidence_score" in data:
            state.confidence_score = data["confidence_score"]
        if "strategic_priority" in data:
            state.strategic_priority = data["strategic_priority"]
    
    def _update_risk_state(self, data: Dict[str, Any]):
        """Update risk state."""
        state = self._current_state.risk_state
        
        if "identified_risks" in data:
            state.identified_risks = data["identified_risks"]
        if "risk_severity_index" in data:
            state.risk_severity_index = data["risk_severity_index"]
        if "stress_test_results" in data:
            state.stress_test_results = data["stress_test_results"]
        if "high_priority_risks" in data:
            state.high_priority_risks = data["high_priority_risks"]
    
    def _update_goal_state(self, data: Dict[str, Any]):
        """Update goal state."""
        state = self._current_state.goal_state
        
        if "active_goals" in data:
            state.active_goals = data["active_goals"]
        if "progress_metrics" in data:
            state.progress_metrics = data["progress_metrics"]
        if "goal_probability_scores" in data:
            state.goal_probability_scores = data["goal_probability_scores"]
    
    def _update_resource_state(self, data: Dict[str, Any]):
        """Update resource state."""
        state = self._current_state.resource_state
        
        if "financial_state" in data:
            state.financial_state = data["financial_state"]
        if "time_allocation" in data:
            state.time_allocation = data["time_allocation"]
        if "system_capacity" in data:
            state.system_capacity = data["system_capacity"]
    
    # ============= Task Management =============
    
    def add_task(self, task: Dict[str, Any]) -> str:
        """Add a task to the current state."""
        task_id = task.get("task_id", str(uuid.uuid4()))
        task["task_id"] = task_id
        task["added_at"] = datetime.utcnow().isoformat()
        
        self._current_state.operational_state.current_tasks.append(task)
        return task_id
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as complete."""
        for task in self._current_state.operational_state.current_tasks:
            if task.get("task_id") == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.utcnow().isoformat()
                return True
        return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the current state."""
        initial_len = len(self._current_state.operational_state.current_tasks)
        self._current_state.operational_state.current_tasks = [
            t for t in self._current_state.operational_state.current_tasks
            if t.get("task_id") != task_id
        ]
        return len(self._current_state.operational_state.current_tasks) < initial_len
    
    # ============= Goal Management =============
    
    def add_goal(self, goal: Dict[str, Any]) -> str:
        """Add a goal to the current state."""
        goal_id = goal.get("goal_id", str(uuid.uuid4()))
        goal["goal_id"] = goal_id
        goal["added_at"] = datetime.utcnow().isoformat()
        
        self._current_state.goal_state.active_goals.append(goal)
        return goal_id
    
    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """Update goal progress."""
        for goal in self._current_state.goal_state.active_goals:
            if goal.get("goal_id") == goal_id:
                goal["progress"] = progress
                goal["updated_at"] = datetime.utcnow().isoformat()
                self._current_state.goal_state.progress_metrics[goal_id] = progress
                return True
        return False
    
    # ============= Risk Management =============
    
    def add_risk(self, risk: Dict[str, Any]) -> str:
        """Add a risk to the current state."""
        risk_id = risk.get("risk_id", str(uuid.uuid4()))
        risk["risk_id"] = risk_id
        risk["identified_at"] = datetime.utcnow().isoformat()
        
        self._current_state.risk_state.identified_risks.append(risk)
        
        # Update high priority risks if severity is high
        severity = risk.get("severity", 0.0)
        if severity >= 0.7:
            self._current_state.risk_state.high_priority_risks.append(risk_id)
        
        return risk_id
    
    def resolve_risk(self, risk_id: str) -> bool:
        """Mark a risk as resolved."""
        for risk in self._current_state.risk_state.identified_risks:
            if risk.get("risk_id") == risk_id:
                risk["status"] = "resolved"
                risk["resolved_at"] = datetime.utcnow().isoformat()
                if risk_id in self._current_state.risk_state.high_priority_risks:
                    self._current_state.risk_state.high_priority_risks.remove(risk_id)
                return True
        return False
    
    # ============= Cycle Management =============
    
    def start_cycle(self) -> str:
        """Start a new strategy cycle."""
        self._current_cycle_id = self._generate_cycle_id()
        self._current_state.cycle_id = self._current_cycle_id
        self._current_state.operational_state.active_cycles += 1
        return self._current_cycle_id
    
    def complete_cycle(self) -> str:
        """Complete the current strategy cycle."""
        if self._current_state.cycle_id:
            self._current_state.operational_state.completed_cycles += 1
            cycle_id = self._current_state.cycle_id
            self._current_state.cycle_id = None
            return cycle_id
        return ""
    
    def get_current_cycle_id(self) -> Optional[str]:
        """Get the current cycle ID."""
        return self._current_cycle_id
    
    # ============= Snapshot Operations =============
    
    def commit_cycle_snapshot(self) -> str:
        """Commit a snapshot of the current state to storage.
        
        Returns:
            The filename of the stored snapshot
        """
        self._current_state.timestamp = datetime.utcnow()
        
        # Store in repository
        filename = self.repository.store_snapshot(self._current_state)
        
        return filename
    
    def get_snapshots(self, limit: int = 10) -> List[SystemStateSnapshot]:
        """Get recent state snapshots."""
        return self.repository.get_recent_snapshots(limit)
    
    # ============= Utility =============
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        return {
            "cycle_id": self._current_cycle_id,
            "timestamp": self._current_state.timestamp.isoformat(),
            "operational": {
                "active_tasks": len(self._current_state.operational_state.current_tasks),
                "priorities": self._current_state.operational_state.active_priorities,
                "status": self._current_state.operational_state.execution_status.value,
            },
            "strategic": {
                "strategies": self._current_state.strategic_state.active_strategies,
                "confidence": self._current_state.strategic_state.confidence_score,
            },
            "goals": {
                "active": len(self._current_state.goal_state.active_goals),
            },
            "risks": {
                "identified": len(self._current_state.risk_state.identified_risks),
                "high_priority": len(self._current_state.risk_state.high_priority_risks),
            },
        }


# ============= Singleton Access =============

_state_engine_instance: Optional[StateEngine] = None


def get_state_engine() -> StateEngine:
    """Get the singleton State Engine instance."""
    global _state_engine_instance
    if _state_engine_instance is None:
        _state_engine_instance = StateEngine()
    return _state_engine_instance


def reset_state_engine():
    """Reset the state engine singleton (for testing)."""
    global _state_engine_instance
    _state_engine_instance = None
