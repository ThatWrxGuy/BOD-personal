"""Review Engine for periodic governance reviews."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_goal import StrategicGoal
from app.models.strategic_plan import StrategicPlan
from app.models.board_meeting import BoardMeeting
from app.governance.goal_tracker import GoalTracker
from app.governance.plan_manager import PlanManager
from app.governance.trigger_engine import TriggerEngine
from app.services.signal_service import SignalService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReviewReport:
    """Structured review report."""

    def __init__(
        self,
        review_type: str,
        summary: str,
        findings: list[dict],
        recommendations: list[str],
        metrics: dict,
    ):
        self.review_type = review_type
        self.summary = summary
        self.findings = findings
        self.recommendations = recommendations
        self.metrics = metrics
        self.generated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "review_type": self.review_type,
            "summary": self.summary,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "generated_at": self.generated_at.isoformat(),
        }


class ReviewEngine:
    """Runs periodic governance reviews."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"

    def __init__(self, session: AsyncSession):
        self.session = session
        self.goal_tracker = GoalTracker(session)
        self.plan_manager = PlanManager(session)
        self.trigger_engine = TriggerEngine(session)
        self.signal_service = SignalService(session)

    async def run_daily_review(self) -> ReviewReport:
        """Run daily tactical review."""
        # Get recent signals
        signals_summary = await self.signal_service.get_signal_summary(hours=24)
        
        # Get pending triggers
        pending_triggers = await self.trigger_engine.get_pending_triggers()
        
        # Get today's meetings
        today = datetime.utcnow().date()
        result = await self.session.execute(
            select(BoardMeeting).where(
                BoardMeeting.created_at >= today
            )
        )
        today_meetings = list(result.scalars().all())
        
        findings = []
        
        # Check for high urgency signals
        if signals_summary.get("high_urgency_count", 0) > 0:
            findings.append({
                "area": "signals",
                "status": "alert",
                "detail": f"{signals_summary['high_urgency_count']} high urgency signals in last 24h",
            })
        
        # Check for pending triggers
        if pending_triggers:
            findings.append({
                "area": "triggers",
                "status": "action_needed",
                "detail": f"{len(pending_triggers)} pending trigger events",
            })
        
        # Check for meetings
        if not today_meetings:
            findings.append({
                "area": "meetings",
                "status": "info",
                "detail": "No board meetings held today",
            })
        
        return ReviewReport(
            review_type=self.DAILY,
            summary="Daily tactical review completed",
            findings=findings,
            recommendations=self._generate_daily_recommendations(findings),
            metrics={
                "signals_total": signals_summary.get("total", 0),
                "high_urgency": signals_summary.get("high_urgency_count", 0),
                "pending_triggers": len(pending_triggers),
                "meetings_today": len(today_meetings),
            },
        )

    async def run_weekly_review(self) -> ReviewReport:
        """Run weekly strategic review."""
        # Get week's signals
        signals_summary = await self.signal_service.get_signal_summary(hours=24 * 7)
        
        # Get active goals
        active_goals = await self.goal_tracker.get_active_goals()
        
        # Get active plans
        active_plans = await self.plan_manager.get_active_plans()
        
        # Get goals at risk
        at_risk_goals = await self.goal_tracker.get_goals_at_risk()
        
        findings = []
        
        # Goal progress
        total_goals = len(active_goals)
        if at_risk_goals:
            findings.append({
                "area": "goals",
                "status": "warning",
                "detail": f"{len(at_risk_goals)} goals at risk of missing targets",
            })
        
        # Plan status
        if active_plans:
            overdue = await self.plan_manager.get_overdue_plans()
            if overdue:
                findings.append({
                    "area": "plans",
                    "status": "warning",
                    "detail": f"{len(overdue)} plans overdue",
                })
        
        return ReviewReport(
            review_type=self.WEEKLY,
            summary="Weekly strategic review completed",
            findings=findings,
            recommendations=self._generate_weekly_recommendations(findings, active_goals),
            metrics={
                "signals_total": signals_summary.get("total", 0),
                "active_goals": total_goals,
                "goals_at_risk": len(at_risk_goals),
                "active_plans": len(active_plans),
            },
        )

    async def run_monthly_review(self) -> ReviewReport:
        """Run monthly capital allocation review."""
        # Get finance signals
        finance_signals = await self.signal_service.get_signals_by_category(
            category="PERSONAL_FINANCE",
            hours=24 * 30,
        )
        
        # Get financial goals
        finance_goals = await self.goal_tracker.list_goals(category="FINANCE")
        
        # Get all goals with progress
        all_goals = await self.goal_tracker.list_goals()
        
        findings = []
        
        # Analyze financial signals
        if finance_signals:
            high_urgency = [s for s in finance_signals if s.urgency >= 7]
            if high_urgency:
                findings.append({
                    "area": "finances",
                    "status": "alert",
                    "detail": f"{len(high_urgency)} high urgency finance signals this month",
                })
        
        return ReviewReport(
            review_type=self.MONTHLY,
            summary="Monthly capital allocation review completed",
            findings=findings,
            recommendations=self._generate_monthly_recommendations(findings),
            metrics={
                "finance_signals": len(finance_signals),
                "finance_goals": len(finance_goals),
                "total_goals": len(all_goals),
            },
        )

    async def run_quarterly_review(self) -> ReviewReport:
        """Run quarterly strategic planning session."""
        # Get quarter signals
        signals_summary = await self.signal_service.get_signal_summary(hours=24 * 90)
        
        # Get all active goals and plans
        active_goals = await self.goal_tracker.get_active_goals()
        active_plans = await self.plan_manager.get_active_plans()
        
        # Calculate completion rates
        total_goals = len(active_goals)
        
        findings = []
        
        if total_goals == 0:
            findings.append({
                "area": "goals",
                "status": "info",
                "detail": "No active strategic goals set",
            })
        
        return ReviewReport(
            review_type=self.QUARTERLY,
            summary="Quarterly strategic planning session completed",
            findings=findings,
            recommendations=self._generate_quarterly_recommendations(findings),
            metrics={
                "signals_total": signals_summary.get("total", 0),
                "active_goals": total_goals,
                "active_plans": len(active_plans),
            },
        )

    async def run_annual_review(self) -> ReviewReport:
        """Run annual strategic review."""
        # Get year signals
        signals_summary = await self.signal_service.get_signal_summary(hours=24 * 365)
        
        # Get all goals
        all_goals = await self.goal_tracker.list_goals()
        
        # Get all plans
        all_plans = await self.plan_manager.list_plans()
        
        # Calculate stats
        completed_goals = len([g for g in all_goals if g.status == "COMPLETED"])
        completed_plans = len([p for p in all_plans if p.status == "COMPLETED"])
        
        findings = []
        
        return ReviewReport(
            review_type=self.ANNUAL,
            summary="Annual strategic review completed",
            findings=findings,
            recommendations=self._generate_annual_recommendations(findings, all_goals),
            metrics={
                "year_signals": signals_summary.get("total", 0),
                "total_goals": len(all_goals),
                "completed_goals": completed_goals,
                "goal_completion_rate": completed_goals / len(all_goals) * 100 if all_goals else 0,
                "completed_plans": completed_plans,
            },
        )

    def _generate_daily_recommendations(self, findings: list[dict]) -> list[str]:
        """Generate daily recommendations."""
        recommendations = []
        
        alert_areas = [f["area"] for f in findings if f.get("status") in ["alert", "action_needed"]]
        
        if "triggers" in alert_areas:
            recommendations.append("Review and address pending trigger events")
        
        if "signals" in alert_areas:
            recommendations.append("Review high urgency signals in board meeting")
        
        return recommendations

    def _generate_weekly_recommendations(self, findings: list[dict], active_goals: list) -> list[str]:
        """Generate weekly recommendations."""
        recommendations = []
        
        warning_areas = [f["area"] for f in findings if f.get("status") == "warning"]
        
        if "goals" in warning_areas:
            recommendations.append("Review goals at risk and adjust timelines or resources")
        
        if "plans" in warning_areas:
            recommendations.append("Review overdue plans and determine next steps")
        
        if not active_goals:
            recommendations.append("Set new strategic goals for the quarter")
        
        return recommendations

    def _generate_monthly_recommendations(self, findings: list[dict]) -> list[str]:
        """Generate monthly recommendations."""
        recommendations = []
        
        if any(f.get("area") == "finances" for f in findings):
            recommendations.append("Review financial position and allocation strategy")
        
        return recommendations

    def _generate_quarterly_recommendations(self, findings: list[dict]) -> list[str]:
        """Generate quarterly recommendations."""
        recommendations = []
        
        recommendations.append("Evaluate strategic direction and adjust as needed")
        recommendations.append("Set goals for next quarter")
        
        return recommendations

    def _generate_annual_recommendations(self, findings: list[dict], goals: list) -> list[str]:
        """Generate annual recommendations."""
        recommendations = []
        
        recommendations.append("Set strategic direction for next year")
        recommendations.append("Review and update personal constitution")
        
        return recommendations


from sqlalchemy import select


async def get_review_engine(session: AsyncSession) -> ReviewEngine:
    """Get a review engine instance."""
    return ReviewEngine(session)
