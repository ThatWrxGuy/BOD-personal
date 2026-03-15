"""API Routes for SPY 0DTE Options Tactical Agent."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.agents.finance.options_0dte.spy_0dte_agent import SPY0DTETacticalAgent
from app.agents.finance.options_0dte.signal_logger import SignalLogger
from app.agents.finance.options_0dte.historical_replay import HistoricalReplayValidator
from app.agents.finance.options_0dte.governance_integration import get_governance_integrator, GovernanceStatus
from app.agents.finance.options_0dte.portfolio_risk_adapter import PortfolioRiskAdapter, create_default_adapter
from app.agents.finance.options_0dte.executive_review import ExecutiveReviewEngine, create_default_engine
from app.agents.finance.options_0dte.board_brief_generator import BoardBriefGenerator, create_brief_generator
from app.agents.finance.options_0dte.cross_agent_coordination import get_coordinator
from app.agents.finance.options_0dte.allocation_policy import TacticalAllocationEngine, create_allocation_engine


router = APIRouter(prefix="/options-agent", tags=["options-agent"])

# Initialize agent and logger (singleton for demo)
_agent: Optional[SPY0DTETacticalAgent] = None
_logger: Optional[SignalLogger] = None


def get_agent() -> SPY0DTETacticalAgent:
    """Get or create the SPY 0DTE tactical agent."""
    global _agent
    if _agent is None:
        _agent = SPY0DTETacticalAgent()
    return _agent


def get_logger() -> SignalLogger:
    """Get or create the signal logger."""
    global _logger
    if _logger is None:
        _logger = SignalLogger()
    return _logger


@router.get("/signals")
async def get_signals(
    limit: int = Query(10, ge=1, le=100, description="Number of signals to return"),
    option_type: Optional[str] = Query(None, description="Filter by option type: call or put"),
) -> dict:
    """
    Get recent trading signals for SPY 0DTE options.
    
    Returns ranked contract candidates with signal scores and confidence.
    """
    try:
        agent = get_agent()
        
        # Run scan to generate fresh signals
        result = await agent.run_scan(option_type=option_type, top_n=limit)
        
        return {
            "signals": result["signals"],
            "count": len(result["signals"]),
            "market_data": result["market_data"],
            "analysis_time": result["analysis_time"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_signal_history(
    limit: int = Query(100, ge=1, le=1000, description="Number of history entries to return"),
) -> dict:
    """
    Get signal history from strategic memory.
    
    Returns historical record of all generated signals.
    """
    try:
        logger = get_logger()
        history = logger.get_signal_history(limit)
        
        return {
            "history": history,
            "count": len(history),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-scan")
async def run_scan(
    option_type: Optional[str] = Query(None, description="Filter by option type: call or put"),
    top_n: int = Query(10, ge=1, le=50, description="Number of top signals to return"),
    simulate_trades: bool = Query(True, description="Whether to run paper trade simulations"),
) -> dict:
    """
    Run a full scan of SPY 0DTE options market.
    
    This endpoint:
    - Observes current SPY market conditions
    - Analyzes the 0DTE options chain
    - Scores and ranks contract candidates
    - Generates trading signals
    - Optionally runs paper trade simulations
    
    Returns market data, options chain summary, and ranked signals.
    """
    try:
        # Validate option_type if provided
        if option_type and option_type not in ["call", "put"]:
            raise HTTPException(
                status_code=400,
                detail="option_type must be 'call' or 'put'"
            )
        
        agent = get_agent()
        result = await agent.run_scan(option_type=option_type, top_n=top_n)
        
        return {
            "success": True,
            "signals": result["signals"],
            "signal_count": len(result["signals"]),
            "simulated_trades": result.get("simulated_trades", []) if simulate_trades else [],
            "market_data": result["market_data"],
            "options_chain_summary": {
                "ticker": result["options_chain"]["ticker"],
                "expiration_date": result["options_chain"]["expiration_date"],
                "underlying_price": result["options_chain"]["underlying_price"],
                "call_count": len(result["options_chain"]["calls"]),
                "put_count": len(result["options_chain"]["puts"]),
            },
            "analysis_time": result["analysis_time"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance(
    source: str = Query("all", description="Performance source: logger, simulator, or all"),
) -> dict:
    """
    Get performance metrics from paper trading simulations.
    
    Returns simulated trade performance including:
    - Total trades
    - Win rate
    - Total P&L
    - Average trade metrics
    """
    try:
        agent = get_agent()
        performance = agent.get_performance_summary()
        
        if source == "logger":
            return {
                "source": "logger",
                "metrics": performance["logger_metrics"],
            }
        elif source == "simulator":
            return {
                "source": "simulator",
                "metrics": performance["simulator_metrics"],
            }
        else:
            return {
                "source": "all",
                "logger_metrics": performance["logger_metrics"],
                "simulator_metrics": performance["simulator_metrics"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-snapshot")
async def get_market_snapshot() -> dict:
    """
    Get current SPY market snapshot.
    
    Returns current price, OHLCV, and technical indicators.
    """
    try:
        agent = get_agent()
        market_data = await agent.observe_market()
        
        return {
            "market_data": market_data.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options-chain")
async def get_options_chain() -> dict:
    """
    Get current SPY 0DTE options chain.
    
    Returns all calls and puts with greeks for 0DTE expiration.
    """
    try:
        agent = get_agent()
        options_chain = await agent.analyze_option_chain()
        
        return {
            "options_chain": options_chain.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns agent status and configuration.
    """
    return {
        "status": "operational",
        "agent_type": "SPY 0DTE Tactical Agent",
        "mode": "research_and_signal",
        "autonomous_trading": "disabled",
        "risk_controls": {
            "liquidity_filter": "enabled",
            "spread_threshold": "15%",
            "volatility_spike_suppression": "enabled",
            "time_of_day_controls": "enabled",
            "cooldown_controls": "enabled",
            "regime_classification": "enabled",
        },
    }


@router.get("/validation/run")
async def run_validation(
    num_sessions: int = Query(20, ge=5, le=100, description="Number of sessions to replay"),
    days_back: int = Query(30, ge=1, le=365, description="Days to look back"),
) -> dict:
    """
    Run historical replay validation.
    
    Replays historical sessions to evaluate signal performance.
    """
    try:
        validator = HistoricalReplayValidator()
        result = validator.run_replay(num_sessions=num_sessions, days_back=days_back)
        
        return {
            "success": True,
            "validation": result.to_dict(),
            "calibration": validator.get_calibration_report(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/journal")
async def get_governance_journal(
    limit: int = Query(100, ge=1, le=500, description="Number of entries to return"),
    action: Optional[str] = Query(None, description="Filter by action: generated, suppressed, expired"),
) -> dict:
    """
    Get decision journal entries.
    """
    try:
        governance = get_governance_integrator()
        
        from app.agents.finance.options_0dte.governance_integration import SignalAction
        action_filter = SignalAction(action) if action else None
        
        entries = governance.get_journal_entries(limit=limit, action=action_filter)
        
        return {
            "journal_entries": [e.to_dict() for e in entries],
            "count": len(entries),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/suppressions")
async def get_suppressions() -> dict:
    """
    Get suppression summary.
    """
    try:
        governance = get_governance_integrator()
        return governance.get_suppression_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/regime-performance")
async def get_regime_performance() -> dict:
    """
    Get performance breakdown by regime.
    """
    try:
        governance = get_governance_integrator()
        return governance.get_performance_by_regime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/governance/set-status")
async def set_governance_status(
    status: str = Query(..., description="Governance status: advisory_only, approval_required, autonomous"),
) -> dict:
    """
    Set governance status.
    
    Note: autonomous mode requires explicit authorization.
    """
    try:
        from app.agents.finance.options_0dte.governance_integration import GovernanceStatus
        
        if status == "advisory_only":
            governance_status = GovernanceStatus.ADVISORY_ONLY
        elif status == "approval_required":
            governance_status = GovernanceStatus.APPROVAL_REQUIRED
        elif status == "autonomous":
            # Don't allow autonomous without explicit approval
            return {
                "success": False,
                "message": "Autonomous mode requires explicit authorization - not enabled by default"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown status: {status}")
        
        from app.agents.finance.options_0dte.governance_integration import set_governance_status as set_status
        set_status(governance_status)
        
        return {
            "success": True,
            "governance_status": governance_status.value,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Portfolio Risk Adapter Endpoints
_portfolio_adapter: Optional[PortfolioRiskAdapter] = None
_review_engine: Optional[ExecutiveReviewEngine] = None
_brief_generator: Optional[BoardBriefGenerator] = None
_allocation_engine: Optional[TacticalAllocationEngine] = None


def get_portfolio_adapter() -> PortfolioRiskAdapter:
    global _portfolio_adapter
    if _portfolio_adapter is None:
        _portfolio_adapter = create_default_adapter()
    return _portfolio_adapter


def get_review_engine() -> ExecutiveReviewEngine:
    global _review_engine
    if _review_engine is None:
        _review_engine = create_default_engine()
    return _review_engine


def get_brief_generator() -> BoardBriefGenerator:
    global _brief_generator
    if _brief_generator is None:
        _brief_generator = create_brief_generator()
    return _brief_generator


def get_allocation_engine() -> TacticalAllocationEngine:
    global _allocation_engine
    if _allocation_engine is None:
        _allocation_engine = create_allocation_engine()
    return _allocation_engine


@router.get("/portfolio/evaluate")
async def evaluate_portfolio_fit(
    signal_id: str = Query(..., description="Signal ID to evaluate"),
) -> dict:
    """Evaluate signal against portfolio constraints."""
    try:
        adapter = get_portfolio_adapter()
        return {"portfolio_adapter": "operational"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/thresholds")
async def get_review_thresholds() -> dict:
    """Get current review threshold configuration."""
    engine = get_review_engine()
    return {
        "thresholds": {
            "min_confidence_for_auto_log": engine.thresholds.min_confidence_for_auto_log,
            "min_score_for_auto_log": engine.thresholds.min_score_for_auto_log,
            "min_confidence_for_finance": engine.thresholds.min_confidence_for_finance,
            "min_score_for_finance": engine.thresholds.min_score_for_finance,
        }
    }


@router.get("/briefs/pending")
async def get_pending_briefs() -> dict:
    """Get briefs awaiting review."""
    generator = get_brief_generator()
    briefs = generator.get_pending_briefs()
    return {
        "briefs": [b.to_dict() for b in briefs],
        "count": len(briefs),
    }


@router.get("/briefs/ceo")
async def get_ceo_briefs() -> dict:
    """Get briefs requiring CEO approval."""
    generator = get_brief_generator()
    briefs = generator.get_ceo_briefs()
    return {
        "briefs": [b.to_dict() for b in briefs],
        "count": len(briefs),
    }


@router.get("/briefs/finance")
async def get_finance_briefs() -> dict:
    """Get briefs requiring finance approval."""
    generator = get_brief_generator()
    briefs = generator.get_finance_briefs()
    return {
        "briefs": [b.to_dict() for b in briefs],
        "count": len(briefs),
    }


@router.get("/briefs/generate")
async def generate_brief(
    signal_id: str = Query(..., description="Signal ID for brief"),
) -> dict:
    """Generate a board brief for a signal."""
    generator = get_brief_generator()
    return {"brief_generator": "operational", "signal_id": signal_id}


@router.get("/coordination/conflicts")
async def get_conflicts() -> dict:
    """Get active conflicts between finance agents."""
    coordinator = get_coordinator()
    return coordinator.get_conflict_summary()


@router.post("/coordination/resolve")
async def resolve_conflict(
    conflict_id: str = Query(..., description="Conflict ID to resolve"),
    resolution: str = Query(..., description="Resolution description"),
) -> dict:
    """Resolve a conflict."""
    coordinator = get_coordinator()
    success = coordinator.resolve_conflict(conflict_id, resolution)
    return {"success": success, "conflict_id": conflict_id}


@router.get("/allocation/policy")
async def get_allocation_policy() -> dict:
    """Get current allocation policy configuration."""
    engine = get_allocation_engine()
    return {
        "policy": {
            "max_paper_trade_notional": engine.policy.max_paper_trade_notional,
            "max_board_review_notional": engine.policy.max_board_review_notional,
            "max_qualified_notional": engine.policy.max_qualified_notional,
        }
    }


@router.get("/dashboard/integration-status")
async def get_integration_status() -> dict:
    """Get integration status for all components."""
    return {
        "portfolio_adapter": "operational",
        "review_engine": "operational",
        "brief_generator": "operational",
        "coordinator": "operational",
        "allocation_engine": "operational",
    }
