# Predictive Intelligence Layer Architecture

This document defines the responsibilities and boundaries of each predictive intelligence subsystem in the BOD Strategic Intelligence Engine.

## Overview

The predictive intelligence layer consists of three interconnected systems that provide increasingly sophisticated strategic analysis:

```
Forecasting (V5-001)
    ↓
Strategy Simulation (V5-002)
    ↓
Monte Carlo Stress Testing (V5-003)
```

Each system builds on the previous, providing deeper insight into strategic decisions.

---

## Subsystem Responsibilities

### 1. Forecasting Engine (`app/forecasting/`)

**Purpose**: Predict future domain states based on historical trends

**Responsibilities**:
- Trend analysis and projection
- Risk trajectory modeling
- Goal probability estimation
- Short/medium/long-horizon predictions

**Outputs**:
- Domain performance projections (30/90/365 days)
- Risk probability forecasts
- Goal completion probabilities
- Opportunity identification

**Use Case**: "Given current trends, what will happen in the next 90 days?"

---

### 2. Strategy Simulation Engine (`app/strategy_simulation/`)

**Purpose**: Evaluate candidate strategic decisions by simulating their outcomes

**Responsibilities**:
- Strategy candidate modeling
- Multi-scenario outcome simulation
- Strategy comparison and ranking
- Recommendation generation with reasoning

**Outputs**:
- Ranked strategy list
- Best strategy recommendation
- Alternative strategies
- Expected outcomes per strategy

**Use Case**: "If I choose strategy A vs B, what happens?"

---

### 3. Monte Carlo Stress Testing Engine (`app/monte_carlo/`)

**Purpose**: Test strategy robustness across thousands of randomized futures

**Responsibilities**:
- Randomized future generation
- Distribution analysis
- Resilience scoring
- Failure mode detection
- Stress test reporting

**Outputs**:
- Outcome distributions
- Resilience scores
- Collapse probabilities
- Fragility detection

**Use Case**: "How does strategy A perform across 1000 possible futures?"

---

## Data Flow

```
Current State
    ↓
┌─────────────────────────────────────────┐
│           Forecasting Engine            │  ← Trend analysis
│  - Analyze historical patterns         │
│  - Project future trajectories         │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│      Strategy Simulation Engine          │  ← Strategy evaluation
│  - Generate candidate strategies        │
│  - Simulate outcomes                   │
│  - Compare and rank                    │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│        Monte Carlo Engine               │  ← Stress testing
│  - Randomize futures                  │
│  - Test robustness                     │
│  - Identify failures                   │
└─────────────────────────────────────────┘
                ↓
          Strategic Decision
```

---

## Key Interfaces

### Forecasting → Strategy Simulation

Forecasting provides:
- Current domain states
- Risk projections
- Trend directions

Strategy Simulation uses these as input for strategy evaluation.

### Strategy Simulation → Monte Carlo

Strategy Simulation provides:
- Candidate strategies
- Baseline outcomes

Monte Carlo tests these strategies across randomized environments.

---

## Shared Concepts

### Domain Model

All three systems use the concept of a "domain" (health, wealth, career, etc.) with:
- Performance score (0-10)
- Risk score (0-10)
- Resource allocation

### Time Horizons

- Short: 30 days
- Medium: 90 days  
- Long: 365 days

### Scoring

- Performance: Higher is better (0-10)
- Risk: Lower is better (0-10)
- Probability: 0-100%

---

## API Endpoints

| System | Endpoint | Description |
|--------|----------|-------------|
| Forecasting | `GET /forecast/domain-trends` | Get domain trend projections |
| Forecasting | `GET /forecast/risk-projections` | Get risk forecasts |
| Forecasting | `GET /forecast/goal-probabilities` | Get goal probabilities |
| Strategy Sim | `GET /simulation/strategies` | List candidate strategies |
| Strategy Sim | `POST /simulation/run` | Run simulation |
| Strategy Sim | `GET /simulation/recommendation` | Get best strategy |
| Monte Carlo | `POST /monte-carlo/run` | Run stress test |
| Monte Carlo | `GET /monte-carlo/report/{id}` | Get stress test report |

---

## Independence

While the systems integrate, they can also operate independently:

- **Forecasting** can run standalone for trend analysis
- **Strategy Simulation** can accept manual strategy definitions
- **Monte Carlo** can stress-test any strategy set

---

## Future Extensions

Potential additions:
- **V5-004**: Long-horizon goal path modeling
- **Meta-strategy layer**: Aggregate recommendations from all three
- **Adaptive learning**: Use Monte Carlo results to improve forecasting

---

*Last Updated: 2026-03-12*
