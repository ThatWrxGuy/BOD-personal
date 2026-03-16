"""Market Data Resolver - BB-INF-007

Central resolver for market data with strict validation.
"""

import os
from datetime import datetime
from typing import Optional
import logging

from app.infrastructure.market_data.market_data_models import (
    LivePriceQuote,
    PriceValidationResult,
    MarketDataPolicy,
    EnvironmentMode,
    ValidationStatus,
    AssetType,
    QuoteRequest,
)

from app.infrastructure.market_data.live_price_provider import (
    get_live_price_provider,
)
from app.infrastructure.market_data.freshness_guard import (
    get_freshness_guard,
)
from app.infrastructure.market_data.market_session_guard import (
    get_market_session_guard,
)
from app.infrastructure.market_data.market_data_cache import (
    get_market_data_cache,
)
from app.infrastructure.market_data.price_integrity_auditor import (
    get_price_integrity_auditor,
)

logger = logging.getLogger(__name__)


class MarketDataResolver:
    """Central resolver for market data with strict validation."""
    
    def __init__(self):
        self._policy = self._load_policy()
        self._provider = get_live_price_provider()
        self._freshness_guard = get_freshness_guard()
        self._session_guard = get_market_session_guard()
        self._cache = get_market_data_cache()
        self._auditor = get_price_integrity_auditor()
    
    def _load_policy(self) -> MarketDataPolicy:
        """Load market data policy from environment."""
        
        env = os.getenv("MARKET_DATA_ENV", "dev").lower()
        
        policy = MarketDataPolicy()
        
        # Set environment
        if env == "live":
            policy.environment = EnvironmentMode.LIVE
            policy.strict_mode = True
            policy.allow_fallback_in_live = False
        elif env == "paper":
            policy.environment = EnvironmentMode.PAPER
            policy.strict_mode = False
            policy.allow_fallback_in_paper = True
        elif env == "backtest":
            policy.environment = EnvironmentMode.BACKTEST
            policy.strict_mode = False
            policy.allow_fallback_in_backtest = True
        else:
            policy.environment = EnvironmentMode.DEV
            policy.strict_mode = False
            policy.allow_fallback_in_dev = True
        
        return policy
    
    async def get_live_quote(
        self,
        symbol: str,
        asset_type: AssetType = AssetType.EQUITY,
        context: str = "general",
        require_live: bool = True,
    ) -> LivePriceQuote:
        """Get a live quote with full validation."""
        
        start_time = datetime.utcnow()
        
        # Try cache first if allowed
        cached = None
        if not require_live:
            cached = self._cache.get(symbol)
            if cached and cached.is_fresh():
                logger.debug(f"Using fresh cached quote for {symbol}")
                return cached
        
        # Get fresh quote from provider
        quote = await self._provider.get_quote(symbol, asset_type)
        
        # Calculate latency
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Validate the quote
        validation = self.validate_quote(quote, context)
        
        # Record the request
        self._auditor.record_request(
            symbol=symbol,
            module=context,
            provider=quote.provider_name,
            latency_ms=latency,
            approved=validation.approved_for_decisioning,
            failure_reason=validation.failure_reason,
            is_fallback=False,
        )
        
        # Handle validation failure
        if not validation.approved_for_decisioning:
            if self._policy.strict_mode and require_live:
                # In strict mode, fail completely
                raise ValueError(
                    f"Quote validation failed for {symbol}: {validation.failure_reason}"
                )
            
            # In non-strict mode, return with warning
            logger.warning(f"Quote validation issue for {symbol}: {validation.failure_reason}")
        
        # Cache the quote
        self._cache.set(quote)
        
        return quote
    
    def validate_quote(
        self,
        quote: LivePriceQuote,
        context: str = "general",
    ) -> PriceValidationResult:
        """Validate a quote for decisioning."""
        
        result = PriceValidationResult(
            symbol=quote.symbol,
            use_case=context,
            quote=quote,
        )
        
        # Check if we have a valid quote
        if quote.last_price is None or quote.last_price <= 0:
            result.passed_integrity_check = False
            result.failure_reason = "Invalid price: missing or zero"
            return result
        
        result.passed_integrity_check = True
        
        # Freshness check
        freshness_result = self._freshness_guard.validate(quote)
        result.passed_freshness_check = freshness_result.passed_freshness_check
        result.staleness_seconds = freshness_result.staleness_seconds
        
        if not freshness_result.passed_freshness_check:
            result.failure_reason = freshness_result.failure_reason
        
        # Session check
        session_result = self._session_guard.validate(quote)
        result.passed_session_check = session_result.passed_session_check
        
        # Range check (basic sanity)
        if not self._check_price_range(quote):
            result.passed_range_check = False
            result.failure_reason = "Price outside reasonable range"
            return result
        
        result.passed_range_check = True
        
        # Determine approval
        approved = (
            result.passed_integrity_check and
            result.passed_freshness_check and
            result.passed_session_check and
            result.passed_range_check
        )
        
        result.approved_for_decisioning = approved
        
        if not approved and not result.failure_reason:
            result.failure_reason = "Validation failed"
        
        return result
    
    def _check_price_range(self, quote: LivePriceQuote) -> bool:
        """Basic price range sanity check."""
        
        price = quote.last_price
        if price is None:
            return False
        
        # Basic sanity: price should be positive
        if price <= 0:
            return False
        
        # For stocks, typical range is $0.01 to $100,000
        # Allow wide range but flag extremes
        if price > 100000 or price < 0.01:
            logger.warning(f"Unusual price for {quote.symbol}: ${price}")
            # Don't block, but could add additional logging
        
        return True
    
    def get_market_state(self) -> dict:
        """Get current market state."""
        
        session = self._session_guard.get_current_session()
        is_open = self._session_guard.is_trading_open()
        
        return {
            "session": session.value,
            "is_open": is_open,
            "timestamp": datetime.utcnow(),
        }
    
    async def get_quote_with_validation(
        self,
        request: QuoteRequest,
    ) -> tuple[LivePriceQuote, PriceValidationResult]:
        """Get quote with full validation results."""
        
        quote = await self.get_live_quote(
            symbol=request.symbol,
            asset_type=request.asset_type,
            context=request.context,
            require_live=request.require_live,
        )
        
        validation = self.validate_quote(quote, request.context)
        
        return quote, validation
    
    def get_policy(self) -> MarketDataPolicy:
        """Get current policy."""
        
        return self._policy


# Global instance
_resolver: Optional[MarketDataResolver] = None


def get_market_data_resolver() -> MarketDataResolver:
    """Get the market data resolver."""
    global _resolver
    
    if _resolver is None:
        _resolver = MarketDataResolver()
    
    return _resolver
