"""Strategy View Builder - displays strategy pipeline data.

The Strategy View Builder constructs the strategy pipeline view showing
active proposals, debate results, simulation outputs, and governance decisions.
"""
from datetime import datetime
from typing import Any, Dict, List

from app.executive_dashboard.dashboard_models import StrategyOverview


class StrategyViewBuilder:
    """
    Displays strategy pipeline data.
    
    Includes:
    - Active proposals
    - Debate results
    - Simulation outputs
    - Governance decisions
    - Approval queues
    """
    
    def build(self) -> StrategyOverview:
        """
        Build strategy overview.
        
        Returns:
            StrategyOverview with pipeline metrics
        """
        return StrategyOverview(
            active_proposals=0,
            pending_debate=0,
            pending_simulation=0,
            pending_governance=0,
            approved_count=0,
            rejected_count=0,
            recent_proposals=[],
        )
    
    def build_detailed(self) -> Dict[str, Any]:
        """
        Build detailed strategy view.
        
        Returns:
            Dictionary with detailed strategy data
        """
        overview = self.build()
        
        return {
            "summary": overview.dict(),
            "pending_actions": {
                "debate": overview.pending_debate,
                "simulation": overview.pending_simulation,
                "governance": overview.pending_governance,
            },
            "decisions": {
                "approved": overview.approved_count,
                "rejected": overview.rejected_count,
            },
            "recent_proposals": overview.recent_proposals,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def build_proposal_detail(self, proposal_id: str) -> Dict[str, Any]:
        """
        Build detailed view for a specific proposal.
        
        Args:
            proposal_id: The proposal ID
            
        Returns:
            Dictionary with proposal details
        """
        return {
            "proposal_id": proposal_id,
            "status": "active",
            "stage": "governance",
            "debate_results": [],
            "simulation_results": {},
            "governance_decision": None,
            "timestamp": datetime.utcnow().isoformat(),
        }
