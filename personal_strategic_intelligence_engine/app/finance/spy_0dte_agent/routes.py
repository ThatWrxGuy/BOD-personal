"""API Routes for SPY 0DTE Intelligence Agent - BB-FIN-019."""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.finance.spy_0dte_agent.spy_0dte_agent_service import (
    get_spy_0dte_agent_service,
    SPY0DTEAgentService,
)

router = APIRouter(prefix="/finance/spy-0dte", tags=["spy-0dte"])


class AnalyzeRequest(BaseModel):
    """Request to analyze SPY 0DTE opportunities."""
    market_regime: Optional[str] = None
    options_environment: Optional[str] = None


@router.get("/status")
async def get_status():
    """Get SPY 0DTE agent status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "module": "BB-FIN-019",
        "capabilities": [
            "delta_velocity_detection",
            "gamma_level_analysis",
            "strike_selection",
            "intraday_flow_analysis",
            "opportunity_detection",
            "structure_analysis",
        ],
        "dependencies": [
            "BB-FIN-014 - Market Regime",
            "BB-FIN-015 - Sector Rotation",
            "BB-FIN-016 - Security Selection",
            "BB-FIN-017 - Options Environment",
            "BB-FIN-018 - Tactical Structure",
            "V39-002 - Options Chain Loader",
        ],
        "governance": "ADVISORY ONLY - Requires Risk Governor & CEO approval for execution",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/opportunities")
async def get_opportunities(
    service: SPY0DTEAgentService = Depends(get_spy_0dte_agent_service),
):
    """Get current SPY 0DTE opportunities."""
    return service.get_opportunities()


@router.get("/gamma-levels")
async def get_gamma_levels(
    service: SPY0DTEAgentService = Depends(get_spy_0dte_agent_service),
):
    """Get current gamma levels for SPY."""
    gamma = service.get_gamma_levels()
    return {
        "symbol": gamma.symbol,
        "gamma_support": gamma.gamma_support,
        "gamma_resistance": gamma.gamma_resistance,
        "gamma_flip": gamma.gamma_flip,
        "net_gamma": gamma.net_gamma,
        "zone": gamma.gamma_zone,
        "pin_level": gamma.pin_level,
        "pinning_probability": gamma.pinning_probability,
        "call_wall": gamma.call_wall,
        "put_wall": gamma.put_wall,
        "timestamp": gamma.timestamp.isoformat(),
    }


@router.get("/strike-recommendations")
async def get_strike_recommendations(
    direction: str = "call",
    service: SPY0DTEAgentService = Depends(get_spy_0dte_agent_service),
):
    """Get strike recommendations."""
    strikes = service.get_strike_recommendations(direction)
    
    return {
        "direction": direction,
        "recommendations": [
            {
                "strike": s.strike,
                "delta": s.delta,
                "gamma": s.gamma,
                "theta": s.theta,
                "open_interest": s.open_interest,
                "volume": s.volume,
                "spread": s.spread,
                "distance_pct": s.distance_from_spot_pct,
                "confidence": s.confidence.value,
                "reasoning": s.reasoning,
            }
            for s in strikes
        ],
    }


@router.get("/report")
async def get_report(
    market_regime: Optional[str] = None,
    options_environment: Optional[str] = None,
    service: SPY0DTEAgentService = Depends(get_spy_0dte_agent_service),
):
    """Get complete SPY 0DTE intelligence report."""
    report = service.analyze(market_regime, options_environment)
    
    return {
        "timestamp": report.timestamp.isoformat(),
        "symbol": report.symbol,
        "current_price": report.current_price,
        
        # Market context
        "market_regime": report.market_regime,
        "options_environment": report.options_environment,
        
        # Intraday
        "intraday_phase": report.intraday.phase.value,
        "iv": report.intraday.current_iv,
        "iv_percentile": report.intraday.iv_percentile,
        "range_pct": report.intraday.range_pct,
        "expansion_probability": report.intraday.expansion_probability,
        
        # Gamma
        "gamma_support": report.gamma_levels.gamma_support,
        "gamma_resistance": report.gamma_levels.gamma_resistance,
        "gamma_flip": report.gamma_levels.gamma_flip,
        "gamma_zone": report.gamma_levels.gamma_zone,
        
        # Delta signal
        "delta_signal": report.delta_signal.signal_type.value if report.delta_signal else None,
        "delta_confirmed": report.delta_signal.confirmed if report.delta_signal else None,
        
        # Opportunity
        "opportunity": {
            "direction": report.opportunity.direction.value,
            "confidence": report.opportunity.confidence.value,
            "strike": report.opportunity.recommended_strike,
            "risk_level": report.opportunity.risk_level.value,
            "entry_window": report.opportunity.entry_window,
            "reasoning": report.opportunity.reasoning,
            "warning": report.opportunity.warning,
        },
        
        # Assessment
        "suitable_for_0dte": report.suitable_for_0dte,
        "primary_risk": report.primary_risk,
        
        # Governance
        "governance_note": report.governance_note,
    }


@router.post("/analyze")
async def analyze(
    request: AnalyzeRequest,
    service: SPY0DTEAgentService = Depends(get_spy_0dte_agent_service),
):
    """Run SPY 0DTE analysis."""
    return service.analyze(
        market_regime=request.market_regime,
        options_environment=request.options_environment,
    )


@router.get("/structure")
async def get_structure(
    service: SPY0DTEAgentService = Depends(get_spy_0dte_agent_service),
):
    """Get intraday market structure for SPY 0DTE."""
    return service.get_intraday_structure()
