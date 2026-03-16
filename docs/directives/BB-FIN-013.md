# Directive BB-FIN-013

Security Selection Intelligence Engine

Classification: Finance Intelligence Directive
Authority: CEO (User)
Priority: Strategic
Target System: Busy Bee / PSIE Finance Domain
Status: ✅ IMPLEMENTED
Objective: Implement an intelligence engine capable of evaluating, scoring, ranking, and recommending securities for investment or tactical deployment based on quantitative, technical, structural, and strategic criteria.

---

## 1. Purpose

Busy Bee currently has:
- Portfolio management capability (BB-FIN-012)
- Tactical trade intelligence (BB-FIN-011)
- Capital allocation logic
- Risk controls

This directive introduces the **Security Selection Intelligence Engine (SSIE)**.

The SSIE acts as the security discovery and ranking layer of the finance domain.

Its purpose is to:
- Scan candidate securities
- Evaluate quality and suitability
- Score opportunities
- Rank them by expected utility
- Submit recommendations to the Finance system

This expands Busy Bee from a system that can manage trades and portfolios into a system that can also choose what deserves capital allocation.

---

## 2. Architecture

**Location:** `app/finance/security_selection/`

**Modules:**

| File | Purpose |
|------|---------|
| `security_selection_engine.py` | Main orchestration |
| `selection_models.py` | Data models |
| `universe_manager.py` | Universe definition |
| `security_screener.py` | Quality filtering |
| `factor_scoring_engine.py` | Weighted scoring |
| `opportunity_ranker.py` | Ranking logic |
| `conviction_engine.py` | Conviction determination |
| `recommendation_engine.py` | Recommendation generation |

---

## 3. Core Role

The Security Selection Intelligence Engine performs five main functions:

| Function | Purpose |
|----------|---------|
| Universe Definition | Determine eligible securities |
| Screening | Remove low-quality candidates |
| Scoring | Assign weighted scores |
| Ranking | Order by attractiveness |
| Recommendation | Submit best ideas to finance |

Supports both:
- Long-term investments
- Tactical opportunities

---

## 4. Universe Manager

**Capabilities:**
- Define security universes
- Manage categories (Core, Investment, Tactical, Income, Options)
- Add/remove securities
- Filter by strategy type

**Default Universes:**

| Universe | Examples |
|----------|----------|
| Core ETFs | SPY, QQQ, DIA, IWM, VOO, VTI |
| Quality Stocks | AAPL, MSFT, GOOGL, AMZN, NVDA |
| Dividend | SCHD, VYM, VNQ, VIG |
| Tactical | SPY, QQQ, IWM, TLT, GLD |

---

## 5. Security Screener

**Screening Criteria:**

| Criterion | Threshold |
|-----------|-----------|
| Min Volume | 500,000 |
| Min Avg Volume | 300,000 |
| Min Market Cap | $1B |
| Max Spread | 2% |
| Min Price | $1.00 |

**Outputs:**
- Eligible list
- Rejected list
- Rejection reasons
- Warnings

---

## 6. Factor Scoring Engine

**Scoring Dimensions:**

| Factor | Weight (Default) |
|--------|-----------------|
| Trend Quality | 20% |
| Momentum | 20% |
| Relative Strength | 15% |
| Liquidity | 15% |
| Volatility Quality | 10% |
| Risk/Reward | 20% |

**Strategy-Specific Weights:**

| Strategy | Key Factors |
|----------|-------------|
| Investment | Fundamental Quality (35%) |
| Tactical | Trend + Momentum (50%) |
| Options | Options Quality (20%) |

---

## 7. Opportunity Ranker

**Ranking Outputs:**

| Output | Meaning |
|--------|---------|
| Rank | Placement |
| Score | Total opportunity score |
| Category | Investment / Tactical |
| Conviction | Confidence level |
| Capital Fit | Allocation bucket |

---

## 8. Conviction Engine

**Conviction Levels:**

| Level | Score Threshold |
|-------|-----------------|
| EXCEPTIONAL | 85+ |
| HIGH | 70+ |
| MODERATE | 50+ |
| LOW | <50 |

**Features:**
- Regime adjustment
- Historical tracking
- Accuracy metrics

---

## 9. Recommendation Engine

**Example Output:**

```
Security Recommendation
======================

Symbol: NVDA
Category: Investment
Score: 87
Conviction: High
Allocation Bucket: Investment
Suggested Weight: 4%

Rationale:
- Strong trend quality
- High relative strength
- Favorable liquidity
```

---

## 10. Selection Models

**Core Models:**

| Model | Purpose |
|-------|---------|
| SecurityProfile | Core security attributes |
| ScreenResult | Pass/fail screening |
| SecurityScore | Factor scores |
| RankedOpportunity | Final ranked result |
| SecurityRecommendation | Recommendation object |

---

## 11. Integration with Portfolio Engine

**Workflow:**

```
Universe Manager
    ↓
Security Screener
    ↓
Factor Scoring Engine
    ↓
Opportunity Ranker
    ↓
Conviction Engine
    ↓
Recommendation Engine
    ↓
Portfolio Engine
    ↓
Risk Controller
    ↓
CFO Review
```

---

## 12. Integration with SPY 0DTE Agent

**Tactical Escalation:**

```
SSIE ranks SPY as top tactical
    ↓
SPY 0DTE Agent activated
    ↓
Strike selection begins
```

This prevents forcing tactical trades when underlying isn't attractive.

---

## 13. Allocation Fit

**Bucket Mapping:**

| Bucket | Use |
|--------|-----|
| Investment | Long-term holdings |
| Tactical | Short-term, SPY 0DTE |
| Income | Covered calls, yield |
| Stability | Cash, reserves |

---

## 14. Executive Reporting

**Example:**

```
Security Selection Report
========================

Top Ranked Opportunities

1. NVDA - Score 87 - High Conviction - Investment
2. SPY - Score 84 - High Conviction - Tactical
3. MSFT - Score 81 - Moderate Conviction - Investment
```

---

## 15. Performance Tracking

**Metrics:**

| Metric | Meaning |
|--------|---------|
| Hit Rate | % of ideas that worked |
| Forward Return | Performance after selection |
| Conviction Accuracy | High conviction outperformance |
| Category Performance | Investment vs Tactical results |

---

## 16. Adaptive Learning

**Capabilities:**
- Adjust factor weights
- Downgrade unreliable signals
- Learn regime-factor relationships
- Identify recurring patterns

---

## 17. Governance

**Authority Chain:**

```
Security Selection Engine
    ↓
Portfolio Engine
    ↓
Risk Controller
    ↓
Chief Financial Officer
    ↓
CEO Approval
```

---

## 18. Status: ✅ IMPLEMENTED

All components operational:

- ✅ Universe management
- ✅ Security screening
- ✅ Factor scoring
- ✅ Opportunity ranking
- ✅ Conviction levels
- ✅ Recommendations
- ✅ Portfolio integration
- ✅ Tactical escalation
- ✅ Executive reporting
- ✅ Adaptive learning

---

## 19. Next Directive

**BB-FIN-014**

Multi-Asset Market Intelligence & Regime Engine

This directive will expand the finance system to understand:
- Market regime
- Cross-asset relationships
- Macro pressure
- Volatility environment
- Sector leadership
- Risk-on / risk-off conditions

---

**✅ Directive BB-FIN-013 Complete**
