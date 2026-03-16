"""API Routes for Options Intelligence - BB-FIN-017."""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.finance.options_intelligence.options_intelligence_service import (
    get_options_intelligence_service,
    OptionsIntelligenceService,
)

router = APIRouter(prefix="/finance/options-intelligence", tags=["options-intelligence"])


class AnalyzeRequest(BaseModel):
    """Request to run options intelligence analysis."""
    symbol: str
    current_price: Optional[float] = 100.0
    market_regime: Optional[str] = None
    sector_context: Optional[str] = None


@router.get("/status")
async def get_status():
    """Get options intelligence system status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "module": "BB-FIN-017",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/iv-regime/{symbol}")
async def get_iv_regime(
    symbol: str,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get IV regime analysis for a symbol."""
    return service.get_iv_regime(symbol)


@router.get("/term-structure/{symbol}")
async def get_term_structure(
    symbol: str,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get volatility term structure analysis."""
    return service.get_term_structure(symbol)


@router.get("/skew/{symbol}")
async def get_skew(
    symbol: str,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get options skew analysis."""
    return service.get_skew(symbol)


@router.get("/gamma/{symbol}")
async def get_gamma(
    symbol: str,
    current_price: float = 100.0,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get gamma exposure analysis."""
    return service.get_gamma(symbol, current_price)


@router.get("/liquidity/{symbol}")
async def get_liquidity(
    symbol: str,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get options liquidity analysis."""
    return service.get_liquidity(symbol)


@router.get("/suitability/{symbol}")
async def get_suitability(
    symbol: str,
    sector: Optional[str] = None,
    market_regime: Optional[str] = None,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get options suitability score."""
    return service.get_suitability(symbol, sector, market_regime)


@router.get("/report/{symbol}")
async def get_report(
    symbol: str,
    current_price: float = 100.0,
    market_regime: Optional[str] = None,
    sector_context: Optional[str] = None,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get complete options intelligence report."""
    return service.analyze(
        symbol=symbol,
        current_price=current_price,
        market_regime=market_regime,
        sector_context=sector_context,
    )


@router.post("/analyze")
async def analyze(
    request: AnalyzeRequest,
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Run options intelligence analysis."""
    return service.analyze(
        symbol=request.symbol,
        current_price=request.current_price,
        market_regime=request.market_regime,
        sector_context=request.sector_context,
    )


@router.get("/conditions")
async def get_global_conditions(
    service: OptionsIntelligenceService = Depends(get_options_intelligence_service),
):
    """Get global options market conditions."""
    return service.get_global_conditions()


# Legacy endpoints (backward compatibility)

@router.get("/strategies")
async def get_strategies():
    return {
        "strategies": [
            {"strategy_id": "strat-diagonal-001", "name": "Diagonal Spread", "category": "income"},
            {"strategy_id": "strat-butterfly-001", "name": "Iron Butterfly", "category": "income"},
            {"strategy_id": "strat-gamma-001", "name": "Gamma Scalp", "category": "volatility"},
        ]
    }


@router.get("/principles")
async def get_principles():
    return {
        "principles": [
            {"name": "SellThetaBuyIntrinsic", "author": "McMillan", "concept": "Time decay arbitrage"},
            {"name": "VolatilityArbitrage", "author": "Gatheral", "concept": "IV/HV spread capture"},
            {"name": "GammaThetaTradeoff", "author": "Taleb", "concept": "Dynamic hedging"},
        ]
    }


@router.get("/greeks/exposure")
async def get_greek_exposure():
    return {
        "net_delta": 0.35,
        "net_gamma": 0.08,
        "net_theta": 0.25,
        "net_vega": 0.15,
        "delta_direction": "long",
        "gamma_risk_level": "medium",
    }


@router.get("/thinkscript/studies")
async def get_thinkscript_studies():
    return {
        "studies": [
            {"name": "PSIE_Gamma_Acceleration", "type": "study"},
            {"name": "PSIE_Theta_Decay", "type": "study"},
            {"name": "PSIE_Volatility_Breakout", "type": "strategy"},
        ]
    }


@router.get("/health")
async def health_check():
    return {
        "status": "operational",
        "subsystem": "Options Intelligence",
        "components": {
            "knowledge_base": "operational",
            "thinkscript_engine": "operational",
            "signals": "operational",
            "backtesting": "operational",
            "agent_interface": "operational",
            "bb-fin-017": "operational",
        }
    }
