"""Audit logging for tracking system operations."""
import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """Audit log for tracking system operations."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class AuditLogger:
    """Service for logging audit events."""

    @staticmethod
    def log_action(
        session,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log an audit event."""
        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
        )
        session.add(audit_log)
        return audit_log


# Action constants
class AuditActions:
    """Audit action constants."""
    PROFILE_CREATED = "profile.created"
    PROFILE_UPDATED = "profile.updated"
    MEETING_CREATED = "meeting.created"
    MEETING_STARTED = "meeting.started"
    MEETING_COMPLETED = "meeting.completed"
    MEETING_FAILED = "meeting.failed"
    DECISION_CREATED = "decision.created"
    DECISION_UPDATED = "decision.updated"
    REVIEW_CREATED = "review.created"
    AGENT_ANALYZED = "agent.analyzed"
    CRITIQUE_GENERATED = "critique.generated"
