"""Market Data API Routes - BB-INF-007"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.infrastructure.market_data.market_data_resolver import (
    get_market_data_resolver,
)
from app.infrastructure.market_data.market_data_models import (
    LivePriceQuote,
    PriceValidationResult,
    MarketDataIntegrityReport,
    MarketDataPolicy,
    AssetType,
    QuoteRequest,
)
from app.infrastructure.market_data.price_integrity_auditor import (
    get_price_integrity_auditor,
)
from app.infrastructure.market_data.market_data_cache import (
    get_market_data_cache,
)

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.get("/quote/{symbol}", response_model=LivePriceQuote)
async def get_quote(
    symbol: str,
    asset_type: str = Query("equity", description="Asset type: equity, option, etf, etc."),
    context: str = Query("general", description="Use context: trading, analysis, reporting"),
    require_live: bool = Query(True, description="Require live quote"),
):
    """Get live price quote for a symbol."""
    resolver = get_market_data_resolver()
    
    try:
        asset = AssetType(asset_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid asset type: {asset_type}")
    
    try:
        quote = await resolver.get_live_quote(
            symbol=symbol.upper(),
            asset_type=asset,
            context=context,
            require_live=require_live,
        )
        return quote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health/{symbol}")
async def get_quote_health(symbol: str):
    """Get health status for a symbol's quote."""
    resolver = get_market_data_resolver()
    
    try:
        quote = await resolver.get_live_quote(symbol=symbol.upper())
        validation = resolver.validate_quote(quote)
        
        return {
            "symbol": symbol.upper(),
            "has_valid_quote": validation.approved_for_decisioning,
            "validation": validation.model_dump(),
        }
    except ValueError as e:
        return {
            "symbol": symbol.upper(),
            "has_valid_quote": False,
            "error": str(e),
        }


@router.post("/validate", response_model=PriceValidationResult)
async def validate_quote(
    quote: LivePriceQuote,
    context: str = Query("general"),
):
    """Validate a quote for decisioning."""
    resolver = get_market_data_resolver()
    
    return resolver.validate_quote(quote, context)


@router.get("/provider-status")
async def get_provider_status():
    """Get market data provider status."""
    resolver = get_market_data_resolver()
    
    return {
        "provider": "demo_provider",
        "status": "healthy",
        "policy": resolver.get_policy().model_dump(),
    }


@router.get("/session")
async def get_market_session():
    """Get current market session state."""
    resolver = get_market_data_resolver()
    
    return resolver.get_market_state()


@router.get("/integrity-report", response_model=MarketDataIntegrityReport)
async def get_integrity_report():
    """Get market data integrity report."""
    auditor = get_price_integrity_auditor()
    
    return auditor.generate_report()


@router.get("/cache-stats")
async def get_cache_stats():
    """Get market data cache statistics."""
    cache = get_market_data_cache()
    
    return cache.get_stats()


@router.post("/cache/invalidate")
async def invalidate_cache(symbol: Optional[str] = None):
    """Invalidate cache for a symbol or all."""
    cache = get_market_data_cache()
    
    if symbol:
        cache.invalidate(symbol.upper())
        return {"status": "invalidated", "symbol": symbol.upper()}
    else:
        cache.invalidate_all()
        return {"status": "cleared"}


@router.get("/policy", response_model=MarketDataPolicy)
async def get_policy():
    """Get current market data policy."""
    resolver = get_market_data_resolver()
    
    return resolver.get_policy()
