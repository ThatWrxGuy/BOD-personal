"""Market Data Infrastructure - BB-INF-007

Live Market Data Integrity & Anti-Stale Pricing Enforcement Layer.

This module provides:
- Live Price Provider: Fetches live market data
- Market Data Resolver: Central resolver with strict validation
- Freshness Guard: Validates quote freshness
- Market Session Guard: Validates market session rules
- Price Integrity Auditor: Monitors data integrity
- Market Data Cache: Manages caching with proper labeling
"""

from app.infrastructure.market_data.market_data_models import (
    LivePriceQuote,
    PriceValidationResult,
    MarketDataPolicy,
    MarketDataIntegrityReport,
    EnvironmentMode,
    AssetType,
    MarketSession,
    ValidationStatus,
    ProviderStatus,
)

from app.infrastructure.market_data.market_data_resolver import (
    MarketDataResolver,
    get_market_data_resolver,
)

__all__ = [
    # Models
    "LivePriceQuote",
    "PriceValidationResult",
    "MarketDataPolicy",
    "MarketDataIntegrityReport",
    "EnvironmentMode",
    "AssetType",
    "MarketSession",
    "ValidationStatus",
    "ProviderStatus",
    # Resolver
    "MarketDataResolver",
    "get_market_data_resolver",
]
