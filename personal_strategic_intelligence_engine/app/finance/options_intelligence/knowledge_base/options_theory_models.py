"""Options Theory Models.

Structured models derived from Master Knowledge Package.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class StrategyCategory(str, Enum):
    VOLATILITY = "volatility"
    INCOME = "income"
    DIRECTIONAL = "directional"
    HEDGING = "hedging"
    ARBITRAGE = "arbitrage"


class OptionLegType(str, Enum):
    LONG_CALL = "long_call"
    SHORT_CALL = "short_call"
    LONG_PUT = "long_put"
    SHORT_PUT = "short_put"
    STOCK = "stock"


class VolatilityRegime(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    ELEVATED = "elevated"
    SPIKE = "spike"
    CRUSH = "crush"


@dataclass
class StrategyPrinciple:
    """Core strategy principle from knowledge package."""
    principle_id: str
    name: str
    author: str
    concept: str
    description: str
    strategic_application: str
    
    def to_dict(self) -> dict:
        return {
            "principle_id": self.principle_id,
            "name": self.name,
            "author": self.author,
            "concept": self.concept,
            "description": self.description,
            "strategic_application": self.strategic_application,
        }


@dataclass
class GreekProfile:
    """Options Greek profile."""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    
    def to_dict(self) -> dict:
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "theta": self.theta,
            "vega": self.vega,
            "rho": self.rho,
        }


@dataclass
class OptionLeg:
    """Single option leg in a strategy."""
    leg_type: OptionLegType
    strike: float
    expiration_days: int
    quantity: int = 1
    
    def to_dict(self) -> dict:
        return {
            "leg_type": self.leg_type.value,
            "strike": self.strike,
            "expiration_days": self.expiration_days,
            "quantity": self.quantity,
        }


@dataclass
class OptionsStrategy:
    """Complete options strategy model."""
    strategy_id: str
    name: str
    category: StrategyCategory
    objective: str
    legs: List[OptionLeg]
    greek_profile: GreekProfile
    volatility_dependency: str
    expiration_profile: str
    risk_characteristics: Dict[str, Any]
    theoretical_basis: str
    
    def to_dict(self) -> dict:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "category": self.category.value,
            "objective": self.objective,
            "legs": [leg.to_dict() for leg in self.legs],
            "greek_profile": self.greek_profile.to_dict(),
            "volatility_dependency": self.volatility_dependency,
            "expiration_profile": self.expiration_profile,
            "risk_characteristics": self.risk_characteristics,
            "theoretical_basis": self.theoretical_basis,
        }


@dataclass
class VolatilityFramework:
    """Volatility analysis framework."""
    framework_id: str
    name: str
    source: str
    description: str
    
    def to_dict(self) -> dict:
        return {
            "framework_id": self.framework_id,
            "name": self.name,
            "source": self.source,
            "description": self.description,
        }


@dataclass
class IVAnalysis:
    """Implied Volatility analysis."""
    symbol: str
    current_iv: float
    iv_rank: float
    iv_percentile: float
    hv: float
    iv_hv_ratio: float
    regime: VolatilityRegime
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "current_iv": self.current_iv,
            "iv_rank": self.iv_rank,
            "iv_percentile": self.iv_percentile,
            "hv": self.hv,
            "iv_hv_ratio": self.iv_hv_ratio,
            "regime": self.regime.value,
            "timestamp": self.timestamp.isoformat(),
        }


# Pre-defined strategy principles
STRATEGY_PRINCIPLES = [
    StrategyPrinciple(
        principle_id="principle-001",
        name="SellThetaBuyIntrinsic",
        author="McMillan",
        concept="Time decay arbitrage",
        description="Sell time value, own intrinsic value. Capture theta decay while maintaining directional exposure.",
        strategic_application="Sell OTM options, exercise or roll at expiration"
    ),
    StrategyPrinciple(
        principle_id="principle-002",
        name="VolatilityArbitrage",
        author="Gatheral",
        concept="IV/HV spread capture",
        description="Buy options when IV is low relative to realized volatility, sell when IV is high.",
        strategic_application="Long volatility positions in low IV, short in elevated IV"
    ),
    StrategyPrinciple(
        principle_id="principle-003",
        name="GammaThetaTradeoff",
        author="Taleb",
        concept="Dynamic hedging",
        description="Long gamma requires frequent rebalancing. Theta decay must be less than gamma profit.",
        strategic_application="Gamma scalping around delta neutral"
    ),
    StrategyPrinciple(
        principle_id="principle-004",
        name="DeltaNeutralHedging",
        author="Hull",
        concept="Risk neutral positioning",
        description="Maintain delta neutral by dynamically hedging underlying exposure.",
        strategic_application="Options market maker hedging"
    ),
    StrategyPrinciple(
        principle_id="principle-005",
        name="SkewTrading",
        author="Natenberg",
        concept="Volatility smile capture",
        description="Trade the difference in IV between strikes (skew) expecting reversion to mean.",
        strategic_application="Trade put/call ratio skew"
    ),
]


# Pre-defined options strategies
OPTIONS_STRATEGIES = [
    OptionsStrategy(
        strategy_id="strat-diagonal-001",
        name="Diagonal Spread",
        category=StrategyCategory.INCOME,
        objective="Sell theta, own intrinsic value with time spread",
        legs=[
            OptionLeg(OptionLegType.SHORT_CALL, 5, 30),
            OptionLeg(OptionLegType.LONG_CALL, 10, 60),
        ],
        greek_profile=GreekProfile(delta=0.3, gamma=-0.02, theta=0.15, vega=-0.1, rho=0.05),
        volatility_dependency="Benefit from IV increase",
        expiration_profile="Time decay accelerates near expiration",
        risk_characteristics={"max_loss": "limited", "break_even": "lower_strike + net_debit"},
        theoretical_basis="McMillan's Time Spread"
    ),
    OptionsStrategy(
        strategy_id="strat-butterfly-001",
        name="Iron Butterfly",
        category=StrategyCategory.INCOME,
        objective="Short volatility, income generation with defined risk",
        legs=[
            OptionLeg(OptionLegType.SHORT_PUT, -5, 30),
            OptionLeg(OptionLegType.LONG_PUT, -10, 30),
            OptionLeg(OptionLegType.SHORT_CALL, 5, 30),
            OptionLeg(OptionLegType.LONG_CALL, 10, 30),
        ],
        greek_profile=GreekProfile(delta=0, gamma=0.05, theta=-0.2, vega=-0.3, rho=0),
        volatility_dependency="Short vega - benefit from IV decrease",
        expiration_profile="Max profit at ATM at expiration",
        risk_characteristics={"max_loss": "strike_width - credit_received", "break_even": ["lower_strike", "upper_strike"]},
        theoretical_basis="TOMIC Framework"
    ),
    OptionsStrategy(
        strategy_id="strat-gamma-001",
        name="Gamma Scalp",
        category=StrategyCategory.VOLATILITY,
        objective="Long gamma, capture volatility through dynamic hedging",
        legs=[
            OptionLeg(OptionLegType.LONG_CALL, 0, 5),
        ],
        greek_profile=GreekProfile(delta=0.5, gamma=0.1, theta=-0.3, vega=0.2, rho=0.02),
        volatility_dependency="Long vega - benefit from IV increase",
        expiration_profile="High theta decay, short duration",
        risk_characteristics={"max_loss": "unlimited", "hedge_frequency": "intraday"},
        theoretical_basis="Taleb Dynamic Hedging"
    ),
    OptionsStrategy(
        strategy_id="strat-straddle-001",
        name="Long Straddle",
        category=StrategyCategory.VOLATILITY,
        objective="Profit from large price move in either direction",
        legs=[
            OptionLeg(OptionLegType.LONG_CALL, 0, 30),
            OptionLeg(OptionLegType.LONG_PUT, 0, 30),
        ],
        greek_profile=GreekProfile(delta=0, gamma=0.05, theta=-0.15, vega=0.25, rho=0),
        volatility_dependency="Long vega - benefit from IV increase",
        expiration_profile="Time decay accelerates, needs move before expiration",
        risk_characteristics={"max_loss": "premium_paid", "break_even": ["strike - premium", "strike + premium"]},
        theoretical_basis="Volatility play"
    ),
]
