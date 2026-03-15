"""Debate API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.debate.debate_engine import DebateEngine
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/debate", tags=["debate"])


@router.get("/sessions")
async def list_sessions(
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """List all debate sessions."""
    engine = DebateEngine(session)
    sessions = await engine.list_sessions(status)
    
    return {
        "sessions": [
            {
                "id": str(s.id),
                "title": s.title,
                "topic": s.topic,
                "status": s.status,
                "rounds_completed": s.rounds_completed,
                "consensus_score": s.consensus_score,
                "final_recommendation": s.final_recommendation,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific debate session."""
    engine = DebateEngine(session)
    
    try:
        sess = await engine.get_session(uuid.UUID(session_id))
        if not sess:
            raise HTTPException(status_code=404, detail="Debate session not found")
        
        return {
            "id": str(sess.id),
            "decision_id": str(sess.decision_id) if sess.decision_id else None,
            "title": sess.title,
            "description": sess.description,
            "topic": sess.topic,
            "status": sess.status,
            "rounds_completed": sess.rounds_completed,
            "max_rounds": sess.max_rounds,
            "consensus_score": sess.consensus_score,
            "final_recommendation": sess.final_recommendation,
            "participants": sess.participants,
            "start_time": sess.start_time.isoformat() if sess.start_time else None,
            "end_time": sess.end_time.isoformat() if sess.end_time else None,
            "created_at": sess.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


@router.get("/sessions/{session_id}/arguments")
async def get_arguments(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get arguments for a debate session."""
    engine = DebateEngine(session)
    
    try:
        arguments = await engine.get_arguments(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    return {
        "arguments": [
            {
                "id": str(a.id),
                "agent_id": a.agent_id,
                "round_number": a.round_number,
                "position": a.position,
                "argument_text": a.argument_text,
                "reasoning": a.reasoning,
                "risk_assessment": a.risk_assessment,
                "confidence_score": a.confidence_score,
                "created_at": a.created_at.isoformat(),
            }
            for a in arguments
        ]
    }


@router.get("/sessions/{session_id}/votes")
async def get_votes(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get votes for a debate session."""
    engine = DebateEngine(session)
    
    try:
        votes = await engine.get_votes(uuid.UUID(session_id))
        details = await engine.get_consensus_details(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    return {
        "votes": [
            {
                "id": str(v.id),
                "agent_id": v.agent_id,
                "agent_name": v.agent_name,
                "vote": v.vote,
                "justification": v.justification,
                "confidence": v.confidence,
                "weight": v.weight,
                "round_number": v.round_number,
            }
            for v in votes
        ],
        "consensus_details": details,
    }


@router.post("/start")
async def start_debate(
    title: str,
    description: str,
    topic: str,
    decision_id: Optional[str] = None,
    context: dict = {},
    session: AsyncSession = Depends(get_db),
):
    """Start a new debate session."""
    engine = DebateEngine(session)
    
    sess = await engine.start_debate(
        decision_id=uuid.UUID(decision_id) if decision_id else None,
        title=title,
        description=description,
        topic=topic,
        context=context,
    )
    
    return {
        "id": str(sess.id),
        "title": sess.title,
        "status": sess.status,
    }


@router.post("/sessions/{session_id}/complete")
async def complete_debate(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Manually complete a debate session."""
    engine = DebateEngine(session)
    
    try:
        sess = await engine.get_session(uuid.UUID(session_id))
        if not sess:
            raise HTTPException(status_code=404, detail="Debate session not found")
        
        sess.status = "COMPLETED"
        await session.commit()
        
        return {
            "id": str(sess.id),
            "status": sess.status,
            "consensus_score": sess.consensus_score,
            "final_recommendation": sess.final_recommendation,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
