"""Memory layer for decision storage and retrieval."""
import json
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_record import DecisionRecord
from app.models.outcome_review import OutcomeReview
from app.schemas.decisions import DecisionCreate, DecisionUpdate
from app.schemas.reviews import OutcomeReviewCreate, OutcomeReviewUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class DecisionMemory:
    """Persistent storage for decision records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, decision_data: DecisionCreate) -> DecisionRecord:
        """Create a new decision record."""
        decision = DecisionRecord(
            meeting_id=decision_data.meeting_id,
            decision_summary=decision_data.decision_summary,
            chosen_action=decision_data.chosen_action,
            rationale=decision_data.rationale,
            status=decision_data.status,
            review_due_at=decision_data.review_due_at,
        )
        
        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        
        return decision

    async def get(self, decision_id: int) -> Optional[DecisionRecord]:
        """Get a decision by ID."""
        result = await self.session.execute(
            select(DecisionRecord).where(DecisionRecord.id == decision_id)
        )
        decision = result.scalars().first()
        
        if decision:
            await self.session.refresh(decision, ["outcome_reviews"])
        
        return decision

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> Tuple[List[DecisionRecord], int]:
        """List decisions with pagination."""
        query = select(DecisionRecord).order_by(desc(DecisionRecord.created_at))
        
        if status:
            query = query.where(DecisionRecord.status == status)
        
        # Get total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        decisions = result.scalars().all()
        
        return list(decisions), total

    async def update(
        self,
        decision_id: int,
        decision_data: DecisionUpdate,
    ) -> Optional[DecisionRecord]:
        """Update a decision."""
        result = await self.session.execute(
            select(DecisionRecord).where(DecisionRecord.id == decision_id)
        )
        decision = result.scalars().first()
        
        if not decision:
            return None

        if decision_data.decision_summary is not None:
            decision.decision_summary = decision_data.decision_summary
        if decision_data.chosen_action is not None:
            decision.chosen_action = decision_data.chosen_action
        if decision_data.rationale is not None:
            decision.rationale = decision_data.rationale
        if decision_data.status is not None:
            decision.status = decision_data.status
        if decision_data.review_due_at is not None:
            decision.review_due_at = decision_data.review_due_at

        await self.session.commit()
        await self.session.refresh(decision)
        
        return decision

    async def get_by_meeting(self, meeting_id: int) -> List[DecisionRecord]:
        """Get decisions linked to a meeting."""
        result = await self.session.execute(
            select(DecisionRecord)
            .where(DecisionRecord.meeting_id == meeting_id)
            .order_by(desc(DecisionRecord.created_at))
        )
        return list(result.scalars().all())

    async def get_pending_reviews(self) -> List[DecisionRecord]:
        """Get decisions pending review."""
        from datetime import datetime
        result = await self.session.execute(
            select(DecisionRecord)
            .where(
                and_(
                    DecisionRecord.status == "decided",
                    DecisionRecord.review_due_at != None,
                    DecisionRecord.review_due_at <= datetime.utcnow()
                )
            )
            .order_by(DecisionRecord.review_due_at)
        )
        return list(result.scalars().all())


class ReviewMemory:
    """Persistent storage for outcome reviews."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, review_data: OutcomeReviewCreate) -> OutcomeReview:
        """Create a new outcome review."""
        review = OutcomeReview(
            decision_id=review_data.decision_id,
            actual_result=review_data.actual_result,
            success_score=review_data.success_score,
            notes=review_data.notes,
            reviewed_at=review_data.reviewed_at or datetime.utcnow(),
        )
        
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        
        # Update decision status
        decision = await self.session.get(DecisionRecord, review_data.decision_id)
        if decision:
            decision.status = "reviewed"
        
        await self.session.commit()
        
        return review

    async def get(self, review_id: int) -> Optional[OutcomeReview]:
        """Get a review by ID."""
        result = await self.session.execute(
            select(OutcomeReview).where(OutcomeReview.id == review_id)
        )
        return result.scalars().first()

    async def list(
        self,
        decision_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[OutcomeReview], int]:
        """List reviews with optional filtering."""
        query = select(OutcomeReview).order_by(desc(OutcomeReview.created_at))
        
        if decision_id:
            query = query.where(OutcomeReview.decision_id == decision_id)
        
        # Get total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        reviews = result.scalars().all()
        
        return list(reviews), total


async def get_decision_memory(session: AsyncSession) -> DecisionMemory:
    """Get a decision memory instance."""
    return DecisionMemory(session)


async def get_review_memory(session: AsyncSession) -> ReviewMemory:
    """Get a review memory instance."""
    return ReviewMemory(session)
