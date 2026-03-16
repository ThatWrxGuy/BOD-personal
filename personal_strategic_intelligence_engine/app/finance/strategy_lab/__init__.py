"""Strategy Lab Module - BB-FIN-020

Strategy Lab & Edge Discovery Engine for the Busy Bee Finance Platform.

This module provides:
- Strategy discovery from market patterns
- Backtesting engine
- Monte Carlo simulation
- Regime performance analysis
- Strategy scoring and ranking
"""

from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    StrategySignal,
    BacktestResult,
    BacktestTrade,
    PerformanceMetrics,
    MonteCarloSimulation,
    RegimePerformance,
    StrategyRobustnessProfile,
    StrategyRanking,
    StrategyLeaderboard,
    StrategySimulationReport,
    StrategyLabStatus,
    StrategyCategory,
    StrategyStatus,
    MarketRegime,
)

from app.finance.strategy_lab.strategy_lab_service import (
    StrategyLabService,
    get_strategy_lab_service,
)

__all__ = [
    # Models
    "StrategyDefinition",
    "StrategySignal",
    "BacktestResult",
    "BacktestTrade",
    "PerformanceMetrics",
    "MonteCarloSimulation",
    "RegimePerformance",
    "StrategyRobustnessProfile",
    "StrategyRanking",
    "StrategyLeaderboard",
    "StrategySimulationReport",
    "StrategyLabStatus",
    "StrategyCategory",
    "StrategyStatus",
    "MarketRegime",
    # Service
    "StrategyLabService",
    "get_strategy_lab_service",
]
