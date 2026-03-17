"""
BB-INT-007: SPY 0DTE Trade Brief Engine

Analyzes market signals and generates 0DTE trade intelligence.

Responsibilities:
- Analyze market regime
- Determine support/resistance levels
- Generate trade setup recommendations
- Provide position sizing and risk management

Usage:
    from app.intelligence.executive_brief import SpyTradeBriefEngine
    
    engine = SpyTradeBriefEngine()
    trade_brief = engine.generate_trade_brief(market_signals)
"""

from dataclasses import dataclass
from datetime import datetime
import random

from .executive_brief_models import (
    SpyTradeBrief,
    MarketRegime,
)


class SpyTradeBriefEngine:
    """
    Generates SPY 0DTE trade intelligence.
    
    Analyzes market conditions and provides actionable trade setups.
    """
    
    def __init__(self):
        self.last_brief: SpyTradeBrief | None = None
    
    def generate_trade_brief(
        self,
        market_signals: dict | None = None
    ) -> SpyTradeBrief:
        """
        Generate SPY 0DTE trade brief.
        
        Args:
            market_signals: Optional market signals data
            
        Returns:
            SpyTradeBrief with trade setup
        """
        market_signals = market_signals or {}
        
        # Analyze market regime
        regime = self._determine_market_regime(market_signals)
        
        # Get price levels
        spy_price = market_signals.get("spy_price", 500.0)
        support = spy_price * 0.995  # 0.5% support
        resistance = spy_price * 1.005  # 0.5% resistance
        
        # Determine strategy based on regime
        strategy, entry_trigger, strike_selection = self._determine_strategy(regime)
        
        # Calculate position parameters
        position_size = self._calculate_position_size(regime)
        profit_target, stop_loss = self._calculate_risk_parameters(regime)
        
        # Build the brief
        brief = SpyTradeBrief(
            market_regime=regime,
            spy_price=spy_price,
            support_level=round(support, 2),
            resistance_level=round(resistance, 2),
            volatility=market_signals.get("volatility", 15.0),
            strategy=strategy,
            entry_trigger=entry_trigger,
            strike_selection=strike_selection,
            expiration="0DTE",
            position_size=position_size,
            profit_target_pct=profit_target,
            stop_loss_pct=stop_loss,
            risk_reward_ratio=round(profit_target / stop_loss, 2) if stop_loss > 0 else 0,
            confidence_score=self._calculate_confidence(regime),
            reasoning=self._generate_reasoning(regime),
            best_entry_window=self._get_entry_window(regime),
            suggested_exit="Pre-market close or upon profit target"
        )
        
        self.last_brief = brief
        return brief
    
    def _determine_market_regime(self, signals: dict) -> MarketRegime:
        """Determine current market regime."""
        # In production, this would analyze actual market data
        # For now, use signals or default
        
        if signals.get("regime"):
            regime_map = {
                "bull": MarketRegime.BULL_TRENDING,
                "bear": MarketRegime.BEAR_TRENDING,
                "consolidation": MarketRegime.CONSOLIDATION,
                "volatile": MarketRegime.VOLATILE,
            }
            return regime_map.get(signals["regime"].lower(), MarketRegime.UNKNOWN)
        
        # Default based on time (simplified)
        return MarketRegime.CONSOLIDATION
    
    def _determine_strategy(
        self,
        regime: MarketRegime
    ) -> tuple[str, str, str]:
        """Determine strategy based on regime."""
        strategies = {
            MarketRegime.BULL_TRENDING: (
                "Bullish Call Spread",
                "Price above VWAP, momentum bullish",
                "ATM or slightly OTM calls"
            ),
            MarketRegime.BEAR_TRENDING: (
                "Bearish Put Spread",
                "Price below VWAP, momentum bearish",
                "ATM or slightly OTM puts"
            ),
            MarketRegime.CONSOLIDATION: (
                "Iron Condor",
                "Price in range, low volatility expected",
                "Sell ATM straddle, buy wings"
            ),
            MarketRegime.VOLATILE: (
                "Long Straddle",
                "High IV, expect big move",
                "Buy ATM call and put"
            ),
            MarketRegime.UNKNOWN: (
                "Cash / No Position",
                "Insufficient data",
                "Wait for clearer signals"
            ),
        }
        return strategies.get(regime, strategies[MarketRegime.UNKNOWN])
    
    def _calculate_position_size(self, regime: MarketRegime) -> int:
        """Calculate position size based on regime."""
        sizes = {
            MarketRegime.BULL_TRENDING: 5,
            MarketRegime.BEAR_TRENDING: 5,
            MarketRegime.CONSOLIDATION: 3,
            MarketRegime.VOLATILE: 2,  # Smaller due to higher risk
            MarketRegime.UNKNOWN: 0,
        }
        return sizes.get(regime, 0)
    
    def _calculate_risk_parameters(
        self,
        regime: MarketRegime
    ) -> tuple[float, float]:
        """Calculate profit target and stop loss percentages."""
        params = {
            MarketRegime.BULL_TRENDING: (1.5, 0.5),
            MarketRegime.BEAR_TRENDING: (1.5, 0.5),
            MarketRegime.CONSOLIDATION: (0.8, 0.4),
            MarketRegime.VOLATILE: (3.0, 1.5),  # Wider due to volatility
            MarketRegime.UNKNOWN: (0, 0),
        }
        return params.get(regime, (0, 0))
    
    def _calculate_confidence(self, regime: MarketRegime) -> float:
        """Calculate confidence score."""
        confidence = {
            MarketRegime.BULL_TRENDING: 0.70,
            MarketRegime.BEAR_TRENDING: 0.70,
            MarketRegime.CONSOLIDATION: 0.60,
            MarketRegime.VOLATILE: 0.45,  # Lower confidence in volatile
            MarketRegime.UNKNOWN: 0.20,
        }
        return confidence.get(regime, 0.20)
    
    def _generate_reasoning(self, regime: MarketRegime) -> str:
        """Generate reasoning for the trade."""
        reasoning = {
            MarketRegime.BULL_TRENDING:
                "Market showing bullish momentum with price above key moving averages. "
                "Bull call spread provides directional exposure with defined risk.",
            MarketRegime.BEAR_TRENDING:
                "Market showing bearish momentum with selling pressure. "
                "Bear put spread profits from downside move with limited risk.",
            MarketRegime.CONSOLIDATION:
                "Market in consolidation phase with tight range. "
                "Iron condor profits from range-bound price action.",
            MarketRegime.VOLATILE:
                "High implied volatility suggests large price move expected. "
                "Long straddle profits from either direction.",
            MarketRegime.UNKNOWN:
                "Insufficient market data to generate reliable trade. "
                "Recommend waiting for clearer signals.",
        }
        return reasoning.get(regime, "Unable to analyze market conditions.")
    
    def _get_entry_window(self, regime: MarketRegime) -> str:
        """Get best entry window."""
        windows = {
            MarketRegime.BULL_TRENDING: "9:45-10:15 AM (momentum confirmation)",
            MarketRegime.BEAR_TRENDING: "9:45-10:15 AM (momentum confirmation)",
            MarketRegime.CONSOLIDATION: "9:30-9:45 AM (opening range)",
            MarketRegime.VOLATILE: "9:30-10:00 AM (volatility spike)",
            MarketRegime.UNKNOWN: "Wait for clearer signals",
        }
        return windows.get(regime, "N/A")


__all__ = [
    "SpyTradeBriefEngine",
]
