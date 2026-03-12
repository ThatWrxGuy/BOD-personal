"""Optimization API routes."""
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.optimization import (
    get_domain_optimizer,
    get_domain_modeler,
    get_domain_scorer,
    get_optimization_logger,
    LifeDomain,
    OptimizationPolicy,
    DomainMetrics,
    DomainDataInput,
)
from app.optimization.optimization_policy import get_optimization_policy_engine


router = APIRouter(prefix="/optimization", tags=["optimization"])


class UpdateDomainRequest(BaseModel):
    """Request to update a domain with new data."""
    domain: LifeDomain
    data: DomainDataInput


class UpdatePolicyRequest(BaseModel):
    """Request to update optimization policy."""
    policy: OptimizationPolicy


class RunCycleResponse(BaseModel):
    """Response from running an optimization cycle."""
    cycle_id: str
    status: str
    balance_score: float
    recommendations_count: int
    conditions_detected: int


@router.get("/domains")
async def get_domain_performance():
    """Returns domain performance metrics for all domains."""
    
    optimizer = get_domain_optimizer()
    modeler = get_domain_modeler()
    scorer = get_domain_scorer()
    
    # Get all domain metrics
    domain_metrics = modeler.get_all_domain_metrics()
    
    # Get detailed reports for each domain
    reports = []
    for dm in domain_metrics:
        report = scorer.get_detailed_domain_report(dm)
        reports.append(report)
    
    return {
        "domains": reports,
        "total_domains": len(reports),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/summary")
async def get_optimization_summary():
    """Returns high-level optimization summary."""
    
    optimizer = get_domain_optimizer()
    logger = get_optimization_logger()
    
    summary = optimizer.get_optimization_summary()
    
    # Add cycle count
    summary["cycles_today"] = logger.get_cycles_today()
    
    return summary


@router.get("/tradeoffs")
async def get_tradeoffs():
    """Returns detected tradeoff situations."""
    
    from app.optimization.tradeoff_engine import get_tradeoff_engine
    
    engine = get_tradeoff_engine()
    
    # Get active conflicts
    optimizer = get_domain_optimizer()
    modeler = get_domain_modeler()
    metrics = modeler.get_all_domain_metrics()
    
    conflicts = engine.detect_conflicts(metrics)
    
    # Get recent tradeoff decisions
    history = engine.get_tradeoff_history(limit=10)
    
    return {
        "active_conflicts": conflicts,
        "recent_decisions": [
            {
                "type": d.tradeoff_type.value,
                "winner": d.winner.value if d.winner else None,
                "loser": d.loser.value if d.loser else None,
                "reasoning": d.reasoning[:200] + "..." if len(d.reasoning) > 200 else d.reasoning,
                "timestamp": d.timestamp.isoformat(),
            }
            for d in history
        ],
        "statistics": engine.get_tradeoff_statistics(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/recommendations")
async def get_recommendations():
    """Returns recommended domain adjustments."""
    
    optimizer = get_domain_optimizer()
    logger = get_optimization_logger()
    
    # Get latest cycle
    latest_cycle = logger.get_latest_cycle()
    
    if not latest_cycle:
        # Run a cycle if none exists
        latest_cycle = optimizer.run_optimization_cycle()
    
    recommendations = []
    for rec in latest_cycle.recommendations:
        recommendations.append({
            "action": rec.action.value,
            "target_domain": rec.target_domain.value,
            "priority": rec.priority,
            "reasoning": rec.reasoning,
            "expected_impact": rec.expected_impact,
            "confidence": rec.confidence,
            "policy_respected": rec.policy_constraints_respected,
            "timestamp": rec.timestamp.isoformat(),
        })
    
    return {
        "recommendations": recommendations,
        "total_count": len(recommendations),
        "cycle_id": latest_cycle.cycle_id,
        "balance_score": latest_cycle.overall_balance_score,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/run-cycle")
async def run_optimization_cycle():
    """Triggers optimization cycle manually."""
    
    optimizer = get_domain_optimizer()
    
    try:
        cycle = optimizer.run_optimization_cycle()
        
        return RunCycleResponse(
            cycle_id=cycle.cycle_id,
            status=cycle.execution_status,
            balance_score=cycle.overall_balance_score,
            recommendations_count=len(cycle.recommendations),
            conditions_detected=len(cycle.detected_conditions),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization cycle failed: {str(e)}"
        )


@router.post("/domains")
async def update_domain(data: UpdateDomainRequest):
    """Update a specific domain with new data."""
    
    modeler = get_domain_modeler()
    scorer = get_domain_scorer()
    
    try:
        # Update domain metrics
        metrics = modeler.update_domain_metrics(data.domain, data.data)
        
        # Get detailed report
        report = scorer.get_detailed_domain_report(metrics)
        
        return {
            "status": "updated",
            "domain": data.domain.value,
            "metrics": report,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Domain update failed: {str(e)}"
        )


@router.get("/policy")
async def get_policy():
    """Get current optimization policy."""
    
    policy_engine = get_optimization_policy_engine()
    
    return {
        "policy": policy_engine.policy.model_dump(),
        "status": policy_engine.get_policy_status(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/policy")
async def update_policy(data: UpdatePolicyRequest):
    """Update optimization policy."""
    
    policy_engine = get_optimization_policy_engine()
    
    try:
        policy_engine.update_policy(data.policy)
        
        return {
            "status": "updated",
            "policy": data.policy.model_dump(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Policy update failed: {str(e)}"
        )


@router.get("/cycles")
async def get_cycle_history(limit: int = 10):
    """Get optimization cycle history."""
    
    logger = get_optimization_logger()
    
    cycles = logger.get_recent_cycles(count=limit)
    
    return {
        "cycles": [
            {
                "cycle_id": c.cycle_id,
                "timestamp": c.timestamp.isoformat(),
                "balance_score": c.overall_balance_score,
                "recommendations_count": len(c.recommendations),
                "conditions_count": len(c.detected_conditions),
                "status": c.execution_status,
            }
            for c in cycles
        ],
        "total": len(cycles),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/statistics")
async def get_statistics():
    """Get optimization statistics."""
    
    logger = get_optimization_logger()
    
    return {
        "logger_stats": logger.get_statistics(),
        "timestamp": datetime.utcnow().isoformat(),
    }
