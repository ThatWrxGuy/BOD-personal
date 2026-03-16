"""Strategy Registry Module - BB-FIN-020

Maintains catalog of strategies with versioning and lifecycle management.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    StrategyStatus,
    StrategyCategory,
    MarketRegime,
)

logger = logging.getLogger(__name__)


class StrategyRegistry:
    """Manages strategy catalog and lifecycle."""
    
    def __init__(self):
        self._strategies: Dict[str, StrategyDefinition] = {}
        self._versions: Dict[str, List[str]] = {}  # strategy_id -> [versions]
        self._status_index: Dict[StrategyStatus, List[str]] = {}
        
        # Initialize with some default strategies
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize with some baseline strategies."""
        default_strategies = [
            StrategyDefinition(
                strategy_id="momentum_breakout",
                name="Momentum Breakout",
                description="Trades breakouts from consolidation patterns with volume confirmation",
                category=StrategyCategory.BREAKOUT_MOMENTUM,
                compatible_regimes=[MarketRegime.RISK_ON_TREND, MarketRegime.RISK_ON_MOMENTUM],
                incompatible_regimes=[MarketRegime.VOLATILITY_STRESS, MarketRegime.RISK_OFF_DEFENSIVE],
                tags=["momentum", "breakout", "volume"],
            ),
            StrategyDefinition(
                strategy_id="liquidity_sweep_reversal",
                name="Liquidity Sweep Reversal",
                description="Enters when liquidity pools are swept and price reverses",
                category=StrategyCategory.LIQUIDITY_SWEEP_REVERSAL,
                compatible_regimes=[MarketRegime.LIQUIDITY_DISLOCATION, MarketRegime.RISK_OFF_DEFENSIVE],
                incompatible_regimes=[MarketRegime.RISK_ON_TREND],
                tags=["liquidity", "reversal", "smart_money"],
            ),
            StrategyDefinition(
                strategy_id="opening_range_breakout",
                name="Opening Range Breakout",
                description="Trades breakouts from the first 15-30 minutes range",
                category=StrategyCategory.OPENING_RANGE_BREAKOUT,
                compatible_regimes=[MarketRegime.RISK_ON_MOMENTUM, MarketRegime.NEUTRAL_MIXED],
                incompatible_regimes=[MarketRegime.VOLATILITY_STRESS],
                tags=["intraday", "opening", "breakout"],
            ),
            StrategyDefinition(
                strategy_id="vwap_reclaim",
                name="VWAP Reclaim",
                description="Trades price reclaiming VWAP after deviation",
                category=StrategyCategory.VWAP_RECLAIM,
                compatible_regimes=[MarketRegime.NEUTRAL_MIXED, MarketRegime.RISK_ON_MOMENTUM],
                incompatible_regimes=[MarketRegime.VOLATILITY_STRESS],
                tags=["vwap", "mean_reversion", "intraday"],
            ),
            StrategyDefinition(
                strategy_id="gamma_magnet",
                name="Gamma Magnet Strategy",
                description="Captures gamma squeeze movements around key levels",
                category=StrategyCategory.GAMMA_MAGNET,
                compatible_regimes=[MarketRegime.VOLATILITY_STRESS, MarketRegime.RISK_ON_MOMENTUM],
                incompatible_regimes=[MarketRegime.RANGE_COMPRESSION],
                tags=["options", "gamma", "volatility"],
            ),
            StrategyDefinition(
                strategy_id="trend_continuation",
                name="Trend Continuation",
                description="Follows trend after pullback to key moving averages",
                category=StrategyCategory.TREND_CONTINUATION,
                compatible_regimes=[MarketRegime.RISK_ON_TREND],
                incompatible_regimes=[MarketRegime.RISK_OFF_DEFENSIVE, MarketRegime.MEAN_REVERSION],
                tags=["trend", "moving_average", "pullback"],
            ),
            StrategyDefinition(
                strategy_id="volatility_compression_breakout",
                name="Volatility Compression Breakout",
                description="Trades breakouts from low volatility compression zones",
                category=StrategyCategory.VOLATILITY_COMPRESSION,
                compatible_regimes=[MarketRegime.RANGE_COMPRESSION, MarketRegime.NEUTRAL_MIXED],
                incompatible_regimes=[MarketRegime.VOLATILITY_STRESS],
                tags=["volatility", "compression", "breakout"],
            ),
            StrategyDefinition(
                strategy_id="mean_reversion",
                name="Mean Reversion",
                description="Trades price returning to moving average after deviation",
                category=StrategyCategory.MEAN_REVERSION,
                compatible_regimes=[MarketRegime.MEAN_REVERSION, MarketRegime.RANGE_COMPRESSION],
                incompatible_regimes=[MarketRegime.RISK_ON_TREND],
                tags=["mean_reversion", "oversold", "overbought"],
            ),
        ]
        
        for strategy in default_strategies:
            self.register_strategy(strategy)
        
        logger.info(f"Initialized {len(default_strategies)} default strategies")
    
    def register_strategy(self, strategy: StrategyDefinition) -> bool:
        """Register a new strategy."""
        
        if strategy.strategy_id in self._strategies:
            logger.warning(f"Strategy {strategy.strategy_id} already exists, updating")
        
        self._strategies[strategy.strategy_id] = strategy
        
        # Track versions
        if strategy.strategy_id not in self._versions:
            self._versions[strategy.strategy_id] = []
        if strategy.version not in self._versions[strategy.strategy_id]:
            self._versions[strategy.strategy_id].append(strategy.version)
        
        # Index by status
        status = StrategyStatus.ACTIVE if not strategy.status else strategy.status
        if status not in self._status_index:
            self._status_index[status] = []
        if strategy.strategy_id not in self._status_index[status]:
            self._status_index[status].append(strategy.strategy_id)
        
        logger.info(f"Registered strategy: {strategy.strategy_id} v{strategy.version}")
        return True
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyDefinition]:
        """Get a strategy by ID."""
        return self._strategies.get(strategy_id)
    
    def get_all_strategies(self) -> List[StrategyDefinition]:
        """Get all registered strategies."""
        return list(self._strategies.values())
    
    def get_strategies_by_status(self, status: StrategyStatus) -> List[StrategyDefinition]:
        """Get strategies by status."""
        strategy_ids = self._status_index.get(status, [])
        return [self._strategies[sid] for sid in strategy_ids if sid in self._strategies]
    
    def get_strategies_by_category(self, category: StrategyCategory) -> List[StrategyDefinition]:
        """Get strategies by category."""
        return [s for s in self._strategies.values() if s.category == category]
    
    def get_strategies_for_regime(self, regime: MarketRegime) -> List[StrategyDefinition]:
        """Get strategies compatible with a given regime."""
        compatible = []
        for strategy in self._strategies.values():
            if regime in strategy.compatible_regimes:
                compatible.append(strategy)
            elif regime in strategy.incompatible_regimes:
                continue
            else:
                # Neutral - include with lower priority
                compatible.append(strategy)
        return compatible
    
    def update_strategy_status(self, strategy_id: str, status: StrategyStatus) -> bool:
        """Update strategy status."""
        strategy = self._strategies.get(strategy_id)
        if not strategy:
            return False
        
        # Remove from old status index
        old_status = getattr(strategy, 'status', StrategyStatus.ACTIVE)
        if old_status in self._status_index:
            if strategy_id in self._status_index[old_status]:
                self._status_index[old_status].remove(strategy_id)
        
        # Update status
        strategy.status = status
        strategy.updated_at = datetime.utcnow()
        
        # Add to new status index
        if status not in self._status_index:
            self._status_index[status] = []
        if strategy_id not in self._status_index[status]:
            self._status_index[status].append(strategy_id)
        
        logger.info(f"Updated strategy {strategy_id} status to {status}")
        return True
    
    def enable_strategy(self, strategy_id: str) -> bool:
        """Enable a strategy."""
        return self.update_strategy_status(strategy_id, StrategyStatus.ACTIVE)
    
    def disable_strategy(self, strategy_id: str) -> bool:
        """Disable a strategy."""
        return self.update_strategy_status(strategy_id, StrategyStatus.RETIRED)
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy."""
        if strategy_id not in self._strategies:
            return False
        
        strategy = self._strategies[strategy_id]
        
        # Remove from status index
        status = getattr(strategy, 'status', StrategyStatus.ACTIVE)
        if status in self._status_index:
            if strategy_id in self._status_index[status]:
                self._status_index[status].remove(strategy_id)
        
        # Remove from registry
        del self._strategies[strategy_id]
        
        logger.info(f"Deleted strategy: {strategy_id}")
        return True
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        return {
            "total_strategies": len(self._strategies),
            "active_strategies": len(self._status_index.get(StrategyStatus.ACTIVE, [])),
            "testing_strategies": len(self._status_index.get(StrategyStatus.TESTING, [])),
            "retired_strategies": len(self._status_index.get(StrategyStatus.RETIRED, [])),
            "by_category": {
                cat.value: len([s for s in self._strategies.values() if s.category == cat])
                for cat in StrategyCategory
            },
        }


# Global registry instance
_strategy_registry: Optional[StrategyRegistry] = None


def get_strategy_registry() -> StrategyRegistry:
    """Get the global strategy registry."""
    global _strategy_registry
    
    if _strategy_registry is None:
        _strategy_registry = StrategyRegistry()
    
    return _strategy_registry
