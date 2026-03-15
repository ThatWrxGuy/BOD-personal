"""Approval gate - human approval interface for execution."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.execution.execution_models import (
    ApprovalGateResult,
    ApprovalStatus,
    ApprovalGateResult,
    ExecutionApproval,
    ExecutionIntent,
    EXECUTION_COOLDOWN_HOURS,
)

logger = logging.getLogger(__name__)


class ApprovalGate:
    """Manages approval workflow for execution intents."""

    def __init__(self, approval_required: bool = True):
        self._approval_required = approval_required
        self._pending_approvals: Dict[str, ExecutionApproval] = {}
        self._approval_history: List[ExecutionApproval] = []
        self._cooldown_tracker: Dict[str, datetime] = {}

    def request_approval(self, intent: ExecutionIntent) -> ApprovalGateResult:
        """
        Request approval for an execution intent.
        
        Args:
            intent: The execution intent to approve
            
        Returns:
            ApprovalGateResult with approval status
        """
        # Check cooldown
        if self._is_in_cooldown(intent):
            return ApprovalGateResult(
                approved=False,
                status=ApprovalStatus.PENDING,
                reason=f"Domain {intent.domain} is in cooldown period",
            )
        
        # If approval not required, auto-approve
        if not self._approval_required:
            approval = self._create_approval(
                intent.intent_id,
                ApprovalStatus.APPROVED,
                "auto_approved",
                "Automatic approval - not required",
            )
            return ApprovalGateResult(
                approved=True,
                status=ApprovalStatus.APPROVED,
                approver_id="system",
                reason="Auto-approved - approval not required",
            )
        
        # Create pending approval
        approval = self._create_approval(
            intent.intent_id,
            ApprovalStatus.PENDING,
            "system",
            "Pending human approval",
        )
        
        self._pending_approvals[intent.intent_id] = approval
        
        return ApprovalGateResult(
            approved=False,
            status=ApprovalStatus.PENDING,
            reason="Approval pending human review",
        )

    def approve(
        self,
        intent_id: str,
        approver_id: str = "human",
        reason: str = "",
    ) -> ApprovalGateResult:
        """
        Approve a pending execution intent.
        
        Args:
            intent_id: ID of the intent to approve
            approver_id: ID of the approver
            reason: Reason for approval
            
        Returns:
            ApprovalGateResult with approval status
        """
        approval = self._pending_approvals.get(intent_id)
        
        if not approval:
            # Check if already decided
            for hist in self._approval_history:
                if hist.intent_id == intent_id:
                    return ApprovalGateResult(
                        approved=hist.status == ApprovalStatus.APPROVED,
                        status=hist.status,
                        approver_id=hist.approver_id,
                        reason=f"Already decided: {hist.reason}",
                    )
            
            return ApprovalGateResult(
                approved=False,
                status=ApprovalStatus.REJECTED,
                reason="Intent not found in pending approvals",
            )
        
        # Update approval
        approval.status = ApprovalStatus.APPROVED
        approval.approver_id = approver_id
        approval.decided_at = datetime.utcnow()
        approval.reason = reason
        
        # Move from pending to history
        del self._pending_approvals[intent_id]
        self._approval_history.append(approval)
        
        # Set cooldown
        self._update_cooldown(intent_id)
        
        logger.info(f"Approved execution intent: {intent_id}")
        
        return ApprovalGateResult(
            approved=True,
            status=ApprovalStatus.APPROVED,
            approver_id=approver_id,
            reason=reason,
        )

    def reject(
        self,
        intent_id: str,
        approver_id: str = "human",
        reason: str = "",
    ) -> ApprovalGateResult:
        """
        Reject a pending execution intent.
        
        Args:
            intent_id: ID of the intent to reject
            approver_id: ID of the rejector
            reason: Reason for rejection
            
        Returns:
            ApprovalGateResult with rejection status
        """
        approval = self._pending_approvals.get(intent_id)
        
        if not approval:
            return ApprovalGateResult(
                approved=False,
                status=ApprovalStatus.REJECTED,
                reason="Intent not found in pending approvals",
            )
        
        # Update approval
        approval.status = ApprovalStatus.REJECTED
        approval.approver_id = approver_id
        approval.decided_at = datetime.utcnow()
        approval.reason = reason
        
        # Move from pending to history
        del self._pending_approvals[intent_id]
        self._approval_history.append(approval)
        
        logger.info(f"Rejected execution intent: {intent_id} - {reason}")
        
        return ApprovalGateResult(
            approved=False,
            status=ApprovalStatus.REJECTED,
            approver_id=approver_id,
            reason=reason,
        )

    def get_pending(self) -> List[ExecutionApproval]:
        """Get all pending approvals."""
        return list(self._pending_approvals.values())

    def get_approval_status(self, intent_id: str) -> Optional[ApprovalGateResult]:
        """Get approval status for an intent."""
        
        # Check pending
        if intent_id in self._pending_approvals:
            approval = self._pending_approvals[intent_id]
            return ApprovalGateResult(
                approved=False,
                status=approval.status,
                approver_id=approval.approver_id,
                reason=approval.reason,
            )
        
        # Check history
        for approval in self._approval_history:
            if approval.intent_id == intent_id:
                return ApprovalGateResult(
                    approved=approval.status == ApprovalStatus.APPROVED,
                    status=approval.status,
                    approver_id=approval.approver_id,
                    reason=approval.reason,
                )
        
        return None

    def _create_approval(
        self,
        intent_id: str,
        status: ApprovalStatus,
        approver_id: str,
        reason: str,
    ) -> ExecutionApproval:
        """Create a new approval record."""
        return ExecutionApproval(
            intent_id=intent_id,
            status=status,
            approver_id=approver_id,
            reason=reason,
        )

    def _is_in_cooldown(self, intent: ExecutionIntent) -> bool:
        """Check if domain is in cooldown period."""
        last_execution = self._cooldown_tracker.get(intent.domain)
        
        if not last_execution:
            return False
        
        cooldown_period = timedelta(hours=EXECUTION_COOLDOWN_HOURS)
        return datetime.utcnow() - last_execution < cooldown_period

    def _update_cooldown(self, intent_id: str):
        """Update cooldown tracker after approval."""
        # Find the intent to get the domain
        for approval in self._approval_history:
            if approval.intent_id == intent_id:
                # Would need to track domain - simplified for now
                pass

    def get_statistics(self) -> dict:
        """Get approval statistics."""
        return {
            "pending": len(self._pending_approvals),
            "total_approved": sum(1 for a in self._approval_history if a.status == ApprovalStatus.APPROVED),
            "total_rejected": sum(1 for a in self._approval_history if a.status == ApprovalStatus.REJECTED),
        }


# Global gate instance
_gate: Optional["ApprovalGate"] = None


def get_approval_gate() -> ApprovalGate:
    """Get the global approval gate instance."""
    global _gate
    if _gate is None:
        _gate = ApprovalGate()
    return _gate
