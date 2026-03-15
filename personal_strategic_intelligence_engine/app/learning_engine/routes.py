"""Learning Engine API routes.

API endpoints for the Strategic Memory & Learning Engine.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.learning_engine.memory_models import (
    LearningStatistics,
    MemoryCategory,
    SourceType,
)
from app.learning_engine.strategic_memory import get_strategic_memory, reset_strategic_memory
from app.learning_engine.outcome_evaluator import get_outcome_evaluator
from app.learning_engine.performance_tracker import get_performance_tracker, reset_performance_tracker
from app.learning_engine.degradation_detector import get_degradation_detector
from app.learning_engine.confidence_calibrator import get_confidence_calibrator
from app.learning_engine.learning_engine import get_learning_engine, reset_learning_engine
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/learning", tags=["learning"])


# ============ Request/Response Models ============

class EvaluateRequest(BaseModel):
    """Request to evaluate an execution."""
    execution_record: dict
    predictions: Optional[dict] = None


class MemoryListResponse(BaseModel):
    """Response for memory list."""
    records: list
    total: int


class PerformanceListResponse(BaseModel):
    """Response for performance list."""
    items: list
    total: int


# ============ Memory Endpoints ============

@router.get("/memory", response_model=MemoryListResponse)
async def list_memory(
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """
    List stored memory records.
    
    Returns memory records, optionally filtered by category or source type.
    """
    memory = get_strategic_memory()
    
    records = []
    
    if category:
        try:
            cat = MemoryCategory(category)
            records = memory.get_by_category(cat)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
    elif source_type:
        try:
            src = SourceType(source_type)
            records = memory.get_by_source_type(src)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source type: {source_type}"
            )
    else:
        records = memory.get_recent(limit + offset)
    
    # Apply pagination
    paginated = records[offset:offset + limit]
    
    return {
        "records": [r.to_dict() for r in paginated],
        "total": len(records),
    }


@router.get("/memory/{record_id}")
async def get_memory_record(record_id: str):
    """Retrieve a specific memory record."""
    memory = get_strategic_memory()
    record = memory.get(record_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory record not found: {record_id}"
        )
    
    return record.to_dict()


@router.get("/memory/search")
async def search_memory(
    query: str,
    limit: int = 50,
):
    """Search memory records."""
    memory = get_strategic_memory()
    results = memory.search(query, limit)
    
    return {
        "results": [r.to_dict() for r in results],
        "total": len(results),
    }


# ============ Performance Endpoints ============

@router.get("/strategies/performance")
async def get_strategy_performance(
    strategy_id: Optional[str] = None,
):
    """
    Get strategy performance metrics.
    
    Returns either a specific strategy's performance or all strategies.
    """
    tracker = get_performance_tracker()
    
    if strategy_id:
        perf = tracker.get_strategy_performance(strategy_id)
        if not perf:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy not found: {strategy_id}"
            )
        
        return {
            "strategy_id": perf.strategy_id,
            "category": perf.category,
            "total_executions": perf.total_executions,
            "successful_executions": perf.successful_executions,
            "failed_executions": perf.failed_executions,
            "win_rate": perf.win_rate,
            "average_return": perf.average_return,
            "max_drawdown": perf.max_drawdown,
            "expectancy": perf.expectancy,
            "last_updated": perf.last_updated.isoformat() if perf.last_updated else None,
        }
    
    # Return all strategies
    all_perf = tracker.get_all_strategy_performance()
    
    return {
        "strategies": [
            {
                "strategy_id": p.strategy_id,
                "category": p.category,
                "total_executions": p.total_executions,
                "win_rate": p.win_rate,
                "average_return": p.average_return,
            }
            for p in all_perf
        ],
        "total": len(all_perf),
    }


@router.get("/agents/performance")
async def get_agent_performance(
    agent_id: Optional[str] = None,
):
    """
    Get agent performance metrics.
    
    Returns either a specific agent's performance or all agents.
    """
    tracker = get_performance_tracker()
    
    if agent_id:
        perf = tracker.get_agent_performance(agent_id)
        if not perf:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}"
            )
        
        return {
            "agent_id": perf.agent_id,
            "agent_name": perf.agent_name,
            "total_proposals": perf.total_proposals,
            "accepted_proposals": perf.accepted_proposals,
            "rejected_proposals": perf.rejected_proposals,
            "approval_rate": perf.approval_rate,
            "average_confidence": perf.average_confidence,
            "governance_override_rate": perf.governance_override_rate,
            "last_updated": perf.last_updated.isoformat() if perf.last_updated else None,
        }
    
    # Return all agents
    all_perf = tracker.get_all_agent_performance()
    
    return {
        "agents": [
            {
                "agent_id": p.agent_id,
                "agent_name": p.agent_name,
                "total_proposals": p.total_proposals,
                "approval_rate": p.approval_rate,
            }
            for p in all_perf
        ],
        "total": len(all_perf),
    }


@router.get("/strategies/performance/top")
async def get_top_strategies(
    limit: int = 10,
):
    """Get top performing strategies by win rate."""
    tracker = get_performance_tracker()
    top = tracker.get_top_performing_strategies(limit)
    
    return {
        "strategies": [
            {
                "strategy_id": p.strategy_id,
                "win_rate": p.win_rate,
                "average_return": p.average_return,
                "total_executions": p.total_executions,
            }
            for p in top
        ],
    }


# ============ Degradation Endpoints ============

@router.get("/degradation")
async def get_degradation_alerts(
    acknowledged: bool = False,
):
    """Get active degradation alerts."""
    detector = get_degradation_detector()
    
    alerts = detector.get_active_alerts()
    
    if not acknowledged:
        alerts = [a for a in alerts if not a.acknowledged]
    
    return {
        "alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "entity_id": a.entity_id,
                "entity_type": a.entity_type,
                "degradation_level": a.degradation_level,
                "metric_name": a.metric_name,
                "previous_value": a.previous_value,
                "current_value": a.current_value,
                "description": a.description,
                "recommendations": a.recommendations,
                "acknowledged": a.acknowledged,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.post("/degradation/{alert_id}/acknowledge")
async def acknowledge_degradation_alert(alert_id: str):
    """Acknowledge a degradation alert."""
    detector = get_degradation_detector()
    
    success = detector.acknowledge_alert(alert_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert not found: {alert_id}"
        )
    
    return {"message": "Alert acknowledged", "alert_id": alert_id}


# ============ Evaluation Endpoints ============

@router.post("/evaluate")
async def trigger_evaluation(request: EvaluateRequest):
    """
    Trigger evaluation of an execution outcome.
    
    This processes an execution record and generates learning insights.
    """
    engine = get_learning_engine()
    
    result = await engine.process_execution_outcome(
        execution_record=request.execution_record,
        predictions=request.predictions,
    )
    
    return result


# ============ Statistics Endpoints ============

@router.get("/statistics")
async def get_learning_statistics():
    """Get learning engine statistics."""
    engine = get_learning_engine()
    stats = engine.get_statistics()
    
    return {
        "total_memory_records": stats.total_memory_records,
        "total_outcome_records": stats.total_outcome_records,
        "total_degradation_alerts": stats.total_degradation_alerts,
        "active_alerts": stats.active_alerts,
        "strategies_tracked": stats.strategies_tracked,
        "agents_tracked": stats.agents_tracked,
        "average_return_accuracy": stats.average_return_accuracy,
        "average_risk_accuracy": stats.average_risk_accuracy,
        "overall_win_rate": stats.overall_win_rate,
        "confidence_adjustments_count": stats.confidence_adjustments_count,
        "learning_cycle_count": stats.learning_cycle_count,
    }


@router.get("/confidence/adjustments")
async def get_confidence_adjustments(
    limit: int = 50,
):
    """Get confidence adjustment history."""
    calibrator = get_confidence_calibrator()
    adjustments = calibrator.get_adjustment_history(limit)
    
    return {
        "adjustments": [
            {
                "id": a.id,
                "entity_id": a.entity_id,
                "entity_type": a.entity_type,
                "previous_confidence": a.previous_confidence,
                "new_confidence": a.new_confidence,
                "adjustment_reason": a.adjustment_reason,
                "based_on_samples": a.based_on_samples,
                "accuracy_delta": a.accuracy_delta,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in adjustments
        ],
    }


# ============ Utility Endpoints ============

@router.post("/reset")
async def reset_learning_engine():
    """Reset the learning engine (for testing)."""
    reset_learning_engine()
    reset_strategic_memory()
    reset_performance_tracker()
    logger.info("Learning engine reset")
    
    return {"message": "Learning engine reset successfully"}


@router.get("/memory-stats")
async def get_memory_stats():
    """Get memory store statistics."""
    memory = get_strategic_memory()
    stats = memory.get_statistics()
    
    return stats
