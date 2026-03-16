"""Gamma Exposure Engine - BB-FIN-017"""

from typing import Optional, Dict, List
import logging

from app.finance.options_intelligence.options_models import (
    GammaZone,
    GammaExposureProfile,
    DealerPositionEstimate,
)

logger = logging.getLogger(__name__)


class GammaExposureEngine:
    """Estimate dealer gamma positioning."""

    def __init__(self):
        self._oi_data: Dict[str, Dict] = {}

    def add_oi_data(
        self,
        symbol: str,
        strike: float,
        call_oi: float,
        put_oi: float,
    ) -> None:
        """Add open interest data for a strike."""
        if symbol not in self._oi_data:
            self._oi_data[symbol] = {"calls": {}, "puts": {}}
        
        self._oi_data[symbol]["calls"][strike] = call_oi
        self._oi_data[symbol]["puts"][strike] = put_oi

    def estimate_dealer_positioning(
        self,
        symbol: str,
        current_price: float,
        oi_data: Optional[Dict] = None,
    ) -> DealerPositionEstimate:
        """Estimate dealer positioning from options data."""
        # Use demo data if not provided
        if oi_data is None:
            oi_data = self._generate_demo_oi(symbol, current_price)
        
        # Store OI data
        for strike, oi in (oi_data.get("calls", {}) or {}).items():
            self.add_oi_data(symbol, strike, oi, 0)
        for strike, oi in (oi_data.get("puts", {}) or {}).items():
            self.add_oi_data(symbol, strike, 0, oi)
        
        # Calculate gamma metrics
        net_gamma = self._calculate_net_gamma(oi_data)
        gamma_zone = self._determine_gamma_zone(net_gamma)
        
        # Find key levels
        gamma_support, gamma_resistance = self._find_gamma_levels(oi_data, current_price)
        
        # Calculate pinning risk
        pinning_risk = self._calculate_pinning_risk(gamma_support, gamma_resistance, current_price)
        
        # OI concentration
        call_concentration = self._calculate_oi_concentration(oi_data.get("calls", {}))
        put_concentration = self._calculate_oi_concentration(oi_data.get("puts", {}))
        
        # Gamma squeeze potential
        squeeze_potential = self._calculate_squeeze_potential(oi_data, current_price)
        
        # Hedging pressure
        hedging_pressure = self._determine_hedging_pressure(net_gamma, call_concentration, put_concentration)
        
        return DealerPositionEstimate(
            symbol=symbol,
            net_gamma=net_gamma,
            gamma_zone=gamma_zone,
            gamma_support=gamma_support,
            gamma_resistance=gamma_resistance,
            pinning_risk=pinning_risk,
            call_oi_concentration=call_concentration,
            put_oi_concentration=put_concentration,
            gamma_squeeze_risk=squeeze_potential,
            hedging_pressure=hedging_pressure,
        )

    def _calculate_net_gamma(self, oi_data: Dict) -> float:
        """Calculate net gamma exposure."""
        # Simplified: calls add positive gamma, puts add negative
        calls = oi_data.get("calls", {})
        puts = oi_data.get("puts", {})
        
        call_gamma = sum(calls.values())
        put_gamma = sum(puts.values())
        
        # Net: positive = market maker long gamma (hedging buys on up, sells on down)
        return call_gamma - put_gamma

    def _determine_gamma_zone(self, net_gamma: float) -> GammaZone:
        """Determine gamma zone."""
        if abs(net_gamma) < 100000:
            return GammaZone.ACCELERATION  # Low gamma = acceleration zone
        elif net_gamma > 0:
            return GammaZone.SUPPORT  # Positive gamma = support
        else:
            return GammaZone.RESISTANCE  # Negative gamma = resistance

    def _find_gamma_levels(
        self,
        oi_data: Dict,
        current_price: float,
    ) -> tuple:
        """Find gamma support and resistance levels."""
        calls = oi_data.get("calls", {})
        puts = oi_data.get("puts", {})
        
        if not calls and not puts:
            return None, None
        
        # Find strikes with highest OI (likely support/resistance)
        all_strikes = list(calls.keys()) + list(puts.keys())
        
        # Gamma support: strike below current price with high put OI
        put_strikes = sorted([(s, puts.get(s, 0)) for s in puts.keys()], key=lambda x: -x[1])
        support = put_strikes[0][0] if put_strikes and put_strikes[0][1] > 50000 else None
        
        # Gamma resistance: strike above current price with high call OI
        call_strikes = sorted([(s, calls.get(s, 0)) for s in calls.keys()], key=lambda x: -x[1])
        resistance = call_strikes[0][0] if call_strikes and call_strikes[0][1] > 50000 else None
        
        return support, resistance

    def _calculate_pinning_risk(
        self,
        support: Optional[float],
        resistance: Optional[float],
        current_price: float,
    ) -> float:
        """Calculate probability of pinning to a strike."""
        if support is None and resistance is None:
            return 0.0
        
        # Check proximity to strikes
        risk = 0.0
        
        if support:
            distance_pct = abs(current_price - support) / current_price
            if distance_pct < 0.02:  # Within 2%
                risk += 0.5 * (1 - distance_pct / 0.02)
        
        if resistance:
            distance_pct = abs(current_price - resistance) / current_price
            if distance_pct < 0.02:  # Within 2%
                risk += 0.5 * (1 - distance_pct / 0.02)
        
        return min(1.0, risk)

    def _calculate_oi_concentration(self, oi_by_strike: Dict) -> float:
        """Calculate OI concentration (0-1)."""
        if not oi_by_strike:
            return 0.0
        
        total_oi = sum(oi_by_strike.values())
        if total_oi == 0:
            return 0.0
        
        # Herfindahl index
        concentrations = [(oi / total_oi) ** 2 for oi in oi_by_strike.values()]
        hhi = sum(concentrations)
        
        # Convert to 0-1 scale (HHI > 0.25 = high concentration)
        return min(1.0, hhi / 0.25)

    def _calculate_squeeze_potential(
        self,
        oi_data: Dict,
        current_price: float,
    ) -> float:
        """Calculate potential for gamma squeeze."""
        # High squeeze potential when:
        # 1. High concentration at one strike
        # 2. Low total gamma (acceleration zone)
        
        call_conc = self._calculate_oi_concentration(oi_data.get("calls", {}))
        put_conc = self._calculate_oi_concentration(oi_data.get("puts", {}))
        
        # High concentration = more squeeze potential
        squeeze = max(call_conc, put_conc) * 0.6
        
        # Add factor for total OI volume
        total_oi = sum(oi_data.get("calls", {}).values()) + sum(oi_data.get("puts", {}).values())
        if total_oi > 500000:
            squeeze += 0.3
        elif total_oi > 200000:
            squeeze += 0.2
        elif total_oi > 100000:
            squeeze += 0.1
        
        return min(1.0, squeeze)

    def _determine_hedging_pressure(
        self,
        net_gamma: float,
        call_concentration: float,
        put_concentration: float,
    ) -> str:
        """Determine dealer hedging pressure."""
        if net_gamma > 100000:
            return "long"  # Dealers long gamma = buy dips, sell rips
        elif net_gamma < -100000:
            return "short"  # Dealers short gamma = sell dips, buy rips
        else:
            return "neutral"

    def _generate_demo_oi(self, symbol: str, current_price: float) -> Dict:
        """Generate demo OI data."""
        import random
        
        # Generate strikes around current price
        calls = {}
        puts = {}
        
        # ATM strikes
        atm = round(current_price / 5) * 5
        
        # Create clustered OI
        for strike in [atm - 20, atm - 15, atm - 10, atm - 5, atm, atm + 5, atm + 10, atm + 15, atm + 20]:
            if strike > 0:
                # Higher OI near ATM
                distance = abs(strike - atm)
                weight = max(10000, 100000 - distance * 5000)
                calls[strike] = weight + random.randint(-10000, 10000)
                puts[strike] = weight + random.randint(-10000, 10000)
        
        return {"calls": calls, "puts": puts}

    def create_gamma_map(
        self,
        symbol: str,
        current_price: float,
        oi_data: Optional[Dict] = None,
    ) -> GammaExposureProfile:
        """Create complete gamma exposure map."""
        positioning = self.estimate_dealer_positioning(symbol, current_price, oi_data)
        
        # Calculate pin level
        pin_level = None
        if positioning.gamma_support and positioning.gamma_resistance:
            # Pin to the closer one
            dist_support = abs(current_price - positioning.gamma_support)
            dist_resistance = abs(current_price - positioning.gamma_resistance)
            pin_level = positioning.gamma_support if dist_support < dist_resistance else positioning.gamma_resistance
        
        # Calculate acceleration zone
        vol_accel = None
        if positioning.gamma_zone == GammaZone.ACCELERATION:
            vol_accel = current_price
        
        return GammaExposureProfile(
            symbol=symbol,
            gamma_max_strike=positioning.gamma_support or positioning.gamma_resistance,
            gamma_support=positioning.gamma_support,
            gamma_resistance=positioning.gamma_resistance,
            pin_level=pin_level,
            pinning_probability=positioning.pinning_risk,
            positive_gamma_zone_low=positioning.gamma_support,
            positive_gamma_zone_high=positioning.gamma_resistance,
            gamma_squeeze_potential=positioning.gamma_squeeze_risk,
            vol_acceleration_zone=vol_accel,
        )


# Singleton
_gamma_engine: Optional[GammaExposureEngine] = None


def get_gamma_exposure_engine() -> GammaExposureEngine:
    """Get the singleton GammaExposureEngine instance."""
    global _gamma_engine
    if _gamma_engine is None:
        _gamma_engine = GammaExposureEngine()
    return _gamma_engine
