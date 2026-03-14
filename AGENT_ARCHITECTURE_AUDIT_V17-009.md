# Agent Architecture Audit Report (V17-009)

**Date:** 2026-03-14  
**Objective:** Audit the repository's agent systems to clarify the architectural relationship between `app/agents/` and `app/executive_agents/`

---

## 1. Agent Inventory Table

### 1.1 `app/agents/` (Board Agents - Domain Layer)

| File | Class | Purpose |
|------|-------|---------|
| `base_agent.py` | `BaseAgent` | Abstract base class for all board agents; defines LLM-based analysis interface |
| `strategy_agent.py` | `StrategyAgent` | Chief Strategy Officer - long-range direction, leverage, timing |
| `finance_agent.py` | `FinanceAgent` | CFO - resource allocation, capital protection, ROI analysis |
| `risk_agent.py` | `RiskAgent` | CRO - risk identification and mitigation |
| `health_agent.py` | `HealthAgent` | Chief Health Officer - health/performance optimization |
| `operations_agent.py` | `OperationsAgent` | COO - operational feasibility and execution |
| `legacy_agent.py` | `LegacyAgent` | Chief Alignment Officer - legacy alignment and doctrine consistency |
| `registry.py` | `AgentRegistry` | Registry for managing board agents |

### 1.2 `app/executive_agents/` (Executive Agents - Governance Layer)

| File | Class | Purpose |
|------|-------|---------|
| `base_agent.py` | `BaseExecutiveAgent` | Abstract base; integrates with StateEngine, MetaCognition |
| `ceo_agent.py` | `CEOAgent` | CEO - orchestrates council cycles, selects final strategy |
| `cfo_agent.py` | `CFOAgent` | CFO - evaluates financial impact and capital allocation |
| `coo_agent.py` | `COOAgent` | COO - evaluates operational feasibility |
| `cso_agent.py` | `CSOAgent` | CSO - long-term strategic planning |
| `cro_agent.py` | `CROAgent` | CRO - risk identification and management |
| `cko_agent.py` | `CKOAgent` | CKO - knowledge management, doctrine alignment |
| `cpo_agent.py` | `CPOAgent` | CPO - system capability improvement |
| `agent_council.py` | `AgentCouncil` | Orchestrates executive agent deliberation cycles |
| `debate_engine.py` | `DebateEngine` | Facilitates structured debate between executive agents |
| `agent_models.py` | `AgentProposal`, `DebateArgument`, etc. | Data models for proposals and debates |
| `agent_types.py` | `ExecutiveRole`, `ProposalStatus`, etc. | Enums for executive agent types |

---

## 2. Role Classification Table

### 2.1 `app/agents/` Classification

| Agent | Role Type | Domain | Notes |
|-------|-----------|--------|-------|
| `StrategyAgent` | Domain Agent | Strategy | CSO-level strategic advice |
| `FinanceAgent` | Domain Agent | Finance | CFO-level financial guidance |
| `RiskAgent` | Domain Agent | Risk | CRO-level risk analysis |
| `HealthAgent` | Domain Agent | Health | Health/performance optimization |
| `OperationsAgent` | Domain Agent | Operations | COO-level operational advice |
| `LegacyAgent` | Domain Agent | Legacy/Doctrine | Alignment and consistency |

### 2.2 `app/executive_agents/` Classification

| Agent | Role Type | Executive | Notes |
|-------|-----------|-----------|-------|
| `CEOAgent` | Executive Agent | CEO | Final decision authority |
| `CFOAgent` | Executive Agent | CFO | Financial impact evaluation |
| `COOAgent` | Executive Agent | COO | Operational feasibility |
| `CSOAgent` | Executive Agent | CSO | Long-term planning |
| `CROAgent` | Executive Agent | CRO | Risk management |
| `CKOAgent` | Executive Agent | CKO | Knowledge/doctrine |
| `CPOAgent` | Executive Agent | CPO | Capability improvement |

---

## 3. Architectural Pattern Analysis

### Finding: **Option C — Incomplete Migration**

The codebase exhibits characteristics of **an incomplete architectural migration**:

1. **`app/agents/`** (Legacy/Active):  
   - Uses LLM-based analysis with `AsyncSession` and database persistence  
   - Integrated with `BoardOrchestrator` for meeting workflows  
   - Agents have `analyze()` method returning `AgentResponse`  
   - Used in production via `/api/board/` endpoints

2. **`app/executive_agents/`** (Newer/Experimental):  
   - Uses `StateEngine` and `MetaCognition` for state management  
   - Integrated with `AgentCouncil` for governance cycles  
   - Agents have `analyze_state()`, `generate_proposal()`, `evaluate_proposal()` methods  
   - **NOT actively integrated** into any API endpoint or workflow
   - Contains `DebateEngine` for executive-level debate

### Key Observation

Both systems are **operationally independent** and serve **different purposes**:
- `app/agents/` → **Advisory Board** (domain experts providing analysis)
- `app/executive_agents/` → **Governance Council** (executives making strategic decisions)

However, `app/executive_agents/` appears to be **unused in the current codebase** - no imports exist outside its own directory.

---

## 4. Dependency Map

### 4.1 `app/agents/` Dependencies

| Subsystem | Imports From | Usage |
|-----------|--------------|-------|
| `core/orchestrator.py` | `AgentRegistry`, domain agents | Board meeting orchestration |
| `api/board.py` | `BoardOrchestrator` | Board meeting API endpoints |
| `agents/registry.py` | All domain agents | Agent instantiation |

### 4.2 `app/executive_agents/` Dependencies

| Subsystem | Imports From | Usage |
|-----------|--------------|-------|
| *(self-contained)* | All executive agents | Internal council coordination |

**Critical Finding:** `app/executive_agents/` has **no external dependencies** - it is completely isolated from the rest of the application.

### 4.3 Debate Engine Duplication

There are **two debate engines**:

| Location | Class | Used By |
|----------|-------|---------|
| `app/debate/debate_engine.py` | `DebateEngine` | `api/debate.py` (active) |
| `app/executive_agents/debate_engine.py` | `DebateEngine` | `agent_council.py` (unused) |

The `app/debate/debate_engine.py` uses **board agents** (from `app/agents/`), while `app/executive_agents/debate_engine.py` is designed for **executive agents**.

---

## 5. Overlap Analysis

### 5.1 Role Overlap Matrix

| Domain Agent | Executive Agent | Overlap Severity |
|-------------|----------------|-----------------|
| `StrategyAgent` (CSO) | `CSOAgent` (CSO) | **HIGH** - Both handle strategy |
| `FinanceAgent` (CFO) | `CFOAgent` (CFO) | **HIGH** - Both handle finance |
| `RiskAgent` (CRO) | `CROAgent` (CRO) | **HIGH** - Both handle risk |
| `OperationsAgent` (COO) | `COOAgent` (COO) | **HIGH** - Both handle operations |
| `LegacyAgent` | `CKOAgent` | **MEDIUM** - Doctrine/alignment |
| (none) | `CEOAgent` | N/A - Executive head |
| (none) | `CPOAgent` | N/A - Product/capability |

### 5.2 Functional Redundancy

| Function | System A | System B |
|----------|----------|----------|
| Board meeting analysis | `app/agents/` + `BoardOrchestrator` | — |
| Strategic proposals | — | `app/executive_agents/` + `AgentCouncil` |
| Multi-agent debate | `app/debate/debate_engine.py` | `app/executive_agents/debate_engine.py` |

---

## 6. Recommended Canonical Architecture

### 6.1 Proposed Directory Structure

```
app/agents/
├── __init__.py
├── base.py                    # Unified base class for ALL agents
├── registry.py                # Agent registry
│
├── domain/                    # Domain Expert Agents
│   ├── __init__.py
│   ├── strategy_agent.py      # CSO - Strategic guidance
│   ├── finance_agent.py       # CFO - Financial analysis
│   ├── risk_agent.py          # CRO - Risk analysis
│   ├── health_agent.py        # Health optimization
│   ├── operations_agent.py    # COO - Operations
│   └── legacy_agent.py       # CKO - Doctrine alignment
│
├── executive/                 # Executive Governance Agents
│   ├── __init__.py
│   ├── ceo_agent.py          # CEO - Final decision authority
│   ├── cfo_agent.py          # CFO - Financial governance
│   ├── coo_agent.py          # COO - Operations governance
│   ├── cso_agent.py          # CSO - Strategy governance
│   ├── cro_agent.py          # CRO - Risk governance
│   ├── cko_agent.py          # CKO - Knowledge governance
│   ├── cpo_agent.py          # CPO - Capability governance
│   ├── council.py            # AgentCouncil orchestration
│   └── debate.py             # Unified debate engine
│
└── interfaces/                # Public API for agents
    ├── __init__.py
    └── adapters.py           # Adapters for orchestrator, API, etc.
```

### 6.2 Ownership Rules

1. **Domain Agents** (`app/agents/domain/`):
   - Provide expert analysis on specific domains
   - Used for advisory board meetings
   - Focus: "What should we consider?"

2. **Executive Agents** (`app/agents/executive/`):
   - Make strategic decisions and proposals
   - Participate in governance cycles
   - Focus: "What should we decide?"

3. **Communication Flow**:
   ```
   Domain Agents (Advisory) ──→ BoardOrchestrator ──→ User
                    │
                    └──→ Executive Agents (Governance) ──→ AgentCouncil ──→ Decisions
   ```

### 6.3 Inheritance Structure

```python
# app/agents/base.py

class BaseAgent(ABC):
    """Unified base for all agents."""
    
    @property
    @abstractmethod
    def role(self) -> ExecutiveRole:
        pass
    
    @abstractmethod
    async def analyze(self, context: dict) -> AgentResult:
        pass

class DomainAgent(BaseAgent):
    """Domain expert agents - advisory role."""
    # Uses LLM for analysis
    # Persists to database
    
class ExecutiveAgent(BaseAgent):
    """Executive agents - governance role."""
    # Uses StateEngine + MetaCognition
    # Generates proposals and decisions
```

---

## 7. Consolidation Opportunities

### 7.1 Immediate Actions

| Priority | Action | Rationale |
|----------|--------|-----------|
| **HIGH** | Merge `app/executive_agents/` into `app/agents/executive/` | Unify agent organization |
| **HIGH** | Create unified `app/agents/base.py` | Standardize inheritance |
| **HIGH** | Integrate `AgentCouncil` into production | Enable governance layer |
| **MEDIUM** | Consolidate debate engines | Single source of truth |
| **MEDIUM** | Deprecate `app/debate/` if redundant | Reduce duplication |

### 7.2 Long-term Recommendations

1. **Phase 1 — Unification**:
   - Move `executive_agents/` → `agents/executive/`
   - Create unified `agents/base.py`

2. **Phase 2 — Integration**:
   - Connect `AgentCouncil` to API endpoints
   - Enable governance workflow

3. **Phase 3 — Consolidation**:
   - Merge debate engines
   - Remove `app/debate/` directory

### 7.3 Migration Path

```bash
# Step 1: Create new structure
mkdir -p app/agents/domain app/agents/executive

# Step 2: Move files (dry run)
# mv app/agents/*.py app/agents/domain/  # For domain agents
# mv app/executive_agents/* app/agents/executive/  # For executive agents

# Step 3: Create unified base
# Create app/agents/base.py with BaseAgent, DomainAgent, ExecutiveAgent

# Step 4: Update imports
# Update all imports across the codebase
```

---

## 8. Summary

| Aspect | Finding |
|--------|---------|
| **Total Agents** | 13 (6 domain + 7 executive) |
| **Architectural Pattern** | Incomplete migration (Option C) |
| **Active System** | `app/agents/` (Board meetings) |
| **Inactive System** | `app/executive_agents/` (Governance council) |
| **Overlap Severity** | HIGH - All executive roles have domain counterparts |
| **Recommendation** | Unify under `app/agents/` with domain/executive subdirectories |

---

*End of Report*
