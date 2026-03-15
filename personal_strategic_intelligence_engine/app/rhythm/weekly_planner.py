"""Weekly planner for generating weekly operating plans."""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class WeeklyPlanner:
    """Generate weekly plans."""
    
    def __init__(self, session):
        self.session = session
    
    async def generate_plan(
        self,
        week_start: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate a weekly plan."""
        
        # Default to Monday of current week
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        # Gather weekly inputs
        priorities = await self._gather_weekly_priorities()
        opportunities = await self._gather_opportunities()
        risks = await self._gather_risks()
        
        # Build plan components
        top_priorities = self._build_top_priorities(priorities)
        focus_themes = self._build_focus_themes(priorities, opportunities)
        strategic_initiatives = self._build_initiatives(opportunities)
        risk_monitoring = self._build_risk_monitoring(risks)
        
        # Create plan
        from app.rhythm.rhythm_types import WeeklyPlan
        
        plan = WeeklyPlan(
            week_start=week_start,
            status="generated",
            top_priorities=top_priorities,
            focus_themes=focus_themes,
            strategic_initiatives=strategic_initiatives,
            risk_monitoring=risk_monitoring,
        )
        
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        
        return {
            "id": str(plan.id),
            "week_start": str(plan.week_start),
            "status": plan.status,
            "top_priorities": plan.top_priorities,
            "focus_themes": plan.focus_themes,
            "strategic_initiatives": plan.strategic_initiatives,
            "risk_monitoring": plan.risk_monitoring,
        }
    
    async def _gather_weekly_priorities(self) -> List[Dict]:
        """Gather weekly priorities from active plans."""
        
        from sqlalchemy import select
        from app.models.planning import StrategicPlan
        
        result = await self.session.execute(
            select(StrategicPlan)
            .where(StrategicPlan.status == "active")
            .limit(10)
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
    
    async def _gather_opportunities(self) -> List[Dict]:
        """Gather opportunities."""
        
        from sqlalchemy import select
        from app.models.detection import DetectedEvent
        
        result = await self.session.execute(
            select(DetectedEvent)
            .where(DetectedEvent.event_type == "opportunity")
            .limit(5)
        )
        events = list(result.scalars().all())
        
        return [
            {
                "title": e.title,
                "domain": e.domain,
            }
            for e in events
        ]
    
    async def _gather_risks(self) -> List[Dict]:
        """Gather risks."""
        
        from sqlalchemy import select
        from app.models.detection import DetectedEvent
        
        result = await self.session.execute(
            select(DetectedEvent)
            .where(DetectedEvent.severity.in_(["high", "critical"]))
            .limit(5)
        )
        events = list(result.scalars().all())
        
        return [
            {
                "title": e.title,
                "domain": e.domain,
            }
            for e in events
        ]
    
    def _build_top_priorities(self, priorities: List[Dict]) -> List[Dict]:
        """Build top 3 priorities."""
        
        return [
            {
                "title": p["title"],
                "priority": p.get("priority", "medium"),
                "action": f"Execute on {p['title']}",
            }
            for p in priorities[:3]
        ]
    
    def _build_focus_themes(
        self,
        priorities: List[Dict],
        opportunities: List[Dict],
    ) -> List[str]:
        """Build weekly focus themes."""
        
        themes = []
        
        # Get unique domains from priorities
        domains = set(p.get("domain") for p in priorities if p.get("domain"))
        
        for domain in list(domains)[:3]:
            themes.append(f"Focus on {domain} initiatives")
        
        return themes
    
    def _build_initiatives(self, opportunities: List[Dict]) -> List[Dict]:
        """Build strategic initiatives."""
        
        return [
            {
                "title": o["title"],
                "domain": o.get("domain", "general"),
                "action": f"Explore: {o['title']}",
            }
            for o in opportunities[:3]
        ]
    
    def _build_risk_monitoring(self, risks: List[Dict]) -> List[Dict]:
        """Build risk monitoring tasks."""
        
        return [
            {
                "title": r["title"],
                "domain": r.get("domain", "general"),
                "action": f"Monitor: {r['title']}",
            }
            for r in risks[:3]
        ]


async def get_weekly_planner(session):
    """Get weekly planner instance."""
    return WeeklyPlanner(session)
