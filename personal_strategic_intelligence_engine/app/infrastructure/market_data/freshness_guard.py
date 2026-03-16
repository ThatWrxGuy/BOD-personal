"""Freshness Guard - BB-INF-007

Ensures quotes meet freshness requirements.
"""

from datetime import datetime
from typing import Optional
import logging

from app.infrastructure.market_data.market_data_models import (
    LivePriceQuote,
    PriceValidationResult,
    AssetType,
)

logger = logging.getLogger(__name__)


class FreshnessGuard:
    """Validates quote freshness based on asset type and use case."""
    
    # Default thresholds (can be overridden by policy)
    DEFAULT_THRESHOLDS = {
        AssetType.EQUITY: {
            "max_age": 15.0,  # seconds
            "warning_age": 5.0,
        },
        AssetType.OPTION: {
            "max_age": 5.0,
            "warning_age": 2.0,
        },
        AssetType.ETF: {
            "max_age": 15.0,
            "warning_age": 5.0,
        },
        AssetType.INDEX: {
            "max_age": 60.0,
            "warning_age": 15.0,
        },
        AssetType.FOREX: {
            "max_age": 30.0,
            "warning_age": 10.0,
        },
        AssetType.CRYPTO: {
            "max_age": 5.0,
            "warning_age": 1.0,
        },
    }
    
    def __init__(self):
        pass
    
    def validate(
        self,
        quote: LivePriceQuote,
        asset_type: AssetType = None,
        max_age: float = None,
    ) -> PriceValidationResult:
        """Validate quote freshness."""
        
        asset_type = asset_type or quote.asset_type
        
        # Get thresholds
        if max_age is None:
            thresholds = self.DEFAULT_THRESHOLDS.get(asset_type, {"max_age": 15.0})
            max_age = thresholds["max_age"]
        
        # Calculate staleness
        staleness = quote.get_age_seconds()
        
        # Check freshness
        is_fresh = staleness <= max_age
        
        result = PriceValidationResult(
            symbol=quote.symbol,
            passed_freshness_check=is_fresh,
            staleness_seconds=staleness,
            quote=quote,
        )
        
        if is_fresh:
            result.approved_for_decisioning = True
            result.passed_freshness_check = True
        else:
            result.failure_reason = f"Quote stale: {staleness:.1f}s old (max: {max_age}s)"
            result.approved_for_decisioning = False
        
        logger.debug(f"Freshness check for {quote.symbol}: {staleness:.1f}s, approved={is_fresh}")
        
        return result
    
    def validate_for_use_case(
        self,
        quote: LivePriceQuote,
        use_case: str,
    ) -> PriceValidationResult:
        """Validate quote for specific use case."""
        
        # Use case specific thresholds
        use_case_thresholds = {
            "trading": {"equity": 15.0, "option": 5.0},
            "analysis": {"equity": 60.0, "option": 30.0},
            "reporting": {"equity": 300.0, "option": 120.0},
            "alerting": {"equity": 15.0, "option": 5.0},
            "backtest": {"equity": float('inf'), "option": float('inf')},
        }
        
        thresholds = use_case_thresholds.get(use_case, {})
        max_age = thresholds.get(quote.asset_type.value, 15.0)
        
        return self.validate(quote, max_age=max_age)
    
    def get_age_warning(self, quote: LivePriceQuote) -> Optional[str]:
        """Get warning message if quote is old but not invalid."""
        
        staleness = quote.get_age_seconds()
        asset_type = quote.asset_type
        
        thresholds = self.DEFAULT_THRESHOLDS.get(asset_type, {"warning_age": 5.0})
        warning_age = thresholds.get("warning_age", 5.0)
        max_age = thresholds.get("max_age", 15.0)
        
        if staleness > warning_age and staleness <= max_age:
            return f"Quote is {staleness:.1f}s old - consider fresh data"
        
        return None


_freshness_guard: Optional[FreshnessGuard] = None


def get_freshness_guard() -> FreshnessGuard:
    """Get the freshness guard."""
    global _freshness_guard
    
    if _freshness_guard is None:
        _freshness_guard = FreshnessGuard()
    
    return _freshness_guard
