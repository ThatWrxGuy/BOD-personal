"""API Routes for Strategic Intelligence Bus."""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/intelligence-bus", tags=["intelligence-bus"])


def generate_mock_stats():
    return {
        "total_signals": 156,
        "by_domain": {
            "finance": 89,
            "health": 32,
            "relationship": 15,
            "career": 12,
            "strategic": 8,
        },
        "by_priority": {
            "critical": 12,
            "high": 45,
            "medium": 62,
            "low": 28,
            "background": 9,
        },
        "subscribers": 8,
        "handlers": 15,
    }


def generate_mock_signals():
    return {
        "signals": [
            {
                "id": "sig-001",
                "type": "spy_delta_velocity_event",
                "domain": "finance",
                "source": "OptionsIntelligence",
                "timestamp": datetime.now().isoformat(),
                "priority": "high",
                "confidence": 0.82,
                "payload": {"ticker": "SPY", "direction": "bullish", "velocity": 0.75},
                "resolution": "pending",
            },
            {
                "id": "sig-002",
                "type": "volatility_regime_shift",
                "domain": "finance",
                "source": "MarketStructureEngine",
                "timestamp": datetime.now().isoformat(),
                "priority": "high",
                "confidence": 0.78,
                "payload": {"symbol": "SPY", "old_regime": "normal", "new_regime": "elevated"},
                "resolution": "pending",
            },
            {
                "id": "sig-003",
                "type": "sleep_degradation_signal",
                "domain": "health",
                "source": "HealthAgent",
                "timestamp": datetime.now().isoformat(),
                "priority": "medium",
                "confidence": 0.65,
                "payload": {"hours": 5.5, "quality_score": 0.6},
                "resolution": "pending",
            },
        ]
    }


def generate_mock_routes():
    return {
        "routes": {
            "spy_delta_velocity_event": ["FinanceAgent", "InvestmentStrategist", "RiskManagementAgent"],
            "volatility_regime_shift": ["FinanceAgent", "OptionsIntelligence"],
            "gamma_acceleration_event": ["FinanceAgent", "OptionsIntelligence"],
            "sleep_degradation_signal": ["HealthAgent"],
            "governance_approval_required": ["GovernanceSystem"],
        }
    }


@router.get("/signals")
async def get_signals(limit: int = Query(20, ge=1, le=100)):
    """Get recent signals."""
    return generate_mock_signals()


@router.get("/signals/{signal_id}")
async def get_signal(signal_id: str):
    """Get signal by ID."""
    return {
        "id": signal_id,
        "type": "spy_delta_velocity_event",
        "domain": "finance",
        "source": "OptionsIntelligence",
        "timestamp": datetime.now().isoformat(),
        "priority": "high",
        "confidence": 0.82,
        "payload": {"ticker": "SPY", "direction": "bullish", "velocity": 0.75},
    }


@router.get("/signals/types")
async def get_signal_types():
    """Get all registered signal types."""
    return {
        "signal_types": [
            "spy_delta_velocity_event",
            "volatility_regime_shift",
            "gamma_acceleration_event",
            "options_liquidity_spike",
            "debt_risk_detected",
            "investment_opportunity_signal",
            "market_volatility_spike",
            "sleep_degradation_signal",
            "health_routine_breakdown",
            "relationship_conflict_signal",
            "career_opportunity_detected",
            "governance_approval_required",
        ]
    }


@router.get("/routes")
async def get_routes():
    """Get routing rules."""
    return generate_mock_routes()


@router.get("/stats")
async def get_stats():
    """Get bus statistics."""
    return generate_mock_stats()


@router.get("/health")
async def health_check():
    """Health check for intelligence bus."""
    return {
        "status": "operational",
        "subsystem": "Strategic Intelligence Bus",
        "components": {
            "signal_models": "operational",
            "signal_registry": "operational",
            "signal_router": "operational",
            "signal_bus": "operational",
            "priority_queue": "operational",
            "event_log": "operational",
        },
    }
