"""Rhythm data models."""
import uuid
from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import DateTime, String, Float, ForeignKey, Time, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DailyPlan(Base, TimestampMixin):
    """Daily plan record."""

    __tablename__ = "rhythm_daily_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    plan_date: Mapped[date] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    strategic_priorities: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    tasks: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    focus_blocks: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    strategic_alignment_score: Mapped[float] = mapped_column(Float, default=0.0)
    reflection_notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class WeeklyPlan(Base, TimestampMixin):
    """Weekly plan record."""

    __tablename__ = "rhythm_weekly_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    week_start: Mapped[date] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    top_priorities: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    focus_themes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    strategic_initiatives: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    risk_monitoring: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    week_summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class Habit(Base, TimestampMixin):
    """Habit record."""

    __tablename__ = "rhythm_habits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(20), default="productivity")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    frequency: Mapped[str] = mapped_column(String(20), default="daily")
    preferred_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    streak_count: Mapped[int] = mapped_column(default=0)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    target_streak: Mapped[Optional[int]] = mapped_column(default=30)


class HabitCompletion(Base, TimestampMixin):
    """Habit completion record."""

    __tablename__ = "rhythm_habit_completions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rhythm_habits.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    completed_date: Mapped[date] = mapped_column(nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class FocusBlock(Base, TimestampMixin):
    """Focus block record."""

    __tablename__ = "rhythm_focus_blocks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    date: Mapped[date] = mapped_column(nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    block_type: Mapped[str] = mapped_column(String(20), default="deep_work")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linked_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    strategic_priority: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class EnergyPattern(Base, TimestampMixin):
    """Energy pattern record."""

    __tablename__ = "rhythm_energy_patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    day_of_week: Mapped[int] = mapped_column(default=0)
    time_of_day: Mapped[time] = mapped_column(Time, nullable=False)
    energy_level: Mapped[float] = mapped_column(Float, default=0.5)
    is_peak: Mapped[bool] = mapped_column(Boolean, default=False)
    is_low: Mapped[bool] = mapped_column(Boolean, default=False)
