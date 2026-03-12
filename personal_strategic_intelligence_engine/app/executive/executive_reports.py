"""Executive reports generation."""
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.executive.command_types import ExecutiveReport, ReportPeriod
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutiveReports:
    """Generates periodic executive reports."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily strategic report."""
        
        period_start = datetime.utcnow().date()
        
        # Get key metrics
        goals = await self._get_goal_summary()
        risks = await self._get_risk_summary()
        habits = await self._get_habit_summary()
        cycles = await self._get_cycle_summary(period_start)
        
        # Build summary
        summary = {
            "period": "daily",
            "date": str(period_start),
            "goals": goals,
            "risks": risks,
            "habits": habits,
            "autonomy": cycles,
        }
        
        # Generate highlights
        highlights = []
        if goals.get("on_track", 0) > goals.get("at_risk", 0):
            highlights.append(f"Goals are progressing well: {goals['on_track']} on track")
        if risks.get("critical_count", 0) > 0:
            highlights.append(f"WARNING: {risks['critical_count']} critical risks require attention")
        if habits.get("avg_completion", 0) > 0.8:
            highlights.append(f"Excellent habit adherence: {int(habits['avg_completion']*100)}%")
        
        # Generate recommendations
        recommendations = []
        if risks.get("critical_count", 0) > 0:
            recommendations.append("Address critical risks immediately")
        if goals.get("at_risk", 0) > 0:
            recommendations.append("Review at-risk goals")
        
        return {
            "report_id": str(uuid.uuid4()),
            "period": "daily",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": summary,
            "highlights": highlights,
            "recommendations": recommendations,
        }
    
    async def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly strategic review."""
        
        period_start = datetime.utcnow().date() - timedelta(days=7)
        
        # Get weekly metrics
        goals = await self._get_goal_summary()
        risks = await self._get_risk_summary()
        habits = await self._get_habit_summary()
        cycles = await self._get_cycle_summary(period_start)
        
        summary = {
            "period": "weekly",
            "week_start": str(period_start),
            "goals": goals,
            "risks": risks,
            "habits": habits,
            "autonomy": cycles,
        }
        
        highlights = [
            f"Strategy loop executed {cycles.get('total_cycles', 0)} times this week",
            f"System made {cycles.get('total_adjustments', 0)} adjustments",
        ]
        
        recommendations = [
            "Review strategic alignment for next week",
            "Assess habit consistency trends",
        ]
        
        return {
            "report_id": str(uuid.uuid4()),
            "period": "weekly",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": summary,
            "highlights": highlights,
            "recommendations": recommendations,
        }
    
    async def generate_monthly_report(self) -> Dict[str, Any]:
        """Generate monthly system performance report."""
        
        period_start = datetime.utcnow().date() - timedelta(days=30)
        
        # Get monthly metrics
        goals = await self._get_goal_summary()
        risks = await self._get_risk_summary()
        habits = await self._get_habit_summary()
        cycles = await self._get_cycle_summary(period_start)
        financial = await self._get_financial_summary()
        
        summary = {
            "period": "monthly",
            "month_start": str(period_start),
            "goals": goals,
            "risks": risks,
            "habits": habits,
            "autonomy": cycles,
            "financial": financial,
        }
        
        highlights = [
            f"Autonomous system made {cycles.get('total_adjustments', 0)} strategic adjustments",
            f"Goal completion rate: {goals.get('completion_rate', 0)}%",
            f"Habit adherence: {int(habits.get('avg_completion', 0)*100)}%",
        ]
        
        recommendations = [
            "Evaluate long-term strategic trends",
            "Plan next quarter's focus areas",
            "Review financial trajectory",
        ]
        
        return {
            "report_id": str(uuid.uuid4()),
            "period": "monthly",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": summary,
            "highlights": highlights,
            "recommendations": recommendations,
        }
    
    async def _get_goal_summary(self) -> Dict[str, Any]:
        """Get goal summary."""
        
        try:
            from sqlalchemy import select
            from app.governance.goal_tracker import Goal
            
            result = await self.session.execute(
                select(Goal).where(Goal.status == "active")
            )
            goals = list(result.scalars().all())
            
            on_track = sum(1 for g in goals if g.progress >= 50)
            at_risk = sum(1 for g in goals if g.progress < 50)
            
            return {
                "active": len(goals),
                "on_track": on_track,
                "at_risk": at_risk,
                "completion_rate": on_track / max(1, len(goals)),
            }
        except:
            return {"active": 0, "on_track": 0, "at_risk": 0}
    
    async def _get_risk_summary(self) -> Dict[str, Any]:
        """Get risk summary."""
        
        try:
            from sqlalchemy import select
            from app.models.detection import DetectedEvent
            
            result = await self.session.execute(
                select(DetectedEvent)
                .where(DetectedEvent.severity.in_(["high", "critical"]))
            )
            risks = list(result.scalars().all())
            
            return {
                "critical_count": sum(1 for r in risks if r.severity == "critical"),
                "high_count": sum(1 for r in risks if r.severity == "high"),
            }
        except:
            return {"critical_count": 0, "high_count": 0}
    
    async def _get_habit_summary(self) -> Dict[str, Any]:
        """Get habit summary."""
        
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
            }
        except:
            return {"total": 0, "avg_completion": 0, "avg_streak": 0}
    
    async def _get_cycle_summary(self, since: date) -> Dict[str, Any]:
        """Get strategy cycle summary."""
        
        try:
            from sqlalchemy import select
            from app.autonomy.loop_types import StrategyLoopCycle
            
            result = await self.session.execute(
                select(StrategyLoopCycle)
                .where(StrategyLoopCycle.created_at >= since)
            )
            cycles = list(result.scalars().all())
            
            return {
                "total_cycles": len(cycles),
                "total_adjustments": sum(c.adjustments_count for c in cycles),
                "completed": sum(1 for c in cycles if c.status == "completed"),
                "failed": sum(1 for c in cycles if c.status == "failed"),
            }
        except:
            return {"total_cycles": 0, "total_adjustments": 0}
    
    async def _get_financial_summary(self) -> Dict[str, Any]:
        """Get financial summary."""
        
        try:
            from app.finance_ops.cashflow_forecaster import get_liquidity_monitor
            
            monitor = await get_liquidity_monitor(self.session)
            liquidity = await monitor.check_liquidity()
            
            return liquidity
        except:
            return {}


async def get_executive_reports(session: AsyncSession) -> ExecutiveReports:
    """Get executive reports instance."""
    return ExecutiveReports(session)
