"""Goal Tracker for strategic goal management."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_goal import StrategicGoal, GoalStatus
from app.models.goal_progress import GoalProgress
from app.core.logging import get_logger

logger = get_logger(__name__)


class GoalTracker:
    """Tracks strategic goals and progress."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_goal(
        self,
        title: str,
        category: str,
        description: Optional[str] = None,
        priority: int = 5,
        target_value: Optional[float] = None,
        current_value: Optional[float] = None,
        unit: Optional[str] = None,
        target_date: Optional[datetime] = None,
    ) -> StrategicGoal:
        """Create a new strategic goal."""
        goal = StrategicGoal(
            title=title,
            description=description,
            category=category,
            priority=priority,
            target_value=target_value,
            current_value=current_value,
            unit=unit,
            target_date=target_date,
            status=GoalStatus.ACTIVE,
        )
        self.session.add(goal)
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def get_goal(self, goal_id: uuid.UUID) -> Optional[StrategicGoal]:
        """Get a goal by ID."""
        return await self.session.get(StrategicGoal, goal_id)

    async def list_goals(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list[StrategicGoal]:
        """List goals with optional filtering."""
        query = select(StrategicGoal).order_by(desc(StrategicGoal.priority))
        
        if status:
            query = query.where(StrategicGoal.status == status)
        if category:
            query = query.where(StrategicGoal.category == category)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_goals(self) -> list[StrategicGoal]:
        """Get all active goals."""
        result = await self.session.execute(
            select(StrategicGoal)
            .where(StrategicGoal.status == GoalStatus.ACTIVE)
            .order_by(desc(StrategicGoal.priority))
        )
        return list(result.scalars().all())

    async def update_goal_progress(
        self,
        goal_id: uuid.UUID,
        value: float,
        notes: Optional[str] = None,
    ) -> GoalProgress:
        """Record progress for a goal."""
        goal = await self.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        
        # Update goal current value
        goal.current_value = value
        
        # Create progress record
        progress = GoalProgress(
            goal_id=goal_id,
            recorded_value=value,
            recorded_at=datetime.utcnow(),
            notes=notes,
        )
        self.session.add(progress)
        await self.session.commit()
        await self.session.refresh(progress)
        
        return progress

    async def complete_goal(self, goal_id: uuid.UUID) -> None:
        """Mark a goal as completed."""
        goal = await self.get_goal(goal_id)
        if goal:
            goal.status = GoalStatus.COMPLETED
            await self.session.commit()

    async def abandon_goal(self, goal_id: uuid.UUID) -> None:
        """Mark a goal as abandoned."""
        goal = await self.get_goal(goal_id)
        if goal:
            goal.status = GoalStatus.ABANDONED
            await self.session.commit()

    async def get_goals_at_risk(self) -> list[StrategicGoal]:
        """Get goals that are at risk of missing targets."""
        now = datetime.utcnow()
        active_goals = await self.get_active_goals()
        
        at_risk = []
        for goal in active_goals:
            if not goal.target_value or not goal.current_value or not goal.target_date:
                continue
            
            # Check if target date is close
            days_until_target = (goal.target_date - now).days
            
            # Calculate expected progress
            total_days = (goal.target_date - now).days + 30  # Approximate
            if total_days <= 0:
                continue
                
            expected_progress = goal.target_value * (1 - days_until_target / total_days)
            actual_progress = goal.current_value
            deviation = abs(expected_progress - actual_progress)
            
            # At risk if: close to deadline and behind schedule
            if days_until_target <= 30 and deviation > goal.target_value * 0.2:
                at_risk.append(goal)
        
        return at_risk

    async def calculate_progress_percentage(self, goal_id: uuid.UUID) -> Optional[float]:
        """Calculate progress percentage for a goal."""
        goal = await self.get_goal(goal_id)
        if not goal or not goal.target_value or not goal.current_value:
            return None
        
        return min(100.0, (goal.current_value / goal.target_value) * 100)

    async def get_goal_progress_history(
        self,
        goal_id: uuid.UUID,
        limit: int = 30,
    ) -> list[GoalProgress]:
        """Get progress history for a goal."""
        result = await self.session.execute(
            select(GoalProgress)
            .where(GoalProgress.goal_id == goal_id)
            .order_by(desc(GoalProgress.recorded_at))
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_goal_tracker(session: AsyncSession) -> GoalTracker:
    """Get a goal tracker instance."""
    return GoalTracker(session)
