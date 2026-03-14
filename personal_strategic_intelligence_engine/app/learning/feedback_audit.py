"""Learning Feedback Audit - Audit trail for feedback usage in planning.

Tracks:
- What feedback was applied
- Which planning run used it
- What impact it had on plan ranking/selection
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class FeedbackAuditEntry(BaseModel):
    """Audit entry for feedback usage."""
    entry_id: UUID = Field(default_factory=uuid4)
    planning_run_id: UUID = Field(..., description="Planning run identifier")
    
    # Feedback info
    feedback_id: UUID = Field(..., description="Feedback identifier")
    feedback_source: str = Field(..., description="Source of feedback")
    feedback_category: str = Field(..., description="Category of feedback")
    
    # Application info
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    applied_by: str = Field(..., description="Component that applied feedback")
    
    # Impact info
    impact_type: str = Field(..., description="Type of impact (weight_adjustment, doctrine_change, etc)")
    impact_details: Dict[str, Any] = Field(default_factory=dict, description="Details of impact")
    
    # Result info
    affected_plans: List[str] = Field(default_factory=list, description="Plans affected")
    plan_selection_changed: bool = Field(False, description="Whether plan selection changed")
    reasoning: str = Field(..., description="Reasoning for applying feedback")


class FeedbackAuditLogger:
    """Logs feedback usage in planning."""
    
    def __init__(self):
        self._entries: List[FeedbackAuditEntry] = []
        self._max_entries = 10000
    
    async def log_feedback_application(
        self,
        planning_run_id: UUID,
        feedback_id: UUID,
        feedback_source: str,
        feedback_category: str,
        applied_by: str,
        impact_type: str,
        impact_details: Dict[str, Any],
        affected_plans: List[str],
        plan_selection_changed: bool,
        reasoning: str,
    ) -> FeedbackAuditEntry:
        """Log feedback application to planning.
        
        Args:
            planning_run_id: ID of planning run
            feedback_id: ID of feedback applied
            feedback_source: Source of feedback
            feedback_category: Category of feedback
            applied_by: Component that applied feedback
            impact_type: Type of impact
            impact_details: Details of impact
            affected_plans: Plans affected
            plan_selection_changed: Whether selection changed
            reasoning: Reasoning for applying feedback
            
        Returns:
            Audit entry
        """
        entry = FeedbackAuditEntry(
            planning_run_id=planning_run_id,
            feedback_id=feedback_id,
            feedback_source=feedback_source,
            feedback_category=feedback_category,
            applied_by=applied_by,
            impact_type=impact_type,
            impact_details=impact_details,
            affected_plans=affected_plans,
            plan_selection_changed=plan_selection_changed,
            reasoning=reasoning,
        )
        
        self._entries.append(entry)
        
        # Trim old entries
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
        
        logger.info(
            f"Feedback audit: applied {feedback_source} ({feedback_category}) "
            f"to planning run {planning_run_id}"
        )
        
        return entry
    
    async def get_entries(
        self,
        planning_run_id: Optional[UUID] = None,
        feedback_id: Optional[UUID] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[FeedbackAuditEntry]:
        """Get audit entries with filters."""
        results = []
        
        for entry in reversed(self._entries):
            if planning_run_id and entry.planning_run_id != planning_run_id:
                continue
            if feedback_id and entry.feedback_id != feedback_id:
                continue
            if since and entry.applied_at < since:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get feedback usage statistics."""
        total = len(self._entries)
        
        if total == 0:
            return {
                "total_applications": 0,
                "plan_selection_changed_count": 0,
            }
        
        changed = sum(1 for e in self._entries if e.plan_selection_changed)
        
        # By category
        by_category: Dict[str, int] = {}
        for entry in self._entries:
            by_category[entry.feedback_category] = by_category.get(entry.feedback_category, 0) + 1
        
        # By impact type
        by_impact: Dict[str, int] = {}
        for entry in self._entries:
            by_impact[entry.impact_type] = by_impact.get(entry.impact_type, 0) + 1
        
        return {
            "total_applications": total,
            "plan_selection_changed_count": changed,
            "plan_selection_changed_rate": changed / total,
            "by_category": by_category,
            "by_impact": by_impact,
        }
    
    async def get_feedback_impact_summary(self, feedback_id: UUID) -> Dict[str, Any]:
        """Get impact summary for a specific feedback item."""
        entries = [e for e in self._entries if e.feedback_id == feedback_id]
        
        if not entries:
            return {"feedback_id": str(feedback_id), "applications": 0}
        
        changed = sum(1 for e in entries if e.plan_selection_changed)
        
        return {
            "feedback_id": str(feedback_id),
            "applications": len(entries),
            "plan_selection_changed_count": changed,
            "affected_plans": list(set(p for e in entries for p in e.affected_plans)),
        }


# Singleton
_feedback_audit_logger: Optional[FeedbackAuditLogger] = None


def get_feedback_audit_logger() -> FeedbackAuditLogger:
    """Get feedback audit logger singleton."""
    global _feedback_audit_logger
    if _feedback_audit_logger is None:
        _feedback_audit_logger = FeedbackAuditLogger()
    return _feedback_audit_logger
