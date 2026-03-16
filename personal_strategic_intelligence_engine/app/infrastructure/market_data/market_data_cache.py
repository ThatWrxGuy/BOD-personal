"""Market Data Cache - BB-INF-007

Manages market data caching with proper labeling.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

from app.infrastructure.market_data.market_data_models import (
    LivePriceQuote,
    ValidationStatus,
)

logger = logging.getLogger(__name__)


class MarketDataCache:
    """Manages market data caching with proper staleness labeling."""
    
    def __init__(self, default_ttl_seconds: int = 60):
        self._cache: Dict[str, LivePriceQuote] = {}
        self._cache_metadata: Dict[str, dict] = {}
        self._default_ttl = default_ttl_seconds
    
    def get(self, symbol: str) -> Optional[LivePriceQuote]:
        """Get cached quote if available and not expired."""
        
        if symbol not in self._cache:
            return None
        
        cached = self._cache[symbol]
        metadata = self._cache_metadata.get(symbol, {})
        
        # Check if expired
        retrieved_at = cached.retrieved_at
        ttl = metadata.get("ttl_seconds", self._default_ttl)
        
        age = (datetime.utcnow() - retrieved_at).total_seconds()
        
        if age > ttl:
            # Expired - remove and return None
            self._remove(symbol)
            return None
        
        # Return cached quote with marked as cached
        cached.is_cached = True
        cached.is_stale = age > 15  # Mark as stale if older than 15s
        
        if cached.is_stale:
            cached.validation_status = ValidationStatus.STALE
        
        logger.debug(f"Cache hit for {symbol}: age={age:.1f}s, stale={cached.is_stale}")
        
        return cached
    
    def set(
        self,
        quote: LivePriceQuote,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Cache a quote with metadata."""
        
        ttl = ttl_seconds or self._default_ttl
        
        self._cache[quote.symbol] = quote
        self._cache_metadata[quote.symbol] = {
            "stored_at": datetime.utcnow(),
            "ttl_seconds": ttl,
            "provider": quote.provider_name,
            "original_timestamp": quote.quote_timestamp,
        }
        
        logger.debug(f"Cached quote for {quote.symbol}: ttl={ttl}s")
    
    def _remove(self, symbol: str) -> None:
        """Remove a quote from cache."""
        
        if symbol in self._cache:
            del self._cache[symbol]
        if symbol in self._cache_metadata:
            del self._cache_metadata[symbol]
    
    def invalidate(self, symbol: str) -> None:
        """Invalidate a specific symbol."""
        
        self._remove(symbol)
        logger.info(f"Invalidated cache for {symbol}")
    
    def invalidate_all(self) -> None:
        """Clear entire cache."""
        
        self._cache.clear()
        self._cache_metadata.clear()
        logger.info("Cleared entire market data cache")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        
        now = datetime.utcnow()
        total = len(self._cache)
        stale = 0
        fresh = 0
        
        for symbol, quote in self._cache.items():
            age = (now - quote.retrieved_at).total_seconds()
            if age > 15:
                stale += 1
            else:
                fresh += 1
        
        return {
            "total_cached": total,
            "fresh": fresh,
            "stale": stale,
        }
    
    def is_live_eligible(self, symbol: str) -> bool:
        """Check if cached quote is still eligible for live use."""
        
        cached = self.get(symbol)
        
        if cached is None:
            return False
        
        # Check freshness
        if cached.get_age_seconds() > 15:
            return False
        
        return True


# Global instance
_market_cache: Optional[MarketDataCache] = None


def get_market_data_cache() -> MarketDataCache:
    """Get the market data cache."""
    global _market_cache
    
    if _market_cache is None:
        _market_cache = MarketDataCache()
    
    return _market_cache
