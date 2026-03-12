"""Operating rhythm engine - main orchestration."""
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


class RhythmEngine:
    """Main operating rhythm engine."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def generate_daily_plan(
        self,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate a daily plan from strategic inputs."""
        
        from app.rhythm.daily_planner import get_daily_planner
        
        planner = await get_daily_planner(self.session)
        return await planner.generate_plan(target_date)
    
    async def generate_weekly_plan(
        self,
        week_start: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate a weekly plan."""
        
        from app.rhythm.weekly_planner import get_weekly_planner
        
        planner = await get_weekly_planner(self.session)
        return await planner.generate_plan(week_start)
    
    async def get_daily_plan(
        self,
        target_date: date,
    ) -> Optional[Dict[str, Any]]:
        """Get an existing daily plan."""
        
        from sqlalchemy import select
        from app.rhythm.rhythm_types import DailyPlan
        
        result = await self.session.execute(
            select(DailyPlan).where(DailyPlan.plan_date == target_date)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            return None
        
        return {
            "id": str(plan.id),
            "date": str(plan.plan_date),
            "status": plan.status,
            "priorities": plan.strategic_priorities,
            "tasks": plan.tasks,
            "focus_blocks": plan.focus_blocks,
            "completion_rate": plan.completion_rate,
            "strategic_alignment_score": plan.strategic_alignment_score,
        }
    
    async def get_weekly_plan(
        self,
        week_start: date,
    ) -> Optional[Dict[str, Any]]:
        """Get an existing weekly plan."""
        
        from sqlalchemy import select
        from app.rhythm.rhythm_types import WeeklyPlan
        
        result = await self.session.execute(
            select(WeeklyPlan).where(WeeklyPlan.week_start == week_start)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            return None
        
        return {
            "id": str(plan.id),
            "week_start": str(plan.week_start),
            "status": plan.status,
            "top_priorities": plan.top_priorities,
            "focus_themes": plan.focus_themes,
            "strategic_initiatives": plan.strategic_initiatives,
        }
    
    async def get_habits(
        self,
        category: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get habits."""
        
        from sqlalchemy import select
        from app.rhythm.rhythm_types import Habit
        
        query = select(Habit)
        
        if active_only:
            query = query.where(Habit.is_active == True)
        
        if category:
            query = query.where(Habit.category == category)
        
        result = await self.session.execute(query)
        habits = list(result.scalars().all())
        
        return [
            {
                "id": str(h.id),
                "name": h.name,
                "category": h.category,
                "frequency": h.frequency,
                "streak_count": h.streak_count,
                "completion_rate": h.completion_rate,
            }
            for h in habits
        ]
    
    async def complete_habit(
        self,
        habit_id: uuid.UUID,
        completion_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Mark a habit as completed."""
        
        from sqlalchemy import select
        from app.rhythm.rhythm_types import Habit, HabitCompletion
        
        # Get habit
        result = await self.session.execute(
            select(Habit).where(Habit.id == habit_id)
        )
        habit = result.scalar_one_or_none()
        
        if not habit:
            return {"error": "Habit not found"}
        
        # Create completion record
        completion = HabitCompletion(
            habit_id=habit_id,
            completed_date=completion_date or date.today(),
            completed_at=datetime.utcnow(),
        )
        self.session.add(completion)
        
        # Update streak
        habit.streak_count += 1
        habit.completion_rate = min(1.0, habit.completion_rate + 0.1)
        
        await self.session.commit()
        
        return {
            "habit_id": str(habit_id),
            "status": "completed",
            "new_streak": habit.streak_count,
        }
    
    async def create_habit(
        self,
        name: str,
        category: str = "productivity",
        frequency: str = "daily",
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new habit."""
        
        from app.rhythm.rhythm_types import Habit
        
        habit = Habit(
            name=name,
            category=category,
            frequency=frequency,
            description=description,
        )
        
        self.session.add(habit)
        await self.session.commit()
        await self.session.refresh(habit)
        
        return {
            "id": str(habit.id),
            "name": habit.name,
            "category": habit.category,
            "status": "created",
        }
    
    async def get_focus_blocks(
        self,
        target_date: date,
    ) -> List[Dict[str, Any]]:
        """Get focus blocks for a date."""
        
        from sqlalchemy import select
        from app.rhythm.rhythm_types import FocusBlock
        
        result = await self.session.execute(
            select(FocusBlock)
            .where(FocusBlock.date == target_date)
            .order_by(FocusBlock.start_time)
        )
        blocks = list(result.scalars().all())
        
        return [
            {
                "id": str(b.id),
                "title": b.title,
                "block_type": b.block_type,
                "start_time": str(b.start_time),
                "end_time": str(b.end_time),
                "is_completed": b.is_completed,
            }
            for b in blocks
        ]


async def get_rhythm_engine(session: AsyncSession) -> RhythmEngine:
    """Get rhythm engine instance."""
    return RhythmEngine(session)
