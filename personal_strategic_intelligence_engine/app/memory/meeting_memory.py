"""Memory layer for meeting storage and retrieval."""
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_meeting import BoardMeeting
from app.models.agent_response import AgentResponse
from app.models.critique_response import CritiqueResponse
from app.schemas.board import BoardMeetingCreate, BoardMeetingUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class MeetingMemory:
    """Persistent storage for board meetings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, meeting_data: BoardMeetingCreate) -> BoardMeeting:
        """Create a new board meeting."""
        meeting = BoardMeeting(
            meeting_type=meeting_data.meeting_type,
            trigger_type=meeting_data.trigger_type,
            question=meeting_data.question,
            status="pending",
        )
        
        self.session.add(meeting)
        await self.session.commit()
        await self.session.refresh(meeting)
        
        return meeting

    async def get(self, meeting_id: int) -> Optional[BoardMeeting]:
        """Get a meeting by ID with all responses."""
        result = await self.session.execute(
            select(BoardMeeting)
            .where(BoardMeeting.id == meeting_id)
        )
        meeting = result.scalars().first()
        
        if meeting:
            # Load related data
            await self.session.refresh(meeting, ["agent_responses", "critique_responses"])
        
        return meeting

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        meeting_type: Optional[str] = None,
    ) -> tuple[list[BoardMeeting], int]:
        """List meetings with pagination."""
        query = select(BoardMeeting).order_by(desc(BoardMeeting.created_at))
        
        if meeting_type:
            query = query.where(BoardMeeting.meeting_type == meeting_type)
        
        # Get total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        meetings = result.scalars().all()
        
        return list(meetings), total

    async def update(
        self,
        meeting_id: int,
        meeting_data: BoardMeetingUpdate,
    ) -> Optional[BoardMeeting]:
        """Update a meeting."""
        result = await self.session.execute(
            select(BoardMeeting).where(BoardMeeting.id == meeting_id)
        )
        meeting = result.scalars().first()
        
        if not meeting:
            return None

        # Update fields if provided
        if meeting_data.executive_summary is not None:
            meeting.executive_summary = meeting_data.executive_summary
        if meeting_data.consensus_recommendation is not None:
            meeting.consensus_recommendation = meeting_data.consensus_recommendation
        if meeting_data.alternatives is not None:
            meeting.alternatives = json.dumps(meeting_data.alternatives)
        if meeting_data.risks is not None:
            meeting.risks = json.dumps(meeting_data.risks)
        if meeting_data.tradeoffs is not None:
            meeting.tradeoffs = json.dumps(meeting_data.tradeoffs)
        if meeting_data.confidence_score is not None:
            meeting.confidence_score = meeting_data.confidence_score
        if meeting_data.data_gaps is not None:
            meeting.data_gaps = json.dumps(meeting_data.data_gaps)
        if meeting_data.status is not None:
            meeting.status = meeting_data.status

        await self.session.commit()
        await self.session.refresh(meeting)
        
        return meeting

    async def get_recent(
        self,
        limit: int = 5,
        meeting_type: Optional[str] = None,
    ) -> list[BoardMeeting]:
        """Get recent meetings for context."""
        query = select(BoardMeeting).order_by(desc(BoardMeeting.created_at))
        
        if meeting_type:
            query = query.where(BoardMeeting.meeting_type == meeting_type)
        
        query = query.limit(limit)
        result = await self.session.execute(query)
        
        return list(result.scalars().all())

    async def get_by_keyword(
        self,
        keyword: str,
        limit: int = 10,
    ) -> list[BoardMeeting]:
        """Search meetings by keyword in question."""
        query = (
            select(BoardMeeting)
            .where(BoardMeeting.question.ilike(f"%{keyword}%"))
            .order_by(desc(BoardMeeting.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        
        return list(result.scalars().all())


async def get_meeting_memory(session: AsyncSession) -> MeetingMemory:
    """Get a meeting memory instance."""
    return MeetingMemory(session)
