"""PSIE Orchestration Layer.

This module provides event-driven workflow orchestration for PSIE.
"""
from app.orchestration.event_types import (
    EventType,
    DomainEvent,
    create_signal_created_event,
    create_decision_proposal_event,
    create_debate_started_event,
    create_debate_completed_event,
    create_decision_approved_event,
    create_execution_requested_event,
    create_execution_completed_event,
    create_outcome_evaluated_event,
)

from app.orchestration.event_bus import EventBus, get_event_bus
from app.orchestration.workflow_engine import WorkflowEngine, get_workflow_engine
from app.orchestration.workflow_state_machine import (
    WorkflowState,
    WorkflowStateMachine,
    get_state_machine,
    InvalidTransitionError,
)

__all__ = [
    "EventType",
    "DomainEvent",
    "EventBus",
    "get_event_bus",
    "WorkflowEngine",
    "get_workflow_engine",
    "WorkflowState",
    "WorkflowStateMachine",
    "get_state_machine",
    "InvalidTransitionError",
    "create_signal_created_event",
    "create_decision_proposal_event",
    "create_debate_started_event",
    "create_debate_completed_event",
    "create_decision_approved_event",
    "create_execution_requested_event",
    "create_execution_completed_event",
    "create_outcome_evaluated_event",
]
