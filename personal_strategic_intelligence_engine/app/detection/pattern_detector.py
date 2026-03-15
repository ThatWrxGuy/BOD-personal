"""Pattern detection for opportunity and risk detection."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.detection_types import DomainType, DetectionSeverity
from app.core.logging import get_logger

logger = get_logger(__name__)


class PatternDetector:
    """Detects patterns in signal data."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def detect_patterns(
        self,
        domain: str,
        time_range_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Detect patterns in domain data."""
        
        patterns = []
        
        if domain == DomainType.FINANCIAL:
            patterns = await self._detect_financial_patterns(time_range_days)
        elif domain == DomainType.HEALTH:
            patterns = await self._detect_health_patterns(time_range_days)
        elif domain == DomainType.PRODUCTIVITY:
            patterns = await self._detect_productivity_patterns(time_range_days)
        
        return patterns
    
    async def _detect_financial_patterns(self, days: int) -> List[Dict[str, Any]]:
        """Detect financial patterns."""
        
        from sqlalchemy import select
        from app.models.learning import DecisionMemory
        
        # Get recent financial decisions
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        patterns = []
        
        # Check for investment-related decisions
        investment_keywords = ["invest", "portfolio", "stock", "bond", "etf", "crypto"]
        investments = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in investment_keywords)
        ]
        
        if len(investments) > 5:
            patterns.append({
                "type": "pattern",
                "pattern_name": "increased_investment_activity",
                "description": f"High investment activity with {len(investments)} decisions in {days} days",
                "severity": DetectionSeverity.LOW,
                "confidence": 0.7,
            })
        
        # Check for savings-related decisions
        savings_keywords = ["savings", "save", "budget", "expense", "spending"]
        savings = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in savings_keywords)
        ]
        
        if len(savings) > 0:
            patterns.append({
                "type": "pattern",
                "pattern_name": "active_financial_planning",
                "description": f"Active financial planning with {len(savings)} decisions",
                "severity": DetectionSeverity.LOW,
                "confidence": 0.8,
            })
        
        return patterns
    
    async def _detect_health_patterns(self, days: int) -> List[Dict[str, Any]]:
        """Detect health patterns."""
        
        from sqlalchemy import select
        from app.models.learning import DecisionMemory
        
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        patterns = []
        
        health_keywords = ["exercise", "workout", "gym", "sleep", "health", "fitness"]
        health_decisions = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in health_keywords)
        ]
        
        if len(health_decisions) > 3:
            patterns.append({
                "type": "pattern",
                "pattern_name": "active_health_focus",
                "description": f"Active health focus with {len(health_decisions)} health decisions",
                "severity": DetectionSeverity.LOW,
                "confidence": 0.8,
            })
        
        return patterns
    
    async def _detect_productivity_patterns(self, days: int) -> List[Dict[str, Any]]:
        """Detect productivity patterns."""
        
        from sqlalchemy import select
        from app.models import BoardMeeting
        
        result = await self.session.execute(
            select(BoardMeeting)
            .where(BoardMeeting.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        meetings = list(result.scalars().all())
        
        patterns = []
        
        # Calculate meeting frequency
        if len(meetings) > 0:
            avg_per_week = len(meetings) / (days / 7)
            
            if avg_per_week > 3:
                patterns.append({
                    "type": "pattern",
                    "pattern_name": "high_meeting_frequency",
                    "description": f"High meeting frequency: {avg_per_week:.1f} meetings per week",
                    "severity": DetectionSeverity.MEDIUM,
                    "confidence": 0.7,
                })
        
        return patterns


class AnomalyDetector:
    """Detects anomalies in signal data."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def detect_anomalies(
        self,
        domain: str,
        time_range_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in domain data."""
        
        anomalies = []
        
        if domain == DomainType.FINANCIAL:
            anomalies = await self._detect_financial_anomalies(time_range_days)
        elif domain == DomainType.HEALTH:
            anomalies = await self._detect_health_anomalies(time_range_days)
        elif domain == DomainType.PRODUCTIVITY:
            anomalies = await self._detect_productivity_anomalies(time_range_days)
        
        return anomalies
    
    async def _detect_financial_anomalies(self, days: int) -> List[Dict[str, Any]]:
        """Detect financial anomalies."""
        
        from sqlalchemy import select
        from app.models.learning import DecisionMemory
        
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        anomalies = []
        
        # Check for sudden increase in financial decisions
        recent = [d for d in decisions if d.created_at >= datetime.utcnow() - timedelta(days=7)]
        
        if len(recent) > 10:
            anomalies.append({
                "type": "anomaly",
                "anomaly_name": "financial_activity_spike",
                "description": f"Sudden increase in financial decisions: {len(recent)} in last 7 days",
                "severity": DetectionSeverity.MEDIUM,
                "confidence": 0.6,
            })
        
        return anomalies
    
    async def _detect_health_anomalies(self, days: int) -> List[Dict[str, Any]]:
        """Detect health anomalies."""
        
        from sqlalchemy import select
        from app.models.learning import DecisionMemory
        
        result = await self.session.execute(
            select(DecisionMemory)
            .where(DecisionMemory.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        decisions = list(result.scalars().all())
        
        anomalies = []
        
        health_keywords = ["tired", "exhausted", "sick", "ill", "stressed"]
        stress_indicators = [
            d for d in decisions
            if any(kw in (d.decision_summary or "").lower() for kw in health_keywords)
        ]
        
        if len(stress_indicators) > 3:
            anomalies.append({
                "type": "anomaly",
                "anomaly_name": "health_stress_indicators",
                "description": f"Multiple health stress indicators: {len(stress_indicators)} mentions",
                "severity": DetectionSeverity.HIGH,
                "confidence": 0.7,
            })
        
        return anomalies
    
    async def _detect_productivity_anomalies(self, days: int) -> List[Dict[str, Any]]:
        """Detect productivity anomalies."""
        
        anomalies = []
        
        # Check for lack of meetings - might indicate isolation
        from sqlalchemy import select
        from app.models import BoardMeeting
        
        result = await self.session.execute(
            select(BoardMeeting)
            .where(BoardMeeting.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        meetings = list(result.scalars().all())
        
        if len(meetings) == 0 and days > 14:
            anomalies.append({
                "type": "anomaly",
                "anomaly_name": "no_recent_meetings",
                "description": "No board meetings in the last 14+ days",
                "severity": DetectionSeverity.MEDIUM,
                "confidence": 0.8,
            })
        
        return anomalies


async def get_pattern_detector(session: AsyncSession) -> PatternDetector:
    """Get pattern detector instance."""
    return PatternDetector(session)


async def get_anomaly_detector(session: AsyncSession) -> AnomalyDetector:
    """Get anomaly detector instance."""
    return AnomalyDetector(session)
