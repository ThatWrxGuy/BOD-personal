"""State monitor - aggregates system state from all subsystems."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.autonomy.loop_types import StateObservation, DomainState
from app.core.logging import get_logger

logger = get_logger(__name__)


class StateMonitor:
    """Aggregates current system state from all subsystems."""
    
    def __init__(self, session):
        self.session = session
    
    async def observe_state(self) -> StateObservation:
        """Create a complete state observation."""
        
        observation_id = str(uuid.uuid4())
        
        # Gather state from each domain
        domains = []
        
        # Strategic priorities
        priorities = await self._get_strategic_priorities()
        domains.append(DomainState(
            domain="strategic",
            state=priorities,
            freshness=datetime.utcnow(),
        ))
        
        # Goals
        goals = await self._get_goals()
        domains.append(DomainState(
            domain="goals",
            state=goals,
            freshness=datetime.utcnow(),
        ))
        
        # Risks
        risks = await self._get_risks()
        domains.append(DomainState(
            domain="risks",
            state=risks,
            freshness=datetime.utcnow(),
        ))
        
        # Opportunities
        opportunities = await self._get_opportunities()
        domains.append(DomainState(
            domain="opportunities",
            state=opportunities,
            freshness=datetime.utcnow(),
        ))
        
        # Habits
        habits = await self._get_habits()
        domains.append(DomainState(
            domain="habits",
            state=habits,
            freshness=datetime.utcnow(),
        ))
        
        # Daily plan
        daily_plan = await self._get_daily_plan()
        domains.append(DomainState(
            domain="daily_plan",
            state=daily_plan,
            freshness=datetime.utcnow(),
        ))
        
        # Weekly plan
        weekly_plan = await self._get_weekly_plan()
        domains.append(DomainState(
            domain="weekly_plan",
            state=weekly_plan,
            freshness=datetime.utcnow(),
        ))
        
        # Financial
        financial = await self._get_financial()
        domains.append(DomainState(
            domain="financial",
            state=financial,
            freshness=datetime.utcnow(),
        ))
        
        # Calculate overall health
        health = self._calculate_health(domains)
        
        return StateObservation(
            observation_id=observation_id,
            timestamp=datetime.utcnow(),
            domains=domains,
            overall_health=health,
        )
    
    async def _get_strategic_priorities(self) -> Dict[str, Any]:
        """Get strategic priorities."""
        
        try:
            from sqlalchemy import select
            from app.models.planning import StrategicPlan
            
            result = await self.session.execute(
                select(StrategicPlan)
                .where(StrategicPlan.status == "active")
                .limit(5)
            )
            plans = list(result.scalars().all())
            
            return {
                "active_plans": [
                    {"id": str(p.id), "title": p.title, "priority": p.priority}
                    for p in plans
                ],
                "count": len(plans),
            }
        except Exception as e:
            logger.warning(f"Error getting strategic priorities: {e}")
            return {"error": str(e), "count": 0}
    
    async def _get_goals(self) -> Dict[str, Any]:
        """Get goals."""
        
        try:
            from sqlalchemy import select
            from app.governance.goal_tracker import Goal
            
            result = await self.session.execute(
                select(Goal)
                .where(Goal.status == "active")
                .limit(10)
            )
            goals = list(result.scalars().all())
            
            return {
                "active_goals": [
                    {"id": str(g.id), "title": g.title, "progress": g.progress}
                    for g in goals
                ],
                "count": len(goals),
            }
        except Exception as e:
            logger.warning(f"Error getting goals: {e}")
            return {"error": str(e), "count": 0}
    
    async def _get_risks(self) -> Dict[str, Any]:
        """Get active risks."""
        
        try:
            from sqlalchemy import select
            from app.models.detection import DetectedEvent
            
            result = await self.session.execute(
                select(DetectedEvent)
                .where(DetectedEvent.severity.in_(["high", "critical"]))
                .limit(10)
            )
            risks = list(result.scalars().all())
            
            return {
                "high_severity_risks": [
                    {"id": str(r.id), "title": r.title, "severity": r.severity}
                    for r in risks
                ],
                "count": len(risks),
            }
        except Exception as e:
            logger.warning(f"Error getting risks: {e}")
            return {"error": str(e), "count": 0}
    
    async def _get_opportunities(self) -> Dict[str, Any]:
        """Get opportunities."""
        
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
                "opportunities": [
                    {"id": str(o.id), "title": o.title, "confidence": o.confidence_score}
                    for o in opportunities
                ],
                "count": len(opportunities),
            }
        except Exception as e:
            logger.warning(f"Error getting opportunities: {e}")
            return {"error": str(e), "count": 0}
    
    async def _get_habits(self) -> Dict[str, Any]:
        """Get habit status."""
        
        try:
            from sqlalchemy import select
            from app.rhythm.rhythm_types import Habit
            
            result = await self.session.execute(
                select(Habit).where(Habit.is_active == True).limit(10)
            )
            habits = list(result.scalars().all())
            
            return {
                "active_habits": [
                    {"id": str(h.id), "name": h.name, "streak": h.streak_count}
                    for h in habits
                ],
                "count": len(habits),
            }
        except Exception as e:
            logger.warning(f"Error getting habits: {e}")
            return {"error": str(e), "count": 0}
    
    async def _get_daily_plan(self) -> Dict[str, Any]:
        """Get latest daily plan."""
        
        try:
            from sqlalchemy import select
            from app.rhythm.rhythm_types import DailyPlan
            from datetime import date
            
            result = await self.session.execute(
                select(DailyPlan)
                .where(DailyPlan.plan_date == date.today())
            )
            plan = result.scalar_one_or_none()
            
            if plan:
                return {
                    "id": str(plan.id),
                    "date": str(plan.plan_date),
                    "status": plan.status,
                    "completion_rate": plan.completion_rate,
                }
            return {"status": "none"}
        except Exception as e:
            logger.warning(f"Error getting daily plan: {e}")
            return {"error": str(e)}
    
    async def _get_weekly_plan(self) -> Dict[str, Any]:
        """Get latest weekly plan."""
        
        try:
            from sqlalchemy import select
            from app.rhythm.rhythm_types import WeeklyPlan
            
            result = await self.session.execute(
                select(WeeklyPlan).order_by(WeeklyPlan.week_start.desc()).limit(1)
            )
            plan = result.scalar_one_or_none()
            
            if plan:
                return {
                    "id": str(plan.id),
                    "week_start": str(plan.week_start),
                    "status": plan.status,
                }
            return {"status": "none"}
        except Exception as e:
            logger.warning(f"Error getting weekly plan: {e}")
            return {"error": str(e)}
    
    async def _get_financial(self) -> Dict[str, Any]:
        """Get financial state."""
        
        try:
            from app.finance_ops.cashflow_forecaster import get_liquidity_monitor
            
            monitor = await get_liquidity_monitor(self.session)
            liquidity = await monitor.check_liquidity()
            
            return liquidity
        except Exception as e:
            logger.warning(f"Error getting financial: {e}")
            return {"error": str(e)}
    
    def _calculate_health(self, domains: List[DomainState]) -> float:
        """Calculate overall system health."""
        
        # Simple health calculation
        health_scores = []
        
        for domain in domains:
            if domain.domain == "risks":
                risk_count = domain.state.get("count", 0)
                health = max(0, 1 - (risk_count * 0.1))
                health_scores.append(health)
            elif domain.domain == "daily_plan":
                completion = domain.state.get("completion_rate", 0.5)
                health_scores.append(completion)
            elif domain.domain == "habits":
                # Higher streak = healthier
                habits = domain.state.get("active_habits", [])
                avg_streak = sum(h.get("streak", 0) for h in habits) / max(1, len(habits))
                health = min(1, avg_streak / 30)  # 30-day streak = perfect
                health_scores.append(health)
        
        return sum(health_scores) / max(1, len(health_scores))


async def get_state_monitor(session):
    """Get state monitor instance."""
    return StateMonitor(session)
