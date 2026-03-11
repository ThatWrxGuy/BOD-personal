# =============================================================================
# Personal Strategic Intelligence Engine - Makefile
# =============================================================================

.PHONY: help install dev test lint docker-up docker-down config-check

# Default target
help:
	@echo "PSIE - Personal Strategic Intelligence Engine"
	@echo ""
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  dev           - Run development server"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linters"
	@echo "  docker-up     - Start Docker services (PostgreSQL, Redis)"
	@echo "  docker-down   - Stop Docker services"
	@echo "  config-check  - Check configuration readiness"
	@echo "  db-init       - Initialize database"
	@echo "  seed          - Seed database with agents"

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest

# Run linters
lint:
	ruff check app/

# Start Docker services
docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✅ PostgreSQL and Redis are running"

# Stop Docker services
docker-down:
	docker-compose down

# Check configuration
config-check:
	python scripts/check_config.py

# Initialize database
db-init:
	python -c "import asyncio; from app.db.init_db import init_db; asyncio.run(init_db())"

# Seed database
seed:
	python -c "import asyncio; from app.db.init_db import seed_agents; asyncio.run(seed_agents())"

# Full setup
setup: docker-up install config-check db-init seed
	@echo "✅ Full setup complete!"
