"""Factor Scoring Engine.

This module assigns weighted scores to securities based on multiple factors.
"""
from typing import Optional

from app.finance.security_selection.selection_models import (
    SecurityCategory,
    SecurityProfile,
    SecurityScore,
    StrategyType,
)


class FactorScoringEngine:
    """Scores securities based on weighted factors."""
    
    # Default weights for different strategy types
    DEFAULT_WEIGHTS = {
        "trend_quality": 0.20,
        "momentum": 0.20,
        "relative_strength": 0.15,
        "liquidity": 0.15,
        "volatility_quality": 0.10,
        "risk_reward": 0.20,
    }
    
    INVESTMENT_WEIGHTS = {
        "trend_quality": 0.15,
        "momentum": 0.10,
        "relative_strength": 0.10,
        "liquidity": 0.10,
        "volatility_quality": 0.05,
        "risk_reward": 0.15,
        "fundamental_quality": 0.35,
    }
    
    TACTICAL_WEIGHTS = {
        "trend_quality": 0.25,
        "momentum": 0.25,
        "relative_strength": 0.20,
        "liquidity": 0.10,
        "volatility_quality": 0.10,
        "risk_reward": 0.10,
    }
    
    OPTIONS_WEIGHTS = {
        "trend_quality": 0.15,
        "momentum": 0.15,
        "relative_strength": 0.10,
        "liquidity": 0.15,
        "volatility_quality": 0.15,
        "risk_reward": 0.10,
        "options_quality": 0.20,
    }
    
    def __init__(
        self,
        strategy_type: StrategyType = StrategyType.INVESTMENT,
        custom_weights: Optional[dict] = None,
    ):
        """Initialize the scoring engine.
        
        Args:
            strategy_type: Type of strategy
            custom_weights: Custom weight overrides
        """
        self.strategy_type = strategy_type
        self.weights = self._get_weights(strategy_type)
        
        if custom_weights:
            self.weights.update(custom_weights)
    
    def _get_weights(self, strategy_type: StrategyType) -> dict:
        """Get weights for strategy type."""
        if strategy_type == StrategyType.INVESTMENT:
            return self.INVESTMENT_WEIGHTS.copy()
        elif strategy_type == StrategyType.TACTICAL:
            return self.TACTICAL_WEIGHTS.copy()
        elif strategy_type == StrategyType.OPTIONS:
            return self.OPTIONS_WEIGHTS.copy()
        else:
            return self.DEFAULT_WEIGHTS.copy()
    
    def score(self, security: SecurityProfile, market_data: dict) -> SecurityScore:
        """Score a security.
        
        Args:
            security: Security profile
            market_data: Market data for scoring
            
        Returns:
            Security score
        """
        score = SecurityScore(
            symbol=security.symbol,
            category=security.category,
            weights=self.weights.copy(),
        )
        
        # Calculate individual factors
        score.trend_quality = self._calculate_trend_quality(security, market_data)
        score.momentum = self._calculate_momentum(security, market_data)
        score.relative_strength = self._calculate_relative_strength(security, market_data)
        score.liquidity = self._calculate_liquidity(security, market_data)
        score.volatility_quality = self._calculate_volatility_quality(security, market_data)
        score.risk_reward = self._calculate_risk_reward(security, market_data)
        
        # Calculate total
        score.calculate_total()
        
        return score
    
    def score_batch(
        self,
        securities: list[SecurityProfile],
        market_data: dict,
    ) -> list[SecurityScore]:
        """Score multiple securities.
        
        Args:
            securities: List of securities
            market_data: Market data dictionary
            
        Returns:
            List of security scores
        """
        return [
            self.score(security, market_data)
            for security in securities
        ]
    
    def update_weights(self, **weights):
        """Update factor weights."""
        self.weights.update(weights)
    
    def get_weights(self) -> dict:
        """Get current weights."""
        return self.weights.copy()
    
    def _calculate_trend_quality(self, security: SecurityProfile, market_data: dict) -> float:
        """Calculate trend quality score (0-100)."""
        # Would use moving average analysis in production
        # Simplified scoring based on price movement
        
        change = security.change_percent
        
        if change > 3.0:
            return 90.0
        elif change > 1.5:
            return 75.0
        elif change > 0.5:
            return 60.0
        elif change > -0.5:
            return 50.0
        elif change > -1.5:
            return 35.0
        else:
            return 20.0
    
    def _calculate_momentum(self, security: SecurityProfile, market_data: dict) -> float:
        """Calculate momentum score (0-100)."""
        # Would use RSI, MACD, etc. in production
        
        change = security.change_percent
        volume = security.volume
        avg_volume = security.avg_volume
        
        # Momentum based on price change and volume
        momentum_score = 50.0
        
        # Price momentum
        if change > 2.0:
            momentum_score += 20
        elif change > 1.0:
            momentum_score += 10
        elif change < -2.0:
            momentum_score -= 10
        
        # Volume momentum
        if volume > avg_volume * 1.5:
            momentum_score += 15
        elif volume > avg_volume:
            momentum_score += 5
        
        return max(0.0, min(100.0, momentum_score))
    
    def _calculate_relative_strength(self, security: SecurityProfile, market_data: dict) -> float:
        """Calculate relative strength score (0-100)."""
        # Compare to market (would use SPY as benchmark in production)
        
        change = security.change_percent
        
        # Simplified: score based on change magnitude
        if change > 5.0:
            return 95.0
        elif change > 3.0:
            return 80.0
        elif change > 1.0:
            return 65.0
        elif change > -1.0:
            return 50.0
        elif change > -3.0:
            return 35.0
        else:
            return 20.0
    
    def _calculate_liquidity(self, security: SecurityProfile, market_data: dict) -> float:
        """Calculate liquidity score (0-100)."""
        volume = security.volume
        avg_volume = security.avg_volume
        
        # Volume ratio
        if avg_volume == 0:
            return 0.0
        
        volume_ratio = volume / avg_volume
        
        # Score based on volume
        if volume > 10_000_000:
            return 95.0
        elif volume > 5_000_000:
            return 85.0
        elif volume > 1_000_000:
            return 70.0
        elif volume > 500_000:
            return 55.0
        elif volume > 100_000:
            return 40.0
        else:
            return 25.0
    
    def _calculate_volatility_quality(self, security: SecurityProfile, market_data: dict) -> float:
        """Calculate volatility quality score (0-100)."""
        # Would use historical volatility in production
        # Higher volatility isn't necessarily bad - it's about quality of movement
        
        change = security.change_percent
        
        # Moderate volatility with direction is better
        if 1.0 < abs(change) < 4.0:
            return 75.0
        elif abs(change) < 2.0:
            return 60.0
        elif abs(change) < 6.0:
            return 50.0
        else:
            return 35.0
    
    def _calculate_risk_reward(self, security: SecurityProfile, market_data: dict) -> float:
        """Calculate risk/reward score (0-100)."""
        # Would use support/resistance levels in production
        
        change = security.change_percent
        
        # Positive change with reasonable magnitude = good risk/reward
        if 1.0 < change < 5.0:
            return 80.0
        elif change > 5.0:
            return 65.0  # Could be overextended
        elif change > 0:
            return 55.0
        elif change > -3.0:
            return 45.0
        else:
            return 30.0


# Global instance
_scoring_engine: Optional[FactorScoringEngine] = None


def get_scoring_engine(
    strategy_type: StrategyType = StrategyType.INVESTMENT,
) -> FactorScoringEngine:
    """Get the global factor scoring engine."""
    global _scoring_engine
    
    if _scoring_engine is None:
        _scoring_engine = FactorScoringEngine(strategy_type)
    
    return _scoring_engine
