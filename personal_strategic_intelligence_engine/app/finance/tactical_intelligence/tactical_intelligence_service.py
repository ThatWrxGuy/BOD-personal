"""Tactical Intelligence Service - BB-FIN-018"""

from datetime import datetime
from typing import Optional, List, Dict
import logging

from app.finance.tactical_intelligence.tactical_models import (
    TacticalAnalysisReport,
    EntryType,
)
from app.finance.tactical_intelligence.structure_detection_engine import get_structure_detection_engine
from app.finance.tactical_intelligence.liquidity_event_engine import get_liquidity_event_engine
from app.finance.tactical_intelligence.volatility_expansion_engine import get_volatility_expansion_engine
from app.finance.tactical_intelligence.momentum_detection_engine import get_momentum_detection_engine
from app.finance.tactical_intelligence.breakout_confirmation_engine import get_breakout_confirmation_engine
from app.finance.tactical_intelligence.entry_signal_engine import get_entry_signal_engine

logger = logging.getLogger(__name__)


class TacticalIntelligenceService:
    """Orchestrates the complete tactical intelligence pipeline."""

    def __init__(self):
        self._structure_engine = get_structure_detection_engine()
        self._liquidity_engine = get_liquidity_event_engine()
        self._volatility_engine = get_volatility_expansion_engine()
        self._momentum_engine = get_momentum_detection_engine()
        self._breakout_engine = get_breakout_confirmation_engine()
        self._entry_engine = get_entry_signal_engine()

    def analyze(
        self,
        symbol: str,
        timeframe: str = "5m",
        candles: Optional[List[Dict]] = None,
        market_regime: Optional[str] = None,
        sector_context: Optional[str] = None,
        options_environment: Optional[str] = None,
    ) -> TacticalAnalysisReport:
        """Run complete tactical analysis."""
        
        # Run all analyses
        structure = self._structure_engine.analyze_structure(symbol, timeframe, candles)
        liquidity_events = self._liquidity_engine.detect_events(symbol, candles)
        volatility = self._volatility_engine.analyze_volatility(symbol, timeframe, candles)
        momentum = self._momentum_engine.analyze_momentum(symbol, timeframe, candles)
        breakout = self._breakout_engine.analyze_breakout(symbol, timeframe, candles)
        
        # Generate entry signal
        entry_signal = self._entry_engine.generate_signal(
            symbol, timeframe, candles, market_regime, sector_context
        )
        
        # Determine risk level
        risk_level = self._assess_risk(structure, volatility, momentum, entry_signal)
        
        # Check avoid conditions
        avoid = entry_signal.entry_type == EntryType.AVOID
        
        # Get current price
        current_price = structure.close if structure.close else 0.0
        
        return TacticalAnalysisReport(
            timestamp=datetime.utcnow(),
            symbol=symbol,
            timeframe=timeframe,
            current_price=current_price,
            structure=structure,
            liquidity_events=liquidity_events,
            volatility=volatility,
            momentum=momentum,
            breakout=breakout,
            entry_signal=entry_signal,
            risk_level=risk_level,
            avoid_conditions=avoid,
            market_regime=market_regime,
            sector_context=sector_context,
            options_environment=options_environment,
        )

    def _assess_risk(
        self,
        structure,
        volatility,
        momentum,
        entry_signal,
    ) -> str:
        """Assess overall risk level."""
        risk_score = 0
        
        # Structure risk
        if structure.structure.value in ["breakout_up", "breakout_down"]:
            risk_score += 1  # Breakouts are higher risk
        
        # Volatility risk
        if volatility.current_state.value == "compressed":
            risk_score += 1  # Imminent expansion
        elif volatility.current_state.value == "expanding":
            risk_score += 2  # High volatility
        
        # Momentum risk
        if momentum.momentum_state.value == "reversing":
            risk_score += 2
        
        # Entry signal risk
        if entry_signal.entry_type == EntryType.AVOID:
            risk_score += 3
        
        if entry_signal.confidence.value == "low":
            risk_score += 1
        
        # Determine level
        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "moderate"
        else:
            return "low"

    def get_structure(self, symbol: str, timeframe: str = "5m") -> Dict:
        """Get market structure analysis."""
        structure = self._structure_engine.analyze_structure(symbol, timeframe)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "structure": structure.structure.value,
            "trend_strength": structure.trend_strength,
            "higher_highs": structure.consecutive_higher_highs,
            "lower_lows": structure.consecutive_lower_lows,
            "compression_ratio": structure.compression_ratio,
            "description": self._structure_engine.get_structure_description(structure),
        }

    def get_liquidity_events(self, symbol: str) -> Dict:
        """Get liquidity events."""
        events = self._liquidity_engine.detect_events(symbol)
        
        return {
            "symbol": symbol,
            "event_count": len(events),
            "events": [
                {
                    "type": e.event_type.value,
                    "direction": e.direction,
                    "level": e.sweep_level,
                    "interpretation": e.interpretation,
                }
                for e in events
            ],
        }

    def get_momentum(self, symbol: str, timeframe: str = "5m") -> Dict:
        """Get momentum analysis."""
        momentum = self._momentum_engine.analyze_momentum(symbol, timeframe)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "state": momentum.momentum_state.value,
            "acceleration": momentum.acceleration,
            "impulse_strength": momentum.impulse_strength,
            "is_burst": momentum.is_burst,
            "follow_through": momentum.follow_through_likely,
        }

    def get_breakouts(self, symbol: str, timeframe: str = "5m") -> Dict:
        """Get breakout analysis."""
        breakout = self._breakout_engine.analyze_breakout(symbol, timeframe)
        
        if not breakout:
            return {
                "symbol": symbol,
                "breakout_detected": False,
                "message": "No breakout detected",
            }
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "breakout_detected": True,
            "direction": breakout.direction,
            "quality": breakout.quality.value,
            "strength": breakout.strength,
            "volume_confirmed": breakout.volume_confirmation,
            "momentum_confirmed": breakout.momentum_confirmation,
            "follow_through_prob": breakout.follow_through_probability,
            "false_breakout_risk": breakout.false_breakout_risk,
            "valid": breakout.breakout_valid,
        }

    def get_entry_signals(
        self,
        symbol: str,
        timeframe: str = "5m",
        market_regime: Optional[str] = None,
    ) -> Dict:
        """Get entry signals."""
        signal = self._entry_engine.generate_signal(symbol, timeframe, None, market_regime)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "entry_type": signal.entry_type.value,
            "confidence": signal.confidence.value,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "target": signal.target,
            "risk_reward": signal.risk_reward_ratio,
            "win_probability": signal.win_probability,
            "reasoning": signal.reasoning,
            "warning": signal.warning,
        }

    def get_report(
        self,
        symbol: str,
        timeframe: str = "5m",
        market_regime: Optional[str] = None,
        sector_context: Optional[str] = None,
        options_environment: Optional[str] = None,
    ) -> Dict:
        """Get complete tactical report."""
        report = self.analyze(symbol, timeframe, None, market_regime, sector_context, options_environment)
        
        return {
            "timestamp": report.timestamp.isoformat(),
            "symbol": report.symbol,
            "timeframe": report.timeframe,
            "current_price": report.current_price,
            "structure": report.structure.structure.value,
            "entry_type": report.entry_signal.entry_type.value,
            "confidence": report.entry_signal.confidence.value,
            "risk_level": report.risk_level,
            "avoid": report.avoid_conditions,
            "volatility_state": report.volatility.current_state.value,
            "momentum_state": report.momentum.momentum_state.value,
            "breakout_valid": report.entry_signal.breakout_confirmed,
        }


# Singleton
_tactical_service: Optional[TacticalIntelligenceService] = None


def get_tactical_intelligence_service() -> TacticalIntelligenceService:
    """Get the singleton TacticalIntelligenceService instance."""
    global _tactical_service
    if _tactical_service is None:
        _tactical_service = TacticalIntelligenceService()
    return _tactical_service
