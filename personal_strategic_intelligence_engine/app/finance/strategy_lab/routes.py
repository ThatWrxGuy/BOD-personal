"""Strategy Lab API Routes - BB-FIN-020"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.finance.strategy_lab.strategy_lab_service import get_strategy_lab_service
from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    StrategyLabStatus,
    StrategyLeaderboard,
    StrategySimulationReport,
    BacktestResult,
)

router = APIRouter(prefix="/finance/strategy-lab", tags=["Strategy Lab"])


@router.get("/status", response_model=StrategyLabStatus)
async def get_status():
    """Get strategy lab status."""
    service = get_strategy_lab_service()
    return service.get_status()


@router.get("/strategies", response_model=List[StrategyDefinition])
async def list_strategies(
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    """List all registered strategies."""
    service = get_strategy_lab_service()
    registry = service.registry
    
    if category:
        from app.finance.strategy_lab.strategy_models import StrategyCategory
        try:
            cat = StrategyCategory(category)
            return registry.get_strategies_by_category(cat)
        except ValueError:
            pass
    
    if status:
        from app.finance.strategy_lab.strategy_models import StrategyStatus
        try:
            stat = StrategyStatus(status)
            return registry.get_strategies_by_status(stat)
        except ValueError:
            pass
    
    return registry.get_all_strategies()


@router.get("/rankings", response_model=StrategyLeaderboard)
async def get_rankings():
    """Get strategy leaderboard."""
    service = get_strategy_lab_service()
    return service.get_leaderboard()


@router.get("/report/{strategy_id}", response_model=StrategySimulationReport)
async def get_strategy_report(strategy_id: str):
    """Get analysis report for a strategy."""
    service = get_strategy_lab_service()
    
    # Check cache first
    cached = service.get_analysis_report(strategy_id)
    if cached:
        return cached
    
    # Run full analysis
    return service.analyze_strategy(strategy_id)


@router.post("/discover")
async def discover_strategies(
    from_alpha: bool = Query(False, description="Discover from alpha signals"),
):
    """Discover new strategies from market patterns."""
    service = get_strategy_lab_service()
    strategies = service.discover_strategies(from_alpha=from_alpha)
    return {
        "discovered": len(strategies),
        "strategies": [s.model_dump() for s in strategies],
    }


@router.post("/backtest/{strategy_id}", response_model=BacktestResult)
async def run_backtest(
    strategy_id: str,
    symbols: Optional[List[str]] = Query(None),
):
    """Run backtest for a strategy."""
    service = get_strategy_lab_service()
    
    try:
        return service.run_backtest(strategy_id, symbols)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/simulate/{strategy_id}", response_model=StrategySimulationReport)
async def run_full_simulation(
    strategy_id: str,
    symbols: Optional[List[str]] = Query(None),
):
    """Run full strategy analysis including backtest, Monte Carlo, and regime analysis."""
    service = get_strategy_lab_service()
    
    try:
        return service.analyze_strategy(strategy_id, symbols)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
