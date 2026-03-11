"""Domain analyzer for strategic reviews."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.reviews.review_types import DomainType
from app.core.logging import get_logger

logger = get_logger(__name__)


class DomainAnalyzer:
    """Analyzes life domains for strategic reviews."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_domain(
        self,
        domain: str,
        time_range_days: int = 30,
    ) -> Dict[str, Any]:
        """Analyze a specific domain."""
        
        if domain == DomainType.FINANCIAL:
            return await self.analyze_financial(time_range_days)
        elif domain == DomainType.HEALTH:
            return await self.analyze_health(time_range_days)
        elif domain == DomainType.PRODUCTIVITY:
            return await self.analyze_productivity(time_range_days)
        elif domain == DomainType.PROJECTS:
            return await self.analyze_projects(time_range_days)
        elif domain == DomainType.RISK:
            return await self.analyze_risk(time_range_days)
        elif domain == DomainType.LONG_TERM_GOALS:
            return await self.analyze_long_term_goals(time_range_days)
        else:
            return {"error": f"Unknown domain: {domain}"}
    
    async def analyze_all_domains(
        self,
        domains: List[str],
        time_range_days: int = 30,
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze multiple domains."""
        
        results = {}
        
        for domain in domains:
            try:
                results[domain] = await self.analyze_domain(domain, time_range_days)
            except Exception as e:
                logger.error(f"Error analyzing domain {domain}: {e}")
                results[domain] = {"error": str(e)}
        
        return results
    
    async def analyze_financial(self, days: int) -> Dict[str, Any]:
        """Analyze financial domain."""
        
        from sqlalchemy import select, func
        from app.models.execution_record import ExecutionRecord
        from app.models.learning import DecisionMemory
        
        # Get recent decisions related to finances
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        # Analyze decisions
        financial_keywords = ["investment", "saving", "budget", "expense", "income", "portfolio"]
        
        financial_decisions = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in financial_keywords)
        ]
        
        # Calculate metrics
        total_decisions = len(decisions)
        financial_decisions_count = len(financial_decisions)
        
        return {
            "domain": DomainType.FINANCIAL,
            "period_days": days,
            "metrics": {
                "total_decisions": total_decisions,
                "financial_decisions": financial_decisions_count,
                "financial_focus_percentage": (
                    (financial_decisions_count / total_decisions * 100)
                    if total_decisions > 0 else 0
                ),
            },
            "insights": [
                {
                    "type": "progress",
                    "description": f"Reviewed {financial_decisions_count} financial decisions in the last {days} days",
                }
            ] if financial_decisions_count > 0 else [],
            "status": "analyzed",
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    
    async def analyze_health(self, days: int) -> Dict[str, Any]:
        """Analyze health domain."""
        
        from sqlalchemy import select
        from app.models.learning import DecisionMemory
        
        # Get recent health-related decisions
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        health_keywords = ["health", "exercise", "sleep", "workout", "fitness", "medical"]
        
        health_decisions = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in health_keywords)
        ]
        
        return {
            "domain": DomainType.HEALTH,
            "period_days": days,
            "metrics": {
                "total_decisions": len(decisions),
                "health_decisions": len(health_decisions),
                "health_focus_percentage": (
                    (len(health_decisions) / len(decisions) * 100)
                    if len(decisions) > 0 else 0
                ),
            },
            "insights": [
                {
                    "type": "progress",
                    "description": f"Reviewed {len(health_decisions)} health-related decisions in the last {days} days",
                }
            ] if len(health_decisions) > 0 else [],
            "status": "analyzed",
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    
    async def analyze_productivity(self, days: int) -> Dict[str, Any]:
        """Analyze productivity domain."""
        
        from sqlalchemy import select
        from app.models.learning import DecisionMemory
        
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        productivity_keywords = ["task", "project", "meeting", "focus", "schedule", "deadline"]
        
        productivity_decisions = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in productivity_keywords)
        ]
        
        return {
            "domain": DomainType.PRODUCTIVITY,
            "period_days": days,
            "metrics": {
                "total_decisions": len(decisions),
                "productivity_decisions": len(productivity_decisions),
            },
            "insights": [
                {
                    "type": "progress",
                    "description": f"Reviewed {len(productivity_decisions)} productivity-related decisions",
                }
            ] if len(productivity_decisions) > 0 else [],
            "status": "analyzed",
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    
    async def analyze_projects(self, days: int) -> Dict[str, Any]:
        """Analyze projects domain."""
        
        from sqlalchemy import select
        from app.models import BoardMeeting
        
        result = await self.session.execute(
            select(BoardMeeting)
            .where(BoardMeeting.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        meetings = list(result.scalars().all())
        
        return {
            "domain": DomainType.PROJECTS,
            "period_days": days,
            "metrics": {
                "meetings_count": len(meetings),
                "meeting_types": self._count_by_field(meetings, "meeting_type"),
            },
            "insights": [
                {
                    "type": "progress",
                    "description": f"Conducted {len(meetings)} meetings in the last {days} days",
                }
            ],
            "status": "analyzed",
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    
    async def analyze_risk(self, days: int) -> Dict[str, Any]:
        """Analyze risk domain."""
        
        from sqlalchemy import select
        from app.models.learning import StrategicLesson
        
        result = await self.session.execute(
            select(StrategicLesson)
            .where(StrategicLesson.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        lessons = list(result.scalars().all())
        
        # Analyze risk-related lessons
        risk_keywords = ["risk", "failure", "mistake", "avoid", "danger"]
        
        risk_lessons = [
            l for l in lessons
            if any(kw in (l.lesson_text or "").lower() for kw in risk_keywords)
        ]
        
        return {
            "domain": DomainType.RISK,
            "period_days": days,
            "metrics": {
                "total_lessons": len(lessons),
                "risk_lessons": len(risk_lessons),
            },
            "insights": [
                {
                    "type": "risk",
                    "description": f"Identified {len(risk_lessons)} risk-related lessons from past experiences",
                }
            ] if len(risk_lessons) > 0 else [
                {
                    "type": "opportunity",
                    "description": "No significant risks identified from recent history",
                }
            ],
            "status": "analyzed",
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    
    async def analyze_long_term_goals(self, days: int) -> Dict[str, Any]:
        """Analyze long-term goals domain."""
        
        from sqlalchemy import select
        from app.models import UserProfile
        
        result = await self.session.execute(select(UserProfile))
        profile = result.scalar_one_or_none()
        
        goals_analysis = {
            "domain": DomainType.LONG_TERM_GOALS,
            "period_days": days,
            "metrics": {
                "has_profile": profile is not None,
            },
            "insights": [],
            "status": "analyzed",
            "analyzed_at": datetime.utcnow().isoformat(),
        }
        
        if profile:
            goals_analysis["insights"].append({
                "type": "progress",
                "description": "User profile exists with mission and goals defined",
            })
            if profile.mission_statement:
                goals_analysis["insights"].append({
                    "type": "progress",
                    "description": f"Mission: {profile.mission_statement[:100]}...",
                })
        
        return goals_analysis
    
    def _count_by_field(self, items: List[Any], field: str) -> Dict[str, int]:
        """Count items by a specific field value."""
        counts = {}
        for item in items:
            value = getattr(item, field, None)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts


async def get_domain_analyzer(session: AsyncSession) -> DomainAnalyzer:
    """Get domain analyzer instance."""
    return DomainAnalyzer(session)
