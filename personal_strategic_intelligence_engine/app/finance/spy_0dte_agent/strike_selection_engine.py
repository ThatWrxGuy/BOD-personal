"""Strike Selection Engine - BB-FIN-019"""

from typing import Optional, List, Dict
import logging
import random
import math

from app.finance.spy_0dte_agent.spy_0dte_models import (
    StrikeRecommendation,
    TradeDirection,
    OpportunityConfidence,
)

logger = logging.getLogger(__name__)


class StrikeSelectionEngine:
    """Selects optimal strike for SPY 0DTE based on delta, gamma, and liquidity."""

    def __init__(self):
        self._strike_cache: Dict = {}

    def select_strike(
        self,
        current_price: float,
        direction: TradeDirection,
        gamma_levels: Optional[Dict] = None,
    ) -> StrikeRecommendation:
        """Select optimal strike for the given direction."""
        
        # Determine strike range based on direction
        if direction == TradeDirection.CALL:
            strikes = self._generate_call_strikes(current_price)
        elif direction == TradeDirection.PUT:
            strikes = self._generate_put_strikes(current_price)
        else:
            # Return a default recommendation for avoid
            return self._default_recommendation(current_price, direction)
        
        # Score each strike
        scored_strikes = []
        for strike_info in strikes:
            score = self._score_strike(
                strike_info, current_price, direction, gamma_levels
            )
            scored_strikes.append((strike_info, score))
        
        # Sort by score (highest first)
        scored_strikes.sort(key=lambda x: x[1], reverse=True)
        
        # Select best strike
        best_strike = scored_strikes[0][0]
        
        # Determine confidence based on score spread
        confidence = self._determine_confidence(scored_strikes)
        
        return StrikeRecommendation(
            symbol="SPY",
            strike=best_strike["strike"],
            direction=direction,
            delta=best_strike["delta"],
            gamma=best_strike["gamma"],
            theta=best_strike["theta"],
            open_interest=best_strike["open_interest"],
            volume=best_strike["volume"],
            spread=best_strike["spread"],
            distance_from_spot_pct=best_strike["distance_pct"],
            confidence=confidence,
            reasoning=best_strike["reasoning"],
        )

    def _generate_call_strikes(self, current_price: float) -> List[Dict]:
        """Generate call strike data."""
        strikes = []
        
        # Generate strikes around current price (OTM calls)
        base_strike = math.ceil(current_price / 5) * 5  # Round to nearest 5
        
        for i in range(8):
            strike = base_strike + (i * 5)  # Every 5 points
            
            # Calculate distance
            distance_pct = ((strike - current_price) / current_price) * 100
            
            # Approximate Greeks (simplified Black-Scholes)
            delta = self._approximate_delta(strike, current_price, "call")
            gamma = self._approximate_gamma(strike, current_price)
            theta = self._approximate_theta(strike, current_price, "call")
            
            # Liquidity increases closer to ATM
            distance_from_atm = abs(strike - current_price)
            base_oi = 50000 / (1 + distance_from_atm / 10)
            open_interest = int(base_oi + random.randint(-10000, 30000))
            volume = int(open_interest * random.uniform(0.2, 0.8))
            spread = 0.05 + (distance_from_atm * 0.01)  # Wider spreads OTM
            
            strikes.append({
                "strike": strike,
                "distance_pct": distance_pct,
                "delta": round(delta, 3),
                "gamma": round(gamma, 4),
                "theta": round(theta, 2),
                "open_interest": max(1000, open_interest),
                "volume": max(100, volume),
                "spread": round(spread, 2),
                "reasoning": self._generate_strike_reasoning(
                    distance_pct, delta, gamma, "call"
                ),
            })
        
        return strikes

    def _generate_put_strikes(self, current_price: float) -> List[Dict]:
        """Generate put strike data."""
        strikes = []
        
        # Generate strikes around current price (OTM puts)
        base_strike = math.floor(current_price / 5) * 5  # Round to nearest 5
        
        for i in range(8):
            strike = base_strike - (i * 5)  # Every 5 points
            
            # Calculate distance
            distance_pct = ((current_price - strike) / current_price) * 100
            
            # Approximate Greeks
            delta = self._approximate_delta(strike, current_price, "put")
            gamma = self._approximate_gamma(strike, current_price)
            theta = self._approximate_theta(strike, current_price, "put")
            
            # Liquidity
            distance_from_atm = abs(strike - current_price)
            base_oi = 50000 / (1 + distance_from_atm / 10)
            open_interest = int(base_oi + random.randint(-10000, 30000))
            volume = int(open_interest * random.uniform(0.2, 0.8))
            spread = 0.05 + (distance_from_atm * 0.01)
            
            strikes.append({
                "strike": strike,
                "distance_pct": distance_pct,
                "delta": round(delta, 3),
                "gamma": round(gamma, 4),
                "theta": round(theta, 2),
                "open_interest": max(1000, open_interest),
                "volume": max(100, volume),
                "spread": round(spread, 2),
                "reasoning": self._generate_strike_reasoning(
                    distance_pct, delta, gamma, "put"
                ),
            })
        
        return strikes

    def _approximate_delta(self, strike: float, spot: float, option_type: str) -> float:
        """Approximate delta using simple model."""
        moneyness = (spot - strike) / spot if option_type == "call" else (strike - spot) / spot
        
        # Simple approximation
        if option_type == "call":
            delta = 0.5 + (moneyness * 10)
        else:
            delta = 0.5 + (moneyness * 10)
        
        return max(0.01, min(0.99, delta))

    def _approximate_gamma(self, strike: float, spot: float) -> float:
        """Approximate gamma."""
        distance = abs(strike - spot) / spot
        # Higher gamma ATM
        gamma = 0.1 / (1 + distance * 10)
        return gamma

    def _approximate_theta(self, strike: float, spot: float, option_type: str) -> float:
        """Approximate theta (time decay per day)."""
        distance = abs(strike - spot) / spot
        # Theta is highest ATM
        theta = -5 / (1 + distance * 5)
        return theta

    def _score_strike(
        self,
        strike_info: Dict,
        current_price: float,
        direction: TradeDirection,
        gamma_levels: Optional[Dict],
    ) -> float:
        """Score a strike based on multiple factors."""
        score = 0.0
        
        # 1. Delta score (prefer 0.20-0.40 delta for 0DTE)
        delta = abs(strike_info["delta"])
        if 0.15 <= delta <= 0.50:
            score += 0.4
        elif delta < 0.15:
            score += 0.2
        else:
            score += 0.1
        
        # 2. Gamma score (higher gamma = more acceleration)
        score += strike_info["gamma"] * 2
        
        # 3. Liquidity score
        liquidity = strike_info["open_interest"] / 1000
        score += min(0.3, liquidity * 0.01)
        
        # 4. Spread score (tighter is better)
        spread_score = 0.2 - (strike_info["spread"] * 0.1)
        score += max(0, spread_score)
        
        # 5. Distance score (not too far OTM)
        distance_pct = strike_info["distance_pct"]
        if distance_pct <= 1.0:
            score += 0.3
        elif distance_pct <= 2.0:
            score += 0.2
        elif distance_pct <= 3.0:
            score += 0.1
        
        # 6. Gamma level alignment
        if gamma_levels:
            target_level = (
                gamma_levels.get("gamma_resistance") if direction == TradeDirection.CALL
                else gamma_levels.get("gamma_support")
            )
            if target_level:
                dist_to_gamma = abs(strike_info["strike"] - target_level)
                if dist_to_gamma < 3:
                    score += 0.3  # Near gamma level
        
        return score

    def _determine_confidence(self, scored_strikes: List[tuple]) -> OpportunityConfidence:
        """Determine confidence based on score spread."""
        if len(scored_strikes) < 2:
            return OpportunityConfidence.LOW
        
        best_score = scored_strikes[0][1]
        second_score = scored_strikes[1][1]
        
        score_diff = best_score - second_score
        
        if score_diff > 0.3:
            return OpportunityConfidence.HIGH
        elif score_diff > 0.15:
            return OpportunityConfidence.MEDIUM
        else:
            return OpportunityConfidence.LOW

    def _generate_strike_reasoning(
        self,
        distance_pct: float,
        delta: float,
        gamma: float,
        option_type: str,
    ) -> List[str]:
        """Generate reasoning for strike selection."""
        reasoning = []
        
        reasoning.append(f"{option_type.upper()} {distance_pct:.1f}% OTM")
        reasoning.append(f"Delta: {delta:.2f}")
        
        if delta >= 0.30:
            reasoning.append("High delta - good directional exposure")
        elif delta >= 0.15:
            reasoning.append("Moderate delta - balanced risk/reward")
        else:
            reasoning.append("Low delta - high risk for small move")
        
        if gamma > 0.05:
            reasoning.append("High gamma - strong acceleration potential")
        
        return reasoning

    def _default_recommendation(
        self,
        current_price: float,
        direction: TradeDirection,
    ) -> StrikeRecommendation:
        """Return default recommendation."""
        return StrikeRecommendation(
            symbol="SPY",
            strike=current_price,
            direction=direction,
            delta=0.0,
            gamma=0.0,
            theta=0.0,
            open_interest=0,
            volume=0,
            spread=0.0,
            distance_from_spot_pct=0.0,
            confidence=OpportunityConfidence.LOW,
            reasoning=["No clear opportunity - avoid"],
        )


# Singleton
_strike_engine: Optional[StrikeSelectionEngine] = None


def get_strike_selection_engine() -> StrikeSelectionEngine:
    """Get the singleton StrikeSelectionEngine instance."""
    global _strike_engine
    if _strike_engine is None:
        _strike_engine = StrikeSelectionEngine()
    return _strike_engine
