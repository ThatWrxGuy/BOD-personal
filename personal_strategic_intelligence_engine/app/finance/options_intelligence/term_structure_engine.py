"""Term Structure Engine - BB-FIN-017"""

from typing import Dict, List, Optional
import logging

from app.finance.options_intelligence.options_models import (
    TermStructureShape,
    VolatilityTermStructure,
)

logger = logging.getLogger(__name__)

# Standard expiration days for term structure
STANDARD_EXPIRATIONS = [7, 14, 21, 30, 45, 60, 90, 180, 365]


class TermStructureEngine:
    """Analyze implied volatility across expirations."""

    def __init__(self):
        self._term_structures: Dict[str, Dict[int, float]] = {}

    def add_observation(self, symbol: str, expiration_days: int, iv: float) -> None:
        """Add IV observation for a specific expiration."""
        if symbol not in self._term_structures:
            self._term_structures[symbol] = {}
        self._term_structures[symbol][expiration_days] = iv

    def analyze_term_structure(
        self,
        symbol: str,
        expiration_ivs: Optional[Dict[int, float]] = None,
    ) -> VolatilityTermStructure:
        """Analyze volatility term structure."""
        # Use demo data if not provided
        if expiration_ivs is None:
            expiration_ivs = self._generate_demo_term_structure(symbol)
        
        # Store observation
        for days, iv in expiration_ivs.items():
            self.add_observation(symbol, days, iv)
        
        # Determine shape
        shape = self._classify_shape(expiration_ivs)
        
        # Calculate contango/backwardation ratios
        front_iv = expiration_ivs.get(7) or expiration_ivs.get(min(expiration_ivs.keys()))
        back_iv = expiration_ivs.get(30) or expiration_ivs.get(max(expiration_ivs.keys()))
        
        contango_ratio = None
        backwardation_ratio = None
        if front_iv and back_iv and front_iv > 0:
            contango_ratio = back_iv / front_iv if shape == TermStructureShape.CONTANGO else None
            backwardation_ratio = front_iv / back_iv if shape == TermStructureShape.BACKWARDATION else None
        
        # Generate signal
        signal = self._generate_signal(shape, front_iv, back_iv)
        
        return VolatilityTermStructure(
            symbol=symbol,
            shape=shape,
            expiration_ivs=expiration_ivs,
            front_iv=float(front_iv) if front_iv else None,
            back_iv=float(back_iv) if back_iv else None,
            contango_ratio=float(contango_ratio) if contango_ratio else None,
            backwardation_ratio=float(backwardation_ratio) if backwardation_ratio else None,
            signal=signal,
        )

    def _classify_shape(self, expiration_ivs: Dict[int, float]) -> TermStructureShape:
        """Classify term structure shape."""
        if not expiration_ivs or len(expiration_ivs) < 2:
            return TermStructureShape.FLAT
        
        # Sort by days to expiration
        sorted_ivs = sorted(expiration_ivs.items(), key=lambda x: x[0])
        
        # Compare front vs back
        front = sorted_ivs[0][1]
        back = sorted_ivs[-1][1]
        
        # Check middle point for inversion detection
        mid_idx = len(sorted_ivs) // 2
        mid = sorted_ivs[mid_idx][1]
        
        # Calculate ratios
        front_back_ratio = back / front if front > 0 else 1.0
        
        # Determine shape
        if front_back_ratio > 1.15:
            if mid > back * 0.95:  # Inversion in the middle
                return TermStructureShape.INVERSION
            elif back / mid > 1.1:
                return TermStructureShape.STEEPENING
            else:
                return TermStructureShape.CONTANGO
        elif front_back_ratio < 0.90:
            if mid < front * 1.05:  # Inversion in the middle
                return TermStructureShape.INVERSION
            elif front / mid > 1.1:
                return TermStructureShape.FLATTENING
            else:
                return TermStructureShape.BACKWARDATION
        else:
            return TermStructureShape.FLAT

    def _generate_signal(
        self,
        shape: TermStructureShape,
        front_iv: Optional[float],
        back_iv: Optional[float],
    ) -> str:
        """Generate trading signal based on term structure."""
        signals = {
            TermStructureShape.CONTANGO: 
                "Contango: Front IV lower than back. Standard for bull markets. "
                "Short front-dated vol, long back-dated vol if holding.",
            TermStructureShape.BACKWARDATION:
                "Backwardation: Front IV higher than back. Typically Bearish. "
                "Could indicate imminent move or crisis premium.",
            TermStructureShape.FLAT:
                "Flat term structure. No clear directional signal. "
                "Standard volatility environment.",
            TermStructureShape.INVERSION:
                "Term structure inversion detected! STRONG signal. "
                "Often precedes significant market moves. Risk-off caution.",
            TermStructureShape.STEEPENING:
                "Steepening: Back vol rising faster than front. "
                "Long-term uncertainty increasing.",
            TermStructureShape.FLATTENING:
                "Flattening: Front and back vol converging. "
                "Market expecting stability.",
        }
        
        base_signal = signals.get(shape, "Unknown term structure.")
        
        # Add specific guidance
        if front_iv and back_iv and front_iv > 30:
            base_signal += " Elevated absolute IV levels - premiums expensive."
        elif front_iv and front_iv < 15:
            base_signal += " Compressed IV - potential for volatility expansion."
        
        return base_signal

    def _generate_demo_term_structure(self, symbol: str) -> Dict[int, float]:
        """Generate demo term structure."""
        import random
        
        # Base IV varies by symbol
        base_iv = {
            "SPY": 14.0,
            "QQQ": 18.0,
            "IWM": 20.0,
            "AAPL": 25.0,
            "TSLA": 55.0,
        }.get(symbol, 25.0)
        
        # Generate term structure (typically contango)
        structure = {}
        for days in [7, 14, 21, 30, 45, 60, 90]:
            # Usually front IV is lower (contango)
            days_factor = 1 + (days / 365) * 0.3  # Up to 30% higher at 1 year
            structure[days] = base_iv * days_factor + random.uniform(-2, 2)
        
        return structure

    def detect_volatility_event(self, expiration_ivs: Dict[int, float]) -> Optional[str]:
        """Detect potential volatility events from term structure."""
        if not expiration_ivs:
            return None
        
        sorted_ivs = sorted(expiration_ivs.items(), key=lambda x: x[0])
        
        # Check for sudden changes
        for i in range(1, len(sorted_ivs)):
            days1, iv1 = sorted_ivs[i-1]
            days2, iv2 = sorted_ivs[i]
            
            change_pct = abs(iv2 - iv1) / iv1 if iv1 > 0 else 0
            
            if change_pct > 0.20:
                days_gap = days2 - days1
                return f"Volatility acceleration expected between {days1}d and {days2}d expiry"
        
        return None


# Singleton
_term_structure_engine: Optional[TermStructureEngine] = None


def get_term_structure_engine() -> TermStructureEngine:
    """Get the singleton TermStructureEngine instance."""
    global _term_structure_engine
    if _term_structure_engine is None:
        _term_structure_engine = TermStructureEngine()
    return _term_structure_engine
