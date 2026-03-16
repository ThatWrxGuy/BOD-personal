"""Execution Gate.

This module controls CEO approval for repository modifications and other
high-impact actions. It prevents autonomous changes and ensures human oversight.
"""
import uuid
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timedelta

from app.core.logging import get_logger

logger = get_logger(__name__)


class ProposalStatus(Enum):
    """Status of a proposal."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


class ExecutionGate:
    """Controls execution of high-impact actions."""

    def __init__(self):
        """Initialize the execution gate."""
        self.pending_proposals: dict[str, dict] = {}
        self.expiration_hours = 24
        
    def create_proposal(
        self,
        action_type: str,
        description: str,
        details: dict,
        requester: str = "system"
    ) -> dict[str, Any]:
        """Create a new execution proposal.
        
        Args:
            action_type: Type of action (code_generation, repository_write, etc.)
            description: Human-readable description
            details: Detailed information about the proposal
            requester: Who requested this action
            
        Returns:
            Proposal with ID and status
        """
        proposal_id = str(uuid.uuid4())
        
        proposal = {
            "id": proposal_id,
            "action_type": action_type,
            "description": description,
            "details": details,
            "requester": requester,
            "status": ProposalStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=self.expiration_hours)).isoformat(),
            "approvals": {
                "council": None,
                "ceo": None,
            },
            "execution_result": None,
        }
        
        self.pending_proposals[proposal_id] = proposal
        
        logger.info(f"Created proposal {proposal_id}: {action_type} - {description}")
        
        return {
            "proposal_id": proposal_id,
            "status": proposal["status"],
            "description": description,
            "created_at": proposal["created_at"],
            "expires_at": proposal["expires_at"],
        }

    def request_approval(
        self,
        action_type: str,
        description: str,
        details: dict,
        requester: str = "system"
    ) -> dict[str, Any]:
        """Request approval for an action through the execution gate.
        
        This is the main entry point for requesting execution approval.
        
        Args:
            action_type: Type of action
            description: Description of the action
            details: Detailed information
            requester: Who is requesting
            
        Returns:
            Proposal information
        """
        # Create proposal
        proposal = self.create_proposal(action_type, description, details, requester)
        
        # Determine required approval level
        if action_type in ["repository_write", "system_change"]:
            return {
                "status": "pending_ceo_approval",
                "proposal_id": proposal["proposal_id"],
                "message": "CEO approval required for this action",
                "proposal": self.get_proposal(proposal["proposal_id"]),
            }
        elif action_type == "code_generation":
            return {
                "status": "pending_council_approval",
                "proposal_id": proposal["proposal_id"],
                "message": "Council approval required for code generation",
                "proposal": self.get_proposal(proposal["proposal_id"]),
            }
        else:
            return {
                "status": "auto_approved",
                "proposal_id": proposal["proposal_id"],
                "message": "Action automatically approved",
            }

    def get_proposal(self, proposal_id: str) -> Optional[dict]:
        """Get a proposal by ID.
        
        Args:
            proposal_id: The proposal ID
            
        Returns:
            Proposal details or None
        """
        return self.pending_proposals.get(proposal_id)

    def approve_by_council(self, proposal_id: str, approved: bool, notes: str = "") -> dict[str, Any]:
        """Approve or reject a proposal by the council.
        
        Args:
            proposal_id: The proposal ID
            approved: Whether approved
            notes: Optional notes
            
        Returns:
            Updated proposal status
        """
        proposal = self.pending_proposals.get(proposal_id)
        
        if not proposal:
            return {
                "success": False,
                "error": "Proposal not found",
            }
        
        if proposal["status"] != ProposalStatus.PENDING.value:
            return {
                "success": False,
                "error": f"Proposal is already {proposal['status']}",
            }
        
        proposal["approvals"]["council"] = {
            "approved": approved,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes,
        }
        
        if approved:
            # Check if CEO approval also needed
            if proposal["action_type"] in ["repository_write", "system_change"]:
                # Still need CEO approval
                logger.info(f"Council approved proposal {proposal_id}, awaiting CEO")
            else:
                # Auto-approve for code generation
                proposal["status"] = ProposalStatus.APPROVED.value
                logger.info(f"Council approved proposal {proposal_id}")
        else:
            proposal["status"] = ProposalStatus.REJECTED.value
            logger.info(f"Council rejected proposal {proposal_id}")
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "status": proposal["status"],
            "approved_by": "council",
        }

    def approve_by_ceo(self, proposal_id: str, approved: bool, notes: str = "") -> dict[str, Any]:
        """Approve or reject a proposal by the CEO.
        
        Args:
            proposal_id: The proposal ID
            approved: Whether approved
            notes: Optional notes
            
        Returns:
            Updated proposal status
        """
        proposal = self.pending_proposals.get(proposal_id)
        
        if not proposal:
            return {
                "success": False,
                "error": "Proposal not found",
            }
        
        if proposal["status"] != ProposalStatus.PENDING.value:
            return {
                "success": False,
                "error": f"Proposal is already {proposal['status']}",
            }
        
        proposal["approvals"]["ceo"] = {
            "approved": approved,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes,
        }
        
        if approved:
            proposal["status"] = ProposalStatus.APPROVED.value
            logger.info(f"CEO approved proposal {proposal_id}")
        else:
            proposal["status"] = ProposalStatus.REJECTED.value
            logger.info(f"CEO rejected proposal {proposal_id}")
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "status": proposal["status"],
            "approved_by": "ceo",
        }

    def execute_proposal(self, proposal_id: str, execution_result: Any = None) -> dict[str, Any]:
        """Mark a proposal as executed.
        
        Args:
            proposal_id: The proposal ID
            execution_result: Result of execution
            
        Returns:
            Execution status
        """
        proposal = self.pending_proposals.get(proposal_id)
        
        if not proposal:
            return {
                "success": False,
                "error": "Proposal not found",
            }
        
        if proposal["status"] != ProposalStatus.APPROVED.value:
            return {
                "success": False,
                "error": f"Cannot execute proposal with status: {proposal['status']}",
            }
        
        proposal["status"] = ProposalStatus.EXECUTED.value
        proposal["execution_result"] = execution_result
        proposal["executed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Proposal {proposal_id} executed")
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "status": proposal["status"],
        }

    def get_pending_proposals(self, filter_by: Optional[str] = None) -> list[dict]:
        """Get all pending proposals.
        
        Args:
            filter_by: Optional filter (e.g., "council", "ceo")
            
        Returns:
            List of pending proposals
        """
        pending = []
        
        for proposal in self.pending_proposals.values():
            if proposal["status"] != ProposalStatus.PENDING.value:
                continue
                
            if filter_by == "council":
                if proposal["action_type"] == "code_generation":
                    pending.append(proposal)
            elif filter_by == "ceo":
                if proposal["action_type"] in ["repository_write", "system_change"]:
                    pending.append(proposal)
            else:
                pending.append(proposal)
        
        return pending

    def get_approved_proposals(self) -> list[dict]:
        """Get all approved proposals that haven't been executed."""
        return [
            p for p in self.pending_proposals.values()
            if p["status"] == ProposalStatus.APPROVED.value
        ]

    def expire_proposals(self):
        """Expire proposals that have passed their expiration time."""
        now = datetime.utcnow()
        
        for proposal in self.pending_proposals.values():
            if proposal["status"] == ProposalStatus.PENDING.value:
                expires = datetime.fromisoformat(proposal["expires_at"])
                if now > expires:
                    proposal["status"] = ProposalStatus.EXPIRED.value
                    logger.info(f"Proposal {proposal['id']} expired")

    def get_status(self) -> dict[str, Any]:
        """Get execution gate status."""
        return {
            "total_proposals": len(self.pending_proposals),
            "pending": len(self.get_pending_proposals()),
            "approved": len(self.get_approved_proposals()),
            "executed": sum(
                1 for p in self.pending_proposals.values()
                if p["status"] == ProposalStatus.EXECUTED.value
            ),
        }


# Global instance
_execution_gate: Optional[ExecutionGate] = None


def get_execution_gate() -> ExecutionGate:
    """Get the execution gate instance."""
    global _execution_gate
    
    if _execution_gate is None:
        _execution_gate = ExecutionGate()
    
    return _execution_gate
