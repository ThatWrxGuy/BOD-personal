"""Workflow state machine for managing valid state transitions."""
from enum import Enum
from typing import Dict, List, Optional, Set


class WorkflowState(str, Enum):
    """Standard workflow states."""
    
    # Generic states
    INITIATED = "INITIATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    
    # Decision workflow states
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    UNDER_DEBATE = "UNDER_DEBATE"
    CONSENSUS_REACHED = "CONSENSUS_REACHED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"
    
    # Signal workflow states
    DETECTED = "DETECTED"
    CLASSIFIED = "CLASSIFIED"
    PROCESSED = "PROCESSED"
    ARCHIVED = "ARCHIVED"


class WorkflowStateMachine:
    """Manages valid state transitions for workflows."""
    
    # Define valid transitions for each workflow type
    TRANSITIONS: Dict[str, Dict[str, Set[str]]] = {
        "decision": {
            WorkflowState.PROPOSED: {
                WorkflowState.UNDER_REVIEW,
                WorkflowState.UNDER_DEBATE,
                WorkflowState.REJECTED,
            },
            WorkflowState.UNDER_REVIEW: {
                WorkflowState.UNDER_DEBATE,
                WorkflowState.APPROVED,
                WorkflowState.REJECTED,
            },
            WorkflowState.UNDER_DEBATE: {
                WorkflowState.CONSENSUS_REACHED,
                WorkflowState.REJECTED,
            },
            WorkflowState.CONSENSUS_REACHED: {
                WorkflowState.APPROVED,
                WorkflowState.REJECTED,
            },
            WorkflowState.APPROVED: {
                WorkflowState.EXECUTING,
                WorkflowState.CANCELLED,
            },
            WorkflowState.EXECUTING: {
                WorkflowState.EXECUTED,
                WorkflowState.FAILED,
                WorkflowState.CANCELLED,
            },
            WorkflowState.EXECUTED: {
                WorkflowState.OUTCOME_RECORDED,
            },
            WorkflowState.OUTCOME_RECORDED: {
                WorkflowState.COMPLETED,
            },
            WorkflowState.REJECTED: {
                WorkflowState.FAILED,
            },
            WorkflowState.FAILED: set(),
            WorkflowState.CANCELLED: set(),
            WorkflowState.COMPLETED: set(),
        },
        "signal": {
            WorkflowState.DETECTED: {
                WorkflowState.CLASSIFIED,
            },
            WorkflowState.CLASSIFIED: {
                WorkflowState.PROCESSED,
                WorkflowState.ARCHIVED,
            },
            WorkflowState.PROCESSED: {
                WorkflowState.COMPLETED,
                WorkflowState.ARCHIVED,
            },
            WorkflowState.COMPLETED: set(),
            WorkflowState.ARCHIVED: set(),
        },
        "debate": {
            WorkflowState.INITIATED: {
                WorkflowState.RUNNING,
                WorkflowState.CANCELLED,
            },
            WorkflowState.RUNNING: {
                WorkflowState.UNDER_DEBATE,
                WorkflowState.COMPLETED,
                WorkflowState.FAILED,
            },
            WorkflowState.UNDER_DEBATE: {
                WorkflowState.CONSENSUS_REACHED,
                WorkflowState.FAILED,
            },
            WorkflowState.CONSENSUS_REACHED: {
                WorkflowState.COMPLETED,
            },
            WorkflowState.COMPLETED: set(),
            WorkflowState.FAILED: set(),
            WorkflowState.CANCELLED: set(),
        },
        "execution": {
            WorkflowState.INITIATED: {
                WorkflowState.RUNNING,
                WorkflowState.CANCELLED,
            },
            WorkflowState.RUNNING: {
                WorkflowState.COMPLETED,
                WorkflowState.FAILED,
                WorkflowState.CANCELLED,
            },
            WorkflowState.COMPLETED: set(),
            WorkflowState.FAILED: set(),
            WorkflowState.CANCELLED: set(),
        },
        "learning": {
            WorkflowState.INITIATED: {
                WorkflowState.RUNNING,
            },
            WorkflowState.RUNNING: {
                WorkflowState.COMPLETED,
                WorkflowState.FAILED,
            },
            WorkflowState.COMPLETED: set(),
            WorkflowState.FAILED: set(),
        },
    }
    
    def __init__(self, workflow_type: str):
        self.workflow_type = workflow_type
        self._transitions = self.TRANSITIONS.get(workflow_type, {})
    
    def can_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is valid."""
        
        if from_state not in self._transitions:
            return False
        
        return to_state in self._transitions[from_state]
    
    def get_valid_transitions(self, from_state: str) -> Set[str]:
        """Get all valid transitions from a state."""
        
        return self._transitions.get(from_state, set())
    
    def validate_transition(self, from_state: str, to_state: str) -> None:
        """Validate a transition, raise if invalid."""
        
        if not self.can_transition(from_state, to_state):
            valid = self.get_valid_transitions(from_state)
            raise InvalidTransitionError(
                f"Invalid transition from {from_state} to {to_state}. "
                f"Valid transitions: {valid}"
            )
    
    def get_initial_state(self) -> str:
        """Get the initial state for this workflow type."""
        
        initial_states = {
            "decision": WorkflowState.PROPOSED,
            "signal": WorkflowState.DETECTED,
            "debate": WorkflowState.INITIATED,
            "execution": WorkflowState.INITIATED,
            "learning": WorkflowState.INITIATED,
        }
        
        return initial_states.get(self.workflow_type, WorkflowState.INITIATED)
    
    def get_terminal_states(self) -> Set[str]:
        """Get all terminal states for this workflow type."""
        
        terminal = set()
        for state, transitions in self._transitions.items():
            if not transitions:
                terminal.add(state)
        return terminal


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


def get_state_machine(workflow_type: str) -> WorkflowStateMachine:
    """Get a state machine for a workflow type."""
    return WorkflowStateMachine(workflow_type)
