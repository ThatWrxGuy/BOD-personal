"""Volatility Signal Engine.

Generates signals based on volatility analysis.
"""

from typing import Dict, List
from datetime import datetime
import uuid

from app.finance.options_intelligence.knowledge_base.volatility_models import (
    VolatilityAnalyzer,
    VolatilityRegimeState,
)


class VolatilitySignal:
    """Volatility-based trading signal."""
    def __init__(self, signal_id: str, signal_type: str, strength: float, 
                 interpretation: str, action: str, confidence: float):
        self.signal_id = signal_id
        self.signal_type = signal_type
        self.strength = strength
        self.interpretation = interpretation
        self.action = action
        self.confidence = confidence
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "interpretation": self.interpretation,
            "action": self.action,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


class VolatilitySignalEngine:
    """Generates volatility-based trading signals."""
    
    def __init__(self):
        self.analyzer = VolatilityAnalyzer()
        self.signal_history = []
    
    def analyze_regime(self, iv: float, iv_rank: float, iv_percentile: float, 
                       hv: float) -> Dict:
        """Analyze volatility regime and generate signals."""
        
        regime = self.analyzer.detect_regime(iv, iv_rank, iv_percentile, hv)
        signals = self._generate_regime_signals(regime)
        
        return {
            "regime": regime.to_dict(),
            "signals": [s.to_dict() for s in signals],
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_regime_signals(self, regime: VolatilityRegimeState) -> List[VolatilitySignal]:
        """Generate signals from regime analysis."""
        
        signals = []
        
        # IV expansion signal
        if regime.regime.value == "elevated" or regime.regime.value == "spike":
            signals.append(VolatilitySignal(
                signal_id=str(uuid.uuid4()),
                signal_type="IV_ELEVATED",
                strength=regime.confidence,
                interpretation="IV is elevated - consider short volatility",
                action="Sell premium or use iron condor",
                confidence=0.8,
            ))
        
        # IV crush signal
        elif regime.regime.value == "crush":
            signals.append(VolatilitySignal(
                signal_id=str(uuid.uuid4()),
                signal_type="IV_CRUSH",
                strength=regime.confidence,
                interpretation="IV crush detected - look for opportunities",
                action="Buy volatility on dips",
                confidence=0.75,
            ))
        
        # Low IV signal
        elif regime.regime.value == "low":
            signals.append(VolatilitySignal(
                signal_id=str(uuid.uuid4()),
                signal_type="IV_LOW",
                strength=regime.confidence,
                interpretation="IV is low - favorable for long options",
                action="Buy straddles or strangles",
                confidence=0.8,
            ))
        
        return signals


def create_engine() -> VolatilitySignalEngine:
    """Create volatility signal engine."""
    return VolatilitySignalEngine()
