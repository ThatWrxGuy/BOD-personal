"""Intelligence Audit Log.

This module provides comprehensive logging for all external intelligence actions.
It tracks OpenAI calls, OpenHands actions, GitHub changes, and reasoning requests.
"""
import json
from typing import Any, Optional
from datetime import datetime
from enum import Enum
from collections import defaultdict

from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    OPENAI_REASONING = "openai_reasoning"
    OPENAI_STRATEGY = "openai_strategy"
    OPENAI_SUMMARIZE = "openai_summarize"
    OPENHANDS_ANALYSIS = "openhands_analysis"
    OPENHANDS_CODE_GENERATION = "openhands_code_generation"
    OPENHANDS_FEATURE = "openhands_feature"
    OPENHANDS_BUGFIX = "openhands_bugfix"
    GITHUB_REPO_ANALYSIS = "github_repo_analysis"
    GITHUB_ISSUE_CREATED = "github_issue_created"
    GITHUB_PR_CREATED = "github_pr_created"
    GITHUB_FILE_ACCESS = "github_file_access"
    GOVERNANCE_CHECK = "governance_check"
    APPROVAL_REQUEST = "approval_request"
    PROPOSAL_EXECUTED = "proposal_executed"


class AuditEventStatus(Enum):
    """Status of audit events."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    BLOCKED = "blocked"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class AuditEvent:
    """Represents an audit event."""
    timestamp: str
    event_type: AuditEventType
    agent: str
    action: str
    status: AuditEventStatus
    details: dict
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class IntelligenceAuditLog:
    """Comprehensive audit logging for external intelligence operations."""

    def __init__(self, log_file: Optional[str] = None):
        """Initialize the audit log.
        
        Args:
            log_file: Optional file path for persistent logging
        """
        self.log_file = log_file
        self.events: list[AuditEvent] = []
        self._event_counts = defaultdict(int)
        
    def log_event(
        self,
        event_type: AuditEventType,
        agent: str,
        action: str,
        status: AuditEventStatus,
        details: dict,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> AuditEvent:
        """Log an audit event.
        
        Args:
            event_type: Type of event
            agent: Agent or service that triggered the event
            action: Description of the action
            status: Status of the action
            details: Additional details
            duration_ms: Duration in milliseconds
            error: Error message if failed
            
        Returns:
            The logged event
        """
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            agent=agent,
            action=action,
            status=status,
            details=details,
            duration_ms=duration_ms,
            error=error,
        )
        
        self.events.append(event)
        self._event_counts[event_type.value] += 1
        
        # Log to file if configured
        if self.log_file:
            self._write_to_file(event)
        
        # Also log to standard logger
        logger.info(
            f"AUDIT: {event_type.value} | {agent} | {action} | {status.value}"
        )
        
        return event

    def log_openai_call(
        self,
        agent: str,
        prompt: str,
        status: AuditEventStatus,
        result: Optional[dict] = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> AuditEvent:
        """Log an OpenAI API call.
        
        Args:
            agent: Calling agent
            prompt: The prompt sent
            status: Call status
            result: Result from OpenAI
            duration_ms: Duration of the call
            error: Error message if failed
            
        Returns:
            Logged event
        """
        return self.log_event(
            event_type=AuditEventType.OPENAI_REASONING,
            agent=agent,
            action=f"OpenAI reasoning: {prompt[:100]}...",
            status=status,
            details={
                "prompt": prompt,
                "result": result,
            },
            duration_ms=duration_ms,
            error=error,
        )

    def log_openhands_action(
        self,
        agent: str,
        action_type: str,
        task: str,
        status: AuditEventStatus,
        result: Optional[dict] = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> AuditEvent:
        """Log an OpenHands action.
        
        Args:
            agent: Calling agent
            action_type: Type of OpenHands action
            task: The task description
            status: Action status
            result: Result from OpenHands
            duration_ms: Duration of the action
            error: Error message if failed
            
        Returns:
            Logged event
        """
        # Map action type to event type
        event_type_map = {
            "analyze": AuditEventType.OPENHANDS_ANALYSIS,
            "implement": AuditEventType.OPENHANDS_FEATURE,
            "fix": AuditEventType.OPENHANDS_BUGFIX,
            "propose": AuditEventType.OPENHANDS_CODE_GENERATION,
        }
        
        event_type = event_type_map.get(action_type, AuditEventType.OPENHANDS_ANALYSIS)
        
        return self.log_event(
            event_type=event_type,
            agent=agent,
            action=f"OpenHands {action_type}: {task[:100]}...",
            status=status,
            details={
                "task": task,
                "action_type": action_type,
                "result": result,
            },
            duration_ms=duration_ms,
            error=error,
        )

    def log_github_action(
        self,
        agent: str,
        action_type: str,
        repo: str,
        status: AuditEventStatus,
        details: dict = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> AuditEvent:
        """Log a GitHub action.
        
        Args:
            agent: Calling agent
            action_type: Type of GitHub action
            repo: Repository name
            status: Action status
            details: Additional details
            duration_ms: Duration of the action
            error: Error message if failed
            
        Returns:
            Logged event
        """
        # Map action type to event type
        event_type_map = {
            "analyze": AuditEventType.GITHUB_REPO_ANALYSIS,
            "create_issue": AuditEventType.GITHUB_ISSUE_CREATED,
            "create_pr": AuditEventType.GITHUB_PR_CREATED,
            "get_file": AuditEventType.GITHUB_FILE_ACCESS,
        }
        
        event_type = event_type_map.get(action_type, AuditEventType.GITHUB_REPO_ANALYSIS)
        
        return self.log_event(
            event_type=event_type,
            agent=agent,
            action=f"GitHub {action_type}: {repo}",
            status=status,
            details=details or {},
            duration_ms=duration_ms,
            error=error,
        )

    def log_governance_check(
        self,
        action_type: str,
        required_level: str,
        approved: bool,
        reason: str,
    ) -> AuditEvent:
        """Log a governance check.
        
        Args:
            action_type: Type of action checked
            required_level: Required approval level
            approved: Whether approved
            reason: Reason for decision
            
        Returns:
            Logged event
        """
        return self.log_event(
            event_type=AuditEventType.GOVERNANCE_CHECK,
            agent="governor",
            action=f"Governance check: {action_type}",
            status=AuditEventStatus.APPROVED if approved else AuditEventStatus.REJECTED,
            details={
                "action_type": action_type,
                "required_level": required_level,
                "approved": approved,
                "reason": reason,
            },
        )

    def log_approval_request(
        self,
        proposal_id: str,
        action_type: str,
        requester: str,
        status: AuditEventStatus,
    ) -> AuditEvent:
        """Log an approval request.
        
        Args:
            proposal_id: Proposal ID
            action_type: Type of action
            requester: Who requested
            status: Request status
            
        Returns:
            Logged event
        """
        return self.log_event(
            event_type=AuditEventType.APPROVAL_REQUEST,
            agent=requester,
            action=f"Approval request: {action_type}",
            status=status,
            details={
                "proposal_id": proposal_id,
                "action_type": action_type,
            },
        )

    def get_events(
        self,
        event_type: Optional[AuditEventType] = None,
        agent: Optional[str] = None,
        status: Optional[AuditEventStatus] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Query audit events.
        
        Args:
            event_type: Filter by event type
            agent: Filter by agent
            status: Filter by status
            limit: Maximum number of events
            
        Returns:
            List of matching events
        """
        results = []
        
        for event in reversed(self.events):
            if event_type and event.event_type != event_type:
                continue
            if agent and event.agent != agent:
                continue
            if status and event.status != status:
                continue
                
            results.append(self._event_to_dict(event))
            
            if len(results) >= limit:
                break
        
        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get audit log statistics.
        
        Returns:
            Statistics about logged events
        """
        total_events = len(self.events)
        
        # Count by status
        status_counts = defaultdict(int)
        for event in self.events:
            status_counts[event.status.value] += 1
        
        # Count by event type
        event_type_counts = defaultdict(int)
        for event in self.events:
            event_type_counts[event.event_type.value] += 1
        
        # Count by agent
        agent_counts = defaultdict(int)
        for event in self.events:
            agent_counts[event.agent] += 1
        
        return {
            "total_events": total_events,
            "by_status": dict(status_counts),
            "by_event_type": dict(event_type_counts),
            "by_agent": dict(agent_counts),
            "oldest_event": self.events[0].timestamp if self.events else None,
            "newest_event": self.events[-1].timestamp if self.events else None,
        }

    def get_failed_events(self, limit: int = 50) -> list[dict]:
        """Get all failed events.
        
        Args:
            limit: Maximum number of events
            
        Returns:
            List of failed events
        """
        return self.get_events(
            status=AuditEventStatus.FAILED,
            limit=limit,
        )

    def clear_old_events(self, days: int = 30):
        """Clear events older than specified days.
        
        Args:
            days: Number of days to keep
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        original_count = len(self.events)
        
        self.events = [
            e for e in self.events
            if datetime.fromisoformat(e.timestamp) > cutoff
        ]
        
        removed = original_count - len(self.events)
        logger.info(f"Cleared {removed} events older than {days} days")

    def export_to_json(self, filepath: str) -> dict[str, Any]:
        """Export audit log to JSON file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            Export result
        """
        try:
            with open(filepath, "w") as f:
                json.dump(
                    [self._event_to_dict(e) for e in self.events],
                    f,
                    indent=2,
                )
            return {
                "success": True,
                "filepath": filepath,
                "events_exported": len(self.events),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _write_to_file(self, event: AuditEvent):
        """Write event to log file."""
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(self._event_to_dict(event)) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit event to file: {e}")

    def _event_to_dict(self, event: AuditEvent) -> dict:
        """Convert event to dictionary."""
        return {
            "timestamp": event.timestamp,
            "event_type": event.event_type.value,
            "agent": event.agent,
            "action": event.action,
            "status": event.status.value,
            "details": event.details,
            "duration_ms": event.duration_ms,
            "error": event.error,
        }


# Global instance
_audit_log: Optional[IntelligenceAuditLog] = None


def get_audit_log() -> IntelligenceAuditLog:
    """Get the intelligence audit log instance."""
    global _audit_log
    
    if _audit_log is None:
        _audit_log = IntelligenceAuditLog()
    
    return _audit_log
