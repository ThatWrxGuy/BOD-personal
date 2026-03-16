"""Capital Flow Engine - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    CapitalFlowSignal,
    CapitalFlowDirection,
)

logger = logging.getLogger(__name__)


class CapitalFlowEngine:
    """Estimates institutional capital movement in sectors."""

    # Thresholds
    VOLUME_EXPANSION_THRESHOLD = 0.20  # 20% volume increase
    MOMENTUM_ACCELERATION_THRESHOLD = 0.15  # 15% momentum increase
    VOLATILITY_COMPRESSION_THRESHOLD = -0.10  # 10% vol decrease

    def __init__(self):
        self._prior_volumes: Dict[str, float] = {}
        self._prior_volatility: Dict[str, float] = {}

    def estimate_capital_flow(
        self,
        sector: SectorProfile,
    ) -> CapitalFlowSignal:
        """Estimate capital flow for a sector."""
        
        symbol = sector.symbol
        
        # Calculate signals from available data
        
        # Volume signal
        volume_signal = 0.0
        if sector.volume and sector.volume_change:
            volume_signal = sector.volume_change / 100.0 if sector.volume_change else 0.0
        
        # Momentum signal
        momentum_signal = sector.momentum_score or 0.0
        
        # Volatility signal (volatility compression in leaders = inflow)
        volatility_signal = 0.0
        if sector.volatility:
            prior_vol = self._prior_volatility.get(symbol, sector.volatility)
            if prior_vol > 0:
                vol_change = (sector.volatility - prior_vol) / prior_vol
                volatility_signal = -vol_change  # Negative = compression = inflow
        
        # Determine direction
        combined_signal = (
            volume_signal * 0.3 +
            momentum_signal * 0.5 +
            volatility_signal * 0.2
        )
        
        if combined_signal > 0.1:
            direction = CapitalFlowDirection.INFLOW
        elif combined_signal < -0.1:
            direction = CapitalFlowDirection.OUTFLOW
        else:
            direction = CapitalFlowDirection.NEUTRAL
        
        # Strength
        strength = min(1.0, abs(combined_signal))
        
        # Confidence
        confidence = "low"
        signal_count = sum([
            volume_signal != 0,
            momentum_signal != 0,
            volatility_signal != 0,
        ])
        if signal_count >= 3:
            confidence = "high"
        elif signal_count >= 2:
            confidence = "moderate"
        
        # Description
        if direction == CapitalFlowDirection.INFLOW:
            description = f"Capital inflow detected in {sector.name}"
        elif direction == CapitalFlowDirection.OUTFLOW:
            description = f"Capital outflow detected in {sector.name}"
        else:
            description = f"No significant capital flow in {sector.name}"
        
        # Update prior values
        if sector.volume:
            self._prior_volumes[symbol] = sector.volume
        if sector.volatility:
            self._prior_volatility[symbol] = sector.volatility
        
        return CapitalFlowSignal(
            symbol=symbol,
            direction=direction,
            strength=strength,
            volume_signal=volume_signal,
            momentum_signal=momentum_signal,
            volatility_signal=volatility_signal,
            confidence=confidence,
            description=description,
        )

    def estimate_all_flows(
        self,
        sector_profiles: List[SectorProfile],
    ) -> List[CapitalFlowSignal]:
        """Estimate capital flows for all sectors."""
        
        flows = []
        
        for sector in sector_profiles:
            flow = self.estimate_capital_flow(sector)
            flows.append(flow)
        
        return flows

    def get_flow_summary(
        self,
        flows: List[CapitalFlowSignal],
    ) -> Dict[str, any]:
        """Get summary of capital flows."""
        
        inflow_count = sum(1 for f in flows if f.direction == CapitalFlowDirection.INFLOW)
        outflow_count = sum(1 for f in flows if f.direction == CapitalFlowDirection.OUTFLOW)
        neutral_count = sum(1 for f in flows if f.direction == CapitalFlowDirection.NEUTRAL)
        
        total_inflow_strength = sum(f.strength for f in flows if f.direction == CapitalFlowDirection.INFLOW)
        total_outflow_strength = sum(f.strength for f in flows if f.direction == CapitalFlowDirection.OUTFLOW)
        
        # Top inflow
        inflows = [f for f in flows if f.direction == CapitalFlowDirection.INFLOW]
        top_inflow = max(inflows, key=lambda f: f.strength) if inflows else None
        
        # Top outflow
        outflows = [f for f in flows if f.direction == CapitalFlowDirection.OUTFLOW]
        top_outflow = max(outflows, key=lambda f: f.strength) if outflows else None
        
        return {
            "inflow_count": inflow_count,
            "outflow_count": outflow_count,
            "neutral_count": neutral_count,
            "total_inflow_strength": total_inflow_strength,
            "total_outflow_strength": total_outflow_strength,
            "top_inflow": top_inflow.symbol if top_inflow else None,
            "top_outflow": top_outflow.symbol if top_outflow else None,
            "net_flow": total_inflow_strength - total_outflow_strength,
        }


# Singleton
_capital_flow_engine: Optional[CapitalFlowEngine] = None


def get_capital_flow_engine() -> CapitalFlowEngine:
    """Get the singleton CapitalFlowEngine instance."""
    global _capital_flow_engine
    if _capital_flow_engine is None:
        _capital_flow_engine = CapitalFlowEngine()
    return _capital_flow_engine
