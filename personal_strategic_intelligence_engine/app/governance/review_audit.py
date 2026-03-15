"""Review Audit - Audit logging for review decisions.

Records every review decision including:
- Proposed action
- Reviewing authority
- Approval outcome
- Reason
- Timestamp
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ReviewAuditEntry(BaseModel):
    """Audit entry for a review decision."""
    entry_id: UUID = Field(..., description="Unique entry ID")
    request_id: UUID = Field(..., description="Review request ID")
    adjustment_id: UUID = Field(..., description="Adjustment ID")
    adjustment_type: str = Field(..., description="Type of adjustment")
    
    # Risk info
    risk_level: str = Field(..., description="Assessed risk level")
    
    # Decision
    decision: str = Field(..., description="Review decision")
    priority: str = Field(..., description="Review priority")
    
    # Reviewer info
    reviewer: str = Field(..., description="Who performed review")
    reviewer_type: str = Field(..., description="Type of reviewer (executive, governance, system)")
    
    # Details
    reason: str = Field(..., description="Reason for decision")
    conditions: Optional[List[str]] = Field(None, description="Conditions for approval")
    
    # Timing
    requested_at: datetime = Field(..., description="When review was requested")
    reviewed_at: datetime = Field(..., description="When review was completed")
    latency_ms: int = Field(..., description="Review latency in milliseconds")
    
    # Source
    source_system: str = Field(..., description="System that initiated review")


class ReviewAuditLogger:
    """Logs review decisions for audit purposes."""
    
    def __init__(self):
        self._entries: List[ReviewAuditEntry] = []
        self._max_entries = 10000
    
    async def log_review_decision(
        self,
        request: Any,
        result: Any,
        reviewer: str,
        reviewer_type: str,
    ) -> ReviewAuditEntry:
        """Log a review decision.
        
        Args:
            request: Review request
            result: Review result
            reviewer: Who performed review
            reviewer_type: Type of reviewer
            
        Returns:
            Audit entry
        """
        latency_ms = int((result.reviewed_at - request.requested_at).total_seconds() * 1000)
        
        entry = ReviewAuditEntry(
            entry_id=result.result_id,
            request_id=request.request_id,
            adjustment_id=request.adjustment_id,
            adjustment_type=request.adjustment_type,
            risk_level=request.risk_level.value,
            decision=result.decision.value,
            priority=result.priority.value,
            reviewer=reviewer,
            reviewer_type=reviewer_type,
            reason=result.reason,
            conditions=result.conditions,
            requested_at=request.requested_at,
            reviewed_at=result.reviewed_at,
            latency_ms=latency_ms,
            source_system=request.source,
        )
        
        self._entries.append(entry)
        
        # Trim old entries
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
        
        logger.info(
            f"Review audit: {result.decision.value} - "
            f"{request.adjustment_type} by {reviewer} ({latency_ms}ms)"
        )
        
        return entry
    
    async def get_entries(
        self,
        decision: Optional[str] = None,
        reviewer: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[ReviewAuditEntry]:
        """Get audit entries with filters."""
        results = []
        
        for entry in reversed(self._entries):
            if decision and entry.decision != decision:
                continue
            if reviewer and entry.reviewer != reviewer:
                continue
            if since and entry.reviewed_at < since:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get review statistics."""
        total = len(self._entries)
        
        if total == 0:
            return {
                "total_reviews": 0,
                "approval_rate": 0,
                "avg_latency_ms": 0,
            }
        
        approved = sum(1 for e in self._entries if e.decision == "approved")
        total_latency = sum(e.latency_ms for e in self._entries)
        
        # By reviewer type
        by_reviewer_type: Dict[str, int] = {}
        for entry in self._entries:
            by_reviewer_type[entry.reviewer_type] = by_reviewer_type.get(entry.reviewer_type, 0) + 1
        
        # By decision
        by_decision: Dict[str, int] = {}
        for entry in self._entries:
            by_decision[entry.decision] = by_decision.get(entry.decision, 0) + 1
        
        return {
            "total_reviews": total,
            "approved": approved,
            "rejected": sum(1 for e in self._entries if e.decision == "rejected"),
            "deferred": sum(1 for e in self._entries if e.decision == "deferred"),
            "approval_rate": approved / total,
            "avg_latency_ms": total_latency / total,
            "by_reviewer_type": by_reviewer_type,
            "by_decision": by_decision,
        }


# Singleton
_review_audit_logger: Optional[ReviewAuditLogger] = None


def get_review_audit_logger() -> ReviewAuditLogger:
    """Get review audit logger singleton."""
    global _review_audit_logger
    if _review_audit_logger is None:
        _review_audit_logger = ReviewAuditLogger()
    return _review_audit_logger
