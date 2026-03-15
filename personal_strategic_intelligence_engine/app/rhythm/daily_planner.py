"""Daily planner for generating daily operating plans."""
from datetime import date, time
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class DailyPlanner:
    """Generate daily plans from strategic inputs."""
    
    def __init__(self, session):
        self.session = session
    
    async def generate_plan(
        self,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate a daily plan."""
        
        target_date = target_date or date.today()
        
        # Gather inputs from strategic systems
        priorities = await self._gather_priorities()
        risks = await self._gather_risks()
        opportunities = await self._gather_opportunities()
        habits = await self._gather_habits()
        
        # Build strategic priorities
        strategic_priorities = self._build_priorities(priorities, risks, opportunities)
        
        # Build tasks
        tasks = self._build_tasks(priorities, opportunities)
        
        # Build focus blocks
        focus_blocks = await self._build_focus_blocks(target_date)
        
        # Create plan
        from app.rhythm.rhythm_types import DailyPlan
        
        plan = DailyPlan(
            plan_date=target_date,
            status="generated",
            strategic_priorities=strategic_priorities,
            tasks=tasks,
            focus_blocks=focus_blocks,
            strategic_alignment_score=0.85,
        )
        
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        
        return {
            "id": str(plan.id),
            "date": str(plan.plan_date),
            "status": plan.status,
            "strategic_priorities": plan.strategic_priorities,
            "tasks": plan.tasks,
            "focus_blocks": plan.focus_blocks,
            "strategic_alignment_score": plan.strategic_alignment_score,
        }
    
    async def _gather_priorities(self) -> List[Dict[str, Any]]:
        """Gather priorities from plans and reviews."""
        
        # Get active strategic plans
        from sqlalchemy import select
        from app.models.planning import StrategicPlan
        
        result = await self.session.execute(
            select(StrategicPlan)
            .where(StrategicPlan.status == "active")
            .limit(5)
        )
        plans = list(result.scalars().all())
        
        return [
            {
                "title": p.title,
                "priority": p.priority,
                "domain": p.domain,
            }
            for p in plans
        ]
    
    async def _gather_risks(self) -> List[Dict[str, Any]]:
        """Gather active risks."""
        
        from sqlalchemy import select
        from app.models.detection import DetectedEvent
        
        result = await self.session.execute(
            select(DetectedEvent)
            .where(DetectedEvent.severity.in_(["high", "critical"]))
            .limit(3)
        )
        events = list(result.scalars().all())
        
        return [
            {
                "title": e.title,
                "severity": e.severity,
                "domain": e.domain,
            }
            for e in events
        ]
    
    async def _gather_opportunities(self) -> List[Dict[str, Any]]:
        """Gather active opportunities."""
        
        from sqlalchemy import select
        from app.models.detection import DetectedEvent
        
        result = await self.session.execute(
            select(DetectedEvent)
            .where(DetectedEvent.event_type == "opportunity")
            .limit(3)
        )
        events = list(result.scalars().all())
        
        return [
            {
                "title": e.title,
                "confidence": e.confidence_score,
                "domain": e.domain,
            }
            for e in events
        ]
    
    async def _gather_habits(self) -> List[Dict[str, Any]]:
        """Gather active habits for today."""
        
        from sqlalchemy import select
        from app.rhythm.rhythm_types import Habit
        
        result = await self.session.execute(
            select(Habit)
            .where(Habit.is_active == True)
            .limit(5)
        )
        habits = list(result.scalars().all())
        
        return [
            {
                "id": str(h.id),
                "name": h.name,
                "category": h.category,
            }
            for h in habits
        ]
    
    def _build_priorities(
        self,
        priorities: List[Dict],
        risks: List[Dict],
        opportunities: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Build strategic priorities list."""
        
        result = []
        
        # Add high-priority plans
        for p in priorities[:3]:
            result.append({
                "type": "plan",
                "title": p["title"],
                "priority": p.get("priority", "medium"),
            })
        
        # Add risk monitoring
        for r in risks[:2]:
            result.append({
                "type": "risk",
                "title": r["title"],
                "severity": r["severity"],
            })
        
        # Add opportunity pursuit
        for o in opportunities[:2]:
            result.append({
                "type": "opportunity",
                "title": o["title"],
                "confidence": o.get("confidence", 0.5),
            })
        
        return result
    
    def _build_tasks(
        self,
        priorities: List[Dict],
        opportunities: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Build task list."""
        
        tasks = []
        
        # Convert priorities to tasks
        for p in priorities[:5]:
            tasks.append({
                "title": f"Work on: {p['title']}",
                "type": "execution",
                "priority": p.get("priority", "medium"),
                "estimated_minutes": 60,
            })
        
        return tasks
    
    async def _build_focus_blocks(
        self,
        target_date: date,
    ) -> List[Dict[str, Any]]:
        """Build focus blocks for the day."""
        
        blocks = [
            {
                "type": "deep_work",
                "title": "Morning Deep Work",
                "start_time": "09:00",
                "end_time": "12:00",
                "description": "High-focus strategic work",
            },
            {
                "type": "operational",
                "title": "Afternoon Operations",
                "start_time": "13:00",
                "end_time": "15:00",
                "description": "Email, meetings, routine tasks",
            },
            {
                "type": "strategic",
                "title": "Strategic Review",
                "start_time": "15:00",
                "end_time": "16:00",
                "description": "Planning and review",
            },
            {
                "type": "creative",
                "title": "Learning & Research",
                "start_time": "16:00",
                "end_time": "17:00",
                "description": "Skill development",
            },
        ]
        
        # Save focus blocks
        from app.rhythm.rhythm_types import FocusBlock
        
        for block in blocks:
            fb = FocusBlock(
                date=target_date,
                start_time=time.fromisoformat(block["start_time"]),
                end_time=time.fromisoformat(block["end_time"]),
                block_type=block["type"],
                title=block["title"],
                description=block["description"],
            )
            self.session.add(fb)
        
        await self.session.commit()
        
        return blocks


async def get_daily_planner(session):
    """Get daily planner instance."""
    return DailyPlanner(session)
