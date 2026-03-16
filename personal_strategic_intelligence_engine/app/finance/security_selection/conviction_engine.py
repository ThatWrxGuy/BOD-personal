"""Conviction Engine.

This module determines conviction levels for security recommendations.
"""
import uuid
from typing import Optional
from datetime import datetime

from app.finance.security_selection.selection_models import (
    ConvictionLevel,
    RankedOpportunity,
    SecurityScore,
)


class ConvictionEngine:
    """Determines conviction levels for recommendations."""
    
    def __init__(self):
        """Initialize the conviction engine."""
        self.history: list[dict] = []
        
    def determine_conviction(
        self,
        security_score: SecurityScore,
        regime: Optional[str] = None,
    ) -> ConvictionLevel:
        """Determine conviction level for a security.
        
        Args:
            security_score: Security score
            regime: Current market regime
            
        Returns:
            Conviction level
        """
        base_score = security_score.total_score
        
        # Adjust based on regime alignment
        regime_adjustment = self._get_regime_adjustment(regime)
        
        adjusted_score = base_score + regime_adjustment
        
        # Determine conviction
        if adjusted_score >= 85:
            return ConvictionLevel.EXCEPTIONAL
        elif adjusted_score >= 70:
            return ConvictionLevel.HIGH
        elif adjusted_score >= 50:
            return ConvictionLevel.MODERATE
        else:
            return ConvictionLevel.LOW
    
    def determine_conviction_from_score(
        self,
        score: float,
        regime: Optional[str] = None,
    ) -> ConvictionLevel:
        """Determine conviction from score.
        
        Args:
            score: Total score
            regime: Market regime
            
        Returns:
            Conviction level
        """
        regime_adjustment = self._get_regime_adjustment(regime)
        adjusted = score + regime_adjustment
        
        if adjusted >= 85:
            return ConvictionLevel.EXCEPTIONAL
        elif adjusted >= 70:
            return ConvictionLevel.HIGH
        elif adjusted >= 50:
            return ConvictionLevel.MODERATE
        else:
            return ConvictionLevel.LOW
    
    def record_outcome(
        self,
        symbol: str,
        conviction: ConvictionLevel,
        actual_return: float,
    ):
        """Record outcome for adaptive learning.
        
        Args:
            symbol: Security symbol
            conviction: Conviction level
            actual_return: Actual return achieved
        """
        self.history.append({
            "symbol": symbol,
            "conviction": conviction.value,
            "actual_return": actual_return,
        })
    
    def get_conviction_accuracy(self) -> dict:
        """Get accuracy of conviction levels."""
        if not self.history:
            return {"message": "No history available"}
        
        results = {}
        
        for conviction in ConvictionLevel:
            convictions = [
                h for h in self.history
                if h["conviction"] == conviction.value
            ]
            
            if convictions:
                correct = sum(1 for c in convictions if c["actual_return"] > 0)
                accuracy = correct / len(convictions) * 100
                
                results[conviction.value] = {
                    "count": len(convictions),
                    "accuracy": accuracy,
                    "avg_return": sum(c["actual_return"] for c in convictions) / len(convictions),
                }
        
        return results
    
    def _get_regime_adjustment(self, regime: Optional[str]) -> float:
        """Get score adjustment based on regime."""
        if not regime:
            return 0.0
        
        regime_adjustments = {
            "trend_up": 5.0,
            "trend_down": -5.0,
            "volatile": -5.0,
            "calm": 3.0,
            "bull": 5.0,
            "bear": -5.0,
        }
        
        return regime_adjustments.get(regime.lower(), 0.0)
    
    def suggest_weight_adjustment(self, conviction: ConvictionLevel) -> float:
        """Suggest position weight adjustment based on conviction."""
        adjustments = {
            ConvictionLevel.EXCEPTIONAL: 1.5,
            ConvictionLevel.HIGH: 1.25,
            ConvictionLevel.MODERATE: 1.0,
            ConvictionLevel.LOW: 0.5,
        }
        
        return adjustments.get(conviction, 1.0)


# Global instance
_conviction_engine: Optional[ConvictionEngine] = None


def get_conviction_engine() -> ConvictionEngine:
    """Get the global conviction engine."""
    global _conviction_engine
    
    if _conviction_engine is None:
        _conviction_engine = ConvictionEngine()
    
    return _conviction_engine
