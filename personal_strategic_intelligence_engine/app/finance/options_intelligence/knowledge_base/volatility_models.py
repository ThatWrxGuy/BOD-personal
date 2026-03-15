"""Volatility Models.

Models derived from Gatheral, Sinclair, and Natenberg frameworks.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

from app.finance.options_intelligence.knowledge_base.options_theory_models import (
    VolatilityRegime,
    IVAnalysis,
)


class VolatilityModel(str, Enum):
    BLACK_SCHOLES = "black_scholes"
    SABR = "sabr"
    SVI = "svi"
    LOCAL_VOL = "local_vol"


@dataclass
class VolatilitySurface:
    """Volatility surface model."""
    symbol: str
    strikes: list
    expirations: list
    iv_matrix: list
    model_type: VolatilityModel
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "strikes": self.strikes,
            "expirations": self.expirations,
            "iv_matrix": self.iv_matrix,
            "model_type": self.model_type.value,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class VolatilityRegimeState:
    """Volatility regime detection."""
    regime: VolatilityRegime
    confidence: float
    characteristics: Dict[str, float]
    recommendation: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "regime": self.regime.value,
            "confidence": self.confidence,
            "characteristics": self.characteristics,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SkewAnalysis:
    """Volatility skew analysis."""
    symbol: str
    put_call_skew: float
    risk_reversal: float
    fly_spread: float
    skew_score: float
    interpretation: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "put_call_skew": self.put_call_skew,
            "risk_reversal": self.risk_reversal,
            "fly_spread": self.fly_spread,
            "skew_score": self.skew_score,
            "interpretation": self.interpretation,
            "timestamp": self.timestamp.isoformat(),
        }


class VolatilityAnalyzer:
    """Analyzes volatility conditions."""
    
    def __init__(self):
        self.iv_history = {}
    
    def detect_regime(
        self,
        iv: float,
        iv_rank: float,
        iv_percentile: float,
        hv: float,
    ) -> VolatilityRegimeState:
        """Detect current volatility regime."""
        
        iv_hv_ratio = iv / hv if hv > 0 else 1.0
        
        # Determine regime
        if iv_percentile < 20:
            regime = VolatilityRegime.LOW
            recommendation = "Favorable for long volatility positions"
        elif iv_percentile > 75 or iv_hv_ratio > 1.3:
            regime = VolatilityRegime.SPIKE
            recommendation = "Consider short volatility strategies"
        elif iv_percentile > 60:
            regime = VolatilityRegime.ELEVATED
            recommendation = "Moderate volatility - selective strategies"
        elif iv_percentile > 30:
            regime = VolatilityRegime.NORMAL
            recommendation = "Normal conditions - standard strategies"
        else:
            regime = VolatilityRegime.CRUSH
            recommendation = "Post-event IV crush - look for opportunities"
        
        confidence = min(0.95, 0.5 + abs(iv_percentile - 50) / 100)
        
        return VolatilityRegimeState(
            regime=regime,
            confidence=confidence,
            characteristics={
                "iv": iv,
                "iv_rank": iv_rank,
                "iv_percentile": iv_percentile,
                "hv": hv,
                "iv_hv_ratio": iv_hv_ratio,
            },
            recommendation=recommendation,
            timestamp=datetime.now(),
        )
    
    def analyze_skew(self, symbol: str, atm_iv: float, put_25d_iv: float, call_25d_iv: float) -> SkewAnalysis:
        """Analyze volatility skew."""
        
        skew = put_25d_iv - atm_iv
        risk_reversal = call_25d_iv - put_25d_iv
        
        # Interpretation
        if skew > 5:
            interpretation = "Elevated put skew - protective demand"
        elif skew < -5:
            interpretation = "Call skew - bullish sentiment"
        else:
            interpretation = "Balanced skew"
        
        return SkewAnalysis(
            symbol=symbol,
            put_call_skew=skew,
            risk_reversal=risk_reversal,
            fly_spread=skew / 2,
            skew_score=abs(skew) / 10,
            interpretation=interpretation,
            timestamp=datetime.now(),
        )
    
    def calculate_iv_hv_spread(self, iv: float, hv: float) -> float:
        """Calculate IV/HV spread."""
        return (iv - hv) / hv * 100 if hv > 0 else 0


def create_analyzer() -> VolatilityAnalyzer:
    """Create volatility analyzer."""
    return VolatilityAnalyzer()
