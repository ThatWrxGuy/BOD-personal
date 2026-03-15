"""Board meeting API routes."""
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.board import (
    BoardMeetingCreate,
    BoardMeetingUpdate,
    BoardMeetingResponse,
    BoardMeetingListResponse,
)
from app.memory.meeting_memory import MeetingMemory
from app.core.orchestrator import BoardOrchestrator
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/board/meetings", tags=["board"])


@router.post("", response_model=BoardMeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: BoardMeetingCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new board meeting and optionally run it."""
    memory = MeetingMemory(session)
    
    # Create meeting
    meeting = await memory.create(meeting_data)
    
    return meeting


@router.post("/{meeting_id}/run", response_model=BoardMeetingResponse)
async def run_meeting(
    meeting_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Run a board meeting (triggers agent analysis)."""
    memory = MeetingMemory(session)
    
    # Get meeting
    meeting = await memory.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    
    # Run the meeting
    orchestrator = BoardOrchestrator(session)
    try:
        meeting = await orchestrator.run_meeting(meeting_id)
    except Exception as e:
        logger.error(f"Error running meeting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running meeting: {str(e)}"
        )
    
    # Reload meeting with responses
    meeting = await memory.get(meeting_id)
    
    return meeting


@router.get("", response_model=BoardMeetingListResponse)
async def list_meetings(
    limit: int = 50,
    offset: int = 0,
    meeting_type: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """List board meetings."""
    memory = MeetingMemory(session)
    meetings, total = await memory.list(
        limit=limit,
        offset=offset,
        meeting_type=meeting_type,
    )
    
    return BoardMeetingListResponse(
        meetings=[await _meeting_to_response(m, session) for m in meetings],
        total=total,
    )


@router.get("/{meeting_id}", response_model=BoardMeetingResponse)
async def get_meeting(
    meeting_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific board meeting with all responses."""
    memory = MeetingMemory(session)
    meeting = await memory.get(meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    
    return await _meeting_to_response(meeting, session)


@router.patch("/{meeting_id}", response_model=BoardMeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_data: BoardMeetingUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a board meeting."""
    memory = MeetingMemory(session)
    meeting = await memory.update(meeting_id, meeting_data)
    
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    
    return await _meeting_to_response(meeting, session)


async def _meeting_to_response(meeting, session) -> BoardMeetingResponse:
    """Convert meeting model to response schema."""
    from app.schemas.board import AgentResponseResponse, CritiqueResponseResponse
    
    # Reload with relationships
    await session.refresh(meeting, ["agent_responses", "critique_responses"])
    
    agent_responses = []
    for ar in meeting.agent_responses:
        await session.refresh(ar, ["agent"])
        agent_responses.append(AgentResponseResponse(
            id=ar.id,
            meeting_id=ar.meeting_id,
            agent_id=ar.agent_id,
            summary_judgment=ar.summary_judgment,
            main_recommendation=ar.main_recommendation,
            supporting_reasons=json.loads(ar.supporting_reasons),
            main_risks=json.loads(ar.main_risks),
            tradeoffs=json.loads(ar.tradeoffs),
            requested_followups=json.loads(ar.requested_followups) if ar.requested_followups else None,
            confidence_score=ar.confidence_score,
            version_id=ar.version_id,
            created_at=ar.created_at,
        ))
    
    critique_responses = []
    for cr in meeting.critique_responses:
        critique_responses.append(CritiqueResponseResponse(
            id=cr.id,
            meeting_id=cr.meeting_id,
            source_agent_id=cr.source_agent_id,
            target_agent_id=cr.target_agent_id,
            critique_text=cr.critique_text,
            severity=cr.severity,
            created_at=cr.created_at,
        ))
    
    return BoardMeetingResponse(
        id=meeting.id,
        meeting_type=meeting.meeting_type,
        trigger_type=meeting.trigger_type,
        question=meeting.question,
        context_snapshot=meeting.context_snapshot,
        executive_summary=meeting.executive_summary,
        consensus_recommendation=meeting.consensus_recommendation,
        alternatives=json.loads(meeting.alternatives) if meeting.alternatives else None,
        risks=json.loads(meeting.risks) if meeting.risks else None,
        tradeoffs=json.loads(meeting.tradeoffs) if meeting.tradeoffs else None,
        confidence_score=meeting.confidence_score,
        data_gaps=json.loads(meeting.data_gaps) if meeting.data_gaps else None,
        status=meeting.status,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        agent_responses=agent_responses,
        critique_responses=critique_responses,
    )
