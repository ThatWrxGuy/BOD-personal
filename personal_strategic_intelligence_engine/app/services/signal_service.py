"""Signal service for retrieving and filtering signals."""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.core.logging import get_logger

logger = get_logger(__name__)


class SignalService:
    """Service for managing strategic signals."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_recent_signals(
        self,
        hours: int = 24,
        limit: int = 50,
    ) -> list[StrategicSignal]:
        """Get signals from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(StrategicSignal)
            .where(StrategicSignal.timestamp >= cutoff)
            .order_by(desc(StrategicSignal.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_signals_by_category(
        self,
        category: str,
        hours: Optional[int] = None,
        limit: int = 50,
    ) -> list[StrategicSignal]:
        """Get signals by category."""
        query = select(StrategicSignal).where(StrategicSignal.category == category)
        
        if hours:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            query = query.where(StrategicSignal.timestamp >= cutoff)
        
        query = query.order_by(desc(StrategicSignal.timestamp)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_high_urgency_signals(
        self,
        threshold: int = 7,
        hours: int = 24,
    ) -> list[StrategicSignal]:
        """Get high urgency signals."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(StrategicSignal)
            .where(
                and_(
                    StrategicSignal.urgency >= threshold,
                    StrategicSignal.timestamp >= cutoff,
                )
            )
            .order_by(desc(StrategicSignal.urgency), desc(StrategicSignal.timestamp))
        )
        return list(result.scalars().all())

    async def get_high_strength_signals(
        self,
        threshold: float = 7.0,
        hours: int = 24,
    ) -> list[StrategicSignal]:
        """Get high strength signals."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(StrategicSignal)
            .where(
                and_(
                    StrategicSignal.signal_strength >= threshold,
                    StrategicSignal.timestamp >= cutoff,
                )
            )
            .order_by(desc(StrategicSignal.signal_strength), desc(StrategicSignal.timestamp))
        )
        return list(result.scalars().all())

    async def rank_by_urgency(
        self,
        hours: int = 24,
        limit: int = 20,
    ) -> list[StrategicSignal]:
        """Rank signals by urgency score."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(StrategicSignal)
            .where(StrategicSignal.timestamp >= cutoff)
            .order_by(
                desc(StrategicSignal.urgency),
                desc(StrategicSignal.signal_strength),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def rank_by_strength(
        self,
        hours: int = 24,
        limit: int = 20,
    ) -> list[StrategicSignal]:
        """Rank signals by strength score."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(StrategicSignal)
            .where(StrategicSignal.timestamp >= cutoff)
            .order_by(
                desc(StrategicSignal.signal_strength),
                desc(StrategicSignal.urgency),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_signals_for_meeting(
        self,
        hours: int = 72,
        high_urgency_only: bool = False,
        limit: int = 30,
    ) -> dict:
        """Get signals formatted for board meeting context."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get all recent signals
        query = select(StrategicSignal).where(StrategicSignal.timestamp >= cutoff)
        
        if high_urgency_only:
            query = query.where(StrategicSignal.urgency >= 7)
        
        query = query.order_by(desc(StrategicSignal.urgency), desc(StrategicSignal.signal_strength)).limit(limit)
        result = await self.session.execute(query)
        signals = list(result.scalars().all())

        # Group by category
        by_category = {}
        for signal in signals:
            if signal.category not in by_category:
                by_category[signal.category] = []
            by_category[signal.category].append(signal)

        return {
            "signals": signals,
            "by_category": by_category,
            "count": len(signals),
            "time_window_hours": hours,
        }

    async def get_signal_summary(self, hours: int = 24) -> dict:
        """Get a summary of recent signals."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(StrategicSignal).where(StrategicSignal.timestamp >= cutoff)
        )
        signals = list(result.scalars().all())
        
        if not signals:
            return {
                "total": 0,
                "by_category": {},
                "avg_urgency": 0,
                "avg_strength": 0,
            }
        
        by_category = {}
        total_urgency = 0
        total_strength = 0
        
        for signal in signals:
            by_category[signal.category] = by_category.get(signal.category, 0) + 1
            total_urgency += signal.urgency
            total_strength += signal.signal_strength
        
        count = len(signals)
        
        return {
            "total": count,
            "by_category": by_category,
            "avg_urgency": total_urgency / count,
            "avg_strength": total_strength / count,
            "high_urgency_count": len([s for s in signals if s.urgency >= 7]),
            "high_strength_count": len([s for s in signals if s.signal_strength >= 7]),
        }


async def get_signal_service(session: AsyncSession) -> SignalService:
    """Get a signal service instance."""
    return SignalService(session)
