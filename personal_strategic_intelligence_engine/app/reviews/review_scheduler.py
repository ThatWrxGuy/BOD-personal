"""Strategic review scheduler."""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import StrategicReview
from app.reviews.review_types import (
    ReviewType,
    ReviewStatus,
    REVIEW_TYPE_CONFIG,
    ReviewFrequency,
)
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReviewScheduler:
    """Schedules and manages strategic reviews."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def schedule_review(
        self,
        review_type: str,
        scheduled_at: Optional[datetime] = None,
    ) -> StrategicReview:
        """Schedule a strategic review."""
        
        config = REVIEW_TYPE_CONFIG.get(review_type)
        if not config:
            raise ValueError(f"Unknown review type: {review_type}")
        
        # Default scheduling
        if not scheduled_at:
            scheduled_at = self._calculate_next_run(review_type)
        
        review = StrategicReview(
            review_type=review_type,
            status=ReviewStatus.PENDING,
            scheduled_at=scheduled_at,
            domains_analyzed=config.get("domains", []),
            agents_involved=config.get("agents", []),
        )
        
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        
        logger.info(f"Scheduled {review_type} review for {scheduled_at}")
        
        return review
    
    def _calculate_next_run(self, review_type: str) -> datetime:
        """Calculate the next run time for a review type."""
        
        config = REVIEW_TYPE_CONFIG.get(review_type)
        frequency = config.get("frequency", ReviewFrequency.ON_DEMAND) if config else ReviewFrequency.ON_DEMAND
        
        now = datetime.utcnow()
        
        if frequency == ReviewFrequency.WEEKLY:
            # Run on Sunday
            days_until_sunday = (6 - now.weekday()) % 7
            if days_until_sunday == 0:
                days_until_sunday = 7
            return now + timedelta(days=days_until_sunday)
        
        elif frequency == ReviewFrequency.MONTHLY:
            # Run on first day of month
            if now.day == 1:
                return datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
            return datetime(now.year, now.month, 1) + timedelta(days=32)
        
        elif frequency == ReviewFrequency.QUARTERLY:
            # Run on first day of quarter
            quarter_month = ((now.month - 1) // 3) * 3 + 1
            if now.month == quarter_month and now.day == 1:
                quarter_month += 3
            return datetime(now.year, quarter_month, 1)
        
        # Default: run in 1 hour
        return now + timedelta(hours=1)
    
    async def get_pending_reviews(self) -> list[StrategicReview]:
        """Get all pending reviews that are due."""
        
        from sqlalchemy import select, and_
        
        now = datetime.utcnow()
        
        result = await self.session.execute(
            select(StrategicReview)
            .where(
                and_(
                    StrategicReview.status == ReviewStatus.PENDING,
                    StrategicReview.scheduled_at <= now,
                )
            )
            .order_by(StrategicReview.scheduled_at)
        )
        
        return list(result.scalars().all())
    
    async def start_review(self, review_id: uuid.UUID) -> StrategicReview:
        """Mark a review as started."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicReview).where(StrategicReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise ValueError(f"Review not found: {review_id}")
        
        review.status = ReviewStatus.RUNNING
        review.started_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(review)
        
        # Publish event
        event_bus = get_event_bus(self.session)
        await event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_STARTED,
                payload={
                    "review_id": str(review_id),
                    "review_type": review.review_type,
                },
                source_module="review_scheduler",
                workflow_id=review.workflow_id,
            )
        )
        
        return review
    
    async def complete_review(
        self,
        review_id: uuid.UUID,
        summary: str,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> StrategicReview:
        """Mark a review as completed."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicReview).where(StrategicReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise ValueError(f"Review not found: {review_id}")
        
        review.status = ReviewStatus.COMPLETED
        review.completed_at = datetime.utcnow()
        review.summary = summary
        review.metrics_snapshot = metrics
        
        await self.session.commit()
        await self.session.refresh(review)
        
        # Publish event
        event_bus = get_event_bus(self.session)
        await event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={
                    "review_id": str(review_id),
                    "review_type": review.review_type,
                    "summary": summary,
                },
                source_module="review_scheduler",
                workflow_id=review.workflow_id,
            )
        )
        
        return review
    
    async def fail_review(
        self,
        review_id: uuid.UUID,
        error_message: str,
    ) -> StrategicReview:
        """Mark a review as failed."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicReview).where(StrategicReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise ValueError(f"Review not found: {review_id}")
        
        review.status = ReviewStatus.FAILED
        review.completed_at = datetime.utcnow()
        review.error_message = error_message
        
        await self.session.commit()
        await self.session.refresh(review)
        
        return review
    
    async def get_review_schedule(self) -> Dict[str, datetime]:
        """Get upcoming review schedule."""
        
        schedule = {}
        
        for review_type in ReviewType:
            config = REVIEW_TYPE_CONFIG.get(review_type)
            if config:
                next_run = self._calculate_next_run(review_type)
                schedule[review_type.value] = next_run.isoformat()
        
        return schedule


async def get_review_scheduler(session: AsyncSession) -> ReviewScheduler:
    """Get review scheduler instance."""
    return ReviewScheduler(session)
