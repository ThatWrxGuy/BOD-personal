"""API Routes for Strategy Simulation Subsystem."""

from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/strategy", tags=["strategy-simulation"])


def generate_mock_simulations():
    """Generate mock simulation results."""
    return {
        "simulations": [
            {
                "simulation_id": "sim-strat-baseline-001",
                "strategy_id": "strat-baseline-001",
                "strategy_name": "Baseline 0DTE Strategy",
                "status": "completed",
                "metrics": {
                    "total_trades": 65,
                    "win_rate": 58.5,
                    "expectancy": 0.42,
                    "sharpe_ratio": 1.2,
                    "sortino_ratio": 1.5,
                    "max_drawdown": 25.0,
                },
            },
            {
                "simulation_id": "sim-strat-var-001",
                "strategy_id": "strat-var-001",
                "strategy_name": "High Signal Threshold",
                "status": "completed",
                "metrics": {
                    "total_trades": 42,
                    "win_rate": 65.2,
                    "expectancy": 0.68,
                    "sharpe_ratio": 1.8,
                    "sortino_ratio": 2.2,
                    "max_drawdown": 18.5,
                },
            },
        ],
    }


def generate_mock_comparisons():
    """Generate mock comparisons."""
    return {
        "comparisons": [
            {
                "comparison_id": "comp-001",
                "baseline_strategy": "strat-baseline-001",
                "candidate_strategy": "strat-var-001",
                "expectancy_improvement": 0.26,
                "sharpe_improvement": 0.6,
                "drawdown_improvement": 6.5,
                "winner": "candidate",
                "recommendation": "Candidate outperforms baseline. Recommend adoption.",
            },
        ],
    }


def generate_mock_discoveries():
    """Generate mock discoveries."""
    return {
        "discoveries": [
            {
                "discovery_id": "disc-001",
                "pattern_name": "Trend + VWAP Acceptance",
                "description": "Strong performance when trend aligns with VWAP acceptance",
                "win_rate": 72.5,
                "expectancy": 1.25,
                "confidence": 0.78,
            },
            {
                "discovery_id": "disc-002",
                "pattern_name": "Higher Signal Threshold",
                "description": "Signals above 60 score have higher win rate",
                "win_rate": 68.0,
                "expectancy": 0.95,
                "confidence": 0.72,
            },
        ],
    }


def generate_mock_proposals():
    """Generate mock optimization proposals."""
    return {
        "proposals": [
            {
                "proposal_id": "prop-001",
                "strategy_id": "strat-baseline-001",
                "optimization_type": "threshold_adjustment",
                "target_parameter": "min_signal_score",
                "current_value": 50,
                "proposed_value": 55,
                "expected_improvement": 12.5,
                "confidence": 0.75,
                "rationale": "Higher threshold reduces false positives",
                "status": "pending",
            },
            {
                "proposal_id": "prop-002",
                "strategy_id": "strat-baseline-001",
                "optimization_type": "timing_rule",
                "target_parameter": "require_momentum_confirmation",
                "current_value": True,
                "proposed_value": True,
                "expected_improvement": 8.0,
                "confidence": 0.68,
                "rationale": "Maintaining momentum filter improves quality",
                "status": "pending",
            },
        ],
    }


@router.get("/simulations")
async def get_simulations(limit: int = Query(10, ge=1, le=50)):
    """Get simulation results."""
    return generate_mock_simulations()


@router.get("/results")
async def get_results(simulation_id: Optional[str] = None):
    """Get detailed simulation results."""
    return {
        "simulation_id": simulation_id,
        "metrics": generate_mock_simulations()["simulations"][0]["metrics"],
        "regime_breakdown": [
            {"regime": "trend_up", "win_rate": 68.5, "expectancy": 0.65},
            {"regime": "trend_down", "win_rate": 62.0, "expectancy": 0.52},
            {"regime": "range_chop", "win_rate": 45.0, "expectancy": 0.18},
        ],
    }


@router.get("/comparisons")
async def get_comparisons():
    """Get strategy comparisons."""
    return generate_mock_comparisons()


@router.get("/discoveries")
async def get_discoveries():
    """Get strategy discoveries."""
    return generate_mock_discoveries()


@router.get("/proposals")
async def get_proposals(status: Optional[str] = Query(None)):
    """Get optimization proposals."""
    proposals = generate_mock_proposals()
    if status:
        proposals["proposals"] = [p for p in proposals["proposals"] if p["status"] == status]
    return proposals


@router.get("/snapshot")
async def get_simulation_snapshot():
    """Get complete simulation snapshot."""
    return {
        "timestamp": datetime.now().isoformat(),
        "simulations": generate_mock_simulations()["simulations"],
        "comparisons": generate_mock_comparisons()["comparisons"],
        "discoveries": generate_mock_discoveries()["discoveries"],
        "proposals": generate_mock_proposals()["proposals"],
        "summary": {
            "total_simulations": 15,
            "winning_candidates": 3,
            "pending_proposals": 2,
        },
    }


@router.get("/health")
async def simulation_health_check():
    """Health check for simulation subsystem."""
    return {
        "status": "operational",
        "subsystem": "Strategy Simulation",
        "components": {
            "strategy_generator": "operational",
            "historical_replay": "operational",
            "monte_carlo": "operational",
            "strategy_evaluator": "operational",
            "strategy_comparator": "operational",
            "strategy_discovery": "operational",
            "simulation_scheduler": "operational",
            "simulation_logger": "operational",
        },
    }
