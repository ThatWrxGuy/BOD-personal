# BB-INF-007: Live Market Data Integrity & Anti-Stale Pricing Enforcement

**Status**: Implemented

**Priority**: Critical

**Owner**: Infrastructure / Finance / Intelligence Council

**Related Directives**:
- BB-001A — Busy Bee Executive Architecture
- BB-INF-005 — External Intelligence Governance & Execution Safety
- BB-INF-006 — Credential Rotation & Secrets Management Hardening
- BB-FIN Series — Finance intelligence, allocation, strategy, and market intelligence directives

---

## 1. Purpose

Implement a canonical live market data enforcement layer across Busy Bee V1 so that:
- All price-dependent modules consume current live market data
- Pinned, placeholder, static, mocked, or default hardcoded price values are prohibited in runtime production pathways
- Stale or unverifiable prices cause the system to fail safely, not silently continue
- Every downstream recommendation, calculation, simulation, or report includes data freshness validation

This directive ensures the system never presents an investment, allocation, trading, or executive recommendation based on fabricated or outdated prices.

---

## 2. Problem Statement

The current system has live integration available, but some paths still allow price to be pinned to a default value. This creates critical risk:
- False portfolio valuation
- Incorrect position sizing
- Invalid risk calculations
- Misleading recommendations
- Hidden degradation in live trading or allocation logic
- Poor trustworthiness of executive outputs

The system must now operate under a strict principle:

> **No live-data-dependent decision may proceed using fallback static prices in production.**

---

## 3. Strategic Objective

Create a unified Market Data Truth Layer that becomes the single approved source for:
- Spot price
- Last trade
- Bid/ask
- Midpoint
- Timestamp
- Source/provider metadata
- Freshness state
- Market session state
- Confidence / validity flags

All finance and market intelligence components must be routed through this layer.

---

## 4. Implementation Summary

### 4.1 Canonical Price Service

Created subsystem: `app/infrastructure/market_data/`

Modules:
- `market_data_models.py` - Core data models
- `live_price_provider.py` - Fetches live prices
- `market_data_resolver.py` - Central resolver with validation
- `freshness_guard.py` - Validates quote freshness
- `market_session_guard.py` - Validates market session rules
- `price_integrity_auditor.py` - Monitors integrity
- `market_data_cache.py` - Manages caching
- `routes.py` - API endpoints

### 4.2 Core Data Models

Implemented:
- `LivePriceQuote` - Canonical quote model with all required fields
- `PriceValidationResult` - Validation results for decisioning
- `MarketDataPolicy` - Policy configuration
- `MarketDataIntegrityReport` - Integrity reporting

### 4.3 Strict Production Rule

Environment modes implemented:
- **LIVE**: No fallback allowed
- **PAPER**: Simulation allowed with labeling
- **BACKTEST**: Historical feed only
- **DEV**: Mock permitted with explicit flags

### 4.4 Decision Gate

Validation enforced for:
- Portfolio valuation
- Allocation strategist
- Security selection
- Options intelligence
- Risk governor
- Trade approval logic
- Executive reporting

---

## 5. API Endpoints

- `GET /market-data/quote/{symbol}` - Get live quote
- `GET /market-data/health/{symbol}` - Quote health status
- `POST /market-data/validate` - Validate a quote
- `GET /market-data/provider-status` - Provider health
- `GET /market-data/session` - Market session state
- `GET /market-data/integrity-report` - Integrity report
- `GET /market-data/cache-stats` - Cache statistics
- `POST /market-data/cache/invalidate` - Invalidate cache

---

## 6. Freshness Thresholds

| Asset Type | Ideal | Warning | Invalid |
|------------|-------|---------|---------|
| Equities | ≤5s | >5s | >15s |
| Options | ≤2s | >2s | >5s |
| ETFs | ≤5s | >5s | >15s |
| Index | ≤15s | >15s | >60s |
| Crypto | ≤1s | >1s | >5s |
| Reporting | ≤60s | >60s | >300s |

---

## 7. Governance Rules

If live data is unavailable, the system must respond with:
- "Live price unavailable"
- "Quote stale; decision deferred"
- "Provider validation failed"
- "Using simulation mode data" (only in non-live environments)

---

## 8. Acceptance Criteria

✅ All price consumers use unified market data resolver
✅ Every quote includes freshness and provenance metadata
✅ Stale or invalid prices block live decisioning
✅ Mock/simulated prices are isolated by environment
✅ Integrity logs and provider health reporting available
✅ No remaining prohibited fallback pricing logic
✅ Finance outputs distinguish live, cached, simulated, or unavailable data

---

## 9. Implementation Doctrine

> **Market data is a governed truth source, not a convenience input.**
> 
> **Any unavailable price is preferable to a false price.**
> 
> **The system must fail transparently, never improvise current market truth.**

---

*Generated: 2026-03-16*
