"""Trigger Engine for signal-triggered governance events."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.models.trigger_event import TriggerEvent, TriggerType, TriggerSeverity
from app.core.logging import get_logger

logger = get_logger(__name__)


class TriggerRule:
    """Represents a trigger rule configuration."""

    def __init__(
        self,
        name: str,
        trigger_type: str,
        condition: callable,
        severity: str = "MEDIUM",
    ):
        self.name = name
        self.trigger_type = trigger_type
        self.condition = condition
        self.severity = severity


class TriggerEngine:
    """Monitors signals and triggers governance events."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> list[TriggerRule]:
        """Initialize trigger rules."""
        return [
            TriggerRule(
                name="critical_financial_signal",
                trigger_type=TriggerType.FINANCE_REVIEW,
                condition=self._check_critical_finance,
                severity=TriggerSeverity.HIGH,
            ),
            TriggerRule(
                name="high_urgency_accumulation",
                trigger_type=TriggerType.RISK_REVIEW,
                condition=self._check_high_urgency_accumulation,
                severity=TriggerSeverity.HIGH,
            ),
            TriggerRule(
                name="calendar_overload",
                trigger_type=TriggerType.OPERATIONS_REVIEW,
                condition=self._check_calendar_overload,
                severity=TriggerSeverity.MEDIUM,
            ),
            TriggerRule(
                name="health_degradation",
                trigger_type=TriggerType.HEALTH_REVIEW,
                condition=self._check_health_degradation,
                severity=TriggerSeverity.CRITICAL,
            ),
            TriggerRule(
                name="market_volatility_spike",
                trigger_type=TriggerType.BOARD_MEETING,
                condition=self._check_market_volatility,
                severity=TriggerSeverity.HIGH,
            ),
            TriggerRule(
                name="macro_instability",
                trigger_type=TriggerType.STRATEGY_REVIEW,
                condition=self._check_macro_instability,
                severity=TriggerSeverity.MEDIUM,
            ),
        ]

    async def _check_critical_finance(self, signals: list[StrategicSignal]) -> bool:
        """Check for critical financial signals."""
        finance_signals = [s for s in signals if s.category == SignalCategory.PERSONAL_FINANCE]
        return any(s.urgency >= 9 for s in finance_signals)

    async def _check_high_urgency_accumulation(self, signals: list[StrategicSignal]) -> bool:
        """Check if 3+ high urgency signals in 24 hours."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        high_urgency = [s for s in signals if s.urgency >= 7 and s.timestamp >= cutoff]
        return len(high_urgency) >= 3

    async def _check_calendar_overload(self, signals: list[StrategicSignal]) -> bool:
        """Check for calendar overload signal."""
        calendar_signals = [s for s in signals if s.category == SignalCategory.CALENDAR]
        return any(s.urgency >= 8 for s in calendar_signals)

    async def _check_health_degradation(self, signals: list[StrategicSignal]) -> bool:
        """Check for health metric degradation."""
        health_signals = [s for s in signals if s.category == SignalCategory.HEALTH]
        return any(s.urgency >= 9 for s in health_signals)

    async def _check_market_volatility(self, signals: list[StrategicSignal]) -> bool:
        """Check for market volatility spike."""
        market_signals = [s for s in signals if s.category == SignalCategory.MARKET]
        return any(s.signal_strength >= 8 for s in market_signals)

    async def _check_macro_instability(self, signals: list[StrategicSignal]) -> bool:
        """Check for macro instability."""
        macro_signals = [s for s in signals if s.category == SignalCategory.MACRO]
        return any(s.urgency >= 8 for s in macro_signals)

    async def check_signals(self) -> list[TriggerEvent]:
        """Check signals against trigger rules and create events."""
        # Get recent signals
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.timestamp >= cutoff
            )
        )
        signals = list(result.scalars().all())
        
        triggered_events = []
        
        for rule in self.rules:
            try:
                if await rule.condition(signals):
                    # Create trigger event
                    event = TriggerEvent(
                        signal_id=signals[0].id if signals else None,
                        trigger_type=rule.trigger_type,
                        trigger_reason=f"Triggered by rule: {rule.name}",
                        severity=rule.severity,
                    )
                    self.session.add(event)
                    triggered_events.append(event)
                    logger.info(f"Triggered: {rule.name} - {rule.trigger_type}")
            except Exception as e:
                logger.error(f"Error checking rule {rule.name}: {e}")
        
        await self.session.commit()
        return triggered_events

    async def get_pending_triggers(self, min_severity: str = "LOW") -> list[TriggerEvent]:
        """Get unresolved trigger events."""
        severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        min_level = severity_order.get(min_severity, 0)
        
        result = await self.session.execute(
            select(TriggerEvent).where(
                and_(
                    TriggerEvent.is_resolved == False,
                )
            )
        )
        all_events = list(result.scalars().all())
        
        return [
            e for e in all_events 
            if severity_order.get(e.severity, 0) >= min_level
        ]

    async def resolve_trigger(self, trigger_id: uuid.UUID) -> None:
        """Mark a trigger as resolved."""
        result = await self.session.get(TriggerEvent, trigger_id)
        if result:
            result.is_resolved = True
            result.resolved_at = datetime.utcnow()
            await self.session.commit()


async def get_trigger_engine(session: AsyncSession) -> TriggerEngine:
    """Get a trigger engine instance."""
    return TriggerEngine(session)
