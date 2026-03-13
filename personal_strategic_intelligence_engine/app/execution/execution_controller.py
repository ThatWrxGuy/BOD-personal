"""Execution controller - central orchestration for execution pipeline."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution.execution_models import (
    ExecutionDecision,
    ExecutionIntent,
    ExecutionOutcome,
    ExecutionRecord,
    ExecutionStatus,
    PolicyGateResult,
    DoctrineGateResult,
    RiskGateResult,
    ExecutionApproval,
    EXECUTION_MODE,
    LIVE_EXECUTION_ENABLED,
    CONFIDENCE_THRESHOLD,
)
from app.execution.execution_intent_builder import get_intent_builder
from app.execution.policy_gate import get_policy_gate
from app.execution.doctrine_gate import get_doctrine_gate
from app.execution.risk_gate import get_risk_gate
from app.execution.approval_gate import get_approval_gate

logger = logging.getLogger(__name__)


class ExecutionController:
    """Central orchestration for the execution pipeline."""

    def __init__(self):
        self.intent_builder = get_intent_builder()
        self.policy_gate = get_policy_gate()
        self.doctrine_gate = get_doctrine_gate()
        self.risk_gate = get_risk_gate()
        self.approval_gate = get_approval_gate()
        
        # Execution records storage
        self._execution_records: Dict[str, ExecutionRecord] = {}

    def create_intent(
        self,
        recommendation_id: str,
        recommendation: Dict[str, Any],
        confidence: float = 0.5,
    ) -> ExecutionIntent:
        """
        Create an execution intent from a recommendation.
        
        Args:
            recommendation_id: ID of the source recommendation
            recommendation: Recommendation dictionary
            confidence: Confidence score
            
        Returns:
            ExecutionIntent ready for validation
        """
        # Safety check
        if LIVE_EXECUTION_ENABLED:
            logger.error("Cannot create execution intent when LIVE_EXECUTION_ENABLED is True")
            raise RuntimeError("Execution blocked: LIVE_EXECUTION_ENABLED is True")
        
        intent = self.intent_builder.build_intent(
            recommendation_id=recommendation_id,
            recommendation=recommendation,
            confidence=confidence,
        )
        
        logger.info(f"Created execution intent: {intent.intent_id}")
        
        return intent

    def validate_intent(
        self,
        intent: ExecutionIntent,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionDecision:
        """
        Validate an execution intent through all gates.
        
        Args:
            intent: The execution intent to validate
            context: Optional context for doctrine evaluation
            
        Returns:
            ExecutionDecision with validation results
        """
        # Run policy gate
        policy_result = self.policy_gate.validate(intent)
        
        # Run doctrine gate
        doctrine_result = self.doctrine_gate.validate(intent, context)
        
        # Run risk gate
        risk_result = self.risk_gate.validate(intent)
        
        # Determine overall approval
        # Must pass all gates
        gates_passed = (
            policy_result.passed and
            doctrine_result.aligned and
            risk_result.passed
        )
        
        # Check confidence threshold
        confidence_ok = intent.confidence >= CONFIDENCE_THRESHOLD
        
        if not confidence_ok:
            logger.warning(f"Intent {intent.intent_id} blocked: confidence {intent.confidence} < {CONFIDENCE_THRESHOLD}")
        
        # Request approval
        approval_result = self.approval_gate.request_approval(intent)
        
        # Determine final decision
        approved = gates_passed and confidence_ok and approval_result.approved
        
        # Create approval record
        approval = ExecutionApproval(
            intent_id=intent.intent_id,
            status=approval_result.status,
            approver_id=approval_result.approver_id or "system",
            reason=approval_result.reason,
            decided_at=datetime.utcnow() if approval_result.status.value in ["approved", "rejected"] else None,
        )
        
        # Build decision
        decision = ExecutionDecision(
            intent_id=intent.intent_id,
            approved=approved,
            status=ExecutionStatus.APPROVED if approved else ExecutionStatus.REJECTED,
            policy_gate=policy_result,
            doctrine_gate=doctrine_result,
            risk_gate=risk_result,
            approval=approval,
            rationale=self._build_rationale(policy_result, doctrine_result, risk_result, confidence_ok),
        )
        
        # Store record
        record = ExecutionRecord(
            record_id=f"record_{intent.intent_id}",
            intent=intent,
            decision=decision,
        )
        
        self._execution_records[intent.intent_id] = record
        
        logger.info(f"Validated intent {intent.intent_id}: approved={approved}")
        
        return decision

    def approve_execution(self, intent_id: str, approver_id: str = "human", reason: str = "") -> bool:
        """
        Approve a pending execution.
        
        Args:
            intent_id: ID of the intent to approve
            approver_id: ID of the approver
            reason: Reason for approval
            
        Returns:
            True if successfully approved
        """
        result = self.approval_gate.approve(intent_id, approver_id, reason)
        
        if result.approved:
            # Update record
            if intent_id in self._execution_records:
                record = self._execution_records[intent_id]
                record.decision.status = ExecutionStatus.APPROVED
                record.decision.approval.status = result.status
                record.updated_at = datetime.utcnow()
        
        return result.approved

    def reject_execution(self, intent_id: str, approver_id: str = "human", reason: str = "") -> bool:
        """
        Reject a pending execution.
        
        Args:
            intent_id: ID of the intent to reject
            approver_id: ID of the rejector
            reason: Reason for rejection
            
        Returns:
            True if successfully rejected
        """
        result = self.approval_gate.reject(intent_id, approver_id, reason)
        
        if not result.approved:
            # Update record
            if intent_id in self._execution_records:
                record = self._execution_records[intent_id]
                record.decision.status = ExecutionStatus.REJECTED
                record.decision.approval.status = result.status
                record.updated_at = datetime.utcnow()
        
        return not result.approved

    def execute(self, intent_id: str) -> ExecutionOutcome:
        """
        Execute an approved intent.
        
        Args:
            intent_id: ID of the intent to execute
            
        Returns:
            ExecutionOutcome with execution result
        """
        # Get record
        record = self._execution_records.get(intent_id)
        
        if not record:
            return ExecutionOutcome(
                outcome_id=f"outcome_{datetime.utcnow().timestamp()}",
                decision_id="",
                intent_id=intent_id,
                status=ExecutionStatus.FAILED,
                error="Intent not found",
            )
        
        # Check if approved
        if record.decision.status != ExecutionStatus.APPROVED:
            return ExecutionOutcome(
                outcome_id=f"outcome_{datetime.utcnow().timestamp()}",
                decision_id=record.decision.decision_id,
                intent_id=intent_id,
                status=ExecutionStatus.REJECTED,
                error="Intent not approved for execution",
            )
        
        # Execute (simulated - no real execution)
        # In production, this would call actual execution handlers
        outcome = ExecutionOutcome(
            outcome_id=f"outcome_{datetime.utcnow().timestamp()}",
            decision_id=record.decision.decision_id,
            intent_id=intent_id,
            status=ExecutionStatus.EXECUTED,
            result={"message": "Execution simulated", "domain": record.intent.domain},
            executed_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        
        # Update record
        record.outcome = outcome
        record.updated_at = datetime.utcnow()
        
        logger.info(f"Executed intent {intent_id}: status={outcome.status.value}")
        
        return outcome

    def get_pending_executions(self) -> List[ExecutionIntent]:
        """Get all pending execution intents."""
        pending_approvals = self.approval_gate.get_pending()
        
        intents = []
        for approval in pending_approvals:
            if approval.intent_id in self._execution_records:
                intents.append(self._execution_records[approval.intent_id].intent)
        
        return intents

    def get_execution_record(self, intent_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by intent ID."""
        return self._execution_records.get(intent_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total = len(self._execution_records)
        approved = sum(1 for r in self._execution_records.values() if r.decision.status == ExecutionStatus.APPROVED)
        rejected = sum(1 for r in self._execution_records.values() if r.decision.status == ExecutionStatus.REJECTED)
        executed = sum(1 for r in self._execution_records.values() if r.outcome and r.outcome.status == ExecutionStatus.EXECUTED)
        
        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "executed": executed,
            "pending": len(self.approval_gate.get_pending()),
            "approval_stats": self.approval_gate.get_statistics(),
        }

    def _build_rationale(
        self,
        policy: PolicyGateResult,
        doctrine: DoctrineGateResult,
        risk: RiskGateResult,
        confidence_ok: bool,
    ) -> str:
        """Build rationale string for the decision."""
        parts = []
        
        if not policy.passed:
            parts.append(f"Policy violations: {', '.join(policy.violations)}")
        
        if not doctrine.aligned:
            parts.append(f"Doctrine misaligned: {doctrine.alignment_level}")
        
        if not risk.passed:
            parts.append(f"Risk too high: {risk.risk_level}")
        
        if not confidence_ok:
            parts.append(f"Confidence below threshold")
        
        if not parts:
            parts.append("All gates passed")
        
        return "; ".join(parts)


# Global controller instance
_controller: Optional["ExecutionController"] = None


def get_execution_controller() -> ExecutionController:
    """Get the global execution controller instance."""
    global _controller
    if _controller is None:
        _controller = ExecutionController()
    return _controller
