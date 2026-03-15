"""API Routes for Tactical Learning Subsystem."""

from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter(prefix="/options-agent/learning", tags=["tactical-learning"])


# Mock data generators
def generate_mock_outcomes():
    """Generate mock signal outcomes."""
    import random
    outcomes = []
    for i in range(20):
        outcomes.append({
            "signal_id": f"sig-{i:03d}",
            "timestamp": datetime.now().isoformat(),
            "ticker": "SPY",
            "strike": 500 + random.randint(-10, 10),
            "option_type": random.choice(["call", "put"]),
            "direction": random.choice(["bullish", "bearish"]),
            "signal_score": random.randint(40, 85),
            "confidence_score": random.randint(45, 80),
            "regime": random.choice(["trend_up", "trend_down", "range_chop"]),
            "vwap_state": random.choice(["acceptance_above", "acceptance_below"]),
            "day_type": random.choice(["trend_up", "trend_down", "range_day"]),
            "timing_decision": random.choice(["enter_now", "wait_for_pullback", "wait_for_confirmation"]),
            "profit_loss": random.uniform(-50, 100) if random.random() > 0.3 else None,
            "outcome": random.choice(["win", "loss", "breakeven"]) if random.random() > 0.2 else "pending",
            "paper_trade": True,
            "suppressed": random.random() < 0.2,
            "suppression_reason": random.choice(["low_liquidity", "overextension_risk", None]),
        })
    return outcomes


def generate_mock_calibration():
    """Generate mock calibration report."""
    return {
        "timestamp": datetime.now().isoformat(),
        "buckets": [
            {"bucket": "very_low", "min_confidence": 0, "max_confidence": 30, "signal_count": 15, "win_rate": 55.0, "predicted_vs_actual": 25.0},
            {"bucket": "low", "min_confidence": 30, "max_confidence": 50, "signal_count": 25, "win_rate": 52.0, "predicted_vs_actual": 2.0},
            {"bucket": "medium", "min_confidence": 50, "max_confidence": 70, "signal_count": 40, "win_rate": 58.0, "predicted_vs_actual": -2.0},
            {"bucket": "high", "min_confidence": 70, "max_confidence": 85, "signal_count": 30, "win_rate": 65.0, "predicted_vs_actual": -10.0},
            {"bucket": "very_high", "min_confidence": 85, "max_confidence": 100, "signal_count": 12, "win_rate": 72.0, "predicted_vs_actual": -18.0},
        ],
        "overall_calibration_error": 14.25,
        "is_overconfident": True,
        "is_underconfident": False,
        "recommended_adjustments": {
            "high": -10.0,
            "very_high": -15.0,
        },
    }


def generate_mock_features():
    """Generate mock feature importance."""
    return {
        "timestamp": datetime.now().isoformat(),
        "top_positive_predictors": [
            {"feature_name": "delta_velocity", "predictive_power": 0.42},
            {"feature_name": "structure_quality", "predictive_power": 0.38},
            {"feature_name": "momentum_state", "predictive_power": 0.35},
            {"feature_name": "vwap_state", "predictive_power": 0.30},
            {"feature_name": "timing_confidence", "predictive_power": 0.28},
        ],
        "top_negative_predictors": [
            {"feature_name": "volatility_spike", "predictive_power": -0.22},
            {"feature_name": "overextension_level", "predictive_power": -0.18},
        ],
        "low_value_features": ["option_volume_ratio", "bid_ask_spread"],
        "false_positive_features": ["iv_rank"],
        "strong_expectancy_features": ["delta_velocity", "structure_quality"],
    }


def generate_mock_suppressions():
    """Generate mock suppression effectiveness."""
    return {
        "timestamp": datetime.now().isoformat(),
        "suppressions": [
            {"category": "low_liquidity", "suppression_count": 45, "protective_rate": 72.0, "false_suppression_rate": 18.0, "net_effect": 54.0},
            {"category": "overextension_risk", "suppression_count": 38, "protective_rate": 65.0, "false_suppression_rate": 28.0, "net_effect": 37.0},
            {"category": "structure_misalignment", "suppression_count": 22, "protective_rate": 58.0, "false_suppression_rate": 22.0, "net_effect": 36.0},
            {"category": "timing_failure", "suppression_count": 18, "protective_rate": 45.0, "false_suppression_rate": 35.0, "net_effect": 10.0},
            {"category": "regime_conflict", "suppression_count": 12, "protective_rate": 38.0, "false_suppression_rate": 42.0, "net_effect": -4.0},
        ],
        "total_suppressions": 135,
        "protective_suppressions": ["low_liquidity", "overextension_risk", "structure_misalignment"],
        "harmful_suppressions": [],
        "neutral_suppressions": ["timing_failure"],
        "over_restricted_categories": ["regime_conflict"],
        "adjustment_recommendations": {
            "low_liquidity": "Effective - maintain current threshold",
            "regime_conflict": "Review threshold - false suppression rate is high (42%)",
        },
    }


def generate_mock_regimes():
    """Generate mock regime performance."""
    return {
        "timestamp": datetime.now().isoformat(),
        "day_type_performance": [
            {"regime": "trend_up", "signal_count": 85, "win_rate": 68.0, "avg_profit_loss": 28.50, "expectancy": 19.38, "best_for_direction": "bullish"},
            {"regime": "trend_down", "signal_count": 72, "win_rate": 62.0, "avg_profit_loss": 22.00, "expectancy": 13.64, "best_for_direction": "bearish"},
            {"regime": "range_chop", "signal_count": 45, "win_rate": 48.0, "avg_profit_loss": 8.00, "expectancy": 3.84, "best_for_direction": None},
        ],
        "vwap_state_performance": [
            {"regime": "acceptance_above", "signal_count": 65, "win_rate": 70.0, "avg_profit_loss": 32.00, "expectancy": 22.40},
            {"regime": "acceptance_below", "signal_count": 58, "win_rate": 64.0, "avg_profit_loss": 25.00, "expectancy": 16.00},
            {"regime": "rejection_above", "signal_count": 22, "win_rate": 45.0, "avg_profit_loss": 12.00, "expectancy": 5.40},
        ],
        "best_regimes_for_calls": ["trend_up", "acceptance_above"],
        "best_regimes_for_puts": ["trend_down", "acceptance_below"],
        "worst_environments": ["range_chop", "rejection_above"],
        "regime_confidence_modifiers": {
            "trend_up": 10.0,
            "trend_down": 8.0,
            "range_chop": -10.0,
            "rejection_above": -8.0,
        },
    }


def generate_mock_timing():
    """Generate mock timing performance."""
    return {
        "timestamp": datetime.now().isoformat(),
        "timing_decisions": [
            {"timing_decision": "enter_now", "signal_count": 45, "win_rate": 58.0, "avg_profit_loss": 22.0, "expectancy": 12.76},
            {"timing_decision": "wait_for_pullback", "signal_count": 38, "win_rate": 68.0, "avg_profit_loss": 28.0, "expectancy": 19.04},
            {"timing_decision": "wait_for_confirmation", "signal_count": 25, "win_rate": 72.0, "avg_profit_loss": 35.0, "expectancy": 25.20},
            {"timing_decision": "avoid_entry", "signal_count": 15, "win_rate": 40.0, "avg_profit_loss": -15.0, "expectancy": -9.00},
        ],
        "timing_recommendations": {
            "best_timing": "wait_for_confirmation has highest expectancy: 25.20",
            "pullback_vs_immediate": "Waiting for pullback outperforms immediate entry by 6.28",
        },
    }


def generate_mock_proposals():
    """Generate mock optimization proposals."""
    return [
        {
            "proposal_id": "prop-001",
            "timestamp": datetime.now().isoformat(),
            "proposal_type": "feature_weight_boost",
            "target_feature": "delta_velocity",
            "current_weight": 1.0,
            "proposed_weight": 1.15,
            "expected_improvement": 8.4,
            "confidence": 0.75,
            "rationale": "Feature delta_velocity shows strong predictive power (0.42)",
            "requires_approval": True,
            "status": "pending",
        },
        {
            "proposal_id": "prop-002",
            "timestamp": datetime.now().isoformat(),
            "proposal_type": "confidence_calibration",
            "target_feature": "confidence_bucket_high",
            "current_weight": None,
            "proposed_weight": -10.0,
            "expected_improvement": 5.0,
            "confidence": 0.7,
            "rationale": "Confidence bucket high shows 10% over-confidence",
            "requires_approval": True,
            "status": "pending",
        },
        {
            "proposal_id": "prop-003",
            "timestamp": datetime.now().isoformat(),
            "proposal_type": "regime_confidence_modifier",
            "target_feature": "regime_range_chop",
            "current_weight": 0.0,
            "proposed_weight": -10.0,
            "expected_improvement": 3.0,
            "confidence": 0.7,
            "rationale": "Regime range_chop shows weak performance",
            "requires_approval": True,
            "status": "pending",
        },
    ]


@router.get("/outcomes")
async def get_signal_outcomes(limit: int = Query(20, ge=1, le=100)):
    """Get historical signal outcomes."""
    return {
        "outcomes": generate_mock_outcomes()[:limit],
        "count": limit,
    }


@router.get("/features")
async def get_feature_importance():
    """Get feature importance analysis."""
    return generate_mock_features()


@router.get("/calibration")
async def get_confidence_calibration():
    """Get confidence calibration report."""
    return generate_mock_calibration()


@router.get("/suppressions")
async def get_suppression_effectiveness():
    """Get suppression effectiveness analysis."""
    return generate_mock_suppressions()


@router.get("/regimes")
async def get_regime_performance():
    """Get regime performance analysis."""
    return generate_mock_regimes()


@router.get("/timing")
async def get_timing_performance():
    """Get timing decision performance analysis."""
    return generate_mock_timing()


@router.get("/proposals")
async def get_optimization_proposals(status: Optional[str] = Query(None)):
    """Get score optimization proposals."""
    proposals = generate_mock_proposals()
    if status:
        proposals = [p for p in proposals if p["status"] == status]
    return {"proposals": proposals, "count": len(proposals)}


@router.get("/snapshot")
async def get_learning_snapshot():
    """Get complete learning snapshot."""
    return {
        "timestamp": datetime.now().isoformat(),
        "total_signals_analyzed": 142,
        "total_outcomes_resolved": 120,
        "overall_win_rate": 58.5,
        "overall_expectancy": 15.2,
        "calibration_report": generate_mock_calibration(),
        "feature_report": generate_mock_features(),
        "suppression_report": generate_mock_suppressions(),
        "regime_report": generate_mock_regimes(),
        "timing_report": generate_mock_timing(),
        "pending_proposals": generate_mock_proposals(),
    }


@router.get("/health")
async def learning_health_check():
    """Health check for learning subsystem."""
    return {
        "status": "operational",
        "subsystem": "Tactical Learning",
        "components": {
            "signal_outcome_analyzer": "operational",
            "feature_importance_engine": "operational",
            "confidence_calibrator": "operational",
            "suppression_effectiveness": "operational",
            "regime_performance_analyzer": "operational",
            "timing_performance_analyzer": "operational",
            "score_optimizer": "operational",
            "learning_logger": "operational",
        },
    }
