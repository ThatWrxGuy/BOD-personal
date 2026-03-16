"""Strategy Discovery Engine - BB-FIN-020

Generates candidate strategies from market patterns and intelligence.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import random

from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    StrategyCategory,
    MarketRegime,
    EntryCondition,
    ExitCondition,
    PositionSizing,
    TradeDirection,
)

logger = logging.getLogger(__name__)


class PatternSignal:
    """Represents a detected market pattern."""
    def __init__(
        self,
        pattern_type: str,
        confidence: float,
        regime: Optional[MarketRegime] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.pattern_type = pattern_type
        self.confidence = confidence
        self.regime = regime
        self.details = details or {}


class StrategyDiscoveryEngine:
    """Discovers and generates candidate strategies."""
    
    # Pattern templates for strategy generation
    PATTERN_TEMPLATES = {
        "breakout": {
            "entry_conditions": [
                {"type": "price_breakout", "param": "high_{period}"},
                {"type": "volume_confirmation", "param": "150%"},
            ],
            "exit_conditions": [
                {"type": "trailing_stop", "param": "atr", "value": 2.0},
                {"type": "time_based", "param": "periods", "value": 10},
            ],
            "categories": [StrategyCategory.BREAKOUT_MOMENTUM, StrategyCategory.OPENING_RANGE_BREAKOUT],
            "compatible_regimes": [MarketRegime.RISK_ON_TREND, MarketRegime.RISK_ON_MOMENTUM],
        },
        "mean_reversion": {
            "entry_conditions": [
                {"type": "price_deviation", "param": "ema_20", "value": -2.0},
                {"type": "oversold", "param": "rsi", "value": 30},
            ],
            "exit_conditions": [
                {"type": "profit_target", "param": "atr", "value": 2.0},
                {"type": "stop_loss", "param": "atr", "value": 1.5},
            ],
            "categories": [StrategyCategory.MEAN_REVERSION, StrategyCategory.VWAP_RECLAIM],
            "compatible_regimes": [MarketRegime.MEAN_REVERSION, MarketRegime.RANGE_COMPRESSION],
        },
        "momentum": {
            "entry_conditions": [
                {"type": "trend_above", "param": "ema_50"},
                {"type": "momentum_confirmation", "param": "rsi", "value": 60},
            ],
            "exit_conditions": [
                {"type": "trailing_stop", "param": "sma", "value": 0.02},
                {"type": "trend_reversal", "param": "ema_20"},
            ],
            "categories": [StrategyCategory.TREND_CONTINUATION, StrategyCategory.MOMENTUM_BREAKOUT],
            "compatible_regimes": [MarketRegime.RISK_ON_TREND, MarketRegime.RISK_ON_MOMENTUM],
        },
        "liquidity": {
            "entry_conditions": [
                {"type": "liquidity_sweep", "param": "recent_low"},
                {"type": "order_block", "param": "zone_identification"},
            ],
            "exit_conditions": [
                {"type": "profit_target", "param": "risk_reward", "value": 2.0},
                {"type": "stop_loss", "param": "swing_low", "value": 1.0},
            ],
            "categories": [StrategyCategory.LIQUIDITY_SWEEP_REVERSAL],
            "compatible_regimes": [MarketRegime.LIQUIDITY_DISLOCATION, MarketRegime.RISK_OFF_DEFENSIVE],
        },
        "volatility": {
            "entry_conditions": [
                {"type": "volatility_compression", "param": "atr_percentile", "value": 10},
                {"type": "range_boundary", "param": "high_low"},
            ],
            "exit_conditions": [
                {"type": "volatility_expansion", "param": "atr_multiplier", "value": 2.0},
                {"type": "time_based", "param": "periods", "value": 5},
            ],
            "categories": [StrategyCategory.VOLATILITY_COMPRESSION, StrategyCategory.GAMMA_MAGNET],
            "compatible_regimes": [MarketRegime.RANGE_COMPRESSION, MarketRegime.VOLATILITY_STRESS],
        },
    }
    
    def __init__(self):
        self._discovered_strategies: List[StrategyDefinition] = []
        self._pattern_cache: List[PatternSignal] = []
    
    def discover_from_patterns(
        self,
        patterns: Optional[List[PatternSignal]] = None,
        min_confidence: float = 0.6,
    ) -> List[StrategyDefinition]:
        """Discover strategies from detected market patterns."""
        
        if patterns is None:
            # Use cached patterns or generate demo patterns
            patterns = self._get_demo_patterns()
        
        discovered = []
        
        for pattern in patterns:
            if pattern.confidence < min_confidence:
                continue
            
            # Find matching templates
            templates = self._find_matching_templates(pattern)
            
            for template in templates:
                strategy = self._generate_strategy_from_template(
                    pattern, template
                )
                if strategy:
                    discovered.append(strategy)
                    self._discovered_strategies.append(strategy)
        
        logger.info(f"Discovered {len(discovered)} strategies from {len(patterns)} patterns")
        return discovered
    
    def _get_demo_patterns(self) -> List[PatternSignal]:
        """Generate demo patterns for testing."""
        return [
            PatternSignal(
                pattern_type="breakout",
                confidence=0.75,
                regime=MarketRegime.RISK_ON_TREND,
                details={"symbol": "SPY", "breakout_type": "intraday_high"},
            ),
            PatternSignal(
                pattern_type="mean_reversion",
                confidence=0.65,
                regime=MarketRegime.MEAN_REVERSION,
                details={"symbol": "QQQ", "deviation_percent": -2.5},
            ),
            PatternSignal(
                pattern_type="liquidity",
                confidence=0.70,
                regime=MarketRegime.LIQUIDITY_DISLOCATION,
                details={"symbol": "SPY", "liquidity_level": "major_low"},
            ),
            PatternSignal(
                pattern_type="volatility",
                confidence=0.80,
                regime=MarketRegime.RANGE_COMPRESSION,
                details={"symbol": "SPY", "compression_days": 5},
            ),
        ]
    
    def _find_matching_templates(self, pattern: PatternSignal) -> List[Dict]:
        """Find templates matching the detected pattern."""
        matching = []
        
        # Direct match by pattern type
        if pattern.pattern_type in self.PATTERN_TEMPLATES:
            matching.append(self.PATTERN_TEMPLATES[pattern.pattern_type])
        
        # Also include related patterns based on regime
        regime_templates = {
            MarketRegime.RISK_ON_TREND: ["momentum", "breakout"],
            MarketRegime.RISK_ON_MOMENTUM: ["momentum", "breakout"],
            MarketRegime.MEAN_REVERSION: ["mean_reversion"],
            MarketRegime.RANGE_COMPRESSION: ["volatility", "mean_reversion"],
            MarketRegime.VOLATILITY_STRESS: ["volatility", "liquidity"],
            MarketRegime.LIQUIDITY_DISLOCATION: ["liquidity"],
            MarketRegime.RISK_OFF_DEFENSIVE: ["liquidity", "mean_reversion"],
        }
        
        if pattern.regime and pattern.regime in regime_templates:
            for pt in regime_templates[pattern.regime]:
                if pt in self.PATTERN_TEMPLATES and self.PATTERN_TEMPLATES[pt] not in matching:
                    matching.append(self.PATTERN_TEMPLATES[pt])
        
        return matching
    
    def _generate_strategy_from_template(
        self,
        pattern: PatternSignal,
        template: Dict,
    ) -> Optional[StrategyDefinition]:
        """Generate a strategy definition from a template."""
        
        # Generate unique ID
        strategy_id = f"{pattern.pattern_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Build entry conditions
        entry_conditions = []
        for ec in template.get("entry_conditions", []):
            entry_conditions.append(EntryCondition(
                condition_type=ec["type"],
                parameter=ec.get("param", ""),
                value=ec.get("value"),
            ))
        
        # Build exit conditions
        exit_conditions = []
        for ec in template.get("exit_conditions", []):
            exit_conditions.append(ExitCondition(
                condition_type=ec["type"],
                parameter=ec.get("param", ""),
                value=ec.get("value"),
            ))
        
        # Get category
        category = template["categories"][0] if template.get("categories") else StrategyCategory.TREND_CONTINUATION
        
        # Build strategy
        strategy = StrategyDefinition(
            strategy_id=strategy_id,
            name=f"{category.value.replace('_', ' ').title()} - {pattern.pattern_type.title()}",
            description=f"Auto-discovered strategy from {pattern.pattern_type} pattern with {pattern.confidence:.0%} confidence",
            category=category,
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
            position_sizing=PositionSizing(
                method="percent_risk",
                value=0.02,
                max_positions=5,
            ),
            target_assets=[pattern.details.get("symbol", "SPY")] if pattern.details else ["SPY"],
            asset_classes=["equity"],
            trade_direction=TradeDirection.BOTH,
            timeframe="intraday",
            compatible_regimes=template.get("compatible_regimes", []),
            incompatible_regimes=[],
            created_by="discovery_engine",
            tags=[pattern.pattern_type, "auto_discovered"],
        )
        
        return strategy
    
    def discover_from_alpha_signals(
        self,
        alpha_signals: Optional[List[Dict]] = None,
    ) -> List[StrategyDefinition]:
        """Discover strategies from alpha engine signals."""
        
        # This would integrate with BB-FIN-XXX (Alpha Engine)
        # For now, return demo discoveries
        
        if alpha_signals is None:
            alpha_signals = [
                {"signal": "momentum_continuation", "strength": 0.75, "assets": ["SPY", "QQQ"]},
                {"signal": "mean_reversion_setup", "strength": 0.65, "assets": ["IWM"]},
            ]
        
        discovered = []
        
        for signal in alpha_signals:
            strategy_id = f"alpha_{signal['signal']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            strategy = StrategyDefinition(
                strategy_id=strategy_id,
                name=f"Alpha: {signal['signal'].replace('_', ' ').title()}",
                description=f"Strategy derived from alpha signal: {signal['signal']}",
                category=StrategyCategory.TREND_CONTINUATION,  # Would map based on signal type
                entry_conditions=[
                    EntryCondition(
                        condition_type="alpha_confirmation",
                        parameter=signal["signal"],
                        value=signal["strength"],
                    )
                ],
                exit_conditions=[
                    ExitCondition(
                        condition_type="signal_reversal",
                        parameter=signal["signal"],
                        value=0.3,
                    )
                ],
                position_sizing=PositionSizing(
                    method="percent_risk",
                    value=0.015,
                    max_positions=3,
                ),
                target_assets=signal.get("assets", ["SPY"]),
                asset_classes=["equity"],
                trade_direction=TradeDirection.BOTH,
                created_by="alpha_engine",
                tags=["alpha", signal["signal"]],
            )
            
            discovered.append(strategy)
        
        logger.info(f"Discovered {len(discovered)} strategies from alpha signals")
        return discovered
    
    def get_discovered_strategies(self) -> List[StrategyDefinition]:
        """Get all discovered strategies."""
        return self._discovered_strategies.copy()
    
    def clear_discovered(self) -> None:
        """Clear discovered strategy cache."""
        self._discovered_strategies.clear()
        logger.info("Cleared discovered strategies cache")


# Global instance
_strategy_discovery_engine: Optional[StrategyDiscoveryEngine] = None


def get_strategy_discovery_engine() -> StrategyDiscoveryEngine:
    """Get the strategy discovery engine."""
    global _strategy_discovery_engine
    
    if _strategy_discovery_engine is None:
        _strategy_discovery_engine = StrategyDiscoveryEngine()
    
    return _strategy_discovery_engine
