# Personal Strategic Intelligence Engine

A persistent, multi-agent, self-improving strategic board of directors system for personal decision-making.

## Overview

The Personal Strategic Intelligence Engine (PSIE) is a sophisticated system designed to help individuals make better long-term decisions by combining multiple specialized AI agents with persistent strategic memory. The system runs structured board meetings where agents provide independent analysis, critique each other's recommendations, and synthesize a final board recommendation.

## Architecture

### Core Components

- **Core Orchestrator**: Manages the board meeting workflow, dispatches tasks to agents, and handles synthesis
- **Six Core Board Agents**: Strategy, Finance, Risk, Health, Operations, and Legacy agents with distinct constitutions
- **Memory Layer**: Persistent storage for profiles, meetings, decisions, and strategic insights
- **Meeting Engine**: Workflow engine for running structured board meetings
- **Synthesis Engine**: Combines agent outputs and critiques into final recommendations
- **API Layer**: FastAPI backend for all operations

### Design Principles

1. **Human Authority**: The user is always the CEO and final decision authority
2. **Multi-Agent Reasoning**: Multiple specialized agents with distinct constitutions
3. **Persistence**: Durable memory and meeting history
4. **Explainability**: Every recommendation includes rationale, risks, tradeoffs, and confidence
5. **Auditability**: Prompt versions, agent outputs, and meeting records are traceable
6. **Controlled Improvement**: Versioned prompts with evaluation hooks for future promotion/rollback
7. **Modular Architecture**: Clean separation of concerns with separable modules

## Tech Stack

- **Language**: Python
- **Backend**: FastAPI
- **Database**: PostgreSQL (async with SQLAlchemy)
- **ORM**: SQLAlchemy / SQLModel
- **Migrations**: Alembic
- **Task Scheduling**: APScheduler
- **LLM Integration**: Modular provider abstraction (OpenAI, Anthropic)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd personal_strategic_intelligence_engine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment file:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```env
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/strategic_board"
OPENAI_API_KEY="your-openai-api-key"
# Or use Anthropic:
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

6. Initialize the database:
```bash
python -m app.db.init_db
```

7. Start the API server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

### Profile
- `POST /profile` - Create a user profile
- `GET /profile` - Get the user profile
- `PUT /profile/{profile_id}` - Update a profile

### Board Meetings
- `POST /board/meetings` - Create a new board meeting
- `GET /board/meetings` - List all meetings
- `GET /board/meetings/{meeting_id}` - Get a specific meeting
- `POST /board/meetings/{meeting_id}/run` - Run a meeting (trigger agent analysis)
- `PATCH /board/meetings/{meeting_id}` - Update meeting results

### Decisions
- `POST /decisions` - Log a decision
- `GET /decisions` - List decisions
- `GET /decisions/{decision_id}` - Get a specific decision
- `PATCH /decisions/{decision_id}` - Update a decision

### Outcome Reviews
- `POST /reviews` - Record an outcome review
- `GET /reviews` - List reviews
- `GET /reviews/{review_id}` - Get a specific review

### Health
- `GET /health` - Health check

## Example Usage

### Create a Profile

```bash
curl -X POST http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{
    "mission_statement": "To build a meaningful career while maintaining work-life balance",
    "values": ["integrity", "growth", "family"],
    "priorities": ["career", "health", "relationships"],
    "non_negotiables": ["never compromise ethics", "always be there for family"],
    "active_goals": ["get promoted", "run a marathon", "spend more time with family"],
    "risk_tolerance": "moderate"
  }'
```

### Run a Board Meeting

1. Create a meeting:
```bash
curl -X POST http://localhost:8000/board/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I take on this leadership opportunity?",
    "meeting_type": "strategic",
    "trigger_type": "manual"
  }'
```

2. Run the meeting (this triggers agent analysis):
```bash
curl -X POST http://localhost:8000/board/meetings/1/run
```

3. Get the results:
```bash
curl http://localhost:8000/board/meetings/1
```

### Log a Decision

```bash
curl -X POST http://localhost:8000/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": 1,
    "decision_summary": "Taking on the leadership role",
    "chosen_action": "Accept the promotion",
    "rationale": "Aligned with career goals and provides growth opportunities"
  }'
```

### Record an Outcome Review

```bash
curl -X POST http://localhost:8000/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": 1,
    "actual_result": "Successfully transitioned into leadership role",
    "success_score": 8.5,
    "notes": "Challenging but rewarding experience"
  }'
```

## Project Structure

```
personal_strategic_intelligence_engine/
├── app/
│   ├── api/              # API route handlers
│   │   ├── profile.py
│   │   ├── board.py
│   │   ├── decisions.py
│   │   ├── reviews.py
│   │   └── health.py
│   ├── core/             # Core business logic
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── orchestrator.py
│   │   ├── context_builder.py
│   │   ├── synthesis.py
│   │   ├── scheduler.py
│   │   └── audit.py
│   ├── agents/           # Board agents
│   │   ├── base_agent.py
│   │   ├── strategy_agent.py
│   │   ├── finance_agent.py
│   │   ├── risk_agent.py
│   │   ├── health_agent.py
│   │   ├── operations_agent.py
│   │   ├── legacy_agent.py
│   │   └── registry.py
│   ├── memory/           # Persistent storage
│   │   ├── profile_memory.py
│   │   ├── meeting_memory.py
│   │   └── decision_memory.py
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # External services
│   │   └── llm_client.py
│   ├── db/              # Database setup
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   └── main.py          # FastAPI application
├── tests/               # Test suite
├── docs/                # Documentation
└── requirements.txt      # Python dependencies
```

## Board Meeting Workflow

1. **Trigger**: Meeting is created manually or scheduled
2. **Context Assembly**: Orchestrator gathers user profile, recent meetings, and decisions
3. **Independent Analysis**: Each of the six agents provides independent analysis
4. **Critique Round**: Agents critique each other's recommendations
5. **Synthesis**: Final recommendation is generated combining all inputs
6. **Persistence**: All data is stored for future reference
7. **Decision**: User logs their actual decision
8. **Review**: User can later review the outcome

## License

MIT
