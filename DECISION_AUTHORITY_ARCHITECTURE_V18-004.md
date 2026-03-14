# Decision Authority Architecture (V18-004)

**Date:** 2026-03-14  
**Objective:** Define canonical decision authority hierarchy across the system

---

## 1. Decision Point Inventory

### 1.1 Detection Layer

| Subsystem | Module | Class/Service | Decision Responsibility | Primary/Overlapping |
|-----------|--------|---------------|------------------------|---------------------|
| **Detection** | `detection_engine.py` | `DetectionEngine` | Signal detection, anomaly identification | **Primary** |
| **Detection** | `pattern_detector.py` | `PatternDetector` | Pattern recognition in data | Primary |
| **Detection** | `opportunity_classifier.py` | `OpportunityClassifier` | Opportunity classification | Primary |
| **Autonomy** | `state_monitor.py` | `StateMonitor` | System state observation | Primary |
| **Autonomy** | `change_detector.py` | `ChangeDetector` | Change detection from observations | Primary |

### 1.2 Intelligence Layer

| Subsystem | Module | Class/Service | Decision Responsibility | Primary/Overlapping |
|-----------|--------|---------------|------------------------|---------------------|
| **Intelligence** | `intelligence_service.py` | `IntelligenceService` | Intelligence synthesis | **Primary** |
| **Intelligence** | `scenario_simulator.py` | `ScenarioSimulator` | Future scenario projection | Primary |
| **Intelligence** | `trend_analyzer.py` | `TrendAnalyzer` | Trend analysis | Primary |
| **Intelligence** | `forecasting_engine.py` | `ForecastingEngine` | Forecasting | Primary |
| **Intelligence** | `risk_projection_engine.py` | `RiskProjectionEngine` | Risk projection | Primary |

### 1.3 Planning Layer

| Subsystem | Module | Class/Service | Decision Responsibility | Primary/Overlapping |
|-----------|--------|---------------|------------------------|---------------------|
| **Planning** | `strategy_generator.py` | `StrategyGenerator` | Strategy creation | **Primary** |
| **Planning** | `strategic_planner.py` | `StrategicPlanner` | Strategic planning | Primary |
| **Planning** | `domain_relationship_mapper.py` | `DomainRelationshipMapper` | Domain relationship mapping | Primary |
| **Governance** | `plan_manager.py` | `PlanManager` | Plan management | Primary |

### 1.4 Decision/Deliberation Layer

| Subsystem | Module | Class/Service | Decision Responsibility | Primary/Overlapping |
|-----------|--------|---------------|------------------------|---------------------|
| **Autonomy** | `strategy_loop.py` | `StrategyLoop` | Overall cycle orchestration | **Primary** |
| **Autonomy** | `strategy_adjuster.py` | `StrategyAdjuster` | Adjustment recommendations | Primary |
| **Governance** | `review_engine.py` | `ReviewEngine` | Executive review | Primary |
| **Governance** | `goal_tracker.py` | `GoalTracker` | Goal tracking | Primary |

### 1.5 Execution Layer

| Subsystem | Module | Class/Service | Decision Responsibility | Primary/Overlapping |
|-----------|--------|---------------|------------------------|---------------------|
| **Execution** | `execution_engine.py` | `ExecutionEngine` | Action execution | **Primary** |
| **Execution** | `execution_controller.py` | `ExecutionController` | Execution control | Primary |
| **Execution** | `approval_gate.py` | `ApprovalGate` | Approval gating | Primary |
| **Execution** | `policy_gate.py` | `PolicyGate` | Policy enforcement | Primary |
| **Execution** | `risk_gate.py` | `RiskGate` | Risk check | Primary |
| **Execution** | `doctrine_gate.py` | `DoctrineGate` | Doctrine validation | Primary |
| **Execution** | `action_router.py` | `ActionRouter` | Action routing | Primary |

### 1.6 Learning Layer

| Subsystem | Module | Class/Service | Decision Responsibility | Primary/Overlapping |
|-----------|--------|---------------|------------------------|---------------------|
| **Learning** | `learning_controller.py` | `LearningController` | Learning orchestration | **Primary** |
| **Learning** | `outcome_evaluator.py` | `OutcomeEvaluator` | Outcome evaluation | Primary |
| **Learning** | `strategic_learning_service.py` | `StrategicLearningService` | Strategic learning | Primary |
| **Learning** | `confidence_calibrator.py` | `ConfidenceCalibrator` | Confidence calibration | Primary |
| **Intelligence/Learning** | `doctrine_updater.py` | `DoctrineUpdater` | Doctrine updates | Primary |
| **Intelligence/Learning** | `decision_tracker.py` | `DecisionTracker` | Decision tracking | Primary |

---

## 2. Current Decision Flow

### 2.1 Primary Flow (Strategy Loop)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           STRATEGY LOOP CYCLE                                        │
│                                                                                     │
│  1. OBSERVE STATE      → StateMonitor.observe_state()                              │
│         ↓                                                                           │
│  2. DETECT CHANGES     → ChangeDetector.detect_changes(observation)                 │
│         ↓                                                                           │
│  3. GENERATE ADJUSTMENTS → StrategyAdjuster.generate_adjustments(changes)          │
│         ↓                                                                           │
│  4. EXECUTE ACTIONS   → StrategyLoop._execute_adjustments(adjustments)            │
│         ↓                                                                           │
│  5. COMPLETE          → CycleOutcome returned                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Event-Driven Flow

```
DETECTION
    ↓
DetectionEngine.detect()
    ↓
OpportunityClassifier.classify()
    ↓
INTELLIGENCE
    ↓
IntelligenceService.synthesize()
    ↓
ScenarioSimulator.simulate()
    ↓
PLANNING
    ↓
StrategyGenerator.generate()
    ↓
DECISION
    ↓
StrategyAdjuster.generate_adjustments()
    ↓
ReviewEngine.review()
    ↓
EXECUTION
    ↓
ApprovalGate.check()
    ↓
ExecutionEngine.execute()
    ↓
LEARNING
    ↓
OutcomeEvaluator.evaluate()
    ↓
DoctrineUpdater.update()
```

### 2.3 Handoff Points

| From | To | Trigger |
|------|-----|---------|
| StateMonitor | ChangeDetector | Observation complete |
| ChangeDetector | StrategyAdjuster | Changes detected |
| StrategyAdjuster | StrategyLoop | Adjustments ready |
| StrategyLoop | ExecutionEngine | Actions to execute |
| ExecutionEngine | OutcomeEvaluator | Action completed |
| OutcomeEvaluator | DoctrineUpdater | Evaluation complete |

---

## 3. Architectural Layer Classification

### 3.1 Layer Assignment Table

| Subsystem | Primary Layer | Secondary | Ownership Status |
|-----------|--------------|-----------|------------------|
| **Detection** | Observation | - | Primary |
| **Autonomy/StateMonitor** | Observation | - | Primary |
| **Autonomy/ChangeDetector** | Observation | Analysis | Primary |
| **Intelligence** | Analysis | - | Primary |
| **Planning** | Planning | - | Primary |
| **Governance/ReviewEngine** | Decision | - | Primary |
| **Autonomy/StrategyLoop** | Decision | Orchestration | Primary |
| **Execution** | Execution | - | Primary |
| **Learning** | Learning | - | Primary |
| **Intelligence/Learning** | Learning | - | Primary |

### 3.2 Layer Definitions

| Layer | Purpose | Owner |
|-------|---------|-------|
| **Observation** | Detect signals, state changes, anomalies | Detection + Autonomy |
| **Analysis** | Synthesize intelligence, forecast, simulate | Intelligence |
| **Planning** | Generate strategies, plans, recommendations | Planning |
| **Decision** | Deliberate, evaluate, approve | Autonomy + Governance |
| **Execution** | Route, gate, execute actions | Execution |
| **Learning** | Evaluate outcomes, adapt doctrine | Learning + Intelligence/Learning |

---

## 4. Authority Ownership

### 4.1 Layer Ownership Matrix

| Layer | Primary Owner | Secondary Owner | Notes |
|-------|--------------|-----------------|-------|
| **Observation** | `DetectionEngine` | `StateMonitor` | Detects signals and state changes |
| **Analysis** | `IntelligenceService` | `ScenarioSimulator` | Synthesizes intelligence |
| **Planning** | `StrategyGenerator` | `StrategicPlanner` | Creates strategies/plans |
| **Decision Authority** | `StrategyLoop` | `ReviewEngine` | Final approval authority |
| **Execution Authorization** | `ApprovalGate` | `PolicyGate` | Gates execution |
| **Learning Feedback** | `OutcomeEvaluator` | `DoctrineUpdater` | Feedback to strategy |

### 4.2 Overlapping Ownership

| Area | Overlap | Resolution |
|------|---------|------------|
| Change Detection | Autonomy/ChangeDetector vs Detection/DetectionEngine | StrategyLoop coordinates |
| Planning | Planning/StrategyGenerator vs Governance/PlanManager | PlanManager manages plans |
| Approval | Governance/ReviewEngine vs Execution/ApprovalGate | ReviewEngine recommends, ApprovalGate decides |

---

## 5. Agent Authority Boundaries

### 5.1 Domain Agents

| Agent | Authority Level | Scope |
|-------|-----------------|-------|
| **Finance Agent** | Advise only | Financial analysis, recommendations |
| **Health Agent** | Advise only | Health insights, recommendations |
| **Fitness Agent** | Advise only | Fitness guidance, recommendations |
| **Operations Agent** | Advise only | Operations analysis, recommendations |

**Current Behavior:** Domain agents provide analysis and recommendations but do NOT execute actions.

### 5.2 Executive Agents

| Agent | Authority Level | Scope |
|-------|-----------------|-------|
| **Executive Agent** | Approve/Reject | Final approval on strategies |
| **Governance Agent** | Review | Policy compliance review |

**Current Behavior:** Executive agents have approval authority through `ReviewEngine`.

### 5.3 Autonomy Loop

| Mode | Behavior |
|------|----------|
| **Full Autonomy** | StrategyLoop executes adjustments without review |
| **Supervised** | StrategyLoop generates recommendations, ReviewEngine approves |
| **Manual** | All decisions require human approval |

**Current Implementation:** `StrategyLoop` executes adjustments directly in `run_cycle()` (line 91-97).

### 5.4 Orchestration Layer

| Responsibility | Current Behavior |
|---------------|------------------|
| Workflow Engine | `WorkflowEngine` manages workflow execution |
| Event Routing | `EventBus` routes events between components |
| State Management | `WorkflowStateMachine` manages workflow state |

**Clarification:** Orchestration is currently a **workflow engine only**, not a control plane. Control decisions flow through StrategyLoop.

---

## 6. Canonical Decision Pipeline

### 6.1 Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CANONICAL DECISION PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   SIGNALS   │  ← External events, state changes, user input
    │   STATE     │
    └──────┬──────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  OBSERVATION LAYER                                                           │
    │  • DetectionEngine: Signal detection                                         │
    │  • StateMonitor: System state observation                                   │
    │  • ChangeDetector: Change identification                                     │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  ANALYSIS LAYER                                                              │
    │  • IntelligenceService: Intelligence synthesis                                │
    │  • ScenarioSimulator: Future projection                                     │
    │  • TrendAnalyzer: Trend analysis                                           │
    │  • RiskProjectionEngine: Risk forecasting                                   │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  PLANNING LAYER                                                             │
    │  • StrategyGenerator: Strategy creation                                      │
    │  • StrategicPlanner: Plan development                                       │
    │  • DomainRelationshipMapper: Domain mapping                                  │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  DELIBERATION LAYER                                                          │
    │  • Domain Agents: Analysis and recommendations                              │
    │  • StrategyAdjuster: Adjustment proposals                                    │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  EXECUTIVE REVIEW LAYER                                                     │
    │  • ReviewEngine: Executive review                                           │
    │  • GoalTracker: Goal alignment check                                        │
    │  → APPROVAL or REJECTION                                                    │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           │                                                   │
           ▼                                                   ▼
    ┌──────────────┐                                   ┌──────────────┐
    │   APPROVED   │                                   │   REJECTED  │
    └──────┬───────┘                                   └──────────────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  EXECUTION GATING LAYER                                                    │
    │  • ApprovalGate: Final approval check                                       │
    │  • PolicyGate: Policy compliance                                            │
    │  • RiskGate: Risk validation                                               │
    │  • DoctrineGate: Doctrine alignment                                        │
    │  • ActionRouter: Action routing                                            │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  EXECUTION LAYER                                                           │
    │  • ExecutionEngine: Action execution                                       │
    │  • ExecutionController: Execution control                                   │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  OPERATIONAL LEARNING                                                       │
    │  • OutcomeEvaluator: Outcome evaluation                                     │
    │  • RecommendationScorer: Recommendation scoring                             │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  STRATEGIC LEARNING                                                        │
    │  • StrategicLearningService: Strategy effectiveness                         │
    │  • ConfidenceCalibrator: Confidence calibration                             │
    │  • DecisionTracker: Decision history                                       │
    └────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  DOCTRINE ADAPTATION                                                        │
    │  • DoctrineUpdater: Strategy/policy updates                                 │
    │  → Updates flow back to Planning and Execution layers                      │
    └──────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Pipeline Summary

| Stage | Owner | Output |
|-------|-------|--------|
| 1. Observation | Detection + Autonomy | Changes detected |
| 2. Analysis | Intelligence | Intelligence report |
| 3. Planning | Planning | Strategy/plan |
| 4. Deliberation | Domain Agents | Recommendations |
| 5. Executive Review | Governance | Approved/Rejected |
| 6. Execution Gating | Execution | Gate pass/fail |
| 7. Execution | Execution | Action results |
| 8. Operational Learning | Learning | Evaluation |
| 9. Strategic Learning | Learning | Effectiveness |
| 10. Doctrine Update | Intelligence/Learning | Doctrine update |

---

## 7. Gap Analysis

### 7.1 Identified Gaps

| Gap | Severity | Description |
|-----|----------|-------------|
| **No explicit approval step in StrategyLoop** | High | StrategyLoop executes adjustments directly without ReviewEngine approval |
| **Domain agents advisory-only** | Medium | Domain agents don't participate in deliberation |
| **Orchestration is passive** | Low | WorkflowEngine only executes, doesn't control |
| **Learning feedback to Planning unclear** | Medium | DoctrineUpdater output not explicitly routed back to StrategyGenerator |
| **Multiple overlapping change detection** | Low | Both DetectionEngine and ChangeDetector detect changes |

### 7.2 Ambiguities

| Area | Ambiguity | Resolution Needed |
|------|-----------|------------------|
| Autonomy vs Executive | When does StrategyLoop act without review? | Define autonomy modes |
| Domain Agent Role | Do domain agents advise or decide? | Clarify deliberation role |
| Orchestration Scope | Is orchestration a control plane? | Define orchestration boundaries |

### 7.3 Risks

| Risk | Impact |
|------|--------|
| StrategyLoop bypasses human review | High - actions execute without approval |
| Learning not feeding planning | Medium - system doesn't improve over time |
| Overlapping detection | Low - redundant processing |

---

## 8. Recommendations

### 8.1 Immediate Actions

1. **Add ReviewGate to StrategyLoop** - Insert ReviewEngine approval before execution
2. **Define Autonomy Modes** - Explicit FULL_AUTOMATED, SUPERVISED, MANUAL modes
3. **Route Doctrine Updates** - Connect DoctrineUpdater output to StrategyGenerator

### 8.2 Future Enhancements

1. **Domain Agent Deliberation** - Include domain agents in recommendation phase
2. **Orchestration Control Plane** - Elevate orchestration to coordinate layers
3. **Unified Learning Pipeline** - Single learning flow feeding all layers

---

## 9. Decision Point Summary

| # | Decision Point | Current Owner | Canonical Owner | Status |
|---|---------------|--------------|-----------------|--------|
| 1 | Signal Detection | DetectionEngine | DetectionEngine | OK |
| 2 | Change Detection | ChangeDetector | ChangeDetector | OK |
| 3 | Intelligence Synthesis | IntelligenceService | IntelligenceService | OK |
| 4 | Strategy Generation | StrategyGenerator | StrategyGenerator | OK |
| 5 | Adjustment Proposal | StrategyAdjuster | StrategyAdjuster | OK |
| 6 | Executive Review | ReviewEngine | ReviewEngine | OK |
| 7 | Approval Gating | ApprovalGate | ApprovalGate | OK |
| 8 | Action Execution | ExecutionEngine | ExecutionEngine | OK |
| 9 | Outcome Evaluation | OutcomeEvaluator | OutcomeEvaluator | OK |
| 10 | Doctrine Update | DoctrineUpdater | DoctrineUpdater | OK |
| 11 | **Autonomy Decision** | StrategyLoop | StrategyLoop | **GAP** - No review |

---

*End of Architecture Document*
