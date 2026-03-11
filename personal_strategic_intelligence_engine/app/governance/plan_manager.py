"""Plan Manager for strategic plan management."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_plan import StrategicPlan, PlanStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class PlanManager:
    """Manages strategic plans and their execution."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_plan(
        self,
        title: str,
        description: Optional[str] = None,
        goal_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Optional[dict] = None,
    ) -> StrategicPlan:
        """Create a new strategic plan."""
        plan = StrategicPlan(
            title=title,
            description=description,
            goal_id=goal_id,
            start_date=start_date,
            end_date=end_date,
            status=PlanStatus.ACTIVE,
            metadata=metadata,
        )
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_plan(self, plan_id: uuid.UUID) -> Optional[StrategicPlan]:
        """Get a plan by ID."""
        return await self.session.get(StrategicPlan, plan_id)

    async def list_plans(
        self,
        status: Optional[str] = None,
        goal_id: Optional[uuid.UUID] = None,
    ) -> list[StrategicPlan]:
        """List plans with optional filtering."""
        query = select(StrategicPlan).order_by(desc(StrategicPlan.created_at))
        
        if status:
            query = query.where(StrategicPlan.status == status)
        if goal_id:
            query = query.where(StrategicPlan.goal_id == goal_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_plans(self) -> list[StrategicPlan]:
        """Get all active plans."""
        result = await self.session.execute(
            select(StrategicPlan)
            .where(StrategicPlan.status == PlanStatus.ACTIVE)
            .order_by(desc(StrategicPlan.created_at))
        )
        return list(result.scalars().all())

    async def get_plans_for_goal(self, goal_id: uuid.UUID) -> list[StrategicPlan]:
        """Get all plans associated with a goal."""
        result = await self.session.execute(
            select(StrategicPlan)
            .where(StrategicPlan.goal_id == goal_id)
            .order_by(desc(StrategicPlan.created_at))
        )
        return list(result.scalars().all())

    async def update_plan(
        self,
        plan_id: uuid.UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[StrategicPlan]:
        """Update a plan."""
        plan = await self.get_plan(plan_id)
        if not plan:
            return None
        
        if title:
            plan.title = title
        if description:
            plan.description = description
        if status:
            plan.status = status
        
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def pause_plan(self, plan_id: uuid.UUID) -> None:
        """Pause a plan."""
        plan = await self.get_plan(plan_id)
        if plan:
            plan.status = PlanStatus.PAUSED
            await self.session.commit()

    async def resume_plan(self, plan_id: uuid.UUID) -> None:
        """Resume a paused plan."""
        plan = await self.get_plan(plan_id)
        if plan and plan.status == PlanStatus.PAUSED:
            plan.status = PlanStatus.ACTIVE
            await self.session.commit()

    async def complete_plan(self, plan_id: uuid.UUID) -> None:
        """Mark a plan as completed."""
        plan = await self.get_plan(plan_id)
        if plan:
            plan.status = PlanStatus.COMPLETED
            await self.session.commit()

    async def get_overdue_plans(self) -> list[StrategicPlan]:
        """Get plans that have passed their end date but are still active."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(StrategicPlan).where(
                StrategicPlan.status == PlanStatus.ACTIVE,
                StrategicPlan.end_date < now,
            )
        )
        return list(result.scalars().all())

    async def get_upcoming_milestones(self, days: int = 30) -> list[dict]:
        """Get upcoming plan milestones within specified days."""
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        
        result = await self.session.execute(
            select(StrategicPlan).where(
                StrategicPlan.status == PlanStatus.ACTIVE,
                StrategicPlan.end_date >= now,
                StrategicPlan.end_date <= future,
            )
        )
        plans = list(result.scalars().all())
        
        milestones = []
        for plan in plans:
            milestones.append({
                "plan_id": plan.id,
                "title": plan.title,
                "end_date": plan.end_date,
                "goal_id": plan.goal_id,
            })
        
        return sorted(milestones, key=lambda x: x["end_date"])


from datetime import timedelta


async def get_plan_manager(session: AsyncSession) -> PlanManager:
    """Get a plan manager instance."""
    return PlanManager(session)
