"""Confidence Evolution Engine.

Adjusts confidence based on historical performance and context.
"""

from datetime import datetime
from typing import Dict, Optional

from app.intelligence.evolution.evolution_models import (
    RegimeType,
)


class ConfidenceEvolutionEngine:
    """Evolves confidence estimates over time."""
    
    def __init__(self):
        self.confidence_adjustments: Dict[str, float] = {}
        self.adjustment_history: Dict[str, list] = {}
    
    def calculate_confidence(
        self,
        base_confidence: float,
        regime: RegimeType,
        pattern_strength: float,
        feature_reliability: float,
    ) -> float:
        """Calculate evolved confidence."""
        
        adjustments = []
        
        # Regime adjustment
        regime_adj = self._get_regime_adjustment(regime)
        adjustments.append(("regime", regime_adj))
        
        # Pattern strength adjustment
        if pattern_strength > 0.7:
            pattern_adj = (pattern_strength - 0.5) * 20
        elif pattern_strength < 0.3:
            pattern_adj = (pattern_strength - 0.5) * 20
        else:
            pattern_adj = 0
        adjustments.append(("pattern", pattern_adj))
        
        # Feature reliability adjustment
        feature_adj = (feature_reliability - 0.5) * 15
        adjustments.append(("feature", feature_adj))
        
        # Apply adjustments
        total_adjustment = sum(adj for _, adj in adjustments)
        evolved_confidence = max(10, min(95, base_confidence + total_adjustment))
        
        # Record adjustment
        key = f"{regime.value}_{datetime.now().strftime('%Y%m%d')}"
        self.confidence_adjustments[key] = total_adjustment
        
        return evolved_confidence
    
    def _get_regime_adjustment(self, regime: RegimeType) -> float:
        """Get regime-based adjustment."""
        
        regime_adjustments = {
            RegimeType.TREND_UP: 8,
            RegimeType.TREND_DOWN: 8,
            RegimeType.RANGE_CHOP: -10,
            RegimeType.VOLATILITY_EXPAND: 5,
            RegimeType.VOLATILITY_COMPRESS: 0,
            RegimeType.LOW_PARTICIPATION: -5,
        }
        
        return regime_adjustments.get(regime, 0)
    
    def get_confidence_trend(self, regime: RegimeType) -> Dict:
        """Get confidence adjustment trend for a regime."""
        
        regime_key = regime.value
        adjustments = [
            v for k, v in self.confidence_adjustments.items()
            if regime_key in k
        ]
        
        if not adjustments:
            return {
                "current_adjustment": self._get_regime_adjustment(regime),
                "average_adjustment": 0,
                "trend": "stable",
            }
        
        avg_adj = sum(adjustments) / len(adjustments)
        
        if len(adjustments) >= 3:
            recent = adjustments[-3:]
            if recent[-1] > recent[0]:
                trend = "improving"
            elif recent[-1] < recent[0]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "current_adjustment": adjustments[-1] if adjustments else 0,
            "average_adjustment": avg_adj,
            "trend": trend,
        }
    
    def reset_adjustments(self) -> None:
        """Reset all adjustments."""
        self.confidence_adjustments = {}
        self.adjustment_history = {}


def create_engine() -> ConfidenceEvolutionEngine:
    """Create a new confidence evolution engine."""
    return ConfidenceEvolutionEngine()
