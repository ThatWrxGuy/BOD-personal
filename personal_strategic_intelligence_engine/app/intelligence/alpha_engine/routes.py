"""API Routes for Alpha Engine."""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/alpha-engine", tags=["alpha-engine"])


def generate_mock_alphas():
    return {
        "alphas": [
            {
                "id": "alpha-001",
                "name": "VWAP-Reclaim-Call-Continuation",
                "domain": "finance",
                "hypothesis": "When SPY reclaims VWAP after downside sweep and nearby call gamma increases, 1-step OTM calls outperform ATM calls over 5-10 minutes.",
                "status": "active",
                "confidence_score": 0.81,
                "regime_requirements": {"regime": "trend_day"},
            },
            {
                "id": "alpha-002",
                "name": "Liquidity-Sweep-Reversal",
                "domain": "finance",
                "hypothesis": "When SPY sweeps liquidity to downside and immediately reverses, short-dated puts capture reversal.",
                "status": "validated",
                "confidence_score": 0.72,
                "regime_requirements": {"regime": "range_day"},
            },
            {
                "id": "alpha-003",
                "name": "Opening-Range-Breakout",
                "domain": "finance",
                "hypothesis": "SPY opening range breakout with high volume leads to sustained momentum.",
                "status": "validated",
                "confidence_score": 0.68,
                "regime_requirements": {"regime": "opening_drive"},
            },
        ]
    }


def generate_mock_rankings():
    return {
        "rankings": [
            {"rank": 1, "alpha_id": "alpha-001", "name": "VWAP-Reclaim-Call-Continuation", "score": 0.85, "regime_fit": 0.9, "recommendation": "Strong opportunity - deploy"},
            {"rank": 2, "alpha_id": "alpha-002", "name": "Liquidity-Sweep-Reversal", "score": 0.72, "regime_fit": 0.8, "recommendation": "Good opportunity - consider"},
            {"rank": 3, "alpha_id": "alpha-003", "name": "Opening-Range-Breakout", "score": 0.65, "regime_fit": 0.7, "recommendation": "Moderate opportunity - monitor"},
        ]
    }


def generate_mock_patterns():
    return {
        "patterns": [
            {
                "id": "pattern-001",
                "signal_sequence": ["vwap_reclaim", "gamma_acceleration", "bullish_outcome"],
                "frequency": 42,
                "confidence": 0.78,
                "outcome_distribution": {"bullish": 68, "neutral": 20, "bearish": 12},
            },
            {
                "id": "pattern-002",
                "signal_sequence": ["liquidity_sweep", "vwap_reclaim", "reversal"],
                "frequency": 28,
                "confidence": 0.65,
                "outcome_distribution": {"reversal": 72, "continuation": 18, "failure": 10},
            },
        ]
    }


@router.get("/alphas")
async def get_alphas(status: Optional[str] = None):
    """Get all alpha candidates."""
    return generate_mock_alphas()


@router.get("/alphas/{alpha_id}")
async def get_alpha(alpha_id: str):
    """Get alpha by ID."""
    return {
        "id": alpha_id,
        "name": "VWAP-Reclaim-Call-Continuation",
        "domain": "finance",
        "hypothesis": "When SPY reclaims VWAP after downside sweep and nearby call gamma increases, 1-step OTM calls outperform ATM calls over 5-10 minutes.",
        "status": "active",
        "confidence_score": 0.81,
    }


@router.get("/rankings")
async def get_rankings(regime: str = Query("trend_day")):
    """Get strategy rankings."""
    return generate_mock_rankings()


@router.get("/patterns")
async def get_patterns():
    """Get discovered patterns."""
    return generate_mock_patterns()


@router.get("/summary")
async def get_summary():
    """Get alpha engine summary."""
    return {
        "total_alphas": 12,
        "by_status": {
            "discovered": 3,
            "validated": 5,
            "active": 3,
            "degraded": 1,
        },
        "patterns_discovered": 8,
        "hypotheses_pending": 3,
        "active_alerts": 1,
    }


@router.get("/health")
async def health_check():
    """Health check for alpha engine."""
    return {
        "status": "operational",
        "subsystem": "Alpha Engine",
        "components": {
            "pattern_mining": "operational",
            "hypothesis_engine": "operational",
            "regime_segmenter": "operational",
            "feature_scoring": "operational",
            "edge_validator": "operational",
            "strategy_ranker": "operational",
            "degradation_monitor": "operational",
            "alpha_registry": "operational",
        },
    }
