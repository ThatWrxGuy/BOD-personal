"""Trend Analyzer for detecting patterns in historical data."""
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.models.goal_progress import GoalProgress
from app.models.strategic_goal import StrategicGoal
from app.core.logging import get_logger

logger = get_logger(__name__)


class TrendIndicator:
    """Represents a detected trend."""

    def __init__(
        self,
        category: str,
        direction: str,  # "up", "down", "stable"
        strength: float,  # 0-10
        confidence: float,  # 0-1
        details: dict,
    ):
        self.category = category
        self.direction = direction
        self.strength = strength
        self.confidence = confidence
        self.details = details
        self.detected_at = datetime.utcnow()


class TrendAnalyzer:
    """Analyzes historical data to detect trends."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_signal_trends(
        self,
        category: Optional[str] = None,
        days: int = 30,
    ) -> list[TrendIndicator]:
        """Analyze trends in signal data."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        query = select(StrategicSignal).where(
            StrategicSignal.timestamp >= cutoff
        )
        
        if category:
            query = query.where(StrategicSignal.category == category)
        
        query = query.order_by(StrategicSignal.timestamp)
        result = await self.session.execute(query)
        signals = list(result.scalars().all())
        
        if not signals:
            return []
        
        # Group by category
        by_category = defaultdict(list)
        for signal in signals:
            by_category[signal.category].append(signal)
        
        trends = []
        
        for cat, cat_signals in by_category.items():
            trend = self._calculate_trend(cat, cat_signals)
            if trend:
                trends.append(trend)
        
        return trends

    def _calculate_trend(
        self,
        category: str,
        signals: list,
    ) -> Optional[TrendIndicator]:
        """Calculate trend for a category."""
        if len(signals) < 3:
            return None
        
        # Calculate average urgency over time
        first_half = signals[:len(signals)//2]
        second_half = signals[len(signals)//2:]
        
        avg_urgency_first = sum(s.urgency for s in first_half) / len(first_half)
        avg_urgency_second = sum(s.urgency for s in second_half) / len(second_half)
        
        avg_strength_first = sum(s.signal_strength for s in first_half) / len(first_half)
        avg_strength_second = sum(s.signal_strength for s in second_half) / len(second_half)
        
        # Determine direction
        urgency_change = avg_urgency_second - avg_urgency_first
        strength_change = avg_strength_second - avg_strength_first
        
        if urgency_change > 0.5 or strength_change > 0.5:
            direction = "up"
        elif urgency_change < -0.5 or strength_change < -0.5:
            direction = "down"
        else:
            direction = "stable"
        
        # Calculate strength
        change_magnitude = abs(urgency_change) + abs(strength_change)
        strength = min(10.0, change_magnitude)
        
        # Calculate confidence based on data points
        confidence = min(0.9, len(signals) / 50)
        
        return TrendIndicator(
            category=category,
            direction=direction,
            strength=strength,
            confidence=confidence,
            details={
                "signal_count": len(signals),
                "urgency_change": urgency_change,
                "strength_change": strength_change,
                "first_period_avg_urgency": avg_urgency_first,
                "second_period_avg_urgency": avg_urgency_second,
            },
        )

    async def analyze_goal_progress_trends(
        self,
        goal_id: Optional[str] = None,
    ) -> list[TrendIndicator]:
        """Analyze trends in goal progress."""
        query = select(GoalProgress).order_by(GoalProgress.recorded_at)
        
        if goal_id:
            query = query.where(GoalProgress.goal_id == goal_id)
        
        result = await self.session.execute(query)
        progress_records = list(result.scalars().all())
        
        if not progress_records:
            return []
        
        # Group by goal
        by_goal = defaultdict(list)
        for record in progress_records:
            by_goal[str(record.goal_id)].append(record)
        
        trends = []
        
        for goal_id_str, records in by_goal.items():
            if len(records) < 2:
                continue
            
            # Calculate velocity (progress per day)
            first_record = records[0]
            last_record = records[-1]
            
            if not first_record.recorded_value or not last_record.recorded_value:
                continue
            
            days_diff = (last_record.recorded_at - first_record.recorded_at).days
            if days_diff <= 0:
                continue
            
            velocity = (last_record.recorded_value - first_record.recorded_value) / days_diff
            
            # Determine direction
            if velocity > 0.01:
                direction = "up"
            elif velocity < -0.01:
                direction = "down"
            else:
                direction = "stable"
            
            strength = min(10.0, abs(velocity) * 10)
            confidence = min(0.8, len(records) / 20)
            
            trends.append(TrendIndicator(
                category=f"goal_{goal_id_str[:8]}",
                direction=direction,
                strength=strength,
                confidence=confidence,
                details={
                    "goal_id": goal_id_str,
                    "progress_records": len(records),
                    "velocity": velocity,
                    "total_progress": last_record.recorded_value - first_record.recorded_value,
                },
            ))
        
        return trends

    async def detect_anomalies(
        self,
        days: int = 7,
    ) -> list[dict]:
        """Detect abnormal patterns in recent data."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.timestamp >= cutoff,
                StrategicSignal.urgency >= 8,
            )
        )
        high_urgency_signals = list(result.scalars().all())
        
        anomalies = []
        
        # Check for clustering of high urgency signals
        if len(high_urgency_signals) >= 3:
            anomalies.append({
                "type": "high_urgency_cluster",
                "severity": "high",
                "description": f"{len(high_urgency_signals)} high urgency signals in {days} days",
                "signals": [s.title for s in high_urgency_signals[:5]],
            })
        
        # Check for unusual categories
        category_counts = defaultdict(int)
        for signal in high_urgency_signals:
            category_counts[signal.category] += 1
        
        for category, count in category_counts.items():
            if count >= 3:
                anomalies.append({
                    "type": "category_spike",
                    "severity": "medium",
                    "description": f"Spike in {category} signals",
                    "count": count,
                })
        
        return anomalies

    async def get_comprehensive_trends(self, days: int = 30) -> dict:
        """Get comprehensive trend analysis."""
        signal_trends = await self.analyze_signal_trends(days=days)
        goal_trends = await self.analyze_goal_progress_trends()
        anomalies = await self.detect_anomalies(days=min(days, 7))
        
        return {
            "signal_trends": [
                {
                    "category": t.category,
                    "direction": t.direction,
                    "strength": t.strength,
                    "confidence": t.confidence,
                    "details": t.details,
                }
                for t in signal_trends
            ],
            "goal_trends": [
                {
                    "category": t.category,
                    "direction": t.direction,
                    "strength": t.strength,
                    "confidence": t.confidence,
                    "details": t.details,
                }
                for t in goal_trends
            ],
            "anomalies": anomalies,
            "analyzed_at": datetime.utcnow().isoformat(),
        }


async def get_trend_analyzer(session: AsyncSession) -> TrendAnalyzer:
    """Get a trend analyzer instance."""
    return TrendAnalyzer(session)
