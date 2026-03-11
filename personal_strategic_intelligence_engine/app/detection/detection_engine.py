"""Detection engine for opportunity and risk detection."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.detection_types import (
    DetectedEvent,
    DetectionEventType,
    DetectionSeverity,
    DetectionStatus,
    DomainType,
)
from app.detection.pattern_detector import get_pattern_detector, get_anomaly_detector
from app.detection.opportunity_classifier import get_opportunity_classifier, get_risk_classifier
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class DetectionEngine:
    """Main detection engine for opportunity and risk detection."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def process_signal(
        self,
        signal_data: Dict[str, Any],
    ) -> Optional[DetectedEvent]:
        """Process a signal and detect opportunities or risks."""
        
        domain = signal_data.get("domain", "")
        
        # Run pattern detection
        pattern_detector = await get_pattern_detector(self.session)
        patterns = await pattern_detector.detect_patterns(domain, signal_data.get("time_range_days", 30))
        
        # Run anomaly detection
        anomaly_detector = await get_anomaly_detector(self.session)
        anomalies = await anomaly_detector.detect_anomalies(domain, signal_data.get("time_range_days", 30))
        
        detected_events = []
        
        # Process patterns
        for pattern in patterns:
            event = await self._create_detection_event(
                event_type=DetectionEventType.PATTERN,
                domain=domain,
                title=pattern.get("title", pattern.get("pattern_name", "Pattern Detected")),
                description=pattern.get("description", ""),
                severity=pattern.get("severity", DetectionSeverity.LOW),
                confidence=pattern.get("confidence", 0.5),
                source_signals=signal_data.get("sources", []),
            )
            detected_events.append(event)
            
            # Publish event
            await self._publish_detection_event(event, "pattern")
            
            # Track metrics
            increment("patterns_detected", domain=MetricDomain.SYSTEM)
        
        # Process anomalies
        for anomaly in anomalies:
            event = await self._create_detection_event(
                event_type=DetectionEventType.ANOMALY,
                domain=domain,
                title=anomaly.get("title", anomaly.get("anomaly_name", "Anomaly Detected")),
                description=anomaly.get("description", ""),
                severity=anomaly.get("severity", DetectionSeverity.MEDIUM),
                confidence=anomaly.get("confidence", 0.5),
                source_signals=signal_data.get("sources", []),
            )
            detected_events.append(event)
            
            # Publish event
            await self._publish_detection_event(event, "anomaly")
            
            # Track metrics
            increment("anomalies_detected", domain=MetricDomain.SYSTEM)
        
        # Classify based on severity
        for event in detected_events:
            if event.severity in [DetectionSeverity.HIGH, DetectionSeverity.CRITICAL]:
                # Classify as opportunity or risk
                if event.severity == DetectionSeverity.HIGH:
                    await self._classify_and_publish(event, signal_data)
        
        increment("signals_processed", domain=MetricDomain.SYSTEM)
        
        return detected_events[0] if detected_events else None
    
    async def run_full_analysis(
        self,
        domains: Optional[List[str]] = None,
        time_range_days: int = 30,
    ) -> List[DetectedEvent]:
        """Run full analysis across all or specified domains."""
        
        if domains is None:
            domains = [d.value for d in DomainType]
        
        all_events = []
        
        for domain in domains:
            try:
                signal_data = {
                    "domain": domain,
                    "time_range_days": time_range_days,
                    "sources": ["scheduled_analysis"],
                }
                
                events = await self.process_signal(signal_data)
                if events:
                    if isinstance(events, list):
                        all_events.extend(events)
                    else:
                        all_events.append(events)
            
            except Exception as e:
                logger.error(f"Error analyzing domain {domain}: {e}")
        
        # Track metrics
        increment("full_analysis_run", domain=MetricDomain.SYSTEM)
        
        return all_events
    
    async def _create_detection_event(
        self,
        event_type: str,
        domain: str,
        title: str,
        description: str,
        severity: str,
        confidence: float,
        source_signals: List[str],
    ) -> DetectedEvent:
        """Create a detection event."""
        
        event = DetectedEvent(
            event_type=event_type,
            domain=domain,
            title=title,
            description=description,
            severity=severity,
            confidence_score=confidence,
            source_signals=source_signals,
            detected_at=datetime.utcnow(),
        )
        
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        
        return event
    
    async def _classify_and_publish(
        self,
        event: DetectedEvent,
        signal_data: Dict[str, Any],
    ) -> None:
        """Classify event as opportunity or risk and publish."""
        
        # Determine if it's an opportunity or risk based on event type
        if event.event_type == DetectionEventType.PATTERN:
            # Classify as opportunity
            classifier = await get_opportunity_classifier(self.session)
            classification = await classifier.classify_opportunity({
                "domain": event.domain,
                "confidence": event.confidence_score,
                "source_signals": event.source_signals,
            })
            
            await self._publish_detection_event(event, "opportunity")
            increment("opportunities_detected", domain=MetricDomain.SYSTEM)
        
        elif event.event_type == DetectionEventType.ANOMALY:
            # Classify as risk
            classifier = await get_risk_classifier(self.session)
            classification = await classifier.classify_risk({
                "domain": event.domain,
                "confidence": event.confidence_score,
                "severity": event.severity,
                "source_signals": event.source_signals,
            })
            
            await self._publish_detection_event(event, "risk")
            increment("risks_detected", domain=MetricDomain.SYSTEM)
    
    async def _publish_detection_event(
        self,
        event: DetectedEvent,
        classification: str,
    ) -> None:
        """Publish detection event to event bus."""
        
        event_bus = get_event_bus(self.session)
        
        if classification == "opportunity":
            event_type = EventType.OUTCOME_EVALUATED  # Reuse for now
        elif classification == "risk":
            event_type = EventType.OUTCOME_EVALUATED
        else:
            event_type = EventType.OUTCOME_EVALUATED
        
        await event_bus.publish_event(
            DomainEvent(
                event_type=event_type,
                payload={
                    "detection_id": str(event.id),
                    "event_type": event.event_type,
                    "domain": event.domain,
                    "title": event.title,
                    "severity": event.severity,
                    "classification": classification,
                },
                source_module="detection_engine",
                correlation_id=event.correlation_id,
            )
        )
    
    async def get_detection_events(
        self,
        event_type: Optional[str] = None,
        domain: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[DetectedEvent]:
        """Get detection events with filters."""
        
        from sqlalchemy import select, desc
        
        query = select(DetectedEvent).order_by(desc(DetectedEvent.detected_at)).limit(limit)
        
        if event_type:
            query = query.where(DetectedEvent.event_type == event_type)
        if domain:
            query = query.where(DetectedEvent.domain == domain)
        if severity:
            query = query.where(DetectedEvent.severity == severity)
        if status:
            query = query.where(DetectedEvent.status == status)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics."""
        
        from sqlalchemy import select, func
        
        # Count by type
        result = await self.session.execute(
            select(DetectedEvent.event_type, func.count(DetectedEvent.id))
            .group_by(DetectedEvent.event_type)
        )
        by_type = {row[0]: row[1] for row in result.all()}
        
        # Count by severity
        result = await self.session.execute(
            select(DetectedEvent.severity, func.count(DetectedEvent.id))
            .group_by(DetectedEvent.severity)
        )
        by_severity = {row[0]: row[1] for row in result.all()}
        
        # Count by domain
        result = await self.session.execute(
            select(DetectedEvent.domain, func.count(DetectedEvent.id))
            .group_by(DetectedEvent.domain)
        )
        by_domain = {row[0]: row[1] for row in result.all()}
        
        return {
            "by_type": by_type,
            "by_severity": by_severity,
            "by_domain": by_domain,
            "total": sum(by_type.values()) if by_type else 0,
        }
    
    async def resolve_event(
        self,
        event_id: uuid.UUID,
        resolution: str = "addressed",
    ) -> DetectedEvent:
        """Resolve a detection event."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(DetectedEvent).where(DetectedEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise ValueError(f"Event not found: {event_id}")
        
        event.status = resolution
        event.resolved_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(event)
        
        return event


async def get_detection_engine(session: AsyncSession) -> DetectionEngine:
    """Get detection engine instance."""
    return DetectionEngine(session)
