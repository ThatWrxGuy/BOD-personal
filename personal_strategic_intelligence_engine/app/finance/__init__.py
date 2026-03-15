"""Finance Module - Complete Financial Intelligence Platform.

This module implements:
- V19-001: Canonical financial state layer
- V19-002: Finance Intelligence Layer
- V19-003: Financial Scenario Simulation Engine
- V19-004: Financial Governance & Board Reporting

The module provides:
- Financial domain models (FinancialProfile, Asset, Liability, CashFlowRecord, FinancialAssumptions, FinancialSnapshot)
- Financial state aggregation engine (FinancialStateEngine)
- Core financial calculators (Net Worth, Cash Flow, Liquidity, Debt, Health Score)
- Financial snapshot system for audit trails
- Financial intelligence (risk detection, opportunity detection, recommendations, confidence scoring)
- Financial simulation (debt payoff, stress testing, shock modeling, allocation projection)
- Financial governance (board briefs, decision routing, audit logging)

No financial execution or automation is implemented. All outputs remain advisory.
"""

from app.finance import models
from app.finance import engine
from app.finance import services
from app.finance import api
from app.finance import intelligence
from app.finance import simulation
from app.finance import governance

__all__ = ["models", "engine", "services", "api", "intelligence", "simulation", "governance"]
