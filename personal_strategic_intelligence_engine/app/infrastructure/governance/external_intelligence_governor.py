"""External Intelligence Governor.

This module provides policy enforcement for all external intelligence actions.
It ensures that reasoning, code generation, and repository modifications
pass through appropriate approval layers.
"""
from enum import Enum
from typing import Any, Optional
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


class ActionType(Enum):
    """Types of external intelligence actions."""
    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    REPOSITORY_READ = "repository_read"
    REPOSITORY_WRITE = "repository_write"
    SYSTEM_CHANGE = "system_change"


class ApprovalLevel(Enum):
    """Required approval levels for actions."""
    NONE = "none"           # No approval needed
    AUTOMATIC = "automatic" # Automatic approval
    COUNCIL = "council"     # Chief Officer approval
    CEO = "ceo"             # CEO approval required


class GovernancePolicy:
    """Defines approval requirements for different action types."""
    
    # Map action types to required approval levels
    APPROVAL_REQUIREMENTS = {
        ActionType.REASONING: ApprovalLevel.AUTOMATIC,
        ActionType.CODE_ANALYSIS: ApprovalLevel.AUTOMATIC,
        ActionType.CODE_GENERATION: ApprovalLevel.COUNCIL,
        ActionType.REPOSITORY_READ: ApprovalLevel.AUTOMATIC,
        ActionType.REPOSITORY_WRITE: ApprovalLevel.CEO,
        ActionType.SYSTEM_CHANGE: ApprovalLevel.CEO,
    }
    
    @classmethod
    def get_approval_level(cls, action_type: ActionType) -> ApprovalLevel:
        """Get the required approval level for an action type."""
        return cls.APPROVAL_REQUIREMENTS.get(action_type, ApprovalLevel.CEO)


class ExternalIntelligenceGovernor:
    """Governs all external intelligence operations."""

    def __init__(self):
        """Initialize the governor."""
        self.enabled = True
        self._audit_log = []
        
    def approve(self, action_type: ActionType, context: Optional[dict] = None) -> dict[str, Any]:
        """Check if an action is approved based on policy.
        
        Args:
            action_type: The type of action to evaluate
            context: Additional context for the decision
            
        Returns:
            Approval decision with details
        """
        required_level = GovernancePolicy.get_approval_level(action_type)
        
        if not self.enabled:
            return {
                "approved": False,
                "reason": "Governance is disabled",
                "required_level": required_level.value,
            }
        
        # Log the approval check
        self._log_check(action_type, context)
        
        # Determine approval based on level
        if required_level == ApprovalLevel.NONE:
            return {
                "approved": True,
                "reason": "No approval required",
                "required_level": required_level.value,
            }
        
        elif required_level == ApprovalLevel.AUTOMATIC:
            return {
                "approved": True,
                "reason": "Automatic approval",
                "required_level": required_level.value,
            }
        
        elif required_level == ApprovalLevel.COUNCIL:
            # In practice, this would check for council approval
            # For now, return pending
            return {
                "approved": False,
                "status": "pending_council_approval",
                "reason": "Council approval required",
                "required_level": required_level.value,
            }
        
        elif required_level == ApprovalLevel.CEO:
            return {
                "approved": False,
                "status": "pending_ceo_approval",
                "reason": "CEO approval required",
                "required_level": required_level.value,
            }
        
        return {
            "approved": False,
            "reason": "Unknown action type",
            "required_level": "unknown",
        }

    def approve_reasoning(self, request: dict) -> dict[str, Any]:
        """Approve a reasoning request.
        
        Args:
            request: The reasoning request
            
        Returns:
            Approval decision
        """
        return self.approve(ActionType.REASONING, request)

    def approve_code_generation(self, proposal: dict) -> dict[str, Any]:
        """Approve a code generation request.
        
        Args:
            proposal: The code generation proposal
            
        Returns:
            Approval decision
        """
        return self.approve(ActionType.CODE_GENERATION, proposal)

    def approve_repository_action(self, action: dict) -> dict[str, Any]:
        """Approve a repository action.
        
        Args:
            action: The repository action
            
        Returns:
            Approval decision
        """
        # Determine if this is read or write
        action_type = ActionType.REPOSITORY_WRITE if action.get("write") else ActionType.REPOSITORY_READ
        return self.approve(action_type, action)

    def set_council_approval(self, request_id: str, approved: bool) -> dict[str, Any]:
        """Set council approval for a pending request.
        
        Args:
            request_id: The request ID
            approved: Whether approved
            
        Returns:
            Updated approval status
        """
        logger.info(f"Council decision for {request_id}: {'approved' if approved else 'denied'}")
        
        return {
            "request_id": request_id,
            "approved": approved,
            "approved_by": "council",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def set_ceo_approval(self, request_id: str, approved: bool) -> dict[str, Any]:
        """Set CEO approval for a pending request.
        
        Args:
            request_id: The request ID
            approved: Whether approved
            
        Returns:
            Updated approval status
        """
        logger.info(f"CEO decision for {request_id}: {'approved' if approved else 'denied'}")
        
        return {
            "request_id": request_id,
            "approved": approved,
            "approved_by": "ceo",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _log_check(self, action_type: ActionType, context: Optional[dict]):
        """Log an approval check."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type.value,
            "context": context,
        }
        self._audit_log.append(entry)
        
    def get_pending_requests(self) -> list[dict]:
        """Get all pending approval requests."""
        # In a real implementation, this would query a database
        return []

    def get_governance_status(self) -> dict[str, Any]:
        """Get current governance status."""
        return {
            "enabled": self.enabled,
            "policy": {
                action_type.value: level.value 
                for action_type, level in GovernancePolicy.APPROVAL_REQUIREMENTS.items()
            },
            "pending_requests": len(self.get_pending_requests()),
        }

    def enable(self):
        """Enable governance."""
        self.enabled = True
        logger.info("External intelligence governance enabled")

    def disable(self):
        """Disable governance (emergency use only)."""
        logger.warning("External intelligence governance DISABLED")
        self.enabled = False


# Global instance
_governor: Optional[ExternalIntelligenceGovernor] = None


def get_governor() -> ExternalIntelligenceGovernor:
    """Get the external intelligence governor instance."""
    global _governor
    
    if _governor is None:
        _governor = ExternalIntelligenceGovernor()
    
    return _governor
