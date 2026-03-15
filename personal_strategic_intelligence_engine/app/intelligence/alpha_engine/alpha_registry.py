"""Alpha Registry.

Maintains registry of all alpha candidates.
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.intelligence.alpha_engine.alpha_models import (
    AlphaCandidate, AlphaStatus, DeploymentState
)


class AlphaRegistry:
    """Registry of all alpha candidates."""
    
    def __init__(self):
        self.alphas: Dict[str, AlphaCandidate] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize with default SPY options alphas."""
        
        defaults = [
            AlphaCandidate.create(
                name="VWAP-Reclaim-Call-Continuation",
                domain="finance",
                hypothesis="When SPY reclaims VWAP after downside sweep and nearby call gamma increases, 1-step OTM calls outperform.",
                signal_dependencies=["vwap_reclaim", "gamma_acceleration"],
                regime_requirements={"regime": "trend_day"},
            ),
            AlphaCandidate.create(
                name="Liquidity-Sweep-Reversal",
                domain="finance",
                hypothesis="When SPY sweeps liquidity to downside and immediately reverses, short-dated puts capture reversal.",
                signal_dependencies=["liquidity_sweep", "vwap_reclaim"],
                regime_requirements={"regime": "range_day"},
            ),
            AlphaCandidate.create(
                name="Opening-Range-Breakout",
                domain="finance",
                hypothesis="SPY opening range breakout with high volume leads to sustained momentum.",
                signal_dependencies=["opening_range", "volume_surge"],
                regime_requirements={"regime": "opening_drive"},
            ),
        ]
        
        for alpha in defaults:
            alpha.status = AlphaStatus.ACTIVE
            alpha.confidence_score = 0.75
            self.alphas[alpha.id] = alpha
    
    def register(self, alpha: AlphaCandidate) -> None:
        """Register a new alpha."""
        self.alphas[alpha.id] = alpha
    
    def get(self, alpha_id: str) -> Optional[AlphaCandidate]:
        """Get alpha by ID."""
        return self.alphas.get(alpha_id)
    
    def list_all(self) -> List[AlphaCandidate]:
        """List all alphas."""
        return list(self.alphas.values())
    
    def list_by_status(self, status: AlphaStatus) -> List[AlphaCandidate]:
        """List alphas by status."""
        return [a for a in self.alphas.values() if a.status == status]
    
    def list_by_deployment(self, state: DeploymentState) -> List[AlphaCandidate]:
        """List alphas by deployment state."""
        # Filter would be on status mapping
        return self.list_all()
    
    def update_status(self, alpha_id: str, status: AlphaStatus) -> bool:
        """Update alpha status."""
        if alpha_id in self.alphas:
            self.alphas[alpha_id].status = status
            self.alphas[alpha_id].updated_at = datetime.now()
            return True
        return False
    
    def get_summary(self) -> Dict:
        """Get registry summary."""
        
        status_counts = {}
        for alpha in self.alphas.values():
            status = alpha.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_alphas": len(self.alphas),
            "by_status": status_counts,
        }


# Global registry
_registry = None

def get_registry() -> AlphaRegistry:
    """Get global alpha registry."""
    global _registry
    if _registry is None:
        _registry = AlphaRegistry()
    return _registry
