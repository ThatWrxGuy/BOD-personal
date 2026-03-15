"""Core Structure Engine for Market Structure Intelligence.

Orchestrates VWAP, price levels, liquidity sweeps, volatility, and day type.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from app.agents.finance.tactical.market_structure.structure_models import (
    MarketStructureSignal,
    VWAPContext,
    IntradayLevelMap,
    LiquiditySweepEvent,
    VolatilityStructureState,
    DayTypeClassification,
    StructureConfidenceProfile,
)
from app.agents.finance.tactical.market_structure.vwap_engine import VWAPEngine, create_vwap_engine
from app.agents.finance.tactical.market_structure.price_levels import PriceLevelEngine, create_price_level_engine
from app.agents.finance.tactical.market_structure.liquidity_sweep_detector import SweepDetector, create_sweep_detector
from app.agents.finance.tactical.market_structure.volatility_structure import VolatilityStructureEngine, create_volatility_engine
from app.agents.finance.tactical.market_structure.day_type_classifier import DayTypeClassifier, create_day_type_classifier


class StructureEngine:
    """
    Core Market Structure Engine.
    
    Orchestrates all market structure components to produce
    unified tactical insights.
    """
    
    def __init__(self):
        self.vwap_engine = create_vwap_engine()
        self.level_engine = create_price_level_engine()
        self.sweep_detector = create_sweep_detector()
        self.volatility_engine = create_volatility_engine()
        self.day_type_classifier = create_day_type_classifier()
        
        self.session_start: Optional[datetime] = None
    
    def initialize_session(
        self,
        session_open: float,
        prior_close: float,
        timestamp: datetime,
    ) -> None:
        """Initialize for a new session."""
        self.session_start = timestamp
        self.level_engine.set_session_open(session_open)
        self.level_engine.set_prior_close(prior_close)
        self.day_type_classifier.set_session_open(session_open)
        
        # Reset engines
        self.vwap_engine.reset()
    
    def update(
        self,
        timestamp: datetime,
        open_price: float,
        high: float,
        low: float,
        close: float,
        volume: int,
    ) -> MarketStructureSignal:
        """
        Update with new bar data.
        
        Args:
            timestamp: Bar timestamp
            open_price: Bar open
            high: Bar high
            low: Bar low
            close: Bar close
            volume: Bar volume
        
        Returns:
            MarketStructureSignal
        """
        # Update all engines
        self.vwap_engine.add_bar(timestamp, high, low, close, volume)
        self.level_engine.update_session(high, low, close)
        self.day_type_classifier.update(close, high, low, timestamp)
        
        # Check for liquidity sweeps
        sweep = self.sweep_detector.update(timestamp, high, low, close, volume)
        
        # Update volatility
        self.volatility_engine.add_bar(timestamp, high, low, close)
        
        # Get contexts
        vwap_context = self.vwap_engine.get_vwap_context(close)
        level_map = self.level_engine.get_level_map(close)
        volatility_state = self.volatility_engine.get_volatility_state(close)
        day_type = self.day_type_classifier.get_current_classification()
        
        # Get recent sweeps
        recent_sweeps = self.sweep_detector.get_recent_sweeps(60)
        
        # Calculate derived metrics
        directional_bias = self._calculate_directional_bias(
            vwap_context, day_type, volatility_state, recent_sweeps
        )
        
        continuation_prob, reversal_prob, chop_prob = self._calculate_probabilities(
            vwap_context, day_type, volatility_state, recent_sweeps
        )
        
        structure_quality = self._calculate_structure_quality(
            vwap_context, volatility_state, recent_sweeps
        )
        
        tactical_suitability = self._calculate_tactical_suitability(
            structure_quality, day_type, volatility_state
        )
        
        # Determine suppression flags
        suppression_flags, suppression_reasons = self._determine_suppressions(
            vwap_context, day_type, volatility_state, structure_quality
        )
        
        return MarketStructureSignal(
            timestamp=timestamp,
            price=close,
            session_open=open_price,
            session_high=high,
            session_low=low,
            vwap_context=vwap_context,
            level_map=level_map,
            volatility_state=volatility_state,
            day_type=day_type,
            directional_bias=directional_bias,
            continuation_probability=continuation_prob,
            reversal_probability=reversal_prob,
            chop_probability=chop_prob,
            structure_quality_score=structure_quality,
            tactical_suitability_score=tactical_suitability,
            suppression_flags=suppression_flags,
            suppression_reasons=suppression_reasons,
            recent_sweeps=recent_sweeps,
        )
    
    def _calculate_directional_bias(
        self,
        vwap_context: VWAPContext,
        day_type: DayTypeClassification,
        volatility: VolatilityStructureState,
        sweeps: List,
    ) -> str:
        """Calculate directional bias."""
        score = 0
        
        # VWAP bias
        if vwap_context.state.value in ["above_vwap_acceptance", "vwap_reclaim_bullish"]:
            score += 2
        elif vwap_context.state.value in ["below_vwap_acceptance", "vwap_reject_bearish"]:
            score -= 2
        
        # Day type bias
        if day_type.day_type.value in ["trend_day_up", "open_drive_up"]:
            score += 2
        elif day_type.day_type.value in ["trend_day_down", "open_drive_down"]:
            score -= 2
        
        # Sweep bias
        bullish_traps = sum(1 for s in sweeps if s.direction.value == "bullish")
        bearish_traps = sum(1 for s in sweeps if s.direction.value == "bearish")
        score += bullish_traps - bearish_traps
        
        if score > 1:
            return "bullish"
        elif score < -1:
            return "bearish"
        return "neutral"
    
    def _calculate_probabilities(
        self,
        vwap_context: VWAPContext,
        day_type: DayTypeClassification,
        volatility: VolatilityStructureState,
        sweeps: List,
    ) -> tuple:
        """Calculate continuation, reversal, and chop probabilities."""
        
        # Base probabilities
        continuation = 0.4
        reversal = 0.2
        chop = 0.4
        
        # Adjust based on VWAP
        if vwap_context.state.value == "above_vwap_acceptance":
            continuation += 0.2
            chop -= 0.2
        elif vwap_context.state.value == "below_vwap_acceptance":
            continuation += 0.2
            chop -= 0.2
        elif vwap_context.state.value == "vwap_chop_neutral":
            chop += 0.2
        
        # Adjust based on day type
        if day_type.day_type.value in ["trend_day_up", "trend_day_down"]:
            continuation += 0.15
            reversal -= 0.05
            chop -= 0.1
        elif day_type.day_type.value in ["chop_day", "range_day"]:
            chop += 0.2
            continuation -= 0.1
        
        # Adjust based on volatility
        if volatility.state.value == "healthy_expansion":
            continuation += 0.1
        elif volatility.state.value == "low_energy_chop":
            chop += 0.2
            continuation -= 0.1
        
        # Normalize
        total = continuation + reversal + chop
        if total > 0:
            continuation = continuation / total
            reversal = reversal / total
            chop = chop / total
        
        return continuation, reversal, chop
    
    def _calculate_structure_quality(
        self,
        vwap_context: VWAPContext,
        volatility: VolatilityStructureState,
        sweeps: List,
    ) -> float:
        """Calculate structure quality score (0-100)."""
        score = 50
        
        # VWAP quality
        if vwap_context.state.value in ["above_vwap_acceptance", "below_vwap_acceptance"]:
            score += 20
        elif vwap_context.state.value == "vwap_chop_neutral":
            score -= 10
        elif vwap_context.state.value == "overextended_from_vwap":
            score -= 15
        
        # Volatility quality
        if volatility.state.value == "healthy_expansion":
            score += 15
        elif volatility.state.value in ["unstable_expansion", "exhaustion_expansion"]:
            score -= 20
        elif volatility.state.value == "low_energy_chop":
            score -= 15
        
        # Sweep quality
        traps = sum(1 for s in sweeps if "trap" in s.outcome.value if s.outcome)
        score -= traps * 10
        
        return max(0, min(100, score))
    
    def _calculate_tactical_suitability(
        self,
        structure_quality: float,
        day_type: DayTypeClassification,
        volatility: VolatilityStructureState,
    ) -> float:
        """Calculate tactical suitability score (0-100)."""
        score = structure_quality
        
        # Day type adjustment
        if day_type.day_type.value in ["trend_day_up", "trend_day_down"]:
            score += 10
        elif day_type.day_type.value in ["chop_day", "low_participation_day"]:
            score -= 20
        
        # Volatility adjustment
        if volatility.state.value == "healthy_expansion":
            score += 10
        elif volatility.state.value in ["unstable_expansion", "exhaustion_expansion"]:
            score -= 25
        
        return max(0, min(100, score))
    
    def _determine_suppressions(
        self,
        vwap_context: VWAPContext,
        day_type: DayTypeClassification,
        volatility: VolatilityStructureState,
        structure_quality: float,
    ) -> tuple:
        """Determine suppression flags and reasons."""
        flags = []
        reasons = []
        
        # Structure quality suppression
        if structure_quality < 30:
            flags.append("poor_structure")
            reasons.append("Structure quality below threshold")
        
        # Volatility suppression
        if volatility.state.value == "unstable_expansion":
            flags.append("unstable_volatility")
            reasons.append("Unstable volatility expansion")
        elif volatility.state.value == "exhaustion_expansion":
            flags.append("exhaustion_volatility")
            reasons.append("Volatility exhaustion detected")
        elif volatility.state.value == "low_energy_chop":
            flags.append("low_energy")
            reasons.append("Low energy chop environment")
        
        # Day type suppression
        if day_type.day_type.value == "low_participation_day":
            flags.append("low_participation")
            reasons.append("Low participation day")
        
        # VWAP suppression
        if vwap_context.state.value == "overextended_from_vwap":
            flags.append("vwap_overextended")
            reasons.append("Price overextended from VWAP")
        
        return flags, reasons
    
    def get_structure_snapshot(self) -> dict:
        """Get current structure engine status."""
        return {
            "vwap_engine": self.vwap_engine.get_vwap_stats(),
            "volatility_engine": self.volatility_engine.get_state_summary(),
            "sweep_detector": self.sweep_detector.get_sweep_summary(),
        }


def create_structure_engine() -> StructureEngine:
    """Factory function to create structure engine."""
    return StructureEngine()
