# Meeting Workflow

## Overview

The board meeting workflow is the core operational process of the Personal Strategic Intelligence Engine. It structures how strategic questions are analyzed, debated, and resolved through multi-agent deliberation.

## Meeting Types

### Strategic Meeting
- **Trigger**: Manual request
- **Purpose**: Address specific strategic questions
- **Typical Duration**: Minutes (depending on LLM response time)

### Weekly Review
- **Trigger**: Scheduled (configurable)
- **Purpose**: Regular progress check and priority adjustment
- **Frequency**: Weekly (typically Monday morning)

### Monthly Review
- **Trigger**: Scheduled (configurable)
- **Purpose**: Comprehensive monthly strategic assessment
- **Frequency**: Monthly (typically 1st of month)

## Workflow Phases

### Phase 1: Trigger

The meeting begins through one of:

1. **Manual API Request**: User creates a meeting via API
2. **Scheduled Weekly**: APScheduler triggers weekly review job
3. **Scheduled Monthly**: APScheduler triggers monthly review job

### Phase 2: Context Assembly

The orchestrator gathers context for the meeting:

1. **User Profile**:
   - Mission statement
   - Core values
   - Current priorities
   - Non-negotiables
   - Active goals
   - Risk tolerance

2. **Recent Meetings**:
   - Last 5 strategic meetings
   - Related meetings by keyword

3. **Recent Decisions**:
   - Last 5 decisions
   - Pending reviews

4. **Context Snapshot**: A text summary is stored with the meeting for audit

### Phase 3: Independent Analysis

Each of the six agents independently analyzes the question:

1. **Strategy Agent** provides strategic positioning advice
2. **Finance Agent** evaluates financial implications
3. **Risk Agent** identifies potential failures
4. **Health Agent** assesses sustainability
5. **Operations Agent** evaluates implementation feasibility
6. **Legacy Agent** checks values alignment

**Critical**: Agents do NOT see each other's initial responses during this phase. This ensures independent thinking.

Each agent returns a structured response:
```json
{
  "summary_judgment": "...",
  "main_recommendation": "...",
  "supporting_reasons": [...],
  "main_risks": [...],
  "tradeoffs": [...],
  "requested_followups": [...],
  "confidence_score": 0-10
}
```

### Phase 4: Critique Round

After all initial analyses are complete, agents critique each other's recommendations:

| Critic | Target |
|--------|--------|
| Finance | Strategy |
| Risk | Strategy, Finance |
| Health | Strategy, Operations |
| Legacy | Strategy, Finance |
| Operations | Strategy |

Critiques are structured as:
```json
{
  "critique_text": "...",
  "severity": "low|medium|high|critical"
}
```

### Phase 5: Synthesis

The synthesis engine combines all inputs into a final recommendation:

1. **Identifies agreement clusters** - Where agents align
2. **Identifies disagreement clusters** - Where perspectives differ
3. **Preserves minority warnings** - Strong objections are escalated
4. **Generates primary recommendation** - One clear recommendation
5. **Provides alternatives** - When certainty is low
6. **Assigns confidence score** - Based on evidence quality and conflict

Output includes:
```json
{
  "executive_summary": "...",
  "consensus_recommendation": "...",
  "alternatives": [...],
  "major_supporting_reasons": [...],
  "major_risks": [...],
  "tradeoffs": [...],
  "disagreement_summary": "...",
  "confidence_score": 0-10,
  "next_suggested_actions": [...],
  "data_gaps": [...]
}
```

### Phase 6: Persistence

All meeting artifacts are stored:

- Meeting record with question and status
- All agent responses with full reasoning
- All critiques
- Synthesis results
- Context snapshot

### Phase 7: Decision Linkage

The meeting creates a decision placeholder that the user can later populate with:
- What decision they actually made
- Their rationale
- Expected review date

## Meeting States

A meeting progresses through these states:

1. `pending` - Created, not yet run
2. `running` - Analysis in progress
3. `completed` - Successfully completed
4. `failed` - Error occurred

## API Workflow

### Complete Meeting Flow

```bash
# 1. Create meeting
POST /board/meetings
{ "question": "Should I take this job?" }

# 2. Run meeting (triggers analysis)
POST /board/meetings/1/run

# 3. Get results
GET /board/meetings/1

# 4. Log decision
POST /decisions
{ "meeting_id": 1, "decision_summary": "..." }

# 5. Later: Review outcome
POST /reviews
{ "decision_id": 1, "actual_result": "..." }
```

## Synthesis Rules

The synthesis engine MUST:

- ✅ Identify agreement clusters
- ✅ Identify disagreement clusters
- ✅ Preserve strong minority warnings
- ✅ Escalate serious risk objections
- ✅ Generate one primary recommendation
- ✅ Provide alternatives when certainty is low
- ✅ Identify missing data
- ✅ Assign confidence based on evidence quality

The synthesis engine MUST NOT:

- ❌ Invent fake consensus
- ❌ Suppress meaningful disagreement
- ❌ Present unjustified certainty
- ❌ Discard strong risk objections for convenience
