"""Signal processor module."""
import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.signals.signal_base import SignalData, SignalScore, BaseSignalProcessor
from app.core.logging import get_logger

logger = get_logger(__name__)


class SignalProcessor:
    """Processes raw signal data into StrategicSignal objects."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_signal(self, signal_data: SignalData) -> StrategicSignal:
        """Process raw signal data into a StrategicSignal."""
        # Calculate scores
        score = self._calculate_scores(signal_data)

        # Create signal
        signal = StrategicSignal(
            timestamp=signal_data.timestamp,
            category=signal_data.category,
            source=signal_data.source,
            title=signal_data.title,
            description=signal_data.description,
            signal_strength=score.signal_strength,
            urgency=score.urgency,
            confidence=score.confidence,
            metadata=signal_data.raw_data,
            processed_at=datetime.utcnow(),
        )

        self.session.add(signal)
        await self.session.commit()
        await self.session.refresh(signal)

        return signal

    async def process_batch(self, signals: list[SignalData]) -> list[StrategicSignal]:
        """Process multiple signals."""
        processed = []
        for signal_data in signals:
            try:
                signal = await self.process_signal(signal_data)
                processed.append(signal)
            except Exception as e:
                logger.error(f"Error processing signal: {e}")
                continue

        return processed

    def _calculate_scores(self, signal_data: SignalData) -> SignalScore:
        """Calculate signal scores based on category and raw data."""
        raw = signal_data.raw_data

        # Default scores
        signal_strength = 5.0
        urgency = 5
        confidence = 0.7

        # Category-specific scoring
        if signal_data.category == SignalCategory.MARKET:
            signal_strength = raw.get("signal_strength", 5.0)
            urgency = raw.get("urgency", 5)
            confidence = raw.get("confidence", 0.7)

        elif signal_data.category == SignalCategory.PERSONAL_FINANCE:
            # Higher urgency for financial risks
            change_pct = abs(raw.get("change_percent", 0))
            signal_strength = min(10.0, change_pct)
            urgency = 7 if raw.get("direction") == "down" else 4
            confidence = 0.8

        elif signal_data.category == SignalCategory.HEALTH:
            # Health metrics
            metric_value = raw.get("metric_value", 0)
            threshold = raw.get("threshold", 0)
            
            if metric_value < threshold:
                signal_strength = min(10.0, (threshold - metric_value) / threshold * 10)
                urgency = 8
            else:
                signal_strength = 3.0
                urgency = 3
            
            confidence = 0.85

        elif signal_data.category == SignalCategory.MACRO:
            # Macro indicators
            signal_strength = raw.get("signal_strength", 5.0)
            urgency = raw.get("urgency", 5)
            confidence = 0.6  # Lower confidence for macro

        elif signal_data.category == SignalCategory.CALENDAR:
            # Calendar overload
            hours_scheduled = raw.get("hours_scheduled", 0)
            capacity = raw.get("capacity", 40)
            
            utilization = hours_scheduled / capacity if capacity > 0 else 0
            signal_strength = min(10.0, utilization * 10)
            
            if utilization > 0.9:
                urgency = 9
            elif utilization > 0.75:
                urgency = 7
            else:
                urgency = 3
            
            confidence = 0.95

        elif signal_data.category == SignalCategory.RESEARCH:
            # Research/knowledge signals
            relevance = raw.get("relevance", 0.5)
            signal_strength = relevance * 10
            urgency = raw.get("urgency", 4)
            confidence = raw.get("confidence", 0.6)

        else:
            # SYSTEM signals
            signal_strength = raw.get("signal_strength", 5.0)
            urgency = raw.get("urgency", 5)
            confidence = 0.9

        return SignalScore(
            signal_strength=signal_strength,
            urgency=min(10, max(1, urgency)),
            confidence=min(1.0, max(0.0, confidence)),
        )


async def get_signal_processor(session: AsyncSession) -> SignalProcessor:
    """Get a signal processor instance."""
    return SignalProcessor(session)
