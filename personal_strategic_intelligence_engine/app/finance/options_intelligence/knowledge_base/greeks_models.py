"""Greeks Models.

Options Greek calculations and analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class GreekSignal(str, Enum):
    DELTA_EXPOSURE = "delta_exposure"
    GAMMA_EXPOSURE = "gamma_exposure"
    THETA_HARVEST = "theta_harvest"
    VEGA_RISK = "vega_risk"
    RHO_SENSITIVITY = "rho_sensitivity"


@dataclass
class OptionGreeks:
    """Complete option Greeks."""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    vanna: float = 0.0
    charm: float = 0.0
    vomma: float = 0.0
    speed: float = 0.0
    zomma: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "theta": self.theta,
            "vega": self.vega,
            "rho": self.rho,
            "vanna": self.vanna,
            "charm": self.charm,
            "vomma": self.vomma,
            "speed": self.speed,
            "zomma": self.zomma,
        }


@dataclass
class GreekExposure:
    """Aggregate Greek exposure for portfolio."""
    net_delta: float
    net_gamma: float
    net_theta: float
    net_vega: float
    net_rho: float
    delta_direction: str
    gamma_risk_level: str
    theta_contribution: float
    
    def to_dict(self) -> dict:
        return {
            "net_delta": self.net_delta,
            "net_gamma": self.net_gamma,
            "net_theta": self.net_theta,
            "net_vega": self.net_vega,
            "net_rho": self.net_rho,
            "delta_direction": self.delta_direction,
            "gamma_risk_level": self.gamma_risk_level,
            "theta_contribution": self.theta_contribution,
        }


@dataclass
class GreekSignal:
    """Greek-based trading signal."""
    signal_type: GreekSignal
    strength: float
    interpretation: str
    action: str
    confidence: float
    
    def to_dict(self) -> dict:
        return {
            "signal_type": self.signal_type.value,
            "strength": self.strength,
            "interpretation": self.interpretation,
            "action": self.action,
            "confidence": self.confidence,
        }


class GreeksCalculator:
    """Calculates option Greeks."""
    
    def __init__(self):
        # Simplified Black-Scholes placeholder
        pass
    
    def calculate_greeks(
        self,
        option_type: str,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
    ) -> OptionGreeks:
        """Calculate Greeks using Black-Scholes."""
        import math
        
        # Simplified calculations
        d1 = (math.log(spot_price / strike_price) + (risk_free_rate + volatility ** 2 / 2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)
        
        if option_type == "call":
            delta = math.exp(-risk_free_rate * time_to_expiry) * (0.5 + math.erf(d1 / math.sqrt(2)) / 2)
            rho = strike_price * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * (0.5 + math.erf(d2 / math.sqrt(2)) / 2) / 100
        else:
            delta = -math.exp(-risk_free_rate * time_to_expiry) * (0.5 - math.erf(d1 / math.sqrt(2)) / 2)
            rho = -strike_price * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * (0.5 - math.erf(d2 / math.sqrt(2)) / 2) / 100
        
        # Gamma and Vega are same for call and put
        gamma = math.exp(-risk_free_rate * time_to_expiry) * math.exp(-d1 ** 2 / 2) / (spot_price * volatility * math.sqrt(2 * math.pi * time_to_expiry))
        vega = spot_price * math.sqrt(time_to_expiry) * math.exp(-d1 ** 2 / 2) / math.sqrt(2 * math.pi) / 100
        
        # Theta (per day)
        theta = (-(spot_price * volatility * math.exp(-d1 ** 2 / 2) / (2 * math.sqrt(2 * math.pi * time_to_expiry))) 
                 - risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * (0.5 + math.erf(d2 / math.sqrt(2)) / 2)) / 365
        
        if option_type == "call":
            theta = theta + risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * (0.5 + math.erf(d2 / math.sqrt(2)) / 2) / 365
        else:
            theta = theta - risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * (0.5 - math.erf(d2 / math.sqrt(2)) / 2) / 365
        
        return OptionGreeks(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
        )
    
    def analyze_exposure(self, positions: list) -> GreekExposure:
        """Analyze portfolio Greek exposure."""
        
        net_delta = sum(p.get("delta", 0) * p.get("quantity", 0) for p in positions)
        net_gamma = sum(p.get("gamma", 0) * p.get("quantity", 0) for p in positions)
        net_theta = sum(p.get("theta", 0) * p.get("quantity", 0) for p in positions)
        net_vega = sum(p.get("vega", 0) * p.get("quantity", 0) for p in positions)
        net_rho = sum(p.get("rho", 0) * p.get("quantity", 0) for p in positions)
        
        # Determine direction
        if net_delta > 0.1:
            delta_direction = "long"
        elif net_delta < -0.1:
            delta_direction = "short"
        else:
            delta_direction = "neutral"
        
        # Gamma risk level
        if abs(net_gamma) > 0.5:
            gamma_risk_level = "high"
        elif abs(net_gamma) > 0.2:
            gamma_risk_level = "medium"
        else:
            gamma_risk_level = "low"
        
        return GreekExposure(
            net_delta=net_delta,
            net_gamma=net_gamma,
            net_theta=net_theta,
            net_vega=net_vega,
            net_rho=net_rho,
            delta_direction=delta_direction,
            gamma_risk_level=gamma_risk_level,
            theta_contribution=net_theta,
        )
    
    def generate_signals(self, exposure: GreekExposure) -> list:
        """Generate Greek-based signals."""
        
        signals = []
        
        # Delta signals
        if abs(exposure.net_delta) > 0.5:
            signals.append(GreekSignal(
                signal_type=GreekSignal.DELTA_EXPOSURE,
                strength=abs(exposure.net_delta),
                interpretation=f"Significant delta {'long' if exposure.net_delta > 0 else 'short'} exposure",
                action="Consider hedging" if abs(exposure.net_delta) > 0.8 else "Monitor",
                confidence=0.8,
            ))
        
        # Gamma signals
        if exposure.gamma_risk_level == "high":
            signals.append(GreekSignal(
                signal_type=GreekSignal.GAMMA_EXPOSURE,
                strength=abs(exposure.net_gamma),
                interpretation="High gamma risk - rapid delta changes",
                action="Prepare for rebalancing",
                confidence=0.85,
            ))
        
        # Theta signals
        if exposure.net_theta > 0:
            signals.append(GreekSignal(
                signal_type=GreekSignal.THETA_HARVEST,
                strength=exposure.net_theta,
                interpretation="Positive theta - time decay working in your favor",
                action="Maintain position",
                confidence=0.9,
            ))
        
        return signals


def create_calculator() -> GreeksCalculator:
    """Create Greeks calculator."""
    return GreeksCalculator()
