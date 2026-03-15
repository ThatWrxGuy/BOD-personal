"""Board Scheduler for autonomous governance scheduling."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_schedule import BoardSchedule, MeetingType
from app.core.logging import get_logger

logger = get_logger(__name__)


class BoardScheduler:
    """Manages automatic scheduling of board meetings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def initialize_default_schedules(self) -> None:
        """Initialize default governance schedules if they don't exist."""
        schedules_config = [
            {
                "meeting_type": MeetingType.DAILY,
                "frequency": "every day",
                "description": "Daily Tactical Review",
            },
            {
                "meeting_type": MeetingType.WEEKLY,
                "frequency": "every monday",
                "description": "Weekly Strategic Review",
            },
            {
                "meeting_type": MeetingType.MONTHLY,
                "frequency": "first of month",
                "description": "Monthly Capital Allocation Review",
            },
            {
                "meeting_type": MeetingType.QUARTERLY,
                "frequency": "first of quarter",
                "description": "Quarterly Strategic Planning Session",
            },
            {
                "meeting_type": MeetingType.ANNUAL,
                "frequency": "january 1st",
                "description": "Annual Strategic Review",
            },
        ]

        for config in schedules_config:
            existing = await self.session.execute(
                select(BoardSchedule).where(
                    BoardSchedule.meeting_type == config["meeting_type"]
                )
            )
            if not existing.scalar_one_or_none():
                next_run = self._calculate_next_run(config["meeting_type"])
                schedule = BoardSchedule(
                    meeting_type=config["meeting_type"],
                    frequency=config["frequency"],
                    is_active=True,
                    next_run=next_run,
                )
                self.session.add(schedule)

        await self.session.commit()
        logger.info("Initialized default board schedules")

    def _calculate_next_run(self, meeting_type: str) -> datetime:
        """Calculate the next run time for a meeting type."""
        now = datetime.utcnow()
        
        if meeting_type == MeetingType.DAILY:
            return now + timedelta(days=1)
        elif meeting_type == MeetingType.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            return now + timedelta(days=days_until_mondary)
        elif meeting_type == MeetingType.MONTHLY:
            # First of next month
            if now.day == 1:
                return (now.replace(day=28) + timedelta(days=4)).replace(day=1)
            return now.replace(day=1, month=now.month + 1 if now.month < 12 else 1)
        elif meeting_type == MeetingType.QUARTERLY:
            quarter_end_month = ((now.month - 1) // 3 + 1) * 3
            if now.month <= quarter_end_month:
                return now.replace(month=quarter_end_month, day=1)
            return now.replace(month=quarter_end_month + 3 if quarter_end_month < 9 else 1, year=now.year + 1 if quarter_end_month == 12 else now.year)
        elif meeting_type == MeetingType.ANNUAL:
            return now.replace(month=1, day=1, year=now.year + 1)
        
        return now + timedelta(days=1)

    async def get_due_schedules(self) -> list[BoardSchedule]:
        """Get all schedules that are due to run."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(BoardSchedule).where(
                and_(
                    BoardSchedule.is_active == True,
                    BoardSchedule.next_run <= now,
                )
            )
        )
        return list(result.scalars().all())

    async def update_schedule_after_run(self, schedule_id: uuid.UUID) -> None:
        """Update schedule after a meeting has run."""
        result = await self.session.get(BoardSchedule, schedule_id)
        if result:
            result.last_run = datetime.utcnow()
            result.next_run = self._calculate_next_run(result.meeting_type)
            await self.session.commit()

    async def get_active_schedules(self) -> list[BoardSchedule]:
        """Get all active schedules."""
        result = await self.session.execute(
            select(BoardSchedule).where(BoardSchedule.is_active == True)
        )
        return list(result.scalars().all())

    async def pause_schedule(self, schedule_id: uuid.UUID) -> None:
        """Pause a schedule."""
        result = await self.session.get(BoardSchedule, schedule_id)
        if result:
            result.is_active = False
            await self.session.commit()

    async def resume_schedule(self, schedule_id: uuid.UUID) -> None:
        """Resume a paused schedule."""
        result = await self.session.get(BoardSchedule, schedule_id)
        if result:
            result.is_active = True
            result.next_run = self._calculate_next_run(result.meeting_type)
            await self.session.commit()


async def get_board_scheduler(session: AsyncSession) -> BoardScheduler:
    """Get a board scheduler instance."""
    return BoardScheduler(session)
