"""Security Selection Routes - BB-FIN-016"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.finance.security_selection.security_selection_engine import (
    get_security_selection_engine,
    SecuritySelectionEngine,
)
from app.finance.security_selection.selection_models import (
    SecurityCategory,
    SelectionReport,
    RankedOpportunity,
)

router = APIRouter(prefix="/finance/security-selection", tags=["security-selection"])


def _get_symbols(engine: SecuritySelectionEngine) -> List[str]:
    """Get symbols from universe."""
    symbols = engine.universe_manager.get_combined_universe()
    if not symbols:
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "UNH", "XOM", "PG"]
    return symbols[:50]


def _generate_market_data(symbols: List[str]) -> dict:
    """Generate demo market data for security scoring."""
    import random
    
    market_data = {}
    for symbol in symbols:
        # Generate realistic demo data
        change_pct = random.uniform(-3.0, 5.0)
        volume = random.randint(500_000, 20_000_000)
        avg_volume = random.randint(500_000, 15_000_000)
        
        market_data[symbol] = {
            "price": random.uniform(50, 500),
            "change_percent": change_pct,
            "volume": volume,
            "avg_volume": avg_volume,
            "market_cap": random.randint(10_000_000_000, 3_000_000_000_000),
        }
    
    return market_data


# Endpoints

@router.get("/status", response_model=dict)
async def get_status(
    engine: SecuritySelectionEngine = Depends(get_security_selection_engine),
):
    """Get security selection system status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "module": "BB-FIN-016",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/rankings", response_model=dict)
async def get_rankings(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
):
    """Get ranked security opportunities."""
    engine = get_security_selection_engine()
    symbols = _get_symbols(engine)
    
    market_data = _generate_market_data(symbols)
    
    categories = [SecurityCategory(cat)] if category else None
    report = engine.run_selection(symbols, market_data, categories)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_candidates": len(report.ranked_opportunities),
        "rankings": [
            {
                "rank": i + 1,
                "symbol": opp.symbol,
                "symbol": opp.symbol,
                "score": opp.score,
                "conviction": opp.conviction.value if hasattr(opp.conviction, 'value') else str(opp.conviction),
                "category": opp.category.value if hasattr(opp.category, 'value') else str(opp.category),
            }
            for i, opp in enumerate(report.ranked_opportunities[:limit])
        ],
    }


@router.get("/watchlist", response_model=dict)
async def get_watchlist(
    bucket: Optional[str] = None,
):
    """Get categorized watchlists."""
    engine = get_security_selection_engine()
    symbols = _get_symbols(engine)
    
    market_data = _generate_market_data(symbols)
    report = engine.run_selection(symbols, market_data)
    
    # Build watchlist buckets
    watchlists = {
        "high_conviction": [],
        "tactical": [],
        "income": [],
        "watchlist": [],
    }
    
    for opp in report.ranked_opportunities:
        if hasattr(opp.conviction, 'value'):
            conv = opp.conviction.value
        else:
            conv = str(opp.conviction)
        
        if conv == "high":
            watchlists["high_conviction"].append({
                "symbol": opp.symbol,
                "symbol": opp.symbol,
                "score": opp.score,
            })
        elif hasattr(opp.category, 'value'):
            cat = opp.category.value
            if cat in watchlists:
                watchlists[cat].append({
                    "symbol": opp.symbol,
                    "symbol": opp.symbol,
                    "score": opp.score,
                })
    
    if bucket and bucket in watchlists:
        return {"bucket": bucket, "securities": watchlists[bucket]}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "watchlists": watchlists,
    }


@router.get("/candidates/top", response_model=dict)
async def get_top_candidates(
    limit: int = Query(10, ge=1, le=50),
):
    """Get top-ranked candidates."""
    engine = get_security_selection_engine()
    symbols = _get_symbols(engine)
    
    market_data = _generate_market_data(symbols)
    report = engine.run_selection(symbols, market_data)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "candidates": [
            {
                "symbol": opp.symbol,
                "symbol": opp.symbol,
                "score": opp.score,
                "conviction": opp.conviction.value if hasattr(opp.conviction, 'value') else str(opp.conviction),
                "reasoning": getattr(opp, 'reasoning', '')[:200],
            }
            for opp in report.ranked_opportunities[:limit]
        ],
    }


@router.get("/candidate/{symbol}", response_model=dict)
async def get_candidate(
    symbol: str,
):
    """Get detailed profile for a candidate."""
    engine = get_security_selection_engine()
    symbols = _get_symbols(engine)
    
    if symbol.upper() not in symbols:
        raise HTTPException(status_code=404, detail="Symbol not in universe")
    
    market_data = engine._generate_demo_data([symbol.upper()])
    report = engine.run_selection([symbol.upper()], market_data)
    
    if not report.ranked_opportunities:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    opp = report.ranked_opportunities[0]
    
    return {
        "symbol": opp.symbol,
        "symbol": opp.symbol,
        "score": opp.score,
        "conviction": opp.conviction.value if hasattr(opp.conviction, 'value') else str(opp.conviction),
        "category": opp.category.value if hasattr(opp.category, 'value') else str(opp.category),
        "reasoning": getattr(opp, 'reasoning', ''),
        "strengths": getattr(opp, 'strengths', []),
        "weaknesses": getattr(opp, 'weaknesses', []),
    }


@router.get("/report/latest", response_model=dict)
async def get_latest_report():
    """Get latest complete selection report."""
    engine = get_security_selection_engine()
    symbols = _get_symbols(engine)
    
    market_data = _generate_market_data(symbols)
    report = engine.run_selection(symbols, market_data)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_candidates": len(report.ranked_opportunities),
        "elite_count": sum(1 for o in report.ranked_opportunities if hasattr(o.conviction, 'value') and o.conviction.value == "high"),
        "top_10": [
            {
                "symbol": opp.symbol,
                "symbol": opp.symbol,
                "score": opp.score,
            }
            for opp in report.ranked_opportunities[:10]
        ],
    }


@router.post("/analyze", response_model=dict)
async def analyze(
    symbols: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
):
    """Run security selection analysis."""
    engine = get_security_selection_engine()
    
    if symbols:
        all_symbols = _get_symbols(engine)
        symbols = [s.upper() for s in symbols if s.upper() in all_symbols]
    else:
        symbols = _get_symbols(engine)
    
    cat_list = [SecurityCategory(c) for c in (categories or [])]
    
    market_data = _generate_market_data(symbols)
    report = engine.run_selection(symbols, market_data, cat_list if cat_list else None)
    
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "total_candidates": len(report.ranked_opportunities),
        "top_candidates": [
            {
                "symbol": opp.symbol,
                "symbol": opp.symbol,
                "score": opp.score,
            }
            for opp in report.ranked_opportunities[:10]
        ],
    }


@router.get("/classifications", response_model=dict)
async def get_classifications():
    """Get available security classifications."""
    return {
        "categories": [c.value for c in SecurityCategory],
        "conviction_levels": ["low", "moderate", "high", "exceptional"],
        "strategy_types": ["investment", "swing", "tactical", "intraday", "options"],
    }
