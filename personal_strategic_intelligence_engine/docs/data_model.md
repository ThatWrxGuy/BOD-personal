# Data Model

## Overview

The Personal Strategic Intelligence Engine uses a relational database (PostgreSQL) for persistent storage. All models are defined using SQLAlchemy ORM with async support.

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   UserProfile   │       │AgentDefinition  │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ mission_statement│      │ name            │
│ values          │       │ role            │
│ priorities      │       │ constitution    │
│ non_negotiables│       │ version_id      │
│ active_goals    │       │ active          │
│ constraints     │       └────────┬────────┘
│ risk_tolerance  │                │
└────────┬────────┘                │
         │                         │
         │              ┌──────────┴──────────┐
         │              │                     │
         │         ┌────┴─────┐         ┌────┴──────┐
         │         │AgentResponse         │CritiqueResponse│
         │         ├────────────┐         ├─────────────┤
         │         │ meeting_id │         │ meeting_id  │
         │         │ agent_id   │         │ source_agent│
         │         │ summary    │         │ target_agent│
         │         │ recommend  │         │ critique    │
         │         │ reasons    │         │ severity    │
         │         │ risks      │         └─────────────┘
         │         │ tradeoffs  │
         │         │ confidence │
         │         └─────┬──────┘
         │               │
         └───────────────┼────────────────────┐
                        │                    │
                   ┌────┴────────┐      ┌────┴──────┐
                   │BoardMeeting │      │DecisionRecord│
                   ├─────────────┤      ├─────────────┤
                   │ id          │      │ id          │
                   │ type        │      │ meeting_id  │
                   │ trigger     │      │ decision    │
                   │ question    │      │ action      │
                   │ context     │      │ rationale   │
                   │ summary     │      │ status      │
                   │ recommendation              │ review_due │
                   │ confidence│      └──────┬──────┘
                   │ status     │             │
                   └─────────────┘        ┌────┴──────┐
                                         │OutcomeReview│
                                         ├────────────┤
                                         │ decision_id │
                                         │ result     │
                                         │ score      │
                                         │ notes      │
                                         │ reviewed_at│
                                         └────────────┘
```

## Models

### UserProfile

Stores the user's personal constitution and strategic context.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| mission_statement | String | User's personal mission |
| values | JSON | List of core values |
| priorities | JSON | Current priorities |
| non_negotiables | JSON | Hard boundaries |
| active_goals | JSON | Current goals |
| constraints | JSON (nullable) | Current constraints |
| risk_tolerance | String | Risk tolerance level |
| name | String (nullable) | User's name |
| email | String (nullable) | User's email |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### AgentDefinition

Defines each board agent with its constitution.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String | Agent name (unique) |
| role | String | Agent role title |
| constitution_text | Text | Agent's system prompt |
| version_id | String | Constitution version |
| active | Boolean | Whether agent is active |
| description | Text (nullable) | Agent description |
| mandate | Text (nullable) | Agent mandate |
| focus_areas | JSON (nullable) | Agent focus areas |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### BoardMeeting

Represents a strategic board meeting session.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| meeting_type | String | strategic/weekly/monthly |
| trigger_type | String | manual/scheduled |
| question | Text | Strategic question |
| context_snapshot | Text (nullable) | Context for the meeting |
| executive_summary | Text (nullable) | Board summary |
| consensus_recommendation | Text (nullable) | Final recommendation |
| alternatives | JSON (nullable) | Alternative options |
| risks | JSON (nullable) | Identified risks |
| tradeoffs | JSON (nullable) | Tradeoffs |
| confidence_score | Float (nullable) | 0-10 confidence |
| data_gaps | JSON (nullable) | Missing information |
| status | String | pending/running/completed/failed |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### AgentResponse

Response from a single agent during a meeting.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| meeting_id | Integer | Foreign key to BoardMeeting |
| agent_id | Integer | Foreign key to AgentDefinition |
| summary_judgment | Text | Agent's summary |
| main_recommendation | Text | Primary recommendation |
| supporting_reasons | JSON | List of reasons |
| main_risks | JSON | List of risks |
| tradeoffs | JSON | List of tradeoffs |
| requested_followups | JSON (nullable) | Questions for follow-up |
| confidence_score | Float (nullable) | Agent's confidence |
| version_id | String | Agent version used |
| raw_output | Text (nullable) | Full raw output |
| created_at | DateTime | Creation timestamp |

### CritiqueResponse

Critique from one agent targeting another's recommendation.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| meeting_id | Integer | Foreign key to BoardMeeting |
| source_agent_id | Integer | Critic agent |
| target_agent_id | Integer | Agent being critiqued |
| critique_text | Text | Critique content |
| severity | String | low/medium/high/critical |
| created_at | DateTime | Creation timestamp |

### DecisionRecord

User's decision following a board recommendation.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| meeting_id | Integer (nullable) | Related meeting |
| decision_summary | Text | Summary of decision |
| chosen_action | Text | What was done |
| rationale | Text (nullable) | User's reasoning |
| status | String | pending/decided/reviewed |
| review_due_at | DateTime (nullable) | When to review |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### OutcomeReview

Review of a decision's outcome.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| decision_id | Integer | Foreign key to DecisionRecord |
| actual_result | Text | What actually happened |
| success_score | Float (nullable) | 0-10 success rating |
| notes | Text (nullable) | Additional notes |
| reviewed_at | DateTime (nullable) | Review timestamp |
| created_at | DateTime | Creation timestamp |

### StrategicInsight

Insight extracted from meetings or reviews.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| category | String | insight category |
| insight_text | Text | The insight |
| supporting_evidence | JSON (nullable) | Evidence |
| confidence_score | Float (nullable) | Confidence |
| meeting_id | Integer (nullable) | Source meeting |
| created_at | DateTime | Creation timestamp |

### AgentPerformance

Performance metrics for agent versions.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| agent_id | Integer | Foreign key to AgentDefinition |
| version_id | String | Agent version |
| accuracy_score | Float (nullable) | Accuracy rating |
| usefulness_score | Float (nullable) | Usefulness rating |
| calibration_score | Float (nullable) | Calibration rating |
| false_positive_rate | Float (nullable) | FP rate |
| false_negative_rate | Float (nullable) | FN rate |
| notes | Text (nullable) | Additional notes |
| created_at | DateTime | Creation timestamp |

## Relationships

- BoardMeeting has many AgentResponses (one-to-many)
- BoardMeeting has many CritiqueResponses (one-to-many)
- BoardMeeting has many DecisionRecords (one-to-many)
- DecisionRecord has many OutcomeReviews (one-to-many)
- AgentResponse belongs to AgentDefinition (many-to-one)
- CritiqueResponse belongs to source and target AgentDefinition (many-to-one)
