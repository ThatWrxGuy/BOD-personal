"""Skew Analysis Engine - BB-FIN-017"""

from typing import Optional, Dict
import logging

from app.finance.options_intelligence.options_models import (
    SkewType,
    SkewProfile,
)

logger = logging.getLogger(__name__)


class SkewAnalysisEngine:
    """Analyze options skew structure."""

    def __init__(self):
        self._historical_skew: Dict[str, Dict] = {}

    def analyze_skew(
        self,
        symbol: str,
        atm_iv: Optional[float] = None,
        call_iv: Optional[float] = None,
        put_iv: Optional[float] = None,
        rr_25: Optional[float] = None,
        rr_10: Optional[float] = None,
    ) -> SkewProfile:
        """Analyze options skew."""
        # Use demo data if not provided
        if atm_iv is None:
            atm_iv, call_iv, put_iv, rr_25, rr_10 = self._generate_demo_skew(symbol)
        
        # Determine skew type
        skew_type = self._classify_skew(rr_25, rr_10, put_iv, call_iv)
        
        # Calculate tail premium
        tail_premium = self._calculate_tail_premium(rr_25, rr_10)
        
        # Determine demand signals
        upside_demand = call_iv > atm_iv if call_iv and atm_iv else False
        downside_protection = put_iv > atm_iv if put_iv and atm_iv else False
        
        return SkewProfile(
            symbol=symbol,
            atm_iv=atm_iv,
            rr_25=rr_25,
            rr_10=rr_10,
            skew_type=skew_type,
            tail_premium=tail_premium,
            upside_demand=upside_demand,
            downside_protection=downside_protection,
        )

    def _classify_skew(
        self,
        rr_25: Optional[float],
        rr_10: Optional[float],
        put_iv: Optional[float],
        call_iv: Optional[float],
    ) -> SkewType:
        """Classify skew type."""
        # Use risk reversal as primary indicator
        if rr_25 is not None:
            if rr_25 > 0.15:  # Significant call skew
                return SkewType.CALL_SKEW
            elif rr_25 < -0.15:  # Significant put skew
                return SkewType.PUT_SKEW
        
        # Check IV differential if risk reversal not available
        if put_iv and call_iv:
            diff = put_iv - call_iv
            if diff > 3:
                return SkewType.PUT_SKEW
            elif diff < -3:
                return SkewType.CALL_SKEW
        
        # Check for tail risk (extreme skew)
        if rr_10 and abs(rr_10) > 0.25:
            return SkewType.TAIL_RISK
        
        return SkewType.SYMMETRIC

    def _calculate_tail_premium(
        self,
        rr_25: Optional[float],
        rr_10: Optional[float],
    ) -> float:
        """Calculate tail risk premium (0-1)."""
        if rr_25 is None and rr_10 is None:
            return 0.5
        
        # Use the more extreme risk reversal
        rr = rr_10 if rr_10 is not None else (rr_25 * 1.5 if rr_25 else 0)
        
        # Convert to 0-1 scale
        # Positive = put skew (downside protection demand)
        # Negative = call skew (upside speculation)
        abs_rr = abs(rr)
        
        if abs_rr > 0.3:
            return 0.9  # Extreme tail pricing
        elif abs_rr > 0.2:
            return 0.7
        elif abs_rr > 0.1:
            return 0.5
        else:
            return 0.3

    def _generate_demo_skew(self, symbol: str):
        """Generate demo skew data."""
        import random
        
        # Base IV
        base_iv = {
            "SPY": 14.0,
            "QQQ": 18.0,
            "AAPL": 25.0,
            "TSLA": 55.0,
        }.get(symbol, 25.0)
        
        atm_iv = base_iv + random.uniform(-2, 2)
        
        # Generate skew based on market conditions (demo)
        # Default to slight put skew (typical market)
        rr_25 = random.uniform(-0.15, 0.05)
        rr_10 = rr_25 * 1.3
        
        call_iv = atm_iv * (1 + rr_25 * 0.5) if rr_25 < 0 else atm_iv * 0.95
        put_iv = atm_iv * (1 - rr_25 * 0.5) if rr_25 > 0 else atm_iv * 1.05
        
        return atm_iv, call_iv, put_iv, rr_25, rr_10

    def get_skew_interpretation(self, profile: SkewProfile) -> str:
        """Get plain language interpretation."""
        interpretations = {
            SkewType.CALL_SKEW: (
                "Call skew elevated - market is bullish. "
                "Upside calls trading at premium to puts. "
                "Speculation bias toward gains."
            ),
            SkewType.PUT_SKEW: (
                "Put skew elevated - market is bearish/defensive. "
                "Downside protection expensive. "
                "Institutions hedging tail risk."
            ),
            SkewType.TAIL_RISK: (
                "EXTREME TAIL PRICING detected. "
                "Significant premium for far OTM options. "
                "Market expects significant move or is in crisis mode."
            ),
            SkewType.SYMMETRIC: (
                "Symmetric volatility smile. "
                "Balanced demand for calls and puts. "
                "No strong directional bias in options market."
            ),
        }
        
        base = interpretations.get(profile.skew_type, "Unknown skew type.")
        
        if profile.tail_premium > 0.7:
            base += " HIGH TAIL RISK PREMIUM in pricing."
        elif profile.tail_premium < 0.3:
            base += " Tail risk premium compressed."
        
        return base


# Singleton
_skew_engine: Optional[SkewAnalysisEngine] = None


def get_skew_analysis_engine() -> SkewAnalysisEngine:
    """Get the singleton SkewAnalysisEngine instance."""
    global _skew_engine
    if _skew_engine is None:
        _skew_engine = SkewAnalysisEngine()
    return _skew_engine
