"""Data Seed Generator for realistic test data."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.models.strategic_goal import StrategicGoal, GoalCategory, GoalStatus
from app.models.strategic_plan import StrategicPlan, PlanStatus
from app.models.goal_progress import GoalProgress
from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.core.logging import get_logger

logger = get_logger(__name__)


class DataSeedGenerator:
    """Generates realistic seed data for simulations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_user_profile(self) -> UserProfile:
        """Seed a default user profile."""
        # Check if profile exists
        from sqlalchemy import select
        result = await self.session.execute(select(UserProfile).limit(1))
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        profile = UserProfile(
            name="Simulated User",
            email="simulated@example.com",
            values="Growth, Health, Financial Security, Legacy",
            goals="Build sustainable wealth, Maintain health, Create impact",
            constraints="Time-limited, Budget-conscious",
            preferences="Data-driven decisions, Regular reviews",
        )
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        return profile

    async def seed_goals(self, goals_config: list) -> list[StrategicGoal]:
        """Seed goals from configuration."""
        goals = []
        
        for config in goals_config:
            goal = StrategicGoal(
                title=config.get("title"),
                description=f"Simulated goal: {config.get('title')}",
                category=config.get("category", GoalCategory.OTHER),
                priority=config.get("priority", 5),
                target_value=config.get("target_value"),
                current_value=config.get("current_value", 0),
                target_date=config.get("target_date"),
                status=GoalStatus.ACTIVE,
            )
            self.session.add(goal)
            goals.append(goal)
        
        await self.session.commit()
        
        for goal in goals:
            await self.session.refresh(goal)
        
        return goals

    async def seed_plans(self, goal: StrategicGoal, plan_config: dict) -> StrategicPlan:
        """Seed a plan for a goal."""
        plan = StrategicPlan(
            title=plan_config.get("title", f"Plan for {goal.title}"),
            description=plan_config.get("description"),
            goal_id=goal.id,
            start_date=datetime.utcnow(),
            end_date=goal.target_date,
            status=PlanStatus.ACTIVE,
            metadata=plan_config.get("metadata", {}),
        )
        
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        
        return plan

    async def seed_goal_progress(
        self,
        goal: StrategicGoal,
        start_value: float,
        current_value: float,
        days_back: int,
    ) -> list[GoalProgress]:
        """Seed goal progress history."""
        progress_records = []
        
        start_date = datetime.utcnow() - timedelta(days=days_back)
        days_span = days_back
        
        if days_span > 0:
            daily_increase = (current_value - start_value) / days_span
            
            for i in range(days_span):
                record_date = start_date + timedelta(days=i)
                record_value = min(goal.target_value or 100, start_value + (daily_increase * (i + 1)))
                
                progress = GoalProgress(
                    goal_id=goal.id,
                    recorded_value=record_value,
                    recorded_at=record_date,
                    notes=f"Day {i+1} progress",
                )
                self.session.add(progress)
                progress_records.append(progress)
        
        await self.session.commit()
        
        return progress_records

    async def seed_signals(self, signals_config: list) -> list[StrategicSignal]:
        """Seed signals from configuration."""
        signals = []
        
        for config in signals_config:
            day = config.get("day", 1)
            signal_date = datetime.utcnow() - timedelta(days=14 - day)
            
            signal = StrategicSignal(
                title=config.get("title"),
                description=f"Simulated signal: {config.get('title')}",
                category=config.get("category", SignalCategory.OTHER),
                urgency=config.get("urgency", 5),
                signal_strength=config.get("signal_strength", 5),
                source="simulation",
                timestamp=signal_date,
                metadata=config.get("metadata", {}),
            )
            self.session.add(signal)
            signals.append(signal)
        
        await self.session.commit()
        
        for signal in signals:
            await self.session.refresh(signal)
        
        return signals

    async def seed_board_schedules(self) -> None:
        """Seed default board schedules."""
        from app.models.board_schedule import BoardSchedule, MeetingType
        from sqlalchemy import select
        
        # Check if schedules exist
        result = await self.session.execute(select(BoardSchedule).limit(1))
        if result.scalar_one_or_none():
            return
        
        schedules = [
            {"type": MeetingType.DAILY, "frequency": "every day"},
            {"type": MeetingType.WEEKLY, "frequency": "every monday"},
            {"type": MeetingType.MONTHLY, "frequency": "first of month"},
            {"type": MeetingType.QUARTERLY, "frequency": "first of quarter"},
            {"type": MeetingType.ANNUAL, "frequency": "january 1st"},
        ]
        
        for config in schedules:
            schedule = BoardSchedule(
                meeting_type=config["type"],
                frequency=config["frequency"],
                is_active=True,
                next_run=datetime.utcnow() + timedelta(days=1),
            )
            self.session.add(schedule)
        
        await self.session.commit()

    async def seed_all(self, scenario: dict) -> dict:
        """Seed all data for a simulation."""
        logger.info("Starting data seed...")
        
        # Seed profile
        profile = await self.seed_user_profile()
        
        # Seed goals
        goals_config = scenario.get("goals", [])
        goals = await self.seed_goals(goals_config)
        
        # Seed some progress for each goal
        for i, goal in enumerate(goals):
            if goal.target_value and goal.current_value:
                days_back = min(30, (datetime.utcnow() - (goal.target_date - timedelta(days=90))).days)
                await self.seed_goal_progress(goal, 0, goal.current_value, days_back)
        
        # Seed signals
        signals_config = scenario.get("signals", [])
        signals = await self.seed_signals(signals_config)
        
        # Seed schedules
        await self.seed_board_schedules()
        
        logger.info(f"Seed complete: {len(goals)} goals, {len(signals)} signals")
        
        return {
            "profile": profile,
            "goals": goals,
            "signals": signals,
        }


async def get_data_seed_generator(session: AsyncSession) -> DataSeedGenerator:
    """Get a data seed generator instance."""
    return DataSeedGenerator(session)
