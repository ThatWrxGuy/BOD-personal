"""Governance bridge for chat commands.

This module ensures all actionable chat commands go through governance approval.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


# Intents that require governance approval
ACTIONABLE_INTENTS = {
    "run_simulation",
    "start_research",
    "generate_plan",
    "run_review",
    "check_finances",  # Financial actions
    "execute_action",
}

# Intents that are read-only queries
READ_ONLY_INTENTS = {
    "query_risks",
    "query_opportunities",
    "query_goals",
    "system_status",
    "list_bills",
    "check_liquidity",
}


class GovernanceBridge:
    """Bridge between chat commands and governance workflow."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def requires_governance(self, intent: str) -> bool:
        """Check if intent requires governance approval."""
        return intent in ACTIONABLE_INTENTS
    
    async def create_proposal(
        self,
        intent: str,
        message: str,
        parameters: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Create a governance proposal for an actionable command."""
        
        if not await self.requires_governance(intent):
            return None
        
        # Create decision proposal
        from app.decisions.decision_proposal import DecisionProposal
        
        proposal = DecisionProposal(
            title=self._generate_title(intent, message),
            description=message,
            decision_type=intent,
            parameters=parameters,
            status="pending_review",
            requested_by="chat_user",
            priority="medium",
        )
        
        self.session.add(proposal)
        await self.session.commit()
        await self.session.refresh(proposal)
        
        logger.info(f"Created governance proposal {proposal.id} for intent {intent}")
        
        return {
            "proposal_id": str(proposal.id),
            "status": "pending_approval",
            "message": f"Your request requires governance approval. Proposal {proposal.id} is pending review.",
        }
    
    def _generate_title(self, intent: str, message: str) -> str:
        """Generate a title for the proposal."""
        
        intent_titles = {
            "run_simulation": "Simulation Request",
            "start_research": "Research Request",
            "generate_plan": "Strategic Plan Request",
            "run_review": "Review Request",
            "check_finances": "Financial Action Request",
        }
        
        base_title = intent_titles.get(intent, "Action Request")
        
        # Truncate message for title
        if len(message) > 50:
            message = message[:47] + "..."
        
        return f"{base_title}: {message}"
    
    async def check_proposal_status(
        self,
        proposal_id: uuid.UUID,
    ) -> Optional[Dict[str, Any]]:
        """Check the status of a governance proposal."""
        
        from sqlalchemy import select
        from app.decisions.decision_proposal import DecisionProposal
        
        result = await self.session.execute(
            select(DecisionProposal).where(DecisionProposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            return None
        
        return {
            "proposal_id": str(proposal.id),
            "status": proposal.status,
            "title": proposal.title,
            "decided_at": proposal.decided_at.isoformat() if proposal.decided_at else None,
        }


async def get_governance_bridge(session: AsyncSession) -> GovernanceBridge:
    """Get governance bridge instance."""
    return GovernanceBridge(session)
