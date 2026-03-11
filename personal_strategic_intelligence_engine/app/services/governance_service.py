"""Governance Service for high-level governance operations."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.governance.board_scheduler import BoardScheduler
from app.governance.trigger_engine import TriggerEngine
from app.governance.goal_tracker import GoalTracker
from app.governance.plan_manager import PlanManager
from app.governance.review_engine import ReviewEngine, ReviewReport
from app.core.logging import get_logger

logger = get_logger(__name__)


class GovernanceService:
    """High-level service coordinating all governance operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.scheduler = BoardScheduler(session)
        self.trigger_engine = TriggerEngine(session)
        self.goal_tracker = GoalTracker(session)
        self.plan_manager = PlanManager(session)
        self.review_engine = ReviewEngine(session)

    # ========== Scheduler Operations ==========

    async def initialize_governance(self) -> None:
        """Initialize governance system with default schedules."""
        await self.scheduler.initialize_default_schedules()
        logger.info("Governance system initialized")

    async def get_due_meetings(self) -> list:
        """Get meetings that are due to run."""
        return await self.scheduler.get_due_schedules()

    async def trigger_scheduled_meeting(self, schedule_id: uuid.UUID) -> dict:
        """Trigger a scheduled meeting."""
        schedule = await self.session.get("BoardSchedule", schedule_id)
        # Return meeting trigger info
        return {
            "meeting_type": schedule.meeting_type if schedule else None,
            "triggered_at": datetime.utcnow().isoformat(),
        }

    # ========== Trigger Operations ==========

    async def check_and_trigger_events(self) -> list:
        """Check signals and create trigger events."""
        return await self.trigger_engine.check_signals()

    async def get_pending_events(self, min_severity: str = "LOW") -> list:
        """Get pending trigger events."""
        return await self.trigger_engine.get_pending_triggers(min_severity)

    async def resolve_event(self, event_id: uuid.UUID) -> None:
        """Resolve a trigger event."""
        await self.trigger_engine.resolve_trigger(event_id)

    # ========== Goal Operations ==========

    async def create_goal(self, **kwargs) -> dict:
        """Create a new goal."""
        goal = await self.goal_tracker.create_goal(**kwargs)
        return {"id": str(goal.id), "title": goal.title, "status": goal.status}

    async def get_goals(self, status: Optional[str] = None, category: Optional[str] = None) -> list:
        """Get goals with optional filtering."""
        goals = await self.goal_tracker.list_goals(status=status, category=category)
        return [
            {
                "id": str(g.id),
                "title": g.title,
                "category": g.category,
                "priority": g.priority,
                "status": g.status,
                "target_value": g.target_value,
                "current_value": g.current_value,
                "progress_pct": await self.goal_tracker.calculate_progress_percentage(g.id),
            }
            for g in goals
        ]

    async def update_goal_progress(self, goal_id: uuid.UUID, value: float, notes: Optional[str] = None) -> dict:
        """Update progress for a goal."""
        progress = await self.goal_tracker.update_goal_progress(goal_id, value, notes)
        return {"id": str(progress.id), "recorded_value": progress.recorded_value}

    async def complete_goal(self, goal_id: uuid.UUID) -> None:
        """Mark a goal as completed."""
        await self.goal_tracker.complete_goal(goal_id)

    async def abandon_goal(self, goal_id: uuid.UUID) -> None:
        """Mark a goal as abandoned."""
        await self.goal_tracker.abandon_goal(goal_id)

    async def get_goals_at_risk(self) -> list:
        """Get goals at risk."""
        goals = await self.goal_tracker.get_goals_at_risk()
        return [{"id": str(g.id), "title": g.title, "target_date": g.target_date} for g in goals]

    # ========== Plan Operations ==========

    async def create_plan(self, **kwargs) -> dict:
        """Create a new plan."""
        plan = await self.plan_manager.create_plan(**kwargs)
        return {"id": str(plan.id), "title": plan.title, "status": plan.status}

    async def get_plans(self, status: Optional[str] = None, goal_id: Optional[uuid.UUID] = None) -> list:
        """Get plans with optional filtering."""
        plans = await self.plan_manager.list_plans(status=status, goal_id=goal_id)
        return [
            {
                "id": str(p.id),
                "title": p.title,
                "goal_id": str(p.goal_id) if p.goal_id else None,
                "status": p.status,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "end_date": p.end_date.isoformat() if p.end_date else None,
            }
            for p in plans
        ]

    async def complete_plan(self, plan_id: uuid.UUID) -> None:
        """Mark a plan as completed."""
        await self.plan_manager.complete_plan(plan_id)

    async def pause_plan(self, plan_id: uuid.UUID) -> None:
        """Pause a plan."""
        await self.plan_manager.pause_plan(plan_id)

    # ========== Review Operations ==========

    async def run_review(self, review_type: str) -> dict:
        """Run a governance review."""
        if review_type == "DAILY":
            report = await self.review_engine.run_daily_review()
        elif review_type == "WEEKLY":
            report = await self.review_engine.run_weekly_review()
        elif review_type == "MONTHLY":
            report = await self.review_engine.run_monthly_review()
        elif review_type == "QUARTERLY":
            report = await self.review_engine.run_quarterly_review()
        elif review_type == "ANNUAL":
            report = await self.review_engine.run_annual_review()
        else:
            raise ValueError(f"Unknown review type: {review_type}")
        
        return report.to_dict()

    # ========== Dashboard ==========

    async def get_governance_dashboard(self) -> dict:
        """Get governance dashboard summary."""
        active_goals = await self.goal_tracker.get_active_goals()
        active_plans = await self.plan_manager.get_active_plans()
        at_risk_goals = await self.goal_tracker.get_goals_at_risk()
        pending_triggers = await self.trigger_engine.get_pending_triggers()
        due_schedules = await self.scheduler.get_due_schedules()

        return {
            "active_goals": len(active_goals),
            "active_plans": len(active_plans),
            "goals_at_risk": len(at_risk_goals),
            "pending_triggers": len(pending_triggers),
            "due_schedules": len(due_schedules),
            "goals": [
                {
                    "id": str(g.id),
                    "title": g.title,
                    "category": g.category,
                    "priority": g.priority,
                    "progress_pct": await self.goal_tracker.calculate_progress_percentage(g.id),
                }
                for g in active_goals[:5]
            ],
        }


async def get_governance_service(session: AsyncSession) -> GovernanceService:
    """Get a governance service instance."""
    return GovernanceService(session)
