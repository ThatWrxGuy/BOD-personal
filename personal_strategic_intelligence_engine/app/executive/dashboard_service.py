"""Executive dashboard service."""
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.executive.command_center import get_command_center
from app.core.logging import get_logger

logger = get_logger(__name__)


class DashboardService:
    """Generates structured executive dashboards."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard data."""
        
        command_center = await get_command_center(self.session)
        
        # Gather all dashboard sections
        strategic = await self._get_strategic_overview()
        goals = await command_center.get_goal_status()
        risks = await command_center.get_risk_dashboard()
        opportunities = await self._get_opportunities()
        financial = await command_center.get_financial_snapshot()
        habits = await self._get_habits()
        autonomy = await self._get_autonomy_dashboard()
        
        return {
            "strategic_overview": strategic,
            "goals": goals,
            "risks": risks,
            "opportunities": opportunities,
            "financial": financial,
            "habits": habits,
            "autonomy": autonomy,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def _get_strategic_overview(self) -> Dict[str, Any]:
        """Get strategic overview."""
        
        try:
            from sqlalchemy import select
            from app.models.planning import StrategicPlan
            
            result = await self.session.execute(
                select(StrategicPlan)
                .where(StrategicPlan.status == "active")
                .limit(10)
            )
            plans = list(result.scalars().all())
            
            return {
                "active_plans": len(plans),
                "plans": [
                    {"id": str(p.id), "title": p.title, "priority": p.priority, "domain": p.domain}
                    for p in plans[:5]
                ],
            }
        except Exception as e:
            logger.warning(f"Error in strategic overview: {e}")
            return {"active_plans": 0, "plans": []}
    
    async def _get_opportunities(self) -> Dict[str, Any]:
        """Get opportunities dashboard."""
        
        try:
            from sqlalchemy import select
            from app.models.detection import DetectedEvent
            
            result = await self.session.execute(
                select(DetectedEvent)
                .where(DetectedEvent.event_type == "opportunity")
                .limit(10)
            )
            opportunities = list(result.scalars().all())
            
            return {
                "count": len(opportunities),
                "high_confidence": sum(1 for o in opportunities if o.confidence_score > 0.7),
                "items": [
                    {"id": str(o.id), "title": o.title, "confidence": o.confidence_score}
                    for o in opportunities[:5]
                ],
            }
        except Exception as e:
            logger.warning(f"Error in opportunities: {e}")
            return {"count": 0, "items": []}
    
    async def _get_habits(self) -> Dict[str, Any]:
        """Get habits dashboard."""
        
        try:
            from sqlalchemy import select
            from app.rhythm.rhythm_types import Habit
            
            result = await self.session.execute(
                select(Habit).where(Habit.is_active == True)
            )
            habits = list(result.scalars().all())
            
            return {
                "total": len(habits),
                "avg_completion": sum(h.completion_rate for h in habits) / max(1, len(habits)),
                "avg_streak": sum(h.streak_count for h in habits) / max(1, len(habits)),
                "habits": [
                    {"id": str(h.id), "name": h.name, "streak": h.streak_count, "category": h.category}
                    for h in habits[:5]
                ],
            }
        except Exception as e:
            logger.warning(f"Error in habits: {e}")
            return {"total": 0, "habits": []}
    
    async def _get_autonomy_dashboard(self) -> Dict[str, Any]:
        """Get autonomy dashboard."""
        
        try:
            from sqlalchemy import select, desc
            from app.autonomy.loop_types import StrategyLoopCycle
            
            result = await self.session.execute(
                select(StrategyLoopCycle)
                .order_by(desc(StrategyLoopCycle.created_at))
                .limit(5)
            )
            cycles = list(result.scalars().all())
            
            # Get autonomy status
            from app.executive.command_center import get_command_center
            cc = await get_command_center(self.session)
            status = await cc._get_autonomy_status()
            
            return {
                "status": status,
                "recent_cycles": len(cycles),
                "last_cycle": {
                    "id": str(cycles[0].id),
                    "status": cycles[0].status,
                    "changes": cycles[0].changes_count,
                    "adjustments": cycles[0].adjustments_count,
                } if cycles else None,
            }
        except Exception as e:
            logger.warning(f"Error in autonomy dashboard: {e}")
            return {"status": "unknown"}


async def get_dashboard_service(session: AsyncSession) -> DashboardService:
    """Get dashboard service instance."""
    return DashboardService(session)
