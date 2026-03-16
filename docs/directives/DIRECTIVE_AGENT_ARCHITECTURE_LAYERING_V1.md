# DIRECTIVE: Agent Architecture Layering & Dependency Governance

**Directive ID**: DIR-ARCH-002

**Applies To**: Personal Strategic Intelligence Engine

**Repository**: BOD-personal

**Status**: Active

**Priority**: Critical

---

## 1. Purpose

This directive establishes mandatory architectural layering rules for the Personal Strategic Intelligence Engine.

The system is designed as a multi-agent strategic reasoning platform composed of autonomous decision agents operating within structured governance workflows.

Without enforced dependency boundaries, the architecture risks:
- Uncontrolled coupling
- Circular dependencies
- Agent logic leaking into infrastructure
- Fragile orchestration pipelines

This directive ensures that agent cognition, orchestration logic, infrastructure, and data layers remain strictly separated.

---

## 2. Architectural Model

The system SHALL follow a layered architecture.

```
API Layer
     ↓
Workflow Layer
     ↓
Agent Layer
     ↓
Service Layer
     ↓
Infrastructure Layer
     ↓
Data Layer
```

Each layer has strict dependency permissions.

---

## 3. Layer Definitions

---

### 3.1 API Layer

**Location**: `app/api`

**Responsibilities**:
- HTTP endpoints
- Request validation
- Response formatting
- Authentication
- User interaction

The API layer is the external boundary of the system.

---

**API Layer MAY depend on**:
- Workflows
- Schemas
- Domain models

**API Layer MUST NOT depend on**:
- Agents directly
- Infrastructure
- Database models

---

### 3.2 Workflow Layer

**Location**: `app/workflows`

**Responsibilities**:
- Board meeting orchestration
- Strategic planning pipelines
- Simulation flows
- Decision pipelines

The workflow layer coordinates agents.

---

**Workflow Layer MAY depend on**:
- Agents
- Domain
- Schemas

**Workflow Layer MUST NOT depend on**:
- Infrastructure
- Database engines
- Connectors

Workflows must remain pure orchestration logic.

---

### 3.3 Agent Layer

**Location**: `app/agents`

**Responsibilities**:
- Decision reasoning
- Strategic analysis
- Advisory output
- Simulated board member behavior

Agents represent cognitive units of reasoning.

---

**Agents MAY depend on**:
- Services
- Domain models
- Schemas

**Agents MUST NOT depend on**:
- API modules
- Workflow modules
- Database engines
- Infrastructure systems

Agents must remain stateless reasoning units wherever possible.

---

### 3.4 Service Layer

**Location**: `app/services`

**Responsibilities**:
- LLM interaction
- External API integrations
- Forecasting engines
- Simulation engines

Services provide capabilities used by agents.

---

**Services MAY depend on**:
- Infrastructure
- Domain models

**Services MUST NOT depend on**:
- Agents
- Workflows
- API modules

This ensures services remain reusable capabilities.

---

### 3.5 Infrastructure Layer

**Location**: `app/infra`

**Responsibilities**:
- Configuration
- Logging
- Task scheduling
- Caching
- Background workers
- System utilities

Infrastructure supports the runtime environment.

---

**Infrastructure MAY depend on**:
- Data layer
- Platform libraries

**Infrastructure MUST NOT depend on**:
- Agents
- Workflows
- Services
- Domain logic

Infrastructure must remain agnostic of system intelligence.

---

### 3.6 Data Layer

**Location**: `app/db`

**Responsibilities**:
- Persistence models
- Database connections
- Migrations
- Repositories

The data layer handles state storage only.

---

**Data Layer MUST NOT depend on**:

ANY higher-level modules.

This layer must remain purely infrastructural.

---

## 4. Dependency Rules

The following dependencies are **allowed**:

```
API → Workflows
Workflows → Agents
Agents → Services
Services → Infrastructure
Infrastructure → Data
```

The following dependencies are **forbidden**:

```
Agents → API
Agents → Workflows
Workflows → Infrastructure
Services → Agents
Infrastructure → Agents
Infrastructure → Workflows
```

---

## 5. Agent Isolation Rules

Agents must behave as isolated reasoning units.

**Agents SHALL NOT**:
- Directly query the database
- Execute system commands
- Interact with external APIs directly
- Control infrastructure components

Agents interact with the world only through services.

---

## 6. Workflow Authority Model

Workflows represent governance processes.

**Examples**:
- Board meeting simulation
- Strategic planning cycles
- Executive decision pipelines
- Scenario analysis

Workflows coordinate agents but do not perform reasoning themselves.

---

## 7. LLM Interaction Policy

All LLM calls MUST occur through the service layer.

**Agents must never directly call**:
- OpenAI
- Anthropic
- Local model runtimes

**Instead they call**:

`LLMService`

This ensures:
- Centralized cost tracking
- Prompt governance
- Model fallback logic
- Observability

---

## 8. Database Access Policy

Direct database access is restricted.

Only the following layers may access persistence:

- Infrastructure
- Services (via repositories)

**Agents and workflows MUST NOT directly access**:
- SQLAlchemy
- SQLModel
- Database sessions

---

## 9. Enforcement Mechanisms

The repository SHALL enforce architecture rules via:

### Static Dependency Checks

Automated scripts must detect forbidden imports.

**Example**: `app/agents` importing `app/api`

This must fail CI.

---

### Continuous Integration

CI pipelines SHALL enforce:
- Dependency direction
- Import cycle detection
- Linting
- Tests

---

### Code Review

Pull requests must be rejected if they violate:
- Dependency rules
- Layer boundaries
- Agent isolation requirements

---

## 10. Architectural Benefits

This directive ensures:

### Cognitive Isolation

Agents remain reasoning units rather than infrastructure actors.

### Testability

Agents can be tested without database or API dependencies.

### Scalability

Infrastructure and services can evolve without breaking agent logic.

### Observability

All external interactions occur through controlled service boundaries.

---

## 11. Example Execution Flow

Example request flow:

```
API
  ↓
Workflow
  ↓
Agent (Strategy Advisor)
  ↓
Service (LLM + Forecast Engine)
  ↓
Infrastructure (logging + config)
  ↓
Database (store decision output)
```

---

## 12. Future Extensions

Future architecture components may include:
- Agent marketplace
- Governance policy engine
- Simulation clusters
- Strategic memory graph

All extensions MUST comply with the layering model defined here.

---

## 13. Compliance

All new modules MUST conform to this directive.

Violations SHALL require architectural review before merge.

---

## End of Directive
