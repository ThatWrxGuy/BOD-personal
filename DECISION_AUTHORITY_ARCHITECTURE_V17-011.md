# Decision Authority Architecture Report (V17-011)

**Date:** 2026-03-14  
**Objective:** Define and document the system's decision authority hierarchy

---

## 1. Decision Point Inventory

| # | Subsystem | File/Module | Purpose | Decision Type |
|---|-----------|-------------|---------|---------------|
| 1 | **Detection** | `detection_engine.py` | Process signals and detect opportunities/risks | Event Detection |
| 2 | **Detection** | `pattern_detector.py` | Identify patterns in historical data | Pattern Recognition |
| 3 | **Detection** | `opportunity_classifier.py` | Classify opportunities by potential | Classification |
| 4 | **Intelligence** | `synthesizer/synthesizer_service.py` | Synthesize insights from multiple signals | Insight Generation |
| 5 | **Intelligence** | `synthesizer/strategy_advisor.py` | Provide strategic recommendations | Advisory |
| 6 | **Intelligence** | `scenario_simulator.py` | Simulate scenarios for planning | Simulation |
| 7 | **Intelligence/Learning** | `learning/strategy_effectiveness.py` | Evaluate strategy effectiveness | Evaluation |
| 8 | **Planning** | `strategy_generator.py` | Generate strategic plans | Plan Creation |
| 9 | **Planning** | `strategic_planner.py` | Create detailed action plans | Planning |
| 10 | **Governance** | `review_engine.py` | Review plans and decisions | Review |
| 11 | **Governance** | `trigger_engine.py` | Trigger governance events | Event Trigger |
| 12 | **Autonomy** | `strategy_loop.py` | Orchestrate strategy cycles | Loop Control |
| 13 | **Autonomy** | `strategy_adjuster.py` | Adjust strategy based on feedback | Adjustment |
| 14 | **Agents (Domain)** | `agents/domain/*_agent.py` | Provide domain-specific analysis | Advisory |
| 15 | **Agents (Executive)** | `agents/executive/agent_council.py` | Deliberate and make strategic decisions | Decision Making |
| 16 | **Execution** | `approval_gate.py` | Approve/reject execution intents | Authorization |
| 17 | **Execution** | `action_validator.py` | Validate actions before execution | Validation |
| 18 | **Execution** | `risk_gate.py` | Assess and approve risk | Risk Approval |
| 19 | **Execution** | `policy_gate.py` | Check policy compliance | Policy Compliance |
| 20 | **Execution** | `execution_engine.py` | Execute approved actions | Execution |
| 21 | **Learning** | `learning/outcome_evaluator.py` | Evaluate execution outcomes | Outcome Evaluation |
| 22 | **Learning** | `learning/confidence_calibrator.py` | Calibrate confidence scores | Calibration |
| 23 | **Intelligence/Learning** | `learning/doctrine_updater.py` | Update strategic doctrine | Doctrine Update |

---

## 2. Decision Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    INPUTS                                                 │
│  Signals │ External Events │ State Changes │ User Queries │ Scheduled Triggers          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  OBSERVATION LAYER                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                          │
│  │  Signal         │  │  Pattern        │  │  Anomaly        │                          │
│  │  Ingestion      │  │  Detection      │  │  Detection      │                          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ANALYSIS LAYER                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Detection      │  │  Intelligence   │  │  Scenario       │  │  Trend          │    │
│  │  Engine         │  │  Synthesizer    │  │  Simulator      │  │  Analysis       │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                                         │
│  OUTPUT: Detected Events → Synthesized Insights → Forecasts → Trends                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  PLANNING LAYER                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                          │
│  │  Strategy       │  │  Strategic      │  │  Domain         │                          │
│  │  Generator      │  │  Planner        │  │  Relationship   │                          │
│  │                 │  │                 │  │  Mapper         │                          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                          │
│                                                                                         │
│  OUTPUT: Strategic Plans → Action Plans → Domain Strategies                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  DELIBERATION/DECISION LAYER                                                            │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────────────────┐   │
│  │  DOMAIN AGENTS                        │  │  EXECUTIVE AGENTS                       │   │
│  │  (Advisory Board)                     │  │  (Governance Council)                   │   │
│  │                                       │  │                                         │   │
│  │  • Strategy Agent (CSO)              │  │  • CEO Agent (Chair)                    │   │
│  │  • Finance Agent (CFO)               │  │  • CFO Agent                            │   │
│  │  • Risk Agent (CRO)                  │  │  • COO Agent                            │   │
│  │  • Health Agent                      │  │  • CSO Agent                           │   │
│  │  • Operations Agent (COO)           │  │  • CRO Agent                           │   │
│  │  • Legacy Agent (CKO)               │  │  • CKO Agent                           │   │
│  │                                       │  │  • CPO Agent                           │   │
│  │  BoardOrchestrator                   │  │  AgentCouncil                          │   │
│  │  (Meeting Facilitation)              │  │  (Deliberation & Decision)             │   │
│  └──────────────────────────────────────┘  └──────────────────────────────────────────┘   │
│                                                                                         │
│  OUTPUT: Recommendations → Proposals → Council Decisions                               │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  GOVERNANCE/APPROVAL LAYER                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Review         │  │  Approval       │  │  Risk          │  │  Policy         │    │
│  │  Engine         │  │  Gate           │  │  Gate          │  │  Gate           │    │
│  │                 │  │                 │  │                 │  │                 │    │
│  │  Human/AI       │  │  Human/         │  │  Risk          │  │  Policy         │    │
│  │  Review         │  │  Auto-approve  │  │  Assessment    │  │  Compliance     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                                         │
│  OUTPUT: Approved Execution Intents                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  EXECUTION LAYER                                                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                          │
│  │  Execution      │  │  Action         │  │  Action         │                          │
│  │  Engine        │  │  Router         │  │  Validator      │                          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                          │
│                                                                                         │
│  OUTPUT: Executed Actions → Connectors → External Systems                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LEARNING LAYER                                                                        │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────────────────┐   │
│  │  OPERATIONAL LEARNING                 │  │  STRATEGIC LEARNING                     │   │
│  │                                       │  │                                         │   │
│  │  • Outcome Evaluator                 │  │  • Strategy Effectiveness Tracker        │   │
│  │  • Recommendation Tracker            │  │  • Doctrine Updater                      │   │
│  │  • Confidence Calibrator            │  │  • Decision Tracker                      │   │
│  └──────────────────────────────────────┘  └──────────────────────────────────────────┘   │
│                                                                                         │
│  OUTPUT: Lessons Learned → Doctrine Updates → Future Decisions                          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer Classification Table

| Layer | Subsystem | Primary Responsibility | Key Files |
|-------|-----------|------------------------|------------|
| **Observation** | `signals/` | Signal ingestion and collection | `signal_collector.py`, `signal_processor.py` |
| **Observation** | `detection/` | Event detection and classification | `detection_engine.py`, `pattern_detector.py` |
| **Analysis** | `intelligence/` | Insight synthesis and forecasting | `synthesizer_service.py`, `scenario_simulator.py` |
| **Analysis** | `forecasting/` | Trend analysis and projection | `trend_analyzer.py`, `forecasting_engine.py` |
| **Planning** | `planning/` | Strategy and plan generation | `strategy_generator.py`, `strategic_planner.py` |
| **Decision** | `agents/domain/` | Domain advisory (Board) | `*_agent.py`, `orchestrator.py` |
| **Decision** | `agents/executive/` | Strategic decisions (Council) | `agent_council.py`, `*_agent.py` |
| **Governance** | `governance/` | Review and trigger management | `review_engine.py`, `trigger_engine.py` |
| **Approval** | `execution/` | Authorization gates | `approval_gate.py`, `risk_gate.py`, `policy_gate.py` |
| **Execution** | `execution/` | Action execution | `execution_engine.py`, `action_router.py` |
| **Learning** | `learning/` | Outcome evaluation | `outcome_evaluator.py`, `recommendation_tracker.py` |
| **Learning** | `intelligence/learning/` | Strategic learning | `strategy_effectiveness.py`, `doctrine_updater.py` |
| **Autonomy** | `autonomy/` | Self-adjustment loops | `strategy_loop.py`, `strategy_adjuster.py` |

---

## 4. Authority Boundary Analysis

### 4.1 Decision Origins

| Stage | Originator | Authority Level |
|-------|------------|-----------------|
| Signal Detection | `signal_ingestion/` | Observation only |
| Pattern Recognition | `detection/` | Observation only |
| Insight Synthesis | `intelligence/synthesizer/` | Advisory (no authority) |
| Strategy Generation | `planning/` | Proposal only |
| Domain Analysis | `agents/domain/` | Advisory (recommendations) |
| Strategic Decisions | `agents/executive/` | **Decision authority** (proposals) |
| Plan Approval | `governance/` | **Governance authority** |
| Execution Authorization | `execution/approval_gate/` | **Execution authority** |

### 4.2 Approval Hierarchy

```
User (Final Authority)
    │
    ▼
┌─────────────────────────────────────┐
│  Governance Layer                    │
│  - Review Engine                    │
│  - Approval Gate                    │
│  - Policy Gate                      │
└─────────────────────────────────────┘
    │ (approves/rejects)
    ▼
┌─────────────────────────────────────┐
│  Executive Agents (AgentCouncil)     │
│  - CEO Agent (Chair)                 │
│  - Strategic deliberation            │
│  - Final proposal selection          │
└─────────────────────────────────────┘
    │ (proposes)
    ▼
┌─────────────────────────────────────┐
│  Domain Agents (Board)              │
│  - Advisory analysis                 │
│  - Multiple perspective synthesis    │
└─────────────────────────────────────┘
    │ (advises)
    ▼
┌─────────────────────────────────────┐
│  Planning Layer                     │
│  - Strategy Generator               │
│  - Strategic Planner                 │
└─────────────────────────────────────┘
    │ (generates plans)
    ▼
┌─────────────────────────────────────┐
│  Intelligence Layer                 │
│  - Synthesizer                      │
│  - Scenario Simulator               │
│  - Trend Analyzer                   │
└─────────────────────────────────────┘
    │ (analyzes)
    ▼
┌─────────────────────────────────────┐
│  Detection Layer                    │
│  - Detection Engine                 │
│  - Pattern Detector                 │
└─────────────────────────────────────┘
    │ (detects)
    ▼
┌─────────────────────────────────────┐
│  Signal Ingestion                   │
│  - External signals                 │
│  - Internal events                  │
└─────────────────────────────────────┘
```

### 4.3 Ambiguities Identified

| Issue | Location | Description |
|-------|----------|-------------|
| **Dual Decision Systems** | `agents/domain/` vs `agents/executive/` | Two independent agent systems - unclear which has precedence |
| **Inactive Executive System** | `agents/executive/` | Executive agents (AgentCouncil) are not integrated into any active workflow |
| **Debate Engine Duplication** | `app/debate/` vs `agents/executive/` | Two debate engines with unclear relationship |
| **Learning Separation** | `learning/` vs `intelligence/learning/` | Two learning systems - operational vs strategic distinction unclear |

---

## 5. Canonical Decision Pipeline

Based on the analysis, the **intended canonical decision pipeline** is:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIGNAL INPUTS                                       │
│   External Signals │ Internal Events │ User Triggers │ Scheduled Events     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. DETECTION (Observation Layer)                                          │
│     DetectionEngine.process_signal()                                        │
│     - Pattern detection                                                      │
│     - Anomaly detection                                                     │
│     - Event classification                                                 │
│     Output: DetectedEvent                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. INTELLIGENCE SYNTHESIS (Analysis Layer)                                │
│     SynthesizerService.synthesize()                                         │
│     - Signal extraction                                                     │
│     - Insight generation                                                   │
│     - Scenario simulation                                                 │
│     Output: SynthesizedInsights                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. STRATEGIC PLANNING (Planning Layer)                                    │
│     StrategyGenerator.generate_plan()                                       │
│     - Plan generation                                                      │
│     - Action sequencing                                                   │
│     - Resource allocation                                                 │
│     Output: StrategicPlan                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. AGENT DELIBERATION (Decision Layer)                                    │
│     Domain: BoardOrchestrator.run_meeting()                                │
│     Executive: AgentCouncil.conduct_council_cycle()                        │
│     - Multi-agent analysis (Board)                                         │
│     - Debate and deliberation (Council)                                    │
│     - Proposal generation                                                  │
│     Output: CouncilDecision, AgentResponse                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. GOVERNANCE REVIEW (Governance Layer)                                   │
│     ReviewEngine.review_plan()                                              │
│     - Compliance checking                                                  │
│     - Risk assessment                                                      │
│     - Priority alignment                                                   │
│     Output: ReviewResult                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. EXECUTION AUTHORIZATION (Approval Layer)                                │
│     ApprovalGate.request_approval()                                        │
│     - PolicyGate.check()                                                   │
│     - RiskGate.assess()                                                   │
│     - ActionValidator.validate()                                           │
│     Output: ExecutionIntent (Approved)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. ACTION EXECUTION (Execution Layer)                                     │
│     ExecutionEngine.execute()                                              │
│     - Action routing                                                       │
│     - Connector invocation                                                 │
│     - Result tracking                                                     │
│     Output: ExecutionResult                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  8. OPERATIONAL LEARNING (Learning Layer)                                  │
│     OutcomeEvaluator.evaluate()                                            │
│     - Outcome tracking                                                    │
│     - Recommendation scoring                                               │
│     - Confidence calibration                                               │
│     Output: OutcomeEvaluation                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  9. STRATEGIC LEARNING (Meta-Learning Layer)                               │
│     StrategyEffectivenessTracker.evaluate()                                 │
│     - Doctrine updates                                                    │
│     - Strategy adjustments                                                │
│     - Pattern recognition for future decisions                             │
│     Output: DoctrineUpdate, StrategyAdjustment                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                               ┌───────────────────┐
                               │ FEEDBACK TO LOOP  │
                               │ (Autonomy Layer)  │
                               └───────────────────┘
```

---

## 6. Authority Summary

### Final Decision Authority Hierarchy

| Level | Authority | Component | Scope |
|-------|-----------|-----------|-------|
| **1 (Highest)** | User | Human operator | Final veto, strategic direction |
| **2** | Governance | `governance/review_engine.py` | Plan approval, priority |
| **3** | Execution | `execution/approval_gate.py` | Execution authorization |
| **4** | Executive | `agents/executive/AgentCouncil` | Strategic decisions |
| **5** | Domain | `agents/domain/BoardOrchestrator` | Advisory analysis |
| **6 (Lowest)** | System | `planning/`, `intelligence/` | Proposals only |

### Key Findings

1. **Two Parallel Decision Systems**: 
   - Domain Agents (Board) → Advisory
   - Executive Agents (Council) → Strategic decisions
   - **Not clearly integrated**

2. **Executive Agents Unused**:
   - `AgentCouncil` exists but not connected to any workflow
   - Represents potential for automated governance

3. **Learning Loop Incomplete**:
   - Operational learning (`learning/`) tracks outcomes
   - Strategic learning (`intelligence/learning/`) updates doctrine
   - **Not closed-loop** with planning

4. **Approval Gates Central**:
   - `ApprovalGate` is the critical authorization point
   - Multiple gates (risk, policy, doctrine) provide checks

---

## 7. Recommendations

### Immediate Actions
1. **Integrate Executive Agents**: Connect `AgentCouncil` to the decision pipeline
2. **Close Learning Loop**: Connect outcome evaluation back to planning
3. **Consolidate Debate Engines**: Single debate system for both agent types

### Architectural Principles
1. **User remains final authority** - All execution requires approval
2. **Domain agents advise** - Executive agents decide
3. **Learning informs planning** - Doctrine updates affect future strategy
4. **Defense in depth** - Multiple approval gates before execution

---

*End of Report*
