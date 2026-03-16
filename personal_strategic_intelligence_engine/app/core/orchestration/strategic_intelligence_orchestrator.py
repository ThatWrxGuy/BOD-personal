"""Strategic Intelligence Orchestrator - BB-CORE-021

Main orchestration service that coordinates all finance intelligence modules.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.core.orchestration.orchestration_models import (
    OrchestrationCycleResult,
    SystemStateSnapshot,
    ActivationDecision,
    CapitalPosture,
    FusedDecision,
    ExecutiveBrief,
    RoutedPriorityItem,
    PriorityLevel,
    SystemStatus,
)

from app.core.orchestration.state_snapshot_engine import (
    StateSnapshotEngine,
    get_state_snapshot_engine,
)
from app.core.orchestration.activation_policy_engine import (
    ActivationPolicyEngine,
    get_activation_policy_engine,
)
from app.core.orchestration.decision_fusion_engine import (
    DecisionFusionEngine,
    get_decision_fusion_engine,
)
from app.core.orchestration.capital_deployment_coordinator import (
    CapitalDeploymentCoordinator,
    get_capital_deployment_coordinator,
)
from app.core.orchestration.priority_router import (
    PriorityRouter,
    get_priority_router,
)

logger = logging.getLogger(__name__)


class StrategicIntelligenceOrchestrator:
    """Coordinates all finance intelligence modules into unified strategic decisions."""
    
    def __init__(self):
        self.snapshot_engine = get_state_snapshot_engine()
        self.activation_engine = get_activation_policy_engine()
        self.fusion_engine = get_decision_fusion_engine()
        self.capital_coordinator = get_capital_deployment_coordinator()
        self.priority_router = get_priority_router()
        
        self._last_result: Optional[OrchestrationCycleResult] = None
    
    def run_cycle(
        self,
        regime: Optional[Dict] = None,
        portfolio: Optional[Dict] = None,
        strategies: Optional[List[Dict]] = None,
        tactical_opportunities: Optional[List[Dict]] = None,
        governance_state: Optional[Dict] = None,
    ) -> OrchestrationCycleResult:
        """Run one complete orchestration cycle."""
        
        start_time = datetime.utcnow()
        
        # Step 1: Build system state snapshot
        snapshot = self.snapshot_engine.build_snapshot(
            regime=regime,
            portfolio=portfolio,
            strategies=strategies,
            tactical_opportunities=tactical_opportunities,
            governance_state=governance_state,
        )
        
        # Step 2: Determine engine activation
        activation = self.activation_engine.determine_activation(snapshot)
        
        # Step 3: Fuse decisions
        fused = self.fusion_engine.fuse_decisions(snapshot, activation)
        
        # Step 4: Determine capital posture
        capital = self.capital_coordinator.determine_posture(snapshot, activation, fused)
        
        # Step 5: Route priority items
        priority_items = self.priority_router.route_items(snapshot, fused, capital.posture)
        
        # Step 6: Generate executive brief
        brief = self._generate_executive_brief(snapshot, activation, capital, fused, priority_items)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Build result
        result = OrchestrationCycleResult(
            timestamp=datetime.utcnow(),
            state_snapshot=snapshot,
            activation=activation,
            capital=capital,
            decision=fused,
            executive_brief=brief,
            cycle_duration_ms=duration,
            engines_consulted=list(activation.engines.keys()),
        )
        
        self._last_result = result
        
        logger.info(f"Orchestration cycle complete: {duration:.1f}ms, "
                   f"action={fused.action}, posture={capital.posture.value}")
        
        return result
    
    def _generate_executive_brief(
        self,
        snapshot: SystemStateSnapshot,
        activation: ActivationDecision,
        capital: CapitalPositionRecommendation,
        fused: FusedDecision,
        priority_items: List[RoutedPriorityItem],
    ) -> ExecutiveBrief:
        """Generate executive brief."""
        
        # Determine system status
        system_status = snapshot.system_status
        
        # Market context
        regime_str = snapshot.current_regime.value if snapshot.current_regime else "Unknown"
        
        # Determine allowed/restricted systems
        allowed = [name for name, status in activation.engines.items() 
                  if status.value == "active"]
        restricted = [name for name, status in activation.engines.items() 
                     if status.value in ["suppressed", "restricted"]]
        
        # Key decision
        if fused.action == "DEPLOY":
            key_decision = f"Deploy capital with {fused.conviction:.0%} conviction"
        elif fused.action == "WITHDRAW":
            key_decision = "Withdraw capital - hostile conditions"
        elif fused.action == "HOLD":
            key_decision = "Hold current positions"
        elif fused.action == "SUPPRESS":
            key_decision = "Suppress all new activity"
        else:
            key_decision = f"Action: {fused.action}"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(snapshot, capital, fused)
        
        # Conditions summary
        conditions = {
            "regime": regime_str,
            "exposure": f"{snapshot.portfolio.total_exposure:.0%}" if snapshot.portfolio else "N/A",
            "risk": snapshot.risk_status,
            "posture": capital.posture.value,
        }
        
        brief = ExecutiveBrief(
            timestamp=datetime.utcnow(),
            system_status=system_status,
            capital_posture=capital.posture,
            market_context=regime_str,
            key_decision=key_decision,
            allowed_systems=allowed,
            restricted_systems=restricted,
            priority_items=[p for p in priority_items if p.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]],
            recommendations=recommendations,
            conditions_summary=conditions,
        )
        
        return brief
    
    def _generate_recommendations(
        self,
        snapshot: SystemStateSnapshot,
        capital: CapitalPositionRecommendation,
        fused: FusedDecision,
    ) -> List[str]:
        """Generate recommendations for the executive."""
        
        recommendations = []
        
        # Capital posture recommendation
        posture_desc = self.capital_coordinator.get_posture_description(capital.posture)
        recommendations.append(f"Capital Posture: {posture_desc}")
        
        # Action recommendation
        if fused.action == "DEPLOY":
            if capital.posture == CapitalPosture.OFFENSIVE:
                recommendations.append("Deploy aggressively to top-ranked opportunities")
            elif capital.posture == CapitalPosture.SELECTIVE:
                recommendations.append("Deploy selectively to high-conviction ideas only")
        elif fused.action == "WITHDRAW":
            recommendations.append("Reduce exposure - hostile market conditions")
        elif fused.action == "HOLD":
            recommendations.append("Maintain current positions - await clearer signals")
        elif fused.action == "SUPPRESS":
            recommendations.append("Suspend new trading activity immediately")
        
        # Risk recommendation
        if snapshot.risk_status == "elevated":
            recommendations.append("Monitor risk closely - elevated conditions")
        elif snapshot.drawdown_breach:
            recommendations.append("URGENT: Review drawdown protection measures")
        
        # Strategy recommendation
        if snapshot.current_regime:
            if snapshot.current_regime.value in ["RISK_ON_TREND", "RISK_ON_MOMENTUM"]:
                recommendations.append("Focus on momentum and trend-following strategies")
            elif snapshot.current_regime.value in ["RISK_OFF_DEFENSIVE", "VOLATILITY_STRESS"]:
                recommendations.append("Prioritize defensive and liquidity-preserving positions")
        
        return recommendations
    
    def get_last_result(self) -> Optional[OrchestrationCycleResult]:
        """Get the last orchestration result."""
        return self._last_result
    
    def get_current_state(self) -> Optional[SystemStateSnapshot]:
        """Get the current system state snapshot."""
        return self.snapshot_engine.get_last_snapshot()
    
    def get_critical_alerts(self) -> List[RoutedPriorityItem]:
        """Get any critical priority alerts."""
        return self.priority_router.get_critical_items()


# Global instance
_strategic_orchestrator: Optional[StrategicIntelligenceOrchestrator] = None


def get_strategic_orchestrator() -> StrategicIntelligenceOrchestrator:
    """Get the strategic intelligence orchestrator."""
    global _strategic_orchestrator
    
    if _strategic_orchestrator is None:
        _strategic_orchestrator = StrategicIntelligenceOrchestrator()
    
    return _strategic_orchestrator
