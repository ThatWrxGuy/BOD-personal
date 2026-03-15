# Phase 2 Agent Layer - Canonical Structure

**Date:** 2026-03-14  
**Directive:** V37-REC-002

---

## Executive Summary

This document defines the canonical structure of the Phase 2 Agent Layer. All future development should reference these canonical paths and naming conventions.

---

## Canonical File Inventory

### Base Abstractions

| File | Purpose | Status |
|------|---------|--------|
| `app/agents/base_agent.py` | Primary base agent abstract class with LLM integration | ✅ CANONICAL |
| `app/agents/base.py` | Additional base utilities | ✅ AUXILIARY |

### Registry Components

| File | Purpose | Status |
|------|---------|--------|
| `app/agents/registry.py` | AgentRegistry for managing and retrieving agents | ✅ CANONICAL |

### Domain Agents

| File | Agent | Status |
|------|-------|--------|
| `app/agents/domain/strategy_agent.py` | Strategy Agent | ✅ CANONICAL |
| `app/agents/domain/finance_agent.py` | Finance Agent | ✅ CANONICAL |
| `app/agents/domain/risk_agent.py` | Risk Agent | ✅ CANONICAL |
| `app/agents/domain/health_agent.py` | Health Agent | ✅ CANONICAL |
| `app/agents/domain/operations_agent.py` | Operations Agent | ✅ CANONICAL |
| `app/agents/domain/legacy_agent.py` | Legacy Agent | ✅ CANONICAL |

### Executive Layer

| File | Purpose | Status |
|------|---------|--------|
| `app/agents/executive/agent_council.py` | Multi-agent debate coordination | ✅ CANONICAL |
| `app/agents/executive/base_agent.py` | Executive agent base | ✅ CANONICAL |
| `app/agents/executive/ceo_agent.py` | CEO Agent | ✅ CANONICAL |
| `app/agents/executive/cfo_agent.py` | CFO Agent | ✅ CANONICAL |
| `app/agents/executive/cro_agent.py` | CRO Agent | ✅ CANONICAL |
| `app/agents/executive/cpo_agent.py` | CPO Agent | ✅ CANONICAL |
| `app/agents/executive/coo_agent.py` | COO Agent | ✅ CANONICAL |
| `app/agents/executive/cko_agent.py` | CKO Agent | ✅ CANONICAL |
| `app/agents/executive/cso_agent.py` | CSO Agent | ✅ CANONICAL |
| `app/agents/executive/agent_models.py` | Executive data models | ✅ CANONICAL |
| `app/agents/executive/agent_types.py` | Agent type definitions | ✅ CANONICAL |
| `app/agents/executive/debate_engine.py` | Debate coordination engine | ✅ CANONICAL |

### Toolkit System

| File | Purpose | Status |
|------|---------|--------|
| `app/agents/toolkits/registry.py` | Toolkit registry | ✅ CANONICAL |
| `app/agents/toolkits/resolver.py` | Toolkit resolver for agent tool injection | ✅ CANONICAL |
| `app/agents/toolkits/base.py` | Base toolkit class | ✅ CANONICAL |
| `app/agents/toolkits/agent_profile.py` | Agent profile management | ✅ CANONICAL |
| `app/agents/toolkits/finance.py` | Finance toolkit | ✅ CANONICAL |
| `app/agents/toolkits/health.py` | Health toolkit | ✅ CANONICAL |
| `app/agents/toolkits/operations.py` | Operations toolkit | ✅ CANONICAL |
| `app/agents/toolkits/fitness.py` | Fitness toolkit | ✅ CANONICAL |
| `app/agents/toolkits/federated.py` | Federated retrieval toolkit | ✅ CANONICAL |

---

## Naming Conventions

### File Naming
- All agent files use **lowercase snake_case**
- Base files: `base_agent.py`, `base.py`
- Registry: `registry.py`
- Domain agents: `*_agent.py`
- Toolkits: `*.py`

### Class Naming
- Agent classes: `PascalCase` ending with `Agent` (e.g., `StrategyAgent`)
- Registry: `PascalCase` ending with `Registry` (e.g., `AgentRegistry`)
- Toolkit: `PascalCase` ending with `Toolkit` (e.g., `FinanceToolkit`)

### Import Conventions
```python
# Correct imports
from app.agents.base_agent import BaseAgent
from app.agents.registry import AgentRegistry
from app.agents.domain.strategy_agent import StrategyAgent

# Avoid these patterns (non-canonical)
from app.agents.agent_base import BaseAgent  # ❌
from app.agents.agent_registry import AgentRegistry  # ❌
from app.agents.agent_context import AgentContext  # ❌
from app.agents.agent_router import AgentRouter  # ❌
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                 Domain Agents                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Strategy │ │ Finance │ │  Risk   │ │Health   │  │
│  │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Base Abstraction                       │
│              base_agent.py                          │
│         (BaseAgent abstract class)                  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 Agent Registry                      │
│              registry.py                            │
│         (AgentRegistry class)                        │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│               Toolkit System                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Registry │ │Resolver │ │ Profile │ │BaseToolk│  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Integration Points

### With Core Services
- LLM client: `app.services.llm_client`
- Database models: `app.models.agent_definition`
- Logging: `app.core.logging`

### With Executive Layer
- Debate engine: `app.agents.executive.debate_engine`
- Agent council: `app.agents.executive.agent_council`

### With Governance
- Access policy: `app.data_platform.governance.access_policy`

---

## Obsolete References (Do Not Use)

The following paths are **NOT canonical** and should not be referenced:

| Obsolete Path | Canonical Alternative |
|--------------|---------------------|
| `app/agents/agent_base.py` | `app/agents/base_agent.py` |
| `app/agents/agent_registry.py` | `app/agents/registry.py` |
| `app/agents/agent_context.py` | N/A (not implemented) |
| `app/agents/agent_router.py` | N/A (use resolver) |

---

## Verification

Run the architecture guard to verify agent layer integrity:

```bash
python scripts/architecture_guard.py --check-agents
```

---

## Maintenance

This document should be updated whenever:
- New canonical agent files are added
- Agent architecture is modified
- New integration points are established

**Last Updated:** 2026-03-14
