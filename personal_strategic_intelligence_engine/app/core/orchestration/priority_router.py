"""Priority Router - BB-CORE-021

Ranks and routes important outputs to executive layers.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.core.orchestration.orchestration_models import (
    SystemStateSnapshot,
    FusedDecision,
    CapitalPosture,
    RoutedPriorityItem,
    PriorityLevel,
)

logger = logging.getLogger(__name__)


class PriorityRouter:
    """Routes priority items to appropriate executive layers."""
    
    def __init__(self):
        self._recent_items: List[RoutedPriorityItem] = []
    
    def route_items(
        self,
        snapshot: SystemStateSnapshot,
        fused_decision: FusedDecision,
        capital_posture: CapitalPosture,
    ) -> List[RoutedPriorityItem]:
        """Route priority items based on current state."""
        
        items = []
        
        # Priority 1: Risk Events (Critical)
        if snapshot.drawdown_breach:
            items.append(RoutedPriorityItem(
                item_id=f"risk_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.utcnow(),
                priority=PriorityLevel.CRITICAL,
                category="risk",
                title="Drawdown Breach Detected",
                description=f"Portfolio drawdown has exceeded {snapshot.max_drawdown_limit:.1%} threshold",
                requires_action=True,
                action_deadline=datetime.utcnow() + timedelta(minutes=30),
                recommended_action="Halt new positions, review risk controls",
                route_to=["CEO", "CFO", "Risk"],
            ))
        
        if snapshot.system_status.value == "emergency":
            items.append(RoutedPriorityItem(
                item_id=f"emergency_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.utcnow(),
                priority=PriorityLevel.CRITICAL,
                category="governance",
                title="System Emergency Status",
                description="System has entered emergency status - all trading halted",
                requires_action=True,
                action_deadline=datetime.utcnow() + timedelta(minutes=15),
                recommended_action="Immediate review required",
                route_to=["CEO", "CFO"],
            ))
        
        # Priority 2: Strategic Decisions (High)
        if fused_decision.action == "DEPLOY" and fused_decision.conviction >= 0.7:
            items.append(RoutedPriorityItem(
                item_id=f"deploy_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.utcnow(),
                priority=PriorityLevel.HIGH,
                category="opportunity",
                title="Capital Deployment Opportunity",
                description=f"High conviction ({fused_decision.conviction:.0%}) signal to deploy capital",
                requires_action=True,
                action_deadline=datetime.utcnow() + timedelta(hours=1),
                recommended_action="Review and approve deployment",
                route_to=["CFO", "Portfolio"],
            ))
        
        if fused_decision.action == "WITHDRAW":
            items.append(RoutedPriorityItem(
                item_id=f"withdraw_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.utcnow(),
                priority=PriorityLevel.HIGH,
                category="risk",
                title="Capital Withdrawal Recommended",
                description="Hostile conditions require capital reduction",
                requires_action=True,
                action_deadline=datetime.utcnow() + timedelta(hours=2),
                recommended_action="Review positions for reduction",
                route_to=["CFO", "Portfolio"],
            ))
        
        # Priority 3: Tactical Opportunities (Medium)
        for opp in snapshot.tactical_opportunities[:2]:
            if opp.confidence >= 0.7:
                items.append(RoutedPriorityItem(
                    item_id=f"tactical_{opp.opportunity_id}",
                    timestamp=datetime.utcnow(),
                    priority=PriorityLevel.MEDIUM,
                    category="opportunity",
                    title=f"Tactical Opportunity: {opp.description}",
                    description=f"Confidence: {opp.confidence:.0%}, Expected return: {opp.expected_return:.2%}",
                    requires_action=False,
                    recommended_action="Review if capital available",
                    route_to=["Portfolio", "Trading"],
                ))
        
        # Priority 4: Regime Changes (Medium)
        if snapshot.current_regime:
            hostile_regimes = ["RISK_OFF_DEFENSIVE", "VOLATILITY_STRESS", "LIQUIDITY_DISLOCATION"]
            if snapshot.current_regime.value in hostile_regimes:
                items.append(RoutedPriorityItem(
                    item_id=f"regime_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    priority=PriorityLevel.MEDIUM,
                    category="strategy",
                    title=f"Hostile Regime: {snapshot.current_regime.value}",
                    description="Market conditions have become hostile - review posture",
                    requires_action=False,
                    recommended_action="Monitor - defensive posture activated",
                    route_to=["Strategy", "Portfolio"],
                ))
        
        # Priority 5: Status Updates (Low)
        items.append(RoutedPriorityItem(
            item_id=f"status_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.utcnow(),
            priority=PriorityLevel.LOW,
            category="governance",
            title="Strategic Intelligence Brief",
            description=f"Capital Posture: {capital_posture.value}, System: {snapshot.system_status.value}",
            requires_action=False,
            recommended_action="Informational only",
            route_to=["CFO"],
        ))
        
        # Store recent items
        self._recent_items.extend(items)
        
        if len(self._recent_items) > 50:
            self._recent_items = self._recent_items[-50:]
        
        logger.info(f"Routed {len(items)} priority items")
        
        return items
    
    def get_critical_items(self) -> List[RoutedPriorityItem]:
        """Get all critical priority items."""
        return [item for item in self._recent_items if item.priority == PriorityLevel.CRITICAL]
    
    def get_high_priority_items(self) -> List[RoutedPriorityItem]:
        """Get all high priority items."""
        return [item for item in self._recent_items if item.priority == PriorityLevel.HIGH]


_priority_router: Optional[PriorityRouter] = None


def get_priority_router() -> PriorityRouter:
    """Get the priority router."""
    global _priority_router
    
    if _priority_router is None:
        _priority_router = PriorityRouter()
    
    return _priority_router
