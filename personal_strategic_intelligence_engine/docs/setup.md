# Setup Guide

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or use SQLite for development)
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd personal_strategic_intelligence_engine
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Application
APP_NAME="Personal Strategic Intelligence Engine"
DEBUG=false

# Database - Use SQLite for local development
DATABASE_URL="sqlite+aiosqlite:///./strategic_board.db"
DATABASE_URL_SYNC="sqlite:///./strategic_board.db"

# LLM Provider
LLM_PROVIDER="openai"  # or "anthropic" or "mock"
OPENAI_API_KEY="your-openai-api-key-here"

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="text"
```

### 5. Database Setup

For SQLite (development):

```bash
# The database will be created automatically on first run
```

For PostgreSQL:

```bash
# Create the database
createdb strategic_board

# Run migrations (if using Alembic)
alembic upgrade head
```

### 6. Initialize the Database

```bash
python -m app.db.init_db
```

This will:
- Create all database tables
- Seed the six board agents with their constitutions

### 7. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

API documentation (Swagger UI) is at http://localhost:8000/docs

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest --cov=app tests/
```

## Development

### Project Structure

```
personal_strategic_intelligence_engine/
├── app/
│   ├── api/          # FastAPI routes
│   ├── core/         # Business logic
│   ├── agents/       # Board agents
│   ├── memory/       # Storage layer
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # External services
│   └── db/          # Database setup
├── tests/            # Test suite
├── docs/            # Documentation
└── requirements.txt
```

### Adding a New Agent

1. Create a new file in `app/agents/` (e.g., `new_agent.py`)
2. Inherit from `BaseAgent`
3. Implement required properties and `analyze()` method
4. Register in `app/agents/registry.py`

### Using Mock LLM

For development without API keys:

```env
LLM_PROVIDER="mock"
```

This will use the `MockLLMClient` which returns predefined responses.

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify credentials are correct

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### LLM API Errors

- Verify API key is correct in .env
- Check API key has sufficient credits
- Try using mock provider for testing

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill <PID>
```

## Next Steps

After setup:

1. Create a user profile via API
2. Create and run a test board meeting
3. Explore the API documentation at /docs
4. Review the agent constitutions
5. Set up scheduled reviews (optional)
