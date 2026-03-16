"""Market Intelligence API Routes - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
import logging

from app.finance.market_intelligence.market_intelligence_service import (
    MarketIntelligenceService,
    get_market_intelligence_service,
)
from app.finance.market_intelligence.market_intelligence_models import (
    MarketIntelligenceReport,
    RegimeState,
    RegimePolicy,
    RegimeScorecard,
    CrossAssetSnapshot,
    RegimeHistoryEntry,
    RegimeTransitionAlert,
    RegimeType,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance/market-intelligence", tags=["market-intelligence"])


@router.get("/status")
async def get_status():
    """Get market intelligence system status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "module": "BB-FIN-014",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/regime/current", response_model=RegimeState)
async def get_current_regime():
    """Get the current market regime."""
    service = get_market_intelligence_service()
    regime = service.get_current_regime()
    
    if not regime:
        # Run analysis if no regime cached
        report = service.analyze_market()
        return report.regime
    
    return regime


@router.post("/analyze", response_model=MarketIntelligenceReport)
async def analyze_market(
    equity_prices: Optional[Dict[str, float]] = None,
    sector_prices: Optional[Dict[str, float]] = None,
    bond_prices: Optional[Dict[str, float]] = None,
    commodity_prices: Optional[Dict[str, float]] = None,
    fx_prices: Optional[Dict[str, float]] = None,
    crypto_prices: Optional[Dict[str, float]] = None,
    vix_level: Optional[float] = None,
    yields: Optional[Dict[str, float]] = None,
    credit_spreads: Optional[Dict[str, float]] = None,
):
    """Run market intelligence analysis with provided data."""
    service = get_market_intelligence_service()
    
    try:
        report = service.analyze_market(
            equity_prices=equity_prices,
            sector_prices=sector_prices,
            bond_prices=bond_prices,
            commodity_prices=commodity_prices,
            fx_prices=fx_prices,
            crypto_prices=crypto_prices,
            vix_level=vix_level,
            yields=yields,
            credit_spreads=credit_spreads,
        )
        return report
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/latest", response_model=MarketIntelligenceReport)
async def get_latest_report():
    """Get the latest market intelligence report."""
    service = get_market_intelligence_service()
    
    # Run analysis to get latest
    report = service.analyze_market()
    return report


@router.get("/signals/scorecard", response_model=RegimeScorecard)
async def get_signal_scorecard():
    """Get the current signal scorecard."""
    service = get_market_intelligence_service()
    report = service.analyze_market()
    return report.scorecard


@router.get("/snapshot/cross-asset", response_model=CrossAssetSnapshot)
async def get_cross_asset_snapshot():
    """Get the current cross-asset snapshot."""
    service = get_market_intelligence_service()
    report = service.analyze_market()
    return report.cross_asset_snapshot


@router.get("/policy/current", response_model=RegimePolicy)
async def get_current_policy():
    """Get the current regime policy recommendations."""
    service = get_market_intelligence_service()
    report = service.analyze_market()
    return report.policy


@router.get("/regime/history", response_model=List[RegimeHistoryEntry])
async def get_regime_history(limit: int = Query(default=20, ge=1, le=100)):
    """Get regime history."""
    service = get_market_intelligence_service()
    return service.get_regime_history(limit=limit)


@router.get("/alerts/transitions", response_model=Optional[RegimeTransitionAlert])
async def get_transition_alerts():
    """Get any active regime transition alerts."""
    service = get_market_intelligence_service()
    report = service.analyze_market()
    return report.transition_alert


# Demo endpoint for quick testing
@router.post("/demo/analyze")
async def run_demo_analysis():
    """Run a demo analysis with sample data."""
    service = get_market_intelligence_service()
    
    # Demo data representing a risk-on environment
    demo_data = {
        "equity_prices": {"SPY": 478.50, "QQQ": 405.20, "IWM": 198.30, "DIA": 385.40},
        "sector_prices": {
            "XLF": 42.15, "XLK": 198.50, "XLE": 88.20, "XLV": 142.30,
            "XLI": 118.75, "XLP": 76.40, "XLY": 172.80, "XLU": 68.90,
        },
        "bond_prices": {"TLT": 92.30, "IEF": 97.50, "SHY": 81.20},
        "commodity_prices": {"GLD": 188.50, "USO": 72.30},
        "fx_prices": {"UUP": 25.80},
        "crypto_prices": {"BTC": 67500.0, "ETH": 3450.0},
        "vix_level": 14.5,
        "yields": {"2Y": 4.15, "10Y": 3.95, "30Y": 4.20},
    }
    
    report = service.analyze_market(**demo_data)
    
    return {
        "status": "success",
        "regime": report.regime.primary_regime.value,
        "confidence": report.regime.confidence.value,
        "risk_posture": report.regime.risk_posture.value,
        "policy": {
            "max_exposure": report.policy.max_gross_exposure,
            "cash_preference": report.policy.cash_preference,
            "aggression": report.policy.aggression_level,
        },
        "timestamp": report.timestamp.isoformat(),
    }
