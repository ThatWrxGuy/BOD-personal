# PSIE Workflows

This document describes the workflow orchestration system in PSIE.

## Overview

PSIE uses an event-driven workflow orchestration system to coordinate complex multi-step processes. Each workflow follows a defined state machine and emits events at key lifecycle points.

## Workflow Types

### Signal Workflow
Manages the lifecycle of strategic signals.

**States:**
```
DETECTED → CLASSIFIED → PROCESSED → COMPLETED / ARCHIVED
```

**Events:**
- `SIGNAL_CREATED`: New signal detected
- `SIGNAL_CLASSIFIED`: Signal has been categorized
- `SIGNAL_PROCESSED`: Signal analysis complete

### Decision Workflow
Manages the lifecycle of strategic decisions.

**States:**
```
PROPOSED → UNDER_REVIEW → UNDER_DEBATE → CONSENSUS_REACHED → APPROVED / REJECTED → EXECUTING → EXECUTED → OUTCOME_RECORDED → COMPLETED
```

**Events:**
- `DECISION_PROPOSAL_CREATED`: New decision proposed
- `GOVERNANCE_REVIEW_REQUESTED`: Decision submitted for review
- `DEBATE_STARTED`: Debate initiated
- `DEBATE_COMPLETED`: Debate finished
- `CONSENSUS_CALCULATED`: Consensus reached
- `DECISION_APPROVED`: Decision approved
- `DECISION_REJECTED`: Decision rejected
- `EXECUTION_REQUESTED`: Execution requested
- `EXECUTION_COMPLETED`: Execution finished

### Debate Workflow
Manages multi-agent debate sessions.

**States:**
```
INITIATED → RUNNING → UNDER_DEBATE → CONSENSUS_REACHED → COMPLETED / FAILED / CANCELLED
```

**Events:**
- `DEBATE_STARTED`: Debate initiated
- `DEBATE_ROUND_COMPLETED`: Round finished
- `DEBATE_COMPLETED`: Debate finished

### Execution Workflow
Manages action execution lifecycle.

**States:**
```
INITIATED → RUNNING → COMPLETED / FAILED / CANCELLED
```

**Events:**
- `EXECUTION_REQUESTED`: Execution requested
- `EXECUTION_STARTED`: Execution started
- `EXECUTION_COMPLETED`: Execution completed
- `EXECUTION_FAILED`: Execution failed
- `EXECUTION_CANCELLED`: Execution cancelled

### Learning Workflow
Manages the strategic learning process.

**States:**
```
INITIATED → RUNNING → COMPLETED / FAILED
```

**Events:**
- `OUTCOME_EVALUATED`: Outcome recorded
- `LESSON_EXTRACTED`: Lesson learned
- `PATTERN_DETECTED`: Pattern identified
- `DOCTRINE_UPDATED`: Strategic doctrine updated

## State Machine

PSIE uses a state machine to enforce valid transitions. Invalid transitions are rejected with an error.

### Decision State Machine

```
PROPOSED ──┬── UNDER_REVIEW ──┬── UNDER_DEBATE ──┬── CONSENSUS_REACHED ──┬── APPROVED ──┬── EXECUTING ──┬── EXECUTED ──┬── OUTCOME_RECORDED ── COMPLETED
           │                   │                  │                      │              │               │               │
           │                   │                  │                      │              │               │               │
           └──> REJECTED ──────┴──> FAILED        └──> REJECTED ─────────┴──> CANCELLED ──┴──> FAILED      └──> FAILED
```

## Workflow Engine

The workflow engine manages workflow instances:

### Starting a Workflow

```python
from app.orchestration.workflow_engine import get_workflow_engine

engine = await get_workflow_engine(session)

workflow = await engine.start_workflow(
    workflow_name="Decision Workflow",
    workflow_type="decision",
    initial_context={"decision_id": "123"}
)
```

### Transitioning a Workflow

```python
workflow = await engine.transition_workflow(
    workflow_id=workflow.id,
    to_state="UNDER_REVIEW",
    trigger_event="GOVERNANCE_REVIEW_REQUESTED",
    context_updates={"reviewed_by": "admin"}
)
```

### Getting Workflow History

```python
history = await engine.get_workflow_history(workflow_id)
```

## Event Publishing

Events are published through the event bus:

```python
from app.orchestration.event_bus import get_event_bus
from app.orchestration.event_types import create_decision_approved_event

event_bus = get_event_bus(session)

event = create_decision_approved_event(
    decision_id=uuid.UUID("..."),
    approved_by="governance"
)

await event_bus.publish_event(event)
```

## Subscribing to Events

```python
from app.orchestration.event_bus import get_event_bus
from app.orchestration.event_types import EventType

event_bus = get_event_bus(session)

@event_bus.subscribe(EventType.DECISION_APPROVED)
async def handle_decision_approved(event):
    # Process approved decision
    pass
```

## Workflow API

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /orchestration/workflows | List workflows |
| GET | /orchestration/workflows/{id} | Get workflow details |
| POST | /orchestration/workflows/start | Start workflow |
| POST | /orchestration/workflows/{id}/transition | Transition workflow |
| GET | /orchestration/workflows/{id}/history | Get workflow history |

### Example: Start Decision Workflow

```bash
curl -X POST http://localhost:8000/orchestration/workflows/start \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Strategic Decision",
    "workflow_type": "decision",
    "initial_context": {"decision_id": "123"}
  }'
```

### Example: Transition Workflow

```bash
curl -X POST http://localhost:8000/orchestration/workflows/{id}/transition \
  -H "Content-Type: application/json" \
  -d '{
    "to_state": "UNDER_REVIEW",
    "trigger_event": "GOVERNANCE_REVIEW_REQUESTED",
    "context_updates": {}
  }'
```

## Correlation IDs

Each workflow carries a correlation ID that allows tracing through the system:

```bash
curl http://localhost:8000/observability/traces/{correlation_id}
```

This returns all events and state transitions for the workflow.

## Workflow Reliability

### Idempotent Handlers

Event handlers should be idempotent to support retries:

```python
async def handle_decision_approved(event):
    # Check if already processed
    existing = await db.get_processed_event(event.event_id)
    if existing:
        return
    
    # Process the event
    await process_decision(event)
```

### Invalid State Transitions

Invalid transitions are blocked:

```python
from app.orchestration.workflow_state_machine import InvalidTransitionError

try:
    await engine.transition_workflow(
        workflow_id,
        "EXECUTING",  # Can't go directly from PROPOSED to EXECUTING
        "EXECUTE"
    )
except InvalidTransitionError as e:
    print(f"Invalid transition: {e}")
```

## Failure Handling

### Workflow Failures

```python
await engine.fail_workflow(
    workflow_id,
    error_message="Decision rejected by governance"
)
```

### Error Recovery

Workflows can be restarted after failure:

```python
# Create new workflow with same context
new_workflow = await engine.start_workflow(
    workflow_name="Retry Decision",
    workflow_type="decision",
    initial_context=old_workflow.context
)
```
