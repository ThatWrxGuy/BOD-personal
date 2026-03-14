"""Financial Audit Logger - records governance and financial intelligence events."""
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.finance.governance.models.financial_audit_event import (
    FinancialAuditEvent,
    AuditEventType,
)


class FinancialAuditLogger:
    """
    Records governance and financial intelligence events.
    
    Responsibilities:
    - Log recommendation creation
    - Log decision submission
    - Log decision outcomes
    - Log scenario execution
    - Log board brief generation
    
    All audit records must be immutable.
    """

    def __init__(self):
        # In-memory storage (would be database in production)
        self._audit_events: Dict[str, FinancialAuditEvent] = {}

    def log_event(
        self,
        profile_id: int,
        event_type: AuditEventType,
        event_reference: str,
        description: str,
    ) -> FinancialAuditEvent:
        """
        Log an audit event.

        Args:
            profile_id: The profile ID
            event_type: Type of event
            event_reference: Reference ID for the event
            description: Event description

        Returns:
            FinancialAuditEvent that was created
        """
        event = FinancialAuditEvent.create(
            profile_id=profile_id,
            event_type=event_type,
            event_reference=event_reference,
            description=description,
        )
        
        self._audit_events[event.event_id] = event
        
        return event

    def log_recommendation_generated(
        self,
        profile_id: str,
        recommendation_id: str,
        title: str,
    ) -> FinancialAuditEvent:
        """
        Log recommendation generation.

        Args:
            profile_id: The profile ID
            recommendation_id: The recommendation ID
            title: Recommendation title

        Returns:
            FinancialAuditEvent that was created
        """
        return self.log_event(
            profile_id=int(profile_id),
            event_type=AuditEventType.RECOMMENDATION_GENERATED,
            event_reference=recommendation_id,
            description=f"Generated recommendation: {title}",
        )

    def log_decision_requested(
        self,
        profile_id: int,
        decision_id: str,
        title: str,
        decision_class: str,
    ) -> FinancialAuditEvent:
        """
        Log decision request submission.

        Args:
            profile_id: The profile ID
            decision_id: The decision ID
            title: Decision title
            decision_class: Classification of decision

        Returns:
            FinancialAuditEvent that was created
        """
        return self.log_event(
            profile_id=profile_id,
            event_type=AuditEventType.DECISION_REQUESTED,
            event_reference=decision_id,
            description=f"Decision requested: {title} ({decision_class})",
        )

    def log_decision_resolved(
        self,
        profile_id: int,
        decision_id: str,
        outcome: str,
        reviewer: str = "system",
    ) -> FinancialAuditEvent:
        """
        Log decision resolution.

        Args:
            profile_id: The profile ID
            decision_id: The decision ID
            outcome: Decision outcome
            reviewer: Who resolved the decision

        Returns:
            FinancialAuditEvent that was created
        """
        return self.log_event(
            profile_id=profile_id,
            event_type=AuditEventType.DECISION_RESOLVED,
            event_reference=decision_id,
            description=f"Decision resolved: {outcome} by {reviewer}",
        )

    def log_board_brief_generated(
        self,
        profile_id: int,
        brief_id: str,
        financial_status: str,
    ) -> FinancialAuditEvent:
        """
        Log board brief generation.

        Args:
            profile_id: The profile ID
            brief_id: The brief ID
            financial_status: Financial status at time of generation

        Returns:
            FinancialAuditEvent that was created
        """
        return self.log_event(
            profile_id=profile_id,
            event_type=AuditEventType.BOARD_BRIEF_GENERATED,
            event_reference=brief_id,
            description=f"Board brief generated: status={financial_status}",
        )

    def log_scenario_executed(
        self,
        profile_id: int,
        scenario_id: str,
        scenario_type: str,
    ) -> FinancialAuditEvent:
        """
        Log scenario execution.

        Args:
            profile_id: The profile ID
            scenario_id: The scenario ID
            scenario_type: Type of scenario

        Returns:
            FinancialAuditEvent that was created
        """
        return self.log_event(
            profile_id=profile_id,
            event_type=AuditEventType.SCENARIO_EXECUTED,
            event_reference=scenario_id,
            description=f"Scenario executed: {scenario_type}",
        )

    def get_audit_log(
        self,
        profile_id: int,
        event_type: Optional[AuditEventType] = None,
        limit: int = 100,
    ) -> List[FinancialAuditEvent]:
        """
        Get audit log for a profile.

        Args:
            profile_id: The profile ID
            event_type: Optional filter by event type
            limit: Maximum number of events to return

        Returns:
            List of FinancialAuditEvent objects
        """
        events = [
            e for e in self._audit_events.values()
            if e.profile_id == profile_id
        ]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Sort by timestamp descending
        events.sort(key=lambda e: e.created_at, reverse=True)
        
        return events[:limit]

    def get_event_count(
        self,
        profile_id: int,
        event_type: Optional[AuditEventType] = None,
    ) -> int:
        """
        Get count of audit events.

        Args:
            profile_id: The profile ID
            event_type: Optional filter by event type

        Returns:
            Number of events
        """
        events = self.get_audit_log(profile_id, event_type, limit=10000)
        return len(events)
