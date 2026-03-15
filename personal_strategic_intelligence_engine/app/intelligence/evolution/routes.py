"""API Routes for Intelligence Evolution Subsystem."""

from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/intelligence/evolution", tags=["intelligence-evolution"])


def generate_mock_patterns():
    """Generate mock pattern discoveries."""
    return {
        "patterns": [
            {
                "pattern_id": "pat-001",
                "pattern_type": "structural",
                "description": "VWAP reclaim followed by liquidity sweep often leads to continuation",
                "conditions": {"vwap_state": "acceptance_above", "liquidity_sweep": True},
                "frequency": 0.12,
                "win_rate": 72.5,
                "avg_return": 28.0,
                "statistical_significance": 0.82,
                "confidence": 0.78,
                "discovered_at": datetime.now().isoformat(),
            },
            {
                "pattern_id": "pat-002",
                "pattern_type": "momentum",
                "description": "Trend continues after healthy pullback to VWAP",
                "conditions": {"day_type": "trend_up", "pullback_to_vwap": True},
                "frequency": 0.18,
                "win_rate": 75.0,
                "avg_return": 32.0,
                "statistical_significance": 0.88,
                "confidence": 0.85,
                "discovered_at": datetime.now().isoformat(),
            },
            {
                "pattern_id": "pat-003",
                "pattern_type": "reversal",
                "description": "Overextended price + shallow pullback often leads to reversal",
                "conditions": {"overextension": True, "pullback_depth": "shallow"},
                "frequency": 0.15,
                "win_rate": 65.0,
                "avg_return": 22.0,
                "statistical_significance": 0.80,
                "confidence": 0.75,
                "discovered_at": datetime.now().isoformat(),
            },
        ],
        "count": 3,
    }


def generate_mock_features():
    """Generate mock feature importance."""
    return {
        "features": [
            {"feature_name": "delta_velocity", "importance_score": 0.85, "category": "options_chain", "correlation": 0.65},
            {"feature_name": "structure_quality", "importance_score": 0.78, "category": "market_structure", "correlation": 0.58},
            {"feature_name": "momentum_strength", "importance_score": 0.72, "category": "execution_timing", "correlation": 0.52},
            {"feature_name": "vwap_distance", "importance_score": 0.68, "category": "market_structure", "correlation": 0.48},
            {"feature_name": "timing_confidence", "importance_score": 0.65, "category": "execution_timing", "correlation": 0.45},
            {"feature_name": "volatility_trend", "importance_score": 0.55, "category": "volatility", "correlation": 0.38},
            {"feature_name": "liquidity_score", "importance_score": 0.48, "category": "liquidity", "correlation": 0.32},
            {"feature_name": "spread_quality", "importance_score": 0.42, "category": "liquidity", "correlation": 0.28},
        ],
        "count": 8,
    }


def generate_mock_calibration():
    """Generate mock calibration report."""
    return {
        "timestamp": datetime.now().isoformat(),
        "calibrated_model": "signal_scoring",
        "calibration_error": 8.5,
        "confidence_accuracy": 91.5,
        "score_reliability": 0.82,
        "recommended_adjustments": {
            "high_score_threshold": -8,
            "mid_score_baseline": 3,
        },
    }


def generate_mock_regimes():
    """Generate mock regime analysis."""
    return {
        "regimes": [
            {
                "regime_type": "trend_up",
                "characteristics": {"description": "Strong upward price movement", "typical_duration": "hours to days"},
                "tactical_performance": {
                    "expectancy": 22.5,
                    "sharpe_ratio": 1.8,
                    "win_rate": 68.0,
                    "total_trades": 85,
                },
                "recommended_modifiers": {"position_size": 1.2, "stop_width": 1.0, "target_multiplier": 2.0},
                "confidence_adjustment": 8,
            },
            {
                "regime_type": "trend_down",
                "characteristics": {"description": "Strong downward price movement", "typical_duration": "hours to days"},
                "tactical_performance": {
                    "expectancy": 18.2,
                    "sharpe_ratio": 1.5,
                    "win_rate": 62.0,
                    "total_trades": 72,
                },
                "recommended_modifiers": {"position_size": 1.2, "stop_width": 1.0, "target_multiplier": 2.0},
                "confidence_adjustment": 8,
            },
            {
                "regime_type": "range_chop",
                "characteristics": {"description": "Sideways price action", "typical_duration": "hours"},
                "tactical_performance": {
                    "expectancy": 5.2,
                    "sharpe_ratio": 0.6,
                    "win_rate": 48.0,
                    "total_trades": 45,
                },
                "recommended_modifiers": {"position_size": 0.7, "stop_width": 1.5, "target_multiplier": 1.5},
                "confidence_adjustment": -10,
            },
        ],
    }


def generate_mock_optimizations():
    """Generate mock optimization proposals."""
    return {
        "proposals": [
            {
                "proposal_id": "opt-001",
                "optimization_type": "score_threshold",
                "target_parameter": "signal_score_min",
                "current_value": 50,
                "proposed_value": 55,
                "expected_improvement": 8.5,
                "confidence": 0.72,
                "required_approval": "finance",
                "rationale": "Analysis shows signals above 55 have 15% higher win rate",
                "created_at": datetime.now().isoformat(),
                "status": "pending",
            },
            {
                "proposal_id": "opt-002",
                "optimization_type": "timing_criteria",
                "target_parameter": "min_momentum_for_entry",
                "current_value": 0.5,
                "proposed_value": 0.7,
                "expected_improvement": 12.0,
                "confidence": 0.78,
                "required_approval": "ceo",
                "rationale": "Stronger momentum correlates with higher win rate",
                "created_at": datetime.now().isoformat(),
                "status": "pending",
            },
        ],
        "count": 2,
    }


@router.get("/patterns")
async def get_patterns():
    """Get discovered patterns."""
    return generate_mock_patterns()


@router.get("/features")
async def get_feature_importance():
    """Get feature importance rankings."""
    return generate_mock_features()


@router.get("/calibration")
async def get_calibration():
    """Get calibration reports."""
    return generate_mock_calibration()


@router.get("/regimes")
async def get_regime_analysis():
    """Get regime analysis."""
    return generate_mock_regimes()


@router.get("/optimizations")
async def get_optimizations(status: Optional[str] = Query(None)):
    """Get optimization proposals."""
    proposals = generate_mock_optimizations()
    if status:
        proposals["proposals"] = [p for p in proposals["proposals"] if p["status"] == status]
        proposals["count"] = len(proposals["proposals"])
    return proposals


@router.get("/snapshot")
async def get_evolution_snapshot():
    """Get complete evolution snapshot."""
    return {
        "timestamp": datetime.now().isoformat(),
        "patterns": generate_mock_patterns()["patterns"],
        "features": generate_mock_features()["features"],
        "calibration": generate_mock_calibration(),
        "regimes": generate_mock_regimes()["regimes"],
        "optimizations": generate_mock_optimizations()["proposals"],
        "learning_summary": {
            "total_patterns_discovered": 3,
            "top_features": 5,
            "calibration_accuracy": 91.5,
            "pending_optimizations": 2,
        },
    }


@router.get("/health")
async def evolution_health_check():
    """Health check for evolution subsystem."""
    return {
        "status": "operational",
        "subsystem": "Intelligence Evolution",
        "components": {
            "quantitative_analysis": "operational",
            "pattern_discovery": "operational",
            "feature_learning": "operational",
            "strategy_optimizer": "operational",
            "regime_adaptation": "operational",
            "model_calibration": "operational",
            "confidence_evolution": "operational",
            "learning_scheduler": "operational",
            "evolution_logger": "operational",
        },
    }
