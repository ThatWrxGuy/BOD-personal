# PSIE Events

This document describes the event system in PSIE.

## Overview

PSIE uses an event-driven architecture to coordinate activities across modules. Events are published to the event bus and consumed by subscribers.

## Event Types

### Signal Events

| Event | Description |
|-------|-------------|
| `SIGNAL_CREATED` | New signal detected or created |
| `SIGNAL_CLASSIFIED` | Signal has been categorized |
| `SIGNAL_PROCESSED` | Signal processing complete |

### Decision Events

| Event | Description |
|-------|-------------|
| `DECISION_PROPOSAL_CREATED` | New decision proposed |
| `DECISION_PROPOSAL_UPDATED` | Decision proposal updated |
| `GOVERNANCE_REVIEW_REQUESTED` | Decision submitted for review |

### Debate Events

| Event | Description |
|-------|-------------|
| `DEBATE_STARTED` | Debate session initiated |
| `DEBATE_ROUND_COMPLETED` | Debate round finished |
| `DEBATE_COMPLETED` | Debate session completed |
| `CONSENSUS_CALCULATED` | Consensus reached |

### Governance Events

| Event | Description |
|-------|-------------|
| `GOVERNANCE_REVIEW_REQUESTED` | Review requested |
| `DECISION_APPROVED` | Decision approved |
| `DECISION_REJECTED` | Decision rejected |

### Execution Events

| Event | Description |
|-------|-------------|
| `EXECUTION_REQUESTED` | Execution requested |
| `EXECUTION_STARTED` | Execution started |
| `EXECUTION_COMPLETED` | Execution completed successfully |
| `EXECUTION_FAILED` | Execution failed |
| `EXECUTION_CANCELLED` | Execution cancelled |

### Learning Events

| Event | Description |
|-------|-------------|
| `OUTCOME_EVALUATED` | Outcome recorded |
| `LESSON_EXTRACTED` | Lesson learned |
| `PATTERN_DETECTED` | Pattern identified |
| `DOCTRINE_UPDATED` | Strategic doctrine updated |

### System Events

| Event | Description |
|-------|-------------|
| `WORKFLOW_STARTED` | Workflow started |
| `WORKFLOW_COMPLETED` | Workflow completed |
| `WORKFLOW_FAILED` | Workflow failed |
| `WORKFLOW_STATE_CHANGED` | Workflow state changed |

## Event Structure

Events follow a consistent structure:

```python
class DomainEvent:
    def __init__(
        self,
        event_type: str,           # Event type identifier
        payload: Dict[str, Any],   # Event data
        source_module: str,         # Originating module
        correlation_id: UUID = None, # Links related events
        workflow_id: UUID = None,   # Associated workflow
    ):
        self.event_id = uuid.uuid4()
        self.event_type = event_type
        self.timestamp = datetime.utcnow()
        self.source_module = source_module
        self.payload = payload
        self.correlation_id = correlation_id
        self.workflow_id = workflow_id
```

### Event Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | UUID | Unique event identifier |
| `event_type` | str | Event type (e.g., `DECISION_APPROVED`) |
| `timestamp` | datetime | When the event occurred |
| `source_module` | str | Module that created the event |
| `payload` | dict | Event-specific data |
| `correlation_id` | UUID | Links related events |
| `workflow_id` | UUID | Associated workflow |

## Publishing Events

### Basic Event Publishing

```python
from app.orchestration.event_bus import get_event_bus
from app.orchestration.event_types import DomainEvent, EventType

event_bus = get_event_bus(session)

event = DomainEvent(
    event_type=EventType.DECISION_APPROVED,
    payload={"decision_id": "123", "approved_by": "governance"},
    source_module="governance",
    correlation_id=correlation_id,
    workflow_id=workflow_id
)

await event_bus.publish_event(event)
```

### Using Event Factory Functions

```python
from app.orchestration.event_types import (
    create_decision_approved_event,
    create_execution_completed_event,
)

# Create decision approved event
event = create_decision_approved_event(
    decision_id=uuid.UUID("..."),
    approved_by="governance"
)

# Create execution completed event
event = create_execution_completed_event(
    execution_id=uuid.UUID("..."),
    result={"status": "success"}
)
```

## Subscribing to Events

### Synchronous Handler

```python
def handle_decision_approved(event: DomainEvent):
    """Handle decision approved events."""
    print(f"Decision {event.payload['decision_id']} approved!")
    # Process the event

event_bus.subscribe(EventType.DECISION_APPROVED, handle_decision_approved)
```

### Asynchronous Handler

```python
async def handle_execution_completed(event: DomainEvent):
    """Handle execution completed events."""
    execution_id = event.payload["execution_id"]
    result = event.payload["result"]
    
    # Update database, send notification, etc.
    await update_execution_record(execution_id, result)

event_bus.subscribe_async(EventType.EXECUTION_COMPLETED, handle_execution_completed)
```

### Wildcard Subscription

```python
def handle_all_events(event: DomainEvent):
    """Log all events."""
    print(f"Event: {event.event_type}")

event_bus.subscribe("*", handle_all_events)
```

## Event Persistence

Events are automatically persisted to the database:

```python
await event_bus.publish_event(event, persist=True)
```

To publish without persistence (e.g., for internal events):

```python
await event_bus.publish_event(event, persist=False)
```

## Event Store API

### List Events

```bash
curl http://localhost:8000/orchestration/events
```

### Filter by Type

```bash
curl "http://localhost:8000/orchestration/events?event_type=DECISION_APPROVED"
```

### Get Event Details

```bash
curl http://localhost:8000/orchestration/events/{event_id}
```

## Correlation and Tracing

### Using Correlation IDs

Events can be linked through correlation IDs:

```python
# Create initial event with correlation ID
correlation_id = uuid.uuid4()

event1 = DomainEvent(
    event_type=EventType.DECISION_PROPOSAL_CREATED,
    payload={...},
    correlation_id=correlation_id
)

event2 = DomainEvent(
    event_type=EventType.DEBATE_STARTED,
    payload={...},
    correlation_id=correlation_id  # Same ID links the events
)
```

### Tracing Events

Use the trace endpoint to see all events for a correlation ID:

```bash
curl http://localhost:8000/observability/traces/{correlation_id}
```

This returns the workflow and all related events.

## Event Handler Best Practices

### Idempotency

Handlers should be idempotent to support retries:

```python
async def handle_event(event):
    # Check if already processed
    processed = await check_event_processed(event.event_id)
    if processed:
        return
    
    # Process event
    await process_event(event)
    
    # Mark as processed
    await mark_event_processed(event.event_id)
```

### Error Handling

Handle errors gracefully:

```python
async def handle_event(event):
    try:
        await process_event(event)
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # Don't re-raise - let the event bus handle errors
```

### Validation

Validate event payload before processing:

```python
def handle_decision_approved(event):
    required_fields = ["decision_id", "approved_by"]
    
    for field in required_fields:
        if field not in event.payload:
            raise ValueError(f"Missing required field: {field}")
    
    # Process validated event
    ...
```

## Event Handler Pattern

A typical event handler pattern:

```python
async def handle_decision_approved(event: DomainEvent):
    """
    Handle decision approval events.
    
    This handler:
    1. Validates the event payload
    2. Checks for duplicates (idempotency)
    3. Updates the database
    4. Publishes follow-up events
    """
    # 1. Validate
    decision_id = event.payload.get("decision_id")
    if not decision_id:
        return
    
    # 2. Check idempotency
    existing = await get_approval_record(decision_id)
    if existing:
        logger.info(f"Decision {decision_id} already approved, skipping")
        return
    
    # 3. Update database
    await approve_decision(decision_id, event.payload)
    
    # 4. Publish follow-up event
    await event_bus.publish_event(
        create_execution_requested_event(decision_id, {...})
    )
```
