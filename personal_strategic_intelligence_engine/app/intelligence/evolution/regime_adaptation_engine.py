"""Regime Adaptation Engine.

Detects and adapts to changing market regimes.
"""

from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.evolution.evolution_models import (
    RegimeAnalysis,
    RegimeType,
    QuantitativeMetrics,
)


class RegimeAdaptationEngine:
    """Adapts to changing market regimes."""
    
    def __init__(self):
        self.current_regime: Optional[RegimeType] = None
        self.regime_history: List[RegimeAnalysis] = []
    
    def detect_regime(
        self,
        market_data: Dict,
    ) -> RegimeType:
        """Detect current market regime."""
        
        # Analyze market conditions
        vwap_state = market_data.get("vwap_state", "neutral")
        volatility = market_data.get("volatility_state", "normal")
        price_trend = market_data.get("price_trend", "neutral")
        volume = market_data.get("volume", 0)
        avg_volume = market_data.get("avg_volume", 0)
        
        # Determine regime
        if price_trend == "up" and volatility == "expansion":
            regime = RegimeType.TREND_UP
        elif price_trend == "down" and volatility == "expansion":
            regime = RegimeType.TREND_DOWN
        elif volatility == "compression":
            regime = RegimeType.VOLATILITY_COMPRESS
        elif volatility == "spike":
            regime = RegimeType.VOLATILITY_EXPAND
        elif volume < avg_volume * 0.7:
            regime = RegimeType.LOW_PARTICIPATION
        else:
            regime = RegimeType.RANGE_CHOP
        
        self.current_regime = regime
        return regime
    
    def analyze_regime(
        self,
        regime: RegimeType,
        historical_data: List[Dict],
    ) -> RegimeAnalysis:
        """Analyze performance for a specific regime."""
        
        # Filter data by regime
        regime_data = [d for d in historical_data if d.get("regime") == regime.value]
        
        # Calculate performance metrics
        metrics = self._calculate_regime_metrics(regime_data)
        
        # Determine recommended modifiers
        modifiers = self._calculate_modifiers(regime, metrics)
        
        # Calculate confidence adjustment
        confidence_adj = self._calculate_confidence_adjustment(metrics)
        
        return RegimeAnalysis(
            regime_type=regime,
            start_time=datetime.now(),
            characteristics=self._get_regime_characteristics(regime),
            tactical_performance=metrics,
            recommended_modifiers=modifiers,
            confidence_adjustment=confidence_adj,
        )
    
    def _calculate_regime_metrics(self, data: List[Dict]) -> QuantitativeMetrics:
        """Calculate metrics for regime."""
        
        if not data:
            return QuantitativeMetrics(
                expectancy=0, sharpe_ratio=0, sortino_ratio=0,
                win_rate=0, avg_win=0, avg_loss=0, max_drawdown=0,
                volatility_adjusted_return=0, reliability_index=0,
                total_trades=0, winning_trades=0, losing_trades=0,
            )
        
        pnls = [d.get("profit_loss", 0) or 0 for d in data if d.get("profit_loss")]
        
        if not pnls:
            return QuantitativeMetrics(
                expectancy=0, sharpe_ratio=0, sortino_ratio=0,
                win_rate=0, avg_win=0, avg_loss=0, max_drawdown=0,
                volatility_adjusted_return=0, reliability_index=0,
                total_trades=len(data), winning_trades=0, losing_trades=0,
            )
        
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 0
        
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        return QuantitativeMetrics(
            expectancy=expectancy,
            sharpe_ratio=expectancy / 10,
            sortino_ratio=expectancy / 8,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_drawdown=min(pnls) if pnls else 0,
            volatility_adjusted_return=expectancy,
            reliability_index=win_rate * 0.8,
            total_trades=len(data),
            winning_trades=len(wins),
            losing_trades=len(losses),
        )
    
    def _calculate_modifiers(self, regime: RegimeType, metrics: QuantitativeMetrics) -> Dict[str, float]:
        """Calculate strategy modifiers for regime."""
        
        modifiers = {}
        
        if regime in [RegimeType.TREND_UP, RegimeType.TREND_DOWN]:
            modifiers["position_size"] = 1.2
            modifiers["stop_width"] = 1.0
            modifiers["target_multiplier"] = 2.0
        elif regime == RegimeType.RANGE_CHOP:
            modifiers["position_size"] = 0.7
            modifiers["stop_width"] = 1.5
            modifiers["target_multiplier"] = 1.5
        elif regime == RegimeType.VOLATILITY_COMPRESS:
            modifiers["position_size"] = 0.8
            modifiers["stop_width"] = 1.2
            modifiers["target_multiplier"] = 1.8
        elif regime == RegimeType.VOLATILITY_EXPAND:
            modifiers["position_size"] = 0.6
            modifiers["stop_width"] = 2.0
            modifiers["target_multiplier"] = 2.5
        else:
            modifiers["position_size"] = 1.0
            modifiers["stop_width"] = 1.0
            modifiers["target_multiplier"] = 2.0
        
        return modifiers
    
    def _calculate_confidence_adjustment(self, metrics: QuantitativeMetrics) -> float:
        """Calculate confidence adjustment based on performance."""
        
        if metrics.total_trades < 10:
            return 0
        
        if metrics.expectancy > 15:
            return 10
        elif metrics.expectancy > 5:
            return 5
        elif metrics.expectancy > 0:
            return 0
        elif metrics.expectancy > -5:
            return -5
        else:
            return -10
    
    def _get_regime_characteristics(self, regime: RegimeType) -> Dict[str, any]:
        """Get characteristics of a regime."""
        
        characteristics = {
            RegimeType.TREND_UP: {
                "description": "Strong upward price movement",
                "typical_duration": "hours to days",
                "best_strategies": ["momentum", "trend_following"],
            },
            RegimeType.TREND_DOWN: {
                "description": "Strong downward price movement",
                "typical_duration": "hours to days",
                "best_strategies": ["momentum", "mean_reversion"],
            },
            RegimeType.RANGE_CHOP: {
                "description": "Sideways price action with low directional bias",
                "typical_duration": "hours",
                "best_strategies": ["range_trading", "mean_reversion"],
            },
            RegimeType.VOLATILITY_EXPAND: {
                "description": "Increasing volatility with directional moves",
                "typical_duration": "minutes to hours",
                "best_strategies": ["momentum", "volatility_breakout"],
            },
            RegimeType.VOLATILITY_COMPRESS: {
                "description": "Declining volatility, often before breakout",
                "typical_duration": "hours to days",
                "best_strategies": ["breakout", "volatility_arb"],
            },
            RegimeType.LOW_PARTICIPATION: {
                "description": "Low trading volume environment",
                "typical_duration": "variable",
                "best_strategies": ["caution", "reduced_size"],
            },
        }
        
        return characteristics.get(regime, {})
    
    def detect_regime_shift(
        self,
        old_regime: RegimeType,
        new_regime: RegimeType,
    ) -> bool:
        """Detect if regime has shifted."""
        return old_regime != new_regime


def create_engine() -> RegimeAdaptationEngine:
    """Create a new regime adaptation engine."""
    return RegimeAdaptationEngine()
