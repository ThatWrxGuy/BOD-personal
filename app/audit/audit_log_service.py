"""
BB-APP-003: Audit Log Service

Centralized audit logging for all strategic state changes.
Per BB-APP-003 Section 9 - Audit Logging System.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Optional
import uuid


@dataclass
class AuditRecord:
    """Single audit log record."""
    id: str
    event_type: str
    entity_type: str
    entity_id: str
    previous_state: Optional[str]
    new_state: Optional[str]
    actor: str
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AuditLogService:
    """Centralized audit logging service."""
    
    def __init__(self):
        self._records: List[AuditRecord] = []
    
    def log_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        actor: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> AuditRecord:
        """Log an audit event."""
        record = AuditRecord(
            id=str(uuid.uuid4()),
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state,
            new_state=new_state,
            actor=actor,
            reason=reason,
            metadata=metadata or {},
            timestamp=datetime.now(),
        )
        
        self._records.append(record)
        return record
    
    def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
    ) -> List[AuditRecord]:
        """Get audit history for a specific entity."""
        return [
            r for r in self._records
            if r.entity_type == entity_type and r.entity_id == entity_id
        ]
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[AuditRecord]:
        """Get audit history for a user."""
        records = [r for r in self._records if r.actor == user_id]
        return sorted(records, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100,
    ) -> List[AuditRecord]:
        """Get audit records by event type."""
        records = [r for r in self._records if r.event_type == event_type]
        return sorted(records, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_recent_events(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> List[AuditRecord]:
        """Get recent audit events."""
        cutoff = datetime.now() - timedelta(hours=hours)
        records = [r for r in self._records if r.timestamp >= cutoff]
        return sorted(records, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_events_in_range(
        self,
        start: datetime,
        end: datetime,
    ) -> List[AuditRecord]:
        """Get audit records in a time range."""
        return [
            r for r in self._records
            if start <= r.timestamp <= end
        ]
    
    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> List[AuditRecord]:
        """Search audit records."""
        query_lower = query.lower()
        results = [
            r for r in self._records
            if query_lower in r.entity_id.lower()
            or query_lower in r.event_type.lower()
            or query_lower in r.reason.lower()
        ]
        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_entity_state_timeline(
        self,
        entity_type: str,
        entity_id: str,
    ) -> List[dict]:
        """Get a timeline of state changes for an entity."""
        history = self.get_entity_history(entity_type, entity_id)
        timeline = []
        
        for record in sorted(history, key=lambda x: x.timestamp):
            timeline.append({
                "timestamp": record.timestamp.isoformat(),
                "event": record.event_type,
                "from": record.previous_state,
                "to": record.new_state,
                "actor": record.actor,
                "reason": record.reason,
            })
        
        return timeline
    
    def get_statistics(self) -> dict:
        """Get audit log statistics."""
        if not self._records:
            return {
                "total_events": 0,
                "by_entity_type": {},
                "by_event_type": {},
                "by_actor": {},
            }
        
        by_entity_type = {}
        by_event_type = {}
        by_actor = {}
        
        for record in self._records:
            by_entity_type[record.entity_type] = by_entity_type.get(record.entity_type, 0) + 1
            by_event_type[record.event_type] = by_event_type.get(record.event_type, 0) + 1
            by_actor[record.actor] = by_actor.get(record.actor, 0) + 1
        
        return {
            "total_events": len(self._records),
            "by_entity_type": by_entity_type,
            "by_event_type": by_event_type,
            "by_actor": by_actor,
        }


# Singleton instance
audit_log_service = AuditLogService()
