# PSIE Architecture

This document describes the overall architecture of the Personal Strategic Intelligence Engine (PSIE).

## Overview

PSIE is a multi-agent strategic board system that helps individuals make better long-term decisions through AI-powered analysis, debate, governance, and execution.

## System Layers

### Frontend Command Center
- Web-based UI for user interaction
- Dashboard for monitoring system state
- Workflow visualization
- Metrics and alerts display

### API Layer (FastAPI)
- RESTful API endpoints
- Authentication middleware
- Request validation
- Response formatting

### Security Layer
- **Identity & RBAC**: User authentication and role-based access control
- **Secrets & Connectors**: Credential management and integration security

### Observability Layer
- Metrics collection and aggregation
- Health monitoring
- Alert management
- Trace correlation

### Workflow Orchestration Layer
- Event bus for asynchronous messaging
- Workflow state machines
- Workflow engine for multi-step processes

### Core Services Layer
- **Strategic Kernel**: Decision-making core with priority, policy, and utility engines
- **Execution Engine**: Safe action execution with validation
- **Learning Layer**: Strategic memory and pattern recognition

### Data Layer
- PostgreSQL database
- SQLAlchemy ORM
- Event and workflow persistence

## Module Structure

```
app/
├── api/                    # API route handlers
│   ├── profile.py
│   ├── board.py
│   ├── decisions.py
│   ├── reviews.py
│   ├── health.py
│   ├── signals.py
│   ├── governance.py
│   ├── intelligence.py
│   ├── simulation.py
│   ├── execution.py
│   ├── debate.py
│   ├── learning.py
│   ├── kernel.py
│   ├── orchestration.py
│   ├── identity.py
│   ├── security.py
│   └── observability.py
│
├── core/                  # Core utilities
│   ├── config.py
│   ├── config_validation.py
│   ├── config_check.py
│   └── logging.py
│
├── identity/              # Authentication & RBAC
│   ├── auth_service.py
│   ├── auth_middleware.py
│   ├── token_service.py
│   └── rbac_engine.py
│
├── security/             # Secrets & Connectors
│   ├── secret_manager.py
│   ├── connector_policy.py
│   └── credential_redactor.py
│
├── orchestration/        # Workflow & Events
│   ├── event_types.py
│   ├── event_bus.py
│   ├── workflow_engine.py
│   └── workflow_state_machine.py
│
├── signals/             # Signal ingestion
├── intelligence/        # Analysis & forecasting
├── debate/             # Multi-agent debate
├── governance/         # Approval workflows
├── execution/          # Action execution
├── learning/           # Strategic memory
├── kernel/             # Strategic kernel
├── memory/             # Data persistence
├── models/             # Database models
├── db/                 # Database setup
└── observability/       # Metrics & health
```

## Data Flow

### Strategic Decision Flow

1. **Signal Detection**: System detects or receives a strategic signal
2. **Intelligence Analysis**: AI agents analyze the signal
3. **Debate**: Multiple agents debate the decision
4. **Governance**: Approval workflow validates the decision
5. **Execution**: Approved actions are executed safely
6. **Learning**: Outcomes are recorded and patterns learned

### Event-Driven Architecture

All major system activities publish events:

```
Signal Created
    ↓
Event: SIGNAL_CREATED
    ↓
Intelligence consumes event
    ↓
Event: DECISION_PROPOSAL_CREATED
    ↓
Debate Engine consumes event
    ↓
Event: DEBATE_COMPLETED
    ↓
Governance reviews
    ↓
Event: DECISION_APPROVED / DECISION_REJECTED
    ↓
Execution Engine consumes (if approved)
    ↓
Event: EXECUTION_COMPLETED
    ↓
Learning Layer records outcome
```

## Security Model

### Authentication
- JWT-based token authentication
- Token expiration and refresh
- Secure password hashing (bcrypt)

### Authorization
- Role-based access control (RBAC)
- Permission domains: system, signals, debate, governance, execution, learning, connectors, administration
- Predefined roles: Owner, Administrator, Operator, Viewer, Auditor

### Connector Security
- All connectors disabled by default
- Risk levels: low, medium, high, critical
- Secret validation before enablement
- Full audit logging

## Observability

### Health Monitoring
- Application health
- Database connectivity
- Event bus status
- Workflow engine status
- Connector readiness
- LLM provider configuration
- Security configuration

### Metrics
- Workflow metrics (started, completed, failed)
- Execution metrics (requested, approved, completed)
- Connector metrics (enabled, errors, access)
- Security metrics (login attempts, failures)
- API metrics (requests, latency, errors)

### Alerts
- Workflow failures
- Connector degradation
- Security alerts
- Execution failures

## Configuration

### Environment Variables

Required:
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: PostgreSQL connection URL

Optional:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `ENABLE_AUTH`: Enable authentication (default: false)
- `APP_ENV`: Environment (development, production)

### Safety Defaults

- Execution disabled by default
- Manual approval required
- Kill switch enabled
- All connectors disabled
- Auth disabled for development

## Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Auth | Disabled | Required |
| CORS | Permissive | Strict |
| Secret Key | Warning | Fail if default |
| Connectors | Warnings | Must validate |
| Execution | Disabled | Disabled + approval |
