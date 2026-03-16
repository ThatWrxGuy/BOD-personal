"""State Snapshot Engine - BB-CORE-021

Builds unified snapshots of system state from all intelligence modules.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.core.orchestration.orchestration_models import (
    SystemStateSnapshot,
    SystemStatus,
    PortfolioState,
    TacticalOpportunity,
    EngineStatus,
    ActivationStatus,
    RegimeType,
)

logger = logging.getLogger(__name__)


class StateSnapshotEngine:
    """Continuously builds unified state snapshots."""
    
    def __init__(self):
        self._last_snapshot: Optional[SystemStateSnapshot] = None
        self._engine_states: Dict[str, EngineStatus] = {}
    
    def build_snapshot(
        self,
        regime: Optional[Dict] = None,
        portfolio: Optional[Dict] = None,
        strategies: Optional[List[Dict]] = None,
        tactical_opportunities: Optional[List[Dict]] = None,
        governance_state: Optional[Dict] = None,
    ) -> SystemStateSnapshot:
        """Build a complete system state snapshot."""
        
        snapshot = SystemStateSnapshot(
            timestamp=datetime.utcnow(),
        )
        
        # Extract regime information
        if regime:
            snapshot.current_regime = RegimeType(regime.get("regime_type", "NEUTRAL_MIXED"))
            snapshot.regime_confidence = regime.get("confidence", 0.5)
        
        # Portfolio state
        if portfolio:
            snapshot.portfolio = PortfolioState(
                total_exposure=portfolio.get("total_exposure", 0.0),
                cash_position=portfolio.get("cash_position", 1.0),
                sector_exposures=portfolio.get("sector_exposures", {}),
                strategy_allocation=portfolio.get("strategy_allocation", {}),
                daily_pnl=portfolio.get("daily_pnl", 0.0),
                total_pnl=portfolio.get("total_pnl", 0.0),
                drawdown_percent=portfolio.get("drawdown_percent", 0.0),
                risk_score=portfolio.get("risk_score", 0.5),
            )
            
            # Check drawdown breach
            snapshot.drawdown_breach = snapshot.portfolio.drawdown_percent > snapshot.max_drawdown_limit
        else:
            # Demo portfolio state
            snapshot.portfolio = PortfolioState(
                total_exposure=0.35,
                cash_position=0.65,
                sector_exposures={"tech": 0.15, "healthcare": 0.10, "financials": 0.10},
                strategy_allocation={"momentum": 0.20, "defensive": 0.15},
                daily_pnl=0.002,
                total_pnl=0.05,
                drawdown_percent=0.03,
                risk_score=0.35,
            )
            snapshot.drawdown_breach = False
        
        # Active strategies
        if strategies:
            snapshot.active_strategies = [s.get("id", "") for s in strategies if s.get("active")]
            snapshot.approved_strategies = [s.get("id", "") for s in strategies if s.get("approved")]
            snapshot.restricted_strategies = [s.get("id", "") for s in strategies if s.get("restricted")]
        else:
            # Demo strategies
            snapshot.active_strategies = ["momentum_breakout", "liquidity_sweep_reversal", "vwap_reclaim"]
            snapshot.approved_strategies = ["momentum_breakout", "trend_continuation"]
            snapshot.restricted_strategies = []
        
        # Tactical opportunities
        if tactical_opportunities:
            snapshot.tactical_opportunities = [
                TacticalOpportunity(
                    opportunity_id=opp.get("id", ""),
                    source=opp.get("source", ""),
                    description=opp.get("description", ""),
                    direction=opp.get("direction", "long"),
                    confidence=opp.get("confidence", 0.5),
                    expected_return=opp.get("expected_return", 0.0),
                    risk_level=opp.get("risk_level", "moderate"),
                    size_recommendation=opp.get("size", 0.0),
                )
                for opp in tactical_opportunities
            ]
        else:
            # Demo tactical opportunities
            snapshot.tactical_opportunities = [
                TacticalOpportunity(
                    opportunity_id="spy_0dte_001",
                    source="SPY 0DTE Agent",
                    description="SPY 450 call - breakout momentum",
                    direction="long",
                    confidence=0.72,
                    expected_return=0.015,
                    risk_level="moderate",
                    size_recommendation=0.02,
                )
            ]
        
        # Engine statuses
        snapshot.engine_statuses = self._get_engine_statuses(regime, portfolio)
        
        # Governance state
        if governance_state:
            snapshot.execution_enabled = governance_state.get("execution_enabled", True)
            snapshot.approval_required = governance_state.get("approval_required", True)
            snapshot.pending_approvals = governance_state.get("pending_approvals", 0)
        else:
            snapshot.execution_enabled = True
            snapshot.approval_required = True
            snapshot.pending_approvals = 0
        
        # Determine overall system status
        snapshot.system_status = self._determine_system_status(snapshot)
        
        # Risk status
        if snapshot.drawdown_breach:
            snapshot.risk_status = "emergency"
        elif snapshot.portfolio and snapshot.portfolio.risk_score > 0.7:
            snapshot.risk_status = "elevated"
        else:
            snapshot.risk_status = "normal"
        
        self._last_snapshot = snapshot
        
        logger.info(f"Built system snapshot: regime={snapshot.current_regime}, "
                   f"exposure={snapshot.portfolio.total_exposure if snapshot.portfolio else 'N/A'}")
        
        return snapshot
    
    def _get_engine_statuses(
        self,
        regime: Optional[Dict],
        portfolio: Optional[Dict],
    ) -> Dict[str, EngineStatus]:
        """Get current status of all engines."""
        
        statuses = {}
        
        # Market Regime Engine
        statuses["market_regime"] = EngineStatus(
            engine_name="Market Regime Intelligence",
            status=ActivationStatus.ACTIVE,
            metadata={"last_classification": regime.get("regime_type") if regime else "RISK_ON_TREND"},
        )
        
        # Strategy Lab
        statuses["strategy_lab"] = EngineStatus(
            engine_name="Strategy Lab",
            status=ActivationStatus.ACTIVE,
            metadata={"strategies_loaded": 8},
        )
        
        # Security Selection
        statuses["security_selection"] = EngineStatus(
            engine_name="Security Selection",
            status=ActivationStatus.ACTIVE,
        )
        
        # SPY 0DTE Agent - check regime for activation
        regime_type = regime.get("regime_type") if regime else "RISK_ON_TREND"
        
        if regime_type in ["RISK_OFF_DEFENSIVE", "VOLATILITY_STRESS"]:
            statuses["spy_0dte"] = EngineStatus(
                engine_name="SPY 0DTE Agent",
                status=ActivationStatus.SUPPRESSED,
                reason="Hostile regime",
            )
        else:
            statuses["spy_0dte"] = EngineStatus(
                engine_name="SPY 0DTE Agent",
                status=ActivationStatus.ACTIVE,
            )
        
        # Portfolio Engine
        statuses["portfolio"] = EngineStatus(
            engine_name="Portfolio Management",
            status=ActivationStatus.ACTIVE,
        )
        
        return statuses
    
    def _determine_system_status(self, snapshot: SystemStateSnapshot) -> SystemStatus:
        """Determine overall system status."""
        
        # Check emergency conditions
        if snapshot.drawdown_breach:
            return SystemStatus.EMERGENCY
        
        if snapshot.risk_status == "elevated":
            return SystemStatus.RESTRICTED
        
        # Check if execution is enabled
        if not snapshot.execution_enabled:
            return SystemStatus.RESTRICTED
        
        return SystemStatus.ACTIVE
    
    def get_last_snapshot(self) -> Optional[SystemStateSnapshot]:
        """Get the last generated snapshot."""
        return self._last_snapshot


# Global instance
_state_snapshot_engine: Optional[StateSnapshotEngine] = None


def get_state_snapshot_engine() -> StateSnapshotEngine:
    """Get the state snapshot engine."""
    global _state_snapshot_engine
    
    if _state_snapshot_engine is None:
        _state_snapshot_engine = StateSnapshotEngine()
    
    return _state_snapshot_engine
