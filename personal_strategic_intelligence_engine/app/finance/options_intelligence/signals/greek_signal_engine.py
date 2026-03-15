"""Greek Signal Engine.

Generates signals based on Greek analysis.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

from app.finance.options_intelligence.knowledge_base.greeks_models import (
    GreekExposure,
    GreeksCalculator,
)


@dataclass
class GreekSignal:
    """Greek-based trading signal."""
    signal_id: str
    signal_type: str
    strength: float
    interpretation: str
    action: str
    confidence: float
    timestamp: datetime
    
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


class GreekSignalEngine:
    """Generates Greek-based trading signals."""
    
    def __init__(self):
        self.calculator = GreeksCalculator()
        self.signal_history = []
    
    def analyze_position(self, positions: List[Dict]) -> Dict:
        """Analyze positions and generate signals."""
        exposure = self.calculator.analyze_exposure(positions)
        signals = self._generate_signals(exposure)
        
        return {
            "exposure": exposure.to_dict(),
            "signals": [s.to_dict() for s in signals],
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_signals(self, exposure: GreekExposure) -> List[GreekSignal]:
        """Generate signals from exposure."""
        signals = []
        
        # Delta exposure signal
        if abs(exposure.net_delta) > 0.5:
            direction = "long" if exposure.net_delta > 0 else "short"
            signals.append(GreekSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="DELTA_EXPOSURE",
                strength=abs(exposure.net_delta),
                interpretation=f"Significant {direction} delta exposure",
                action="Consider hedging" if abs(exposure.net_delta) > 0.8 else "Monitor",
                confidence=0.8,
                timestamp=datetime.now(),
            ))
        
        # Gamma risk signal
        if exposure.gamma_risk_level == "high":
            signals.append(GreekSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="GAMMA_RISK",
                strength=abs(exposure.net_gamma),
                interpretation="High gamma risk - rapid delta changes expected",
                action="Prepare for frequent rebalancing",
                confidence=0.85,
                timestamp=datetime.now(),
            ))
        
        # Theta harvest signal
        if exposure.net_theta > 0:
            signals.append(GreekSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="THETA_HARVEST",
                strength=exposure.net_theta,
                interpretation="Positive theta - time decay working in your favor",
                action="Maintain position to collect theta",
                confidence=0.9,
                timestamp=datetime.now(),
            ))
        
        return signals
    
    def detect_gamma_spike(self, current_gamma: float, gamma_history: List[float]) -> Optional[GreekSignal]:
        """Detect gamma spike."""
        if len(gamma_history) < 5:
            return None
        
        avg_gamma = sum(gamma_history) / len(gamma_history)
        
        if current_gamma > avg_gamma * 1.5:
            return GreekSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="GAMMA_SPIKE",
                strength=current_gamma / avg_gamma,
                interpretation=f"Gamma spike detected: {current_gamma:.3f} vs avg {avg_gamma:.3f}",
                action="Consider gamma scalping opportunity",
                confidence=0.8,
                timestamp=datetime.now(),
            )
        
        return None


def create_engine() -> GreekSignalEngine:
    """Create Greek signal engine."""
    return GreekSignalEngine()
