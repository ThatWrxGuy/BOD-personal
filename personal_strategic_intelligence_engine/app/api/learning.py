"""Learning API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.learning.strategic_learning_service import StrategicLearningService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/memories")
async def list_memories(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List decision memories."""
    service = StrategicLearningService(session)
    memories = await service.get_memories(limit)
    
    return {
        "memories": [
            {
                "id": str(m.id),
                "decision_type": m.decision_type,
                "decision_summary": m.decision_summary,
                "consensus_score": m.consensus_score,
                "outcome_category": m.outcome_category,
                "outcome_delta": m.outcome_delta,
                "outcome_evaluated": m.outcome_evaluated,
                "created_at": m.created_at.isoformat(),
            }
            for m in memories
        ]
    }


@router.get("/memories/{memory_id}")
async def get_memory(
    memory_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific decision memory."""
    from app.models.learning import DecisionMemory
    
    service = StrategicLearningService(session)
    
    try:
        memory = await session.get(DecisionMemory, uuid.UUID(memory_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {
        "id": str(memory.id),
        "decision_id": str(memory.decision_id) if memory.decision_id else None,
        "debate_session_id": str(memory.debate_session_id) if memory.debate_session_id else None,
        "execution_id": str(memory.execution_id) if memory.execution_id else None,
        "decision_type": memory.decision_type,
        "decision_summary": memory.decision_summary,
        "rationale_summary": memory.rationale_summary,
        "consensus_score": memory.consensus_score,
        "approval_result": memory.approval_result,
        "execution_result": memory.execution_result,
        "predicted_outcome": memory.predicted_outcome,
        "actual_outcome": memory.actual_outcome,
        "outcome_delta": memory.outcome_delta,
        "outcome_category": memory.outcome_category,
        "outcome_evaluated": memory.outcome_evaluated,
        "lessons_learned": memory.lessons_learned,
        "created_at": memory.created_at.isoformat(),
    }


@router.get("/lessons")
async def list_lessons(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List strategic lessons."""
    service = StrategicLearningService(session)
    lessons = await service.get_lessons(limit)
    
    return {
        "lessons": [
            {
                "id": str(l.id),
                "lesson_type": l.lesson_type,
                "title": l.title,
                "description": l.description,
                "domain": l.domain,
                "confidence": l.confidence,
                "is_provisional": l.is_provisional,
                "times_referenced": l.times_referenced,
                "created_at": l.created_at.isoformat(),
            }
            for l in lessons
        ]
    }


@router.get("/patterns")
async def list_patterns(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List strategic patterns."""
    from app.models.learning import StrategicPattern
    
    result = await session.execute(
        select(StrategicPattern)
        .order_by(StrategicPattern.historical_frequency.desc())
        .limit(limit)
    )
    patterns = list(result.scalars().all())
    
    return {
        "patterns": [
            {
                "id": str(p.id),
                "pattern_type": p.pattern_type,
                "title": p.title,
                "description": p.description,
                "domain": p.domain,
                "historical_frequency": p.historical_frequency,
                "average_outcome_score": p.average_outcome_score,
                "created_at": p.created_at.isoformat(),
            }
            for p in patterns
        ]
    }


@router.get("/agents/scorecards")
async def list_agent_scorecards(
    session: AsyncSession = Depends(get_db),
):
    """List all agent scorecards."""
    service = StrategicLearningService(session)
    scorecards = await service.get_all_agent_performance()
    
    return {
        "scorecards": [
            {
                "id": str(s.id),
                "agent_id": s.agent_id,
                "agent_name": s.agent_name,
                "total_decisions": s.total_decisions,
                "accurate_predictions": s.accurate_predictions,
                "accuracy_score": s.accuracy_score,
                "avg_confidence": s.avg_confidence,
                "confidence_accuracy": s.confidence_accuracy,
                "current_weight": s.current_weight,
            }
            for s in scorecards
        ]
    }


@router.get("/agents/{agent_id}/performance")
async def get_agent_performance(
    agent_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get specific agent performance."""
    service = StrategicLearningService(session)
    scorecard = await service.get_agent_performance(agent_id)
    
    if not scorecard:
        raise HTTPException(status_code=404, detail="Agent scorecard not found")
    
    return {
        "agent_id": scorecard.agent_id,
        "agent_name": scorecard.agent_name,
        "total_decisions": scorecard.total_decisions,
        "accurate_predictions": scorecard.accurate_predictions,
        "accuracy_score": scorecard.accuracy_score,
        "domain_scores": scorecard.domain_scores,
        "avg_confidence": scorecard.avg_confidence,
        "confidence_accuracy": scorecard.confidence_accuracy,
        "current_weight": scorecard.current_weight,
    }


@router.post("/evaluate/{decision_id}")
async def evaluate_decision(
    decision_id: str,
    actual_outcome: str,
    outcome_delta: float = 0.0,
    session: AsyncSession = Depends(get_db),
):
    """Evaluate a decision outcome."""
    from app.models.learning import DecisionMemory
    
    service = StrategicLearningService(session)
    
    try:
        memory_id = uuid.UUID(decision_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        memory = await service.evaluate_outcome(memory_id, actual_outcome, outcome_delta)
        
        return {
            "id": str(memory.id),
            "outcome_category": memory.outcome_category,
            "outcome_delta": memory.outcome_delta,
            "outcome_evaluated": memory.outcome_evaluated,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/record")
async def record_memory(
    decision_id: str,
    decision_type: str = "STRATEGIC",
    decision_summary: str = "",
    rationale_summary: str = "",
    predicted_outcome: str = "",
    debate_session_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """Record a decision in memory."""
    service = StrategicLearningService(session)
    
    memory = await service.record_decision_memory(
        decision_id=uuid.UUID(decision_id) if decision_id else uuid.uuid4(),
        debate_session_id=uuid.UUID(debate_session_id) if debate_session_id else None,
        execution_id=uuid.UUID(execution_id) if execution_id else None,
        decision_type=decision_type,
        decision_summary=decision_summary,
        rationale_summary=rationale_summary,
        predicted_outcome=predicted_outcome,
    )
    
    return {
        "id": str(memory.id),
        "decision_type": memory.decision_type,
        "created_at": memory.created_at.isoformat(),
    }
