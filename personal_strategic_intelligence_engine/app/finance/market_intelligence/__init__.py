"""Market Intelligence Module - BB-FIN-014

Multi-Asset Market Intelligence & Regime Engine

This module provides comprehensive market regime detection and intelligence:
- Multi-asset data normalization
- Trend, breadth, volatility, correlation, liquidity analysis
- Macro pressure assessment
- Regime classification
- Policy mapping for portfolio guidance
"""

from app.finance.market_intelligence.market_intelligence_models import (
    # Enums
    RegimeType,
    ConfidenceLevel,
    RiskPosture,
    TrendDirection,
    VolatilityState,
    BreadthState,
    LiquidityState,
    MacroPressureState,
    # Models
    AssetSignal,
    CrossAssetSnapshot,
    SignalScore,
    RegimeScorecard,
    RegimeState,
    MacroPressureProfile,
    BreadthProfile,
    VolatilityProfile,
    CorrelationProfile,
    LiquidityProfile,
    RegimeTransitionAlert,
    RegimePolicy,
    MarketIntelligenceReport,
    RegimeHistoryEntry,
)

from app.finance.market_intelligence.data_normalizer import DataNormalizer, get_normalizer
from app.finance.market_intelligence.trend_engine import TrendEngine, get_trend_engine
from app.finance.market_intelligence.breadth_engine import BreadthEngine, get_breadth_engine
from app.finance.market_intelligence.volatility_engine import VolatilityEngine, get_volatility_engine
from app.finance.market_intelligence.correlation_engine import CorrelationEngine, get_correlation_engine
from app.finance.market_intelligence.macro_pressure_engine import MacroPressureEngine, get_macro_pressure_engine
from app.finance.market_intelligence.liquidity_stress_engine import LiquidityStressEngine, get_liquidity_stress_engine
from app.finance.market_intelligence.regime_classifier import RegimeClassifier, get_regime_classifier
from app.finance.market_intelligence.regime_policy_mapper import RegimePolicyMapper, get_regime_policy_mapper
from app.finance.market_intelligence.market_intelligence_service import MarketIntelligenceService, get_market_intelligence_service
from app.finance.market_intelligence.routes import router

__all__ = [
    # Enums
    "RegimeType",
    "ConfidenceLevel",
    "RiskPosture",
    "TrendDirection",
    "VolatilityState",
    "BreadthState",
    "LiquidityState",
    "MacroPressureState",
    # Models
    "AssetSignal",
    "CrossAssetSnapshot",
    "SignalScore",
    "RegimeScorecard",
    "RegimeState",
    "MacroPressureProfile",
    "BreadthProfile",
    "VolatilityProfile",
    "CorrelationProfile",
    "LiquidityProfile",
    "RegimeTransitionAlert",
    "RegimePolicy",
    "MarketIntelligenceReport",
    "RegimeHistoryEntry",
    # Engines
    "DataNormalizer",
    "get_normalizer",
    "TrendEngine",
    "get_trend_engine",
    "BreadthEngine",
    "get_breadth_engine",
    "VolatilityEngine",
    "get_volatility_engine",
    "CorrelationEngine",
    "get_correlation_engine",
    "MacroPressureEngine",
    "get_macro_pressure_engine",
    "LiquidityStressEngine",
    "get_liquidity_stress_engine",
    "RegimeClassifier",
    "get_regime_classifier",
    "RegimePolicyMapper",
    "get_regime_policy_mapper",
    # Service
    "MarketIntelligenceService",
    "get_market_intelligence_service",
    # Routes
    "router",
]
