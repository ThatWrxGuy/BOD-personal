"""Executive Command Center - main orchestration."""
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.executive.command_types import (
    SystemOverview,
    DashboardData,
    ExecutiveCommand,
    OverrideCommand,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class CommandCenter:
    """Primary orchestration layer for Executive Command Center."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide overview."""
        
        # Get strategic focus
        strategic_focus = await self._get_strategic_focus()
        
        # Get goal status
        goal_progress = await self._get_goal_status()
        
        # Get risk level
        risk_level = await self._get_risk_level()
        
        # Get habit adherence
        habit_adherence = await self._get_habit_adherence()
        
        # Get autonomy status
        autonomy_status = await self._get_autonomy_status()
        
        # Get recent changes
        recent_changes = await self._get_recent_strategy_changes()
        
        return {
            "strategic_focus": strategic_focus,
            "goal_progress": goal_progress,
            "risk_level": risk_level,
            "habit_adherence": habit_adherence,
            "autonomy_status": autonomy_status,
            "recent_strategy_changes": recent_changes,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def get_strategic_state(self) -> Dict[str, Any]:
        """Get detailed strategic state."""
        
        # Get active plans
        plans = await self._get_active_plans()
        
        # Get opportunities
        opportunities = await self._get_opportunities()
        
        # Get recent reviews
        reviews = await self._get_recent_reviews()
        
        return {
            "active_plans": plans,
            "opportunities": opportunities,
            "recent_reviews": reviews,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def get_goal_status(self) -> Dict[str, Any]:
        """Get goal status."""
        
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
                "active_goals": len(goals),
                "on_track": on_track,
                "at_risk": at_risk,
            }
        except Exception as e:
            logger.warning(f"Error getting goal status: {e}")
            return {"active_goals": 0, "on_track": 0, "at_risk": 0}
    
    async def get_risk_dashboard(self) -> Dict[str, Any]:
        """Get risk dashboard."""
        
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
                "critical_count": sum(1 for r in risks if r.severity == "critical"),
                "high_count": sum(1 for r in risks if r.severity == "high"),
                "recent_risks": [
                    {"title": r.title, "severity": r.severity, "domain": r.domain}
                    for r in risks[:5]
                ],
            }
        except Exception as e:
            logger.warning(f"Error getting risk dashboard: {e}")
            return {"critical_count": 0, "high_count": 0, "recent_risks": []}
    
    async def get_financial_snapshot(self) -> Dict[str, Any]:
        """Get financial state snapshot."""
        
        try:
            from app.finance_ops.cashflow_forecaster import get_liquidity_monitor
            
            monitor = await get_liquidity_monitor(self.session)
            liquidity = await monitor.check_liquidity()
            
            return liquidity
        except Exception as e:
            logger.warning(f"Error getting financial snapshot: {e}")
            return {"error": str(e)}
    
    async def get_recent_strategy_cycles(self) -> List[Dict[str, Any]]:
        """Get recent strategy loop cycles."""
        
        try:
            from sqlalchemy import select, desc
            from app.autonomy.loop_types import StrategyLoopCycle
            
            result = await self.session.execute(
                select(StrategyLoopCycle)
                .order_by(desc(StrategyLoopCycle.created_at))
                .limit(10)
            )
            cycles = list(result.scalars().all())
            
            return [
                {
                    "id": str(c.id),
                    "status": c.status,
                    "trigger_type": c.trigger_type,
                    "changes_count": c.changes_count,
                    "adjustments_count": c.adjustments_count,
                    "runtime_ms": c.runtime_ms,
                }
                for c in cycles
            ]
        except Exception as e:
            logger.warning(f"Error getting strategy cycles: {e}")
            return []
    
    async def execute_command(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Execute an executive command."""
        
        logger.info(f"Executing command: {command.command_type}")
        
        # Log command
        from app.executive.command_types import ExecutiveCommandLog
        
        log = ExecutiveCommandLog(
            command_id=command.command_id,
            command_type=command.command_type,
            category=command.category.value,
            target=command.target,
            parameters=command.parameters,
            issued_by=command.issued_by,
            status="completed",
        )
        self.session.add(log)
        await self.session.commit()
        
        # Route to appropriate handler
        if command.category.value == "autonomy":
            return await self._handle_autonomy_command(command)
        elif command.category.value == "goal":
            return await self._handle_goal_command(command)
        elif command.category.value == "strategic":
            return await self._handle_strategic_command(command)
        
        return {"status": "executed", "command_id": command.command_id}
    
    async def _handle_autonomy_command(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle autonomy commands."""
        
        if command.command_type == "pause_autonomy":
            from app.executive.override_manager import get_override_manager
            override_mgr = await get_override_manager(self.session)
            return await override_mgr.pause_autonomy(command.issued_by)
        
        elif command.command_type == "resume_autonomy":
            from app.executive.override_manager import get_override_manager
            override_mgr = await get_override_manager(self.session)
            return await override_mgr.resume_autonomy(command.issued_by)
        
        return {"status": "unknown_command"}
    
    async def _handle_goal_command(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle goal commands."""
        
        return {"status": "goal_command_executed"}
    
    async def _handle_strategic_command(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle strategic commands."""
        
        return {"status": "strategic_command_executed"}
    
    async def _get_strategic_focus(self) -> str:
        """Get current strategic focus."""
        
        try:
            from sqlalchemy import select
            from app.models.planning import StrategicPlan
            
            result = await self.session.execute(
                select(StrategicPlan)
                .where(StrategicPlan.status == "active")
                .order_by(StrategicPlan.priority.desc())
                .limit(1)
            )
            plan = result.scalar_one_or_none()
            
            if plan:
                return plan.title
        except:
            pass
        
        return "General Optimization"
    
    async def _get_risk_level(self) -> str:
        """Get overall risk level."""
        
        try:
            from sqlalchemy import select
            from app.models.detection import DetectedEvent
            
            result = await self.session.execute(
                select(DetectedEvent)
                .where(DetectedEvent.severity == "critical")
            )
            critical = len(list(result.scalars().all()))
            
            if critical > 0:
                return "critical"
            
            result = await self.session.execute(
                select(DetectedEvent)
                .where(DetectedEvent.severity == "high")
            )
            high = len(list(result.scalars().all()))
            
            if high > 3:
                return "high"
            elif high > 0:
                return "moderate"
            
            return "low"
        except:
            return "unknown"
    
    async def _get_habit_adherence(self) -> float:
        """Get habit adherence rate."""
        
        try:
            from sqlalchemy import select
            from app.rhythm.rhythm_types import Habit
            
            result = await self.session.execute(
                select(Habit).where(Habit.is_active == True)
            )
            habits = list(result.scalars().all())
            
            if not habits:
                return 0.0
            
            avg_rate = sum(h.completion_rate for h in habits) / len(habits)
            return round(avg_rate, 2)
        except:
            return 0.0
    
    async def _get_autonomy_status(self) -> str:
        """Get autonomy status."""
        
        try:
            from sqlalchemy import select
            from app.executive.command_types import AutonomyOverride
            
            result = await self.session.execute(
                select(AutonomyOverride)
                .where(AutonomyOverride.is_active == True)
                .order_by(AutonomyOverride.started_at.desc())
            )
            override = result.scalar_one_or_none()
            
            if override and override.override_type == "pause_autonomy":
                return "paused"
            
            return "running"
        except:
            return "unknown"
    
    async def _get_recent_strategy_changes(self) -> int:
        """Get count of recent strategy changes."""
        
        try:
            from sqlalchemy import select
            from app.autonomy.loop_types import StrategyLoopCycle
            from datetime import timedelta
            
            from datetime import datetime
            since = datetime.utcnow() - timedelta(days=1)
            
            result = await self.session.execute(
                select(StrategyLoopCycle)
                .where(StrategyLoopCycle.created_at >= since)
            )
            cycles = list(result.scalars().all())
            
            return sum(c.adjustments_count for c in cycles)
        except:
            return 0
    
    async def _get_active_plans(self) -> List[Dict]:
        """Get active plans."""
        
        try:
            from sqlalchemy import select
            from app.models.planning import StrategicPlan
            
            result = await self.session.execute(
                select(StrategicPlan)
                .where(StrategicPlan.status == "active")
                .limit(5)
            )
            plans = list(result.scalars().all())
            
            return [
                {"id": str(p.id), "title": p.title, "priority": p.priority}
                for p in plans
            ]
        except:
            return []
    
    async def _get_opportunities(self) -> List[Dict]:
        """Get opportunities."""
        
        try:
            from sqlalchemy import select
            from app.models.detection import DetectedEvent
            
            result = await self.session.execute(
                select(DetectedEvent)
                .where(DetectedEvent.event_type == "opportunity")
                .limit(5)
            )
            events = list(result.scalars().all())
            
            return [
                {"id": str(e.id), "title": e.title, "confidence": e.confidence_score}
                for e in events
            ]
        except:
            return []
    
    async def _get_recent_reviews(self) -> List[Dict]:
        """Get recent reviews."""
        
        return []


async def get_command_center(session: AsyncSession) -> CommandCenter:
    """Get command center instance."""
    return CommandCenter(session)
