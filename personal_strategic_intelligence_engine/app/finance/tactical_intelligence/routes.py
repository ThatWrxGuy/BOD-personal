"""API Routes for Tactical Intelligence - BB-FIN-018."""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.finance.tactical_intelligence.tactical_intelligence_service import (
    get_tactical_intelligence_service,
    TacticalIntelligenceService,
)

router = APIRouter(prefix="/finance/tactical-intelligence", tags=["tactical-intelligence"])


class AnalyzeRequest(BaseModel):
    """Request to run tactical analysis."""
    symbol: str
    timeframe: Optional[str] = "5m"
    market_regime: Optional[str] = None
    sector_context: Optional[str] = None
    options_environment: Optional[str] = None


@router.get("/status")
async def get_status():
    """Get tactical intelligence system status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "module": "BB-FIN-018",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/structure/{symbol}")
async def get_structure(
    symbol: str,
    timeframe: str = "5m",
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Get market structure analysis."""
    return service.get_structure(symbol, timeframe)


@router.get("/liquidity-events/{symbol}")
async def get_liquidity_events(
    symbol: str,
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Get liquidity events analysis."""
    return service.get_liquidity_events(symbol)


@router.get("/momentum/{symbol}")
async def get_momentum(
    symbol: str,
    timeframe: str = "5m",
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Get momentum analysis."""
    return service.get_momentum(symbol, timeframe)


@router.get("/breakouts/{symbol}")
async def get_breakouts(
    symbol: str,
    timeframe: str = "5m",
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Get breakout analysis."""
    return service.get_breakouts(symbol, timeframe)


@router.get("/entry-signals/{symbol}")
async def get_entry_signals(
    symbol: str,
    timeframe: str = "5m",
    market_regime: Optional[str] = None,
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Get entry signals."""
    return service.get_entry_signals(symbol, timeframe, market_regime)


@router.get("/report/{symbol}")
async def get_report(
    symbol: str,
    timeframe: str = "5m",
    market_regime: Optional[str] = None,
    sector_context: Optional[str] = None,
    options_environment: Optional[str] = None,
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Get complete tactical report."""
    return service.get_report(symbol, timeframe, market_regime, sector_context, options_environment)


@router.post("/analyze")
async def analyze(
    request: AnalyzeRequest,
    service: TacticalIntelligenceService = Depends(get_tactical_intelligence_service),
):
    """Run tactical analysis."""
    return service.analyze(
        symbol=request.symbol,
        timeframe=request.timeframe,
        market_regime=request.market_regime,
        sector_context=request.sector_context,
        options_environment=request.options_environment,
    )
