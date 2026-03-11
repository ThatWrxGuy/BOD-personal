"""Risk Projection Engine for identifying emerging risks."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.models.risk_projection import RiskProjection, RiskCategory
from app.models.strategic_goal import StrategicGoal
from app.models.goal_progress import GoalProgress
from app.core.logging import get_logger

logger = get_logger(__name__)


class RiskProjectionEngine:
    """Projects emerging risks from signals and trends."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def project_financial_risks(self) -> list[RiskProjection]:
        """Project financial risks."""
        risks = []
        
        # Check for high urgency financial signals
        cutoff = datetime.utcnow() - timedelta(days=14)
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.category == SignalCategory.PERSONAL_FINANCE,
                StrategicSignal.urgency >= 7,
                StrategicSignal.timestamp >= cutoff,
            )
        )
        finance_signals = list(result.scalars().all())
        
        if len(finance_signals) >= 3:
            risk = RiskProjection(
                risk_category=RiskCategory.FINANCIAL,
                risk_probability=0.7,
                impact_estimate=0.8,
                time_horizon="30_days",
                risk_description="Multiple high-priority financial signals detected in recent weeks",
                indicators={"signal_count": len(finance_signals), "signals": [s.title for s in finance_signals[:3]]},
                mitigation_suggestions=[
                    "Review financial goals and allocation",
                    "Schedule finance-focused board review",
                    "Consider consulting financial advisor",
                ],
            )
            risks.append(risk)
        
        return risks

    async def project_health_risks(self) -> list[RiskProjection]:
        """Project health-related risks."""
        risks = []
        
        cutoff = datetime.utcnow() - timedelta(days=14)
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.category == SignalCategory.HEALTH,
                StrategicSignal.urgency >= 7,
                StrategicSignal.timestamp >= cutoff,
            )
        )
        health_signals = list(result.scalars().all())
        
        if len(health_signals) >= 2:
            risk = RiskProjection(
                risk_category=RiskCategory.HEALTH,
                risk_probability=0.8,
                impact_estimate=0.9,
                time_horizon="30_days",
                risk_description="Multiple health-related concerns detected",
                indicators={"signal_count": len(health_signals)},
                mitigation_suggestions=[
                    "Prioritize health check-ups",
                    "Review sleep and exercise patterns",
                ],
            )
            risks.append(risk)
        
        return risks

    async def project_operational_risks(self) -> list[RiskProjection]:
        """Project operational risks."""
        risks = []
        
        cutoff = datetime.utcnow() - timedelta(days=7)
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.category == SignalCategory.CALENDAR,
                StrategicSignal.urgency >= 7,
                StrategicSignal.timestamp >= cutoff,
            )
        )
        calendar_signals = list(result.scalars().all())
        
        if len(calendar_signals) >= 3:
            risk = RiskProjection(
                risk_category=RiskCategory.OPERATIONS,
                risk_probability=0.75,
                impact_estimate=0.7,
                time_horizon="14_days",
                risk_description="Calendar overload detected - risk of burnout",
                indicators={"overloaded_days": len(calendar_signals)},
                mitigation_suggestions=[
                    "Review and cancel non-essential commitments",
                    "Delegate tasks where possible",
                ],
            )
            risks.append(risk)
        
        return risks

    async def project_goal_failure_risks(self) -> list[RiskProjection]:
        """Project risks of goal failure."""
        risks = []
        
        result = await self.session.execute(
            select(StrategicGoal).where(StrategicGoal.status == "ACTIVE")
        )
        active_goals = list(result.scalars().all())
        
        for goal in active_goals:
            if not goal.target_value or not goal.current_value or not goal.target_date:
                continue
            
            days_remaining = (goal.target_date - datetime.utcnow()).days
            
            if days_remaining <= 0:
                risk = RiskProjection(
                    risk_category=RiskCategory.OPERATIONS,
                    risk_probability=0.9,
                    impact_estimate=0.8,
                    time_horizon="immediate",
                    risk_description=f"Goal '{goal.title}' is past deadline",
                    indicators={"goal_id": str(goal.id), "days_overdue": abs(days_remaining)},
                    mitigation_suggestions=["Extend deadline or reassess goal"],
                )
                risks.append(risk)
        
        return risks

    async def project_all_risks(self) -> list[RiskProjection]:
        """Project all risk categories."""
        all_risks = []
        
        try:
            financial_risks = await self.project_financial_risks()
            all_risks.extend(financial_risks)
        except Exception as e:
            logger.error(f"Error projecting financial risks: {e}")
        
        try:
            health_risks = await self.project_health_risks()
            all_risks.extend(health_risks)
        except Exception as e:
            logger.error(f"Error projecting health risks: {e}")
        
        try:
            operational_risks = await self.project_operational_risks()
            all_risks.extend(operational_risks)
        except Exception as e:
            logger.error(f"Error projecting operational risks: {e}")
        
        try:
            goal_risks = await self.project_goal_failure_risks()
            all_risks.extend(goal_risks)
        except Exception as e:
            logger.error(f"Error projecting goal risks: {e}")
        
        for risk in all_risks:
            self.session.add(risk)
        
        await self.session.commit()
        
        return all_risks


async def get_risk_projection_engine(session: AsyncSession) -> RiskProjectionEngine:
    """Get a risk projection engine instance."""
    return RiskProjectionEngine(session)
