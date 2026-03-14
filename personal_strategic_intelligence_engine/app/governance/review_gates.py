"""Executive Review Gate - Review gate for executive/governance approval.

This gate handles:
- High-risk actions require executive review
- Policy-sensitive actions require governance review
- Low-risk actions can auto-approve
"""
from typing import Optional, List
import logging

from app.governance.review_gate import (
    BaseReviewGate,
    ReviewRequest,
    ReviewResult,
    ReviewDecision,
    ReviewPriority,
    RiskLevel,
    get_review_gate_manager,
)

logger = logging.getLogger(__name__)


class ExecutiveReviewGate(BaseReviewGate):
    """Executive review gate for high-priority decisions.
    
    Routes decisions to executive agents for approval.
    """
    
    def __init__(self):
        super().__init__()
        self.pending_reviews: dict = {}
    
    @property
    def gate_id(self) -> str:
        return "executive_review_gate"
    
    @property
    def gate_type(self) -> str:
        return "executive"
    
    async def check_approval_required(self, request: ReviewRequest) -> bool:
        """Check if executive approval is required."""
        # Always require approval for high/critical risk
        if request.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True
        
        # Check if adjustment type requires review
        review_required_types = [
            "doctrine_change",
            "strategy_change",
            "budget_allocation",
            "risk_mitigation",
            "new_initiative",
        ]
        
        if request.adjustment_type in review_required_types:
            return True
        
        return True  # Default: require approval
    
    async def can_auto_approve(self, request: ReviewRequest) -> bool:
        """Check if can auto-approve."""
        # Never auto-approve critical
        if request.risk_level == RiskLevel.CRITICAL:
            return False
        
        # Auto-approve low-risk internal adjustments
        if request.risk_level == RiskLevel.LOW:
            auto_approve_types = [
                "logging",
                "state_update",
                "internal_optimization",
            ]
            if request.adjustment_type in auto_approve_types:
                return True
        
        return False
    
    async def submit_for_review(self, request: ReviewRequest) -> ReviewResult:
        """Submit for executive review.
        
        In production, this would:
        1. Queue the request
        2. Notify executive agent
        3. Wait for decision
        
        For now, returns a placeholder - in production would integrate with executive agents.
        """
        logger.info(
            f"Executive review: {request.adjustment_type} "
            f"(risk: {request.risk_level.value})"
        )
        
        # Placeholder: In production would call executive agent
        # For now, reject if high/critical risk pending manual review
        if request.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return ReviewResult(
                request_id=request.request_id,
                decision=ReviewDecision.DEFERRED,
                priority=ReviewPriority.HIGH,
                reason=f"Deferred to executive - {request.risk_level.value} risk",
                is_final=False,
            )
        
        # Auto-approve medium risk for now
        return ReviewResult(
            request_id=request.request_id,
            decision=ReviewDecision.APPROVED,
            priority=ReviewPriority.MEDIUM,
            reason="Executive review - approved",
        )


class PolicyReviewGate(BaseReviewGate):
    """Policy review gate for governance compliance.
    
    Validates actions against policies before execution.
    """
    
    def __init__(self):
        super().__init__()
        self.policies: dict = {}
    
    @property
    def gate_id(self) -> str:
        return "policy_review_gate"
    
    @property
    def gate_type(self) -> str:
        return "policy"
    
    async def check_approval_required(self, request: ReviewRequest) -> bool:
        """Check if policy review is required."""
        # Policy-sensitive types always require review
        policy_sensitive = [
            "doctrine_change",
            "policy_update",
            "access_control",
            "resource_allocation",
        ]
        
        if request.adjustment_type in policy_sensitive:
            return True
        
        # High risk always needs policy check
        if request.risk_level == RiskLevel.HIGH:
            return True
        
        return False
    
    async def can_auto_approve(self, request: ReviewRequest) -> bool:
        """Check if can auto-approve based on policy."""
        # Policy changes never auto-approve
        if request.adjustment_type in ["doctrine_change", "policy_update"]:
            return False
        
        return False
    
    async def submit_for_review(self, request: ReviewRequest) -> ReviewResult:
        """Submit for policy review."""
        logger.info(f"Policy review: {request.adjustment_type}")
        
        # Placeholder: In production would check policies
        return ReviewResult(
            request_id=request.request_id,
            decision=ReviewDecision.APPROVED,
            priority=ReviewPriority.MEDIUM,
            reason="Policy review - passed",
        )


# Auto-register gates when module loads
get_review_gate_manager()
