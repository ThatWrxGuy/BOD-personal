"""Operating rhythm API routes."""
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.rhythm.rhythm_engine import get_rhythm_engine

router = APIRouter(prefix="/rhythm", tags=["rhythm"])


@router.post("/generate-daily")
async def generate_daily_plan(
    target_date: Optional[str] = Query(None, description="Target date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_db),
):
    """Generate a daily plan."""
    
    engine = await get_rhythm_engine(session)
    
    target = None
    if target_date:
        target = date.fromisoformat(target_date)
    
    plan = await engine.generate_daily_plan(target)
    
    return plan


@router.get("/daily-plan")
async def get_daily_plan(
    target_date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_db),
):
    """Get a daily plan."""
    
    engine = await get_rhythm_engine(session)
    
    target = date.fromisoformat(target_date)
    plan = await engine.get_daily_plan(target)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    
    return plan


@router.post("/generate-weekly")
async def generate_weekly_plan(
    week_start: Optional[str] = Query(None, description="Week start date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_db),
):
    """Generate a weekly plan."""
    
    engine = await get_rhythm_engine(session)
    
    week = None
    if week_start:
        week = date.fromisoformat(week_start)
    
    plan = await engine.generate_weekly_plan(week)
    
    return plan


@router.get("/weekly-plan")
async def get_weekly_plan(
    week_start: str = Query(..., description="Week start date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_db),
):
    """Get a weekly plan."""
    
    engine = await get_rhythm_engine(session)
    
    week = date.fromisoformat(week_start)
    plan = await engine.get_weekly_plan(week)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")
    
    return plan


@router.get("/habits")
async def list_habits(
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    session: AsyncSession = Depends(get_db),
):
    """List habits."""
    
    engine = await get_rhythm_engine(session)
    habits = await engine.get_habits(category, active_only)
    
    return {"habits": habits}


@router.post("/habits")
async def create_habit(
    name: str = Query(...),
    category: str = Query("productivity"),
    frequency: str = Query("daily"),
    description: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """Create a new habit."""
    
    engine = await get_rhythm_engine(session)
    habit = await engine.create_habit(name, category, frequency, description)
    
    return habit


@router.post("/habits/{habit_id}/complete")
async def complete_habit(
    habit_id: uuid.UUID,
    completion_date: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """Mark a habit as completed."""
    
    engine = await get_rhythm_engine(session)
    
    completed = None
    if completion_date:
        completed = date.fromisoformat(completion_date)
    
    result = await engine.complete_habit(habit_id, completed)
    
    return result


@router.get("/focus-blocks")
async def get_focus_blocks(
    target_date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_db),
):
    """Get focus blocks for a date."""
    
    engine = await get_rhythm_engine(session)
    
    target = date.fromisoformat(target_date)
    blocks = await engine.get_focus_blocks(target)
    
    return {"focus_blocks": blocks}


@router.get("/monthly-summary")
async def get_monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    session: AsyncSession = Depends(get_db),
):
    """Get monthly summary."""
    
    import calendar
    
    if not year:
        year = date.today().year
    if not month:
        month = date.today().month
    
    # Get first and last day of month
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Get daily plans for the month
    engine = await get_rhythm_engine(session)
    
    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "first_day": str(first_day),
        "last_day": str(last_day),
        "summary": "Monthly summary placeholder",
    }
