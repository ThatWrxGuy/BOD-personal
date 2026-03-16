"""Macro Pressure Engine - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    CrossAssetSnapshot,
    MacroPressureProfile,
    MacroPressureState,
    SignalScore,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class MacroPressureEngine:
    """Analyzes macro economic pressures."""

    def __init__(self):
        self._prior_macro_state: Optional[MacroPressureState] = None

    def analyze_rate_pressure(
        self,
        yields: Dict[str, float],
        bond_changes: List[float],
    ) -> float:
        """Analyze rate pressure from yields and bond prices."""
        if not yields and not bond_changes:
            return 0.0

        score = 0.0
        signals = []

        # Bond prices down = yields up = rate pressure
        if bond_changes:
            avg_bond_change = sum(bond_changes) / len(bond_changes)
            if avg_bond_change < -1:
                score = 0.8  # Significant rate pressure
                signals.append("Bond prices falling sharply")
            elif avg_bond_change < 0:
                score = 0.4  # Some pressure
                signals.append("Bond prices under pressure")
            elif avg_bond_change > 1:
                score = -0.6  # Rates falling = easing
                signals.append("Bond prices rising (easing)")
            else:
                score = 0.0

        return score

    def analyze_dollar_pressure(
        self,
        dollar_signal,
    ) -> float:
        """Analyze dollar pressure from FX."""
        if dollar_signal is None or dollar_signal.change_pct is None:
            return 0.0

        change = dollar_signal.change_pct

        if change > 2:
            return 0.8  # Strong dollar
        elif change > 0.5:
            return 0.4  # Moderate dollar strength
        elif change < -2:
            return -0.8  # Dollar weakening
        elif change < -0.5:
            return -0.4  # Moderate dollar weakness
        else:
            return 0.0

    def analyze_commodity_pressure(
        self,
        commodities,
    ) -> float:
        """Analyze commodity/inflation pressure."""
        if not commodities:
            return 0.0

        changes = [c.change_pct for c in commodities if c.change_pct is not None]
        if not changes:
            return 0.0

        avg_change = sum(changes) / len(changes)

        if avg_change > 3:
            return 0.8  # Strong inflation pressure
        elif avg_change > 1:
            return 0.4  # Moderate pressure
        elif avg_change < -3:
            return -0.6  # Deflationary
        elif avg_change < -1:
            return -0.3  # Some easing
        else:
            return 0.0

    def infer_growth_outlook(
        self,
        equity_changes: List[float],
        bond_changes: List[float],
        commodity_changes: List[float],
    ) -> str:
        """Infer growth vs slowdown from asset behavior."""
        signals = []

        # Rising equities + rising bonds = growth positive
        # Rising equities + falling bonds = potential inflation concern
        # Falling equities + rising bonds = risk-off / growth concern

        if equity_changes:
            avg_equity = sum(equity_changes) / len(equity_changes)
        else:
            avg_equity = 0.0

        if bond_changes:
            avg_bond = sum(bond_changes) / len(bond_changes)
        else:
            avg_bond = 0.0

        if commodity_changes:
            avg_commodity = sum(commodity_changes) / len(commodity_changes)
        else:
            avg_commodity = 0.0

        # Simple inference
        growth_score = avg_equity * 0.5 + avg_bond * 0.3 + avg_commodity * 0.2

        if growth_score > 3:
            return "growth"
        elif growth_score < -3:
            return "slowdown"
        else:
            return "neutral"

    def analyze_macro_pressure(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> MacroPressureProfile:
        """Analyze macro pressure from snapshot."""
        # Collect changes
        equity_changes = [e.change_pct for e in snapshot.equities if e.change_pct is not None]
        bond_changes = [b.change_pct for b in snapshot.bonds if b.change_pct is not None]
        commodity_changes = [c.change_pct for c in snapshot.commodities if c.change_pct is not None]

        # Analyze each pressure type
        rate_pressure = self.analyze_rate_pressure(snapshot.yields, bond_changes)
        dollar_pressure = self.analyze_dollar_pressure(snapshot.dollar)
        commodity_pressure = self.analyze_commodity_pressure(snapshot.commodities)

        # Overall macro state
        pressures = [p for p in [rate_pressure, dollar_pressure, commodity_pressure] if p != 0]
        if pressures:
            avg_pressure = sum(pressures) / len(pressures)
            if avg_pressure > 0.4:
                macro_state = MacroPressureState.STRESS
            elif avg_pressure > 0.15:
                macro_state = MacroPressureState.TIGHTENING
            elif avg_pressure < -0.4:
                macro_state = MacroPressureState.STIMULUS
            elif avg_pressure < -0.15:
                macro_state = MacroPressureState.NEUTRAL
            else:
                macro_state = MacroPressureState.NEUTRAL
        else:
            macro_state = MacroPressureState.NEUTRAL

        # Build signals
        rate_signals = []
        if rate_pressure > 0.5:
            rate_signals.append("Rising rate pressure detected")
        elif rate_pressure < -0.3:
            rate_signals.append("Rate easing detected")

        dollar_signals = []
        if snapshot.dollar and snapshot.dollar.change_pct:
            dollar_signals.append(f"Dollar: {snapshot.dollar.change_pct:+.1f}%")

        commodity_signals = []
        if commodity_changes:
            commodity_signals.append(f"Commodities: {sum(commodity_changes)/len(commodity_changes):+.1f}%")

        # Infer growth
        growth = self.infer_growth_outlook(equity_changes, bond_changes, commodity_changes)

        return MacroPressureProfile(
            rate_pressure=rate_pressure,
            dollar_pressure=dollar_pressure,
            commodity_pressure=commodity_pressure,
            growth_inference=growth,
            overall_macro_state=macro_state,
            rate_signals=rate_signals,
            dollar_signals=dollar_signals,
            commodity_signals=commodity_signals,
        )

    def generate_macro_pressure_score(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> SignalScore:
        """Generate macro pressure signal score."""
        profile = self.analyze_macro_pressure(snapshot)

        # Positive score = favorable for risk (easing)
        # Negative score = headwind (tightening)
        
        pressures = []
        if profile.rate_pressure:
            pressures.append(profile.rate_pressure)
        if profile.dollar_pressure:
            pressures.append(profile.dollar_pressure * 0.5)  # Dollar less weight
        if profile.commodity_pressure:
            pressures.append(profile.commodity_pressure * 0.5)  # Commodities less weight

        if pressures:
            score = sum(pressures) / len(pressures)
        else:
            score = 0.0

        # Invert: easing (negative pressure) = positive for risk
        score = -score

        # Clamp
        score = max(-1.0, min(1.0, score))

        # Determine confidence
        confidence = ConfidenceLevel.MODERATE if pressures else ConfidenceLevel.LOW

        direction = "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral")

        contributing_factors = []
        contributing_factors.extend(profile.rate_signals[:2])
        contributing_factors.extend(profile.dollar_signals[:2])
        contributing_factors.extend(profile.commodity_signals[:2])
        contributing_factors.append(f"Growth outlook: {profile.growth_inference}")

        return SignalScore(
            family="macro_pressure",
            score=score,
            direction=direction,
            confidence=confidence,
            contributing_factors=contributing_factors,
            timestamp=datetime.utcnow(),
        )


# Singleton
_macro_pressure_engine: Optional[MacroPressureEngine] = None


def get_macro_pressure_engine() -> MacroPressureEngine:
    """Get the singleton MacroPressureEngine instance."""
    global _macro_pressure_engine
    if _macro_pressure_engine is None:
        _macro_pressure_engine = MacroPressureEngine()
    return _macro_pressure_engine
