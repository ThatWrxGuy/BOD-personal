# Directive BB-INF-005

External Intelligence Governance & Execution Safety

Classification: Infrastructure Control Directive
Authority: CEO (User)
Priority: Critical
Objective: Establish governance, approval workflows, safety controls, and observability for the External Intelligence Layer.

---

## 1. Purpose

Directive BB-INF-004 successfully introduced the External Intelligence Layer enabling:

| Capability | Service |
|------------|---------|
| Strategic reasoning | OpenAI |
| Autonomous software engineering | OpenHands |
| Repository interaction | GitHub |

While powerful, these integrations introduce systemic risk if not governed properly.

This directive introduces:
- Execution controls
- Human approval layers
- Change simulation
- Safety guardrails
- Audit logging

The goal is to ensure the system remains intelligent but controlled.

---

## 2. New Governance Architecture

Created infrastructure module:

```
app/infrastructure/governance/
├── external_intelligence_governor.py
├── change_validator.py
├── execution_gate.py
└── intelligence_audit_log.py
```

**Purpose:**

| Module | Function |
|--------|----------|
| external_intelligence_governor | policy enforcement |
| change_validator | validate code changes |
| execution_gate | CEO approval control |
| intelligence_audit_log | log all AI actions |

---

## 3. External Intelligence Governor

File: `external_intelligence_governor.py`

**Purpose:** Ensure all external intelligence actions pass through a control layer.

**Rules:**

| Action | Approval |
|--------|----------|
| reasoning | automatic |
| code generation | council approval |
| repository modification | CEO approval |

**Approval Levels:**
- NONE - No approval needed
- AUTOMATIC - Automatic approval
- COUNCIL - Chief Officer approval
- CEO - CEO approval required

---

## 4. Execution Gate

File: `execution_gate.py`

**Purpose:** Prevent autonomous repository changes.

**Workflow:**

```
Agent
↓
OpenHands proposal
↓
Execution Gate
↓
CEO approval required
↓
GitHub PR creation
```

**Proposal States:**
- PENDING - Awaiting approval
- APPROVED - Approved for execution
- REJECTED - Denied
- EXPIRED - Timed out
- EXECUTED - Completed

---

## 5. Change Validator

File: `change_validator.py`

**Purpose:** Analyze OpenHands code before allowing it into the repository.

**Validation Checks:**

| Check | Purpose |
|-------|---------|
| syntax validation | prevent broken code |
| security scan | detect secrets |
| dependency safety | prevent malicious packages |
| architecture rules | enforce project standards |

---

## 6. Intelligence Audit Log

File: `intelligence_audit_log.py`

**Purpose:** Log every external intelligence action.

**Logged Events:**

| Event | Logged |
|-------|--------|
| OpenAI calls | yes |
| OpenHands actions | yes |
| GitHub changes | yes |
| Governance checks | yes |
| Approval requests | yes |

**Event Structure:**

```json
{
  "timestamp": "2026-03-15T20:15:02",
  "agent": "InvestmentStrategist",
  "action": "openai_reasoning",
  "status": "success"
}
```

---

## 7. Intelligence Router Upgrade

Updated: `intelligence_router.py`

**New Architecture:**

```
Agent
↓
Intelligence Router
↓
External Intelligence Governor
↓
Service Gateway
```

All tasks now pass through governance checks before execution.

---

## 8. Sandbox Environment for Code Changes

All OpenHands code generation is validated in sandbox before execution.

**Sandbox Directory:** `/sandbox/proposals/`

**Process:**

```
OpenHands generates code
↓
Change validator runs
↓
Tests executed (if applicable)
↓
Proposal sent for approval
↓
GitHub PR created (if approved)
```

No direct commits allowed.

---

## 9. Governance Status Endpoint

Added endpoint to check intelligence layer status:

```
GET /intelligence/status
```

**Response:**

```json
{
  "services": {
    "openai": true,
    "openhands": true,
    "github": true
  },
  "governance": {
    "governor": {
      "enabled": true,
      "pending_requests": 2
    },
    "execution_gate": {
      "pending": 1,
      "approved": 0
    },
    "audit_log": {
      "total_events": 15
    }
  }
}
```

---

## 10. System Capability After Directive

Once BB-INF-005 is implemented the system operates like this:

```
Signal
↓
Agent
↓
External Intelligence
↓
Governance Layer
↓
Simulation
↓
Decision
↓
CEO
```

This ensures the system becomes:

**Controlled Self-Improving Intelligence System**

instead of

**Unrestricted Autonomous System**

---

## 11. Validation Tests

### Test 1 — Reasoning

**Input:**
```
Evaluate optimal debt payoff strategy
```

**Expected:** Structured strategy analysis (auto-approved)

---

### Test 2 — Development Proposal

**Task:**
```
Add new agent module
```

**Expected:** 
- Proposal created
- Council approval required
- Code validated in sandbox

---

### Test 3 — Repository Action

**Command:**
```
Create issue
```

**Expected:**
- GitHub issue created successfully
- Logged in audit trail

---

## 12. Next Directive

After governance is implemented, initiate:

**BB-FIN-011**

Autonomous Investment Intelligence Agent

This directive will implement:

SPY 0DTE Options Intelligence Agent

**Capabilities:**
- 1-minute market data
- Options chain analysis
- Gamma exposure detection
- Delta velocity detection
- Strike selection
- Entry timing

This will integrate directly into the Finance domain of Busy Bee.

---

**✅ Directive BB-INF-005 Ready for Execution**
