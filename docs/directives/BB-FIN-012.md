# Directive BB-FIN-012

Autonomous Portfolio Management Engine

Classification: Finance Intelligence Directive
Authority: CEO (User)
Priority: Strategic
Target System: Busy Bee / PSIE Finance Domain
Status: ✅ IMPLEMENTED
Objective: Implement a portfolio management engine capable of monitoring, allocating, and optimizing capital across assets while coordinating with the Finance Intelligence agents.

---

## 1. Purpose

With the implementation of:
- BB-FIN-011 – SPY 0DTE Investment Intelligence Agent

Busy Bee now has the ability to detect trading opportunities.

However, opportunity detection alone is insufficient. The system must also manage:
- Capital allocation
- Portfolio exposure
- Position sizing
- Risk management
- Performance evaluation

This directive introduces the **Autonomous Portfolio Management Engine (APME)**.

The APME functions as the central financial control layer responsible for managing capital across strategies.

---

## 2. Architecture

**Location:** `app/finance/portfolio_management/`

**Modules:**

| File | Purpose |
|------|---------|
| `portfolio_engine.py` | Main orchestration engine |
| `portfolio_models.py` | Data models |
| `portfolio_allocator.py` | Capital distribution |
| `position_manager.py` | Position lifecycle |
| `risk_controller.py` | Risk limits |
| `performance_tracker.py` | Performance metrics |
| `rebalancer.py` | Rebalancing logic |

---

## 3. Portfolio Engine Role

The Portfolio Engine acts as the financial coordination layer between:
- Investment agents
- Risk governance
- Capital allocation
- Performance tracking

It receives trade proposals from agents and determines:
- Whether the trade should be accepted
- How much capital should be allocated
- How it affects the entire portfolio

---

## 4. Portfolio Model

### Core Models

| Model | Purpose |
|-------|---------|
| `PortfolioState` | Snapshot of portfolio |
| `Position` | Individual holding |
| `CapitalAllocation` | Allocation distribution |
| `PortfolioMetrics` | Performance statistics |
| `TradeProposal` | Agent trade proposal |
| `RiskLimits` | Risk configuration |
| `PortfolioSignal` | System signals |

### Allocation Tiers

| Tier | Description |
|------|-------------|
| STABILITY | Emergency capital (20%) |
| DEBT | Liability reduction (25%) |
| INCOME | Income strategies (15%) |
| INVESTMENT | Long-term investing (30%) |
| TACTICAL | Active trading (10%) |

---

## 5. Portfolio Allocator

**Responsibilities:**
- Calculate tier allocations
- Determine available capital
- Validate allocation requests
- Detect rebalancing needs

**Methods:**
- `calculate_allocation()` - Get tier allocation
- `can_allocate()` - Check if allocation possible
- `rebalance_required()` - Detect drift

---

## 6. Position Manager

**Responsibilities:**
- Track open positions
- Calculate profit/loss
- Manage exits
- Track exposure

**Methods:**
- `open_position()` - Open new position
- `close_position()` - Close position
- `update_positions()` - Update with market prices
- `check_stop_loss()` - Validate stop loss
- `check_take_profit()` - Validate take profit

---

## 7. Risk Controller

**Risk Limits:**

| Metric | Limit |
|--------|-------|
| Max trade risk | 2% |
| Max portfolio exposure | 50% |
| Max drawdown | 10% |
| Max position concentration | 20% |
| Max daily loss | 5% |

**Methods:**
- `validate_trade()` - Check trade against limits
- `get_portfolio_risk()` - Calculate risk metrics
- `check_risk_limits()` - Validate all limits
- `calculate_var()` - Value at Risk

---

## 8. Performance Tracker

**Metrics Tracked:**

| Metric | Purpose |
|--------|---------|
| Win rate | Trade success |
| Expectancy | Expected return |
| Sharpe ratio | Risk adjusted return |
| Drawdown | Risk evaluation |
| Profit factor | Strategy health |

**Methods:**
- `calculate_metrics()` - Compute all metrics
- `get_win_rate()` - Win percentage
- `get_expectancy()` - Trade expectancy
- `get_sharpe_ratio()` - Risk-adjusted return

---

## 9. Portfolio Rebalancer

**Trigger Conditions:**

| Condition | Action |
|-----------|--------|
| Allocation drift > 5% | Rebalance |
| Volatility spike | Reduce risk |
| Strategy underperformance | Reduce allocation |

**Methods:**
- `should_rebalance()` - Check rebalance need
- `get_rebalance_actions()` - Get action list
- `execute_rebalance()` - Perform rebalancing

---

## 10. Integration with Investment Agents

**Workflow:**

```
Investment Agent
↓
Trade Proposal
↓
Portfolio Engine
↓
Risk Controller
↓
Capital Allocator
↓
Position Manager
↓
Simulation Engine
↓
CFO Review
```

---

## 11. Portfolio Signals

| Signal | Meaning | Severity |
|--------|---------|-----------|
| overexposed | Too much capital deployed | High |
| underutilized | Idle capital | Medium |
| strategy_degradation | Performance dropping | Low |
| risk_spike | Volatility increasing | High |

---

## 12. Executive Portfolio Report

**Example:**

```
Portfolio Report
===============

Equity: $12,500
Cash: $4,200

Exposure:
Tactical: 8%
Investment: 28%

Performance:
Win Rate: 61%
Sharpe Ratio: 1.42
Drawdown: 3.8%
```

---

## 13. Performance Goals

| Metric | Goal |
|--------|------|
| Risk per trade | ≤ 2% |
| Portfolio drawdown | ≤ 10% |
| Sharpe ratio | ≥ 1.5 |
| Trade expectancy | Positive |

---

## 14. Validation Tests

### Test 1: Trade Evaluation

**Input:** Trade proposal received

**Expected:** Portfolio engine evaluates allocation

### Test 2: Risk Limit

**Input:** Portfolio exposure exceeds threshold

**Expected:** Risk controller blocks new trades

### Test 3: Rebalancing

**Input:** Strategy underperforms

**Expected:** Allocation reduced

---

## 15. Status: ✅ IMPLEMENTED

All components operational:

- ✅ Portfolio engine tracks all positions
- ✅ Allocation system functions
- ✅ Risk controller blocks unsafe trades
- ✅ Performance tracker calculates metrics
- ✅ Portfolio reports generate
- ✅ Integration with SPY 0DTE agent
- ✅ CFO review workflow

---

## 16. Next Directive

Following successful implementation:

**BB-FIN-013**

Security Selection Intelligence Engine

This module will enable Busy Bee to:
- Evaluate stocks
- Rank investment opportunities
- Generate portfolio recommendations
- Identify high probability trades across assets

---

**✅ Directive BB-FIN-012 Complete**
