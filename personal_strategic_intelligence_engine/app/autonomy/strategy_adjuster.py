"""Strategy adjuster - generates strategic adjustments from detected changes."""
import uuid
from typing import List, Dict, Any, Optional

from app.autonomy.loop_types import (
    ChangeEvent, 
    StrategicAdjustment, 
    AdjustmentType,
    ChangeSeverity,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategyAdjuster:
    """Generates strategic adjustments based on detected changes."""
    
    def __init__(self):
        pass
    
    async def generate_adjustments(
        self,
        changes: List[ChangeEvent],
    ) -> List[StrategicAdjustment]:
        """Generate adjustments from detected changes."""
        
        adjustments = []
        
        for change in changes:
            adjustment = await self._generate_adjustment(change)
            if adjustment:
                adjustments.append(adjustment)
        
        return adjustments
    
    async def _generate_adjustment(
        self,
        change: ChangeEvent,
    ) -> Optional[StrategicAdjustment]:
        """Generate adjustment for a single change."""
        
        # Determine adjustment based on change category and severity
        if change.category.value == "risk_increase":
            return await self._handle_risk_increase(change)
        
        elif change.category.value == "opportunity_emerge":
            return await self._handle_opportunity_emerge(change)
        
        elif change.category.value == "habit_decline":
            return await self._handle_habit_decline(change)
        
        elif change.category.value == "goal_progress_accelerate":
            return await self._handle_goal_accelerate(change)
        
        elif change.category.value == "execution_overload":
            return await self._handle_execution_overload(change)
        
        elif change.category.value == "focus_misalign":
            return await self._handle_focus_misalign(change)
        
        # No adjustment for other changes
        return None
    
    async def _handle_risk_increase(
        self,
        change: ChangeEvent,
    ) -> StrategicAdjustment:
        """Handle increased risk."""
        
        if change.severity == ChangeSeverity.CRITICAL:
            return StrategicAdjustment(
                adjustment_id=str(uuid.uuid4()),
                adjustment_type=AdjustmentType.INCREASE_RISK_MITIGATION,
                reason=change.explanation,
                domain=change.domain,
                target="risk_mitigation",
                parameters={"severity": "critical"},
            )
        
        elif change.severity == ChangeSeverity.HIGH:
            return StrategicAdjustment(
                adjustment_id=str(uuid.uuid4()),
                adjustment_type=AdjustmentType.REGENERATE_DAILY_PLAN,
                reason=f"Risk increase detected: {change.explanation}",
                domain=change.domain,
                parameters={"focus": "risk_mitigation"},
            )
        
        return None
    
    async def _handle_opportunity_emerge(
        self,
        change: ChangeEvent,
    ) -> StrategicAdjustment:
        """Handle new opportunity."""
        
        return StrategicAdjustment(
            adjustment_id=str(uuid.uuid4()),
            adjustment_type=AdjustmentType.INCREASE_OPPORTUNITY_RESPONSE,
            reason=f"New opportunity: {change.explanation}",
            domain=change.domain,
            parameters={"new_opportunities": change.current_value},
        )
    
    async def _handle_habit_decline(
        self,
        change: ChangeEvent,
    ) -> StrategicAdjustment:
        """Handle habit streak decline."""
        
        return StrategicAdjustment(
            adjustment_id=str(uuid.uuid4()),
            adjustment_type=AdjustmentType.INCREASE_RECOVERY,
            reason=f"Habit decline: {change.explanation}",
            domain=change.domain,
            parameters={"focus": "habit_recovery"},
        )
    
    async def _handle_goal_accelerate(
        self,
        change: ChangeEvent,
    ) -> StrategicAdjustment:
        """Handle goal progress acceleration."""
        
        return StrategicAdjustment(
            adjustment_id=str(uuid.uuid4()),
            adjustment_type=AdjustmentType.ACCELERATE_INITIATIVE,
            reason=f"Goal progressing well: {change.explanation}",
            domain=change.domain,
            parameters={"progress_increase": change.current_value - change.prior_value},
        )
    
    async def _handle_execution_overload(
        self,
        change: ChangeEvent,
    ) -> StrategicAdjustment:
        """Handle execution overload."""
        
        return StrategicAdjustment(
            adjustment_id=str(uuid.uuid4()),
            adjustment_type=AdjustmentType.REDUCE_PRIORITY,
            reason=f"Execution overload: {change.explanation}",
            domain=change.domain,
            parameters={"action": "reduce_workload"},
        )
    
    async def _handle_focus_misalign(
        self,
        change: ChangeEvent,
    ) -> StrategicAdjustment:
        """Handle focus misalignment."""
        
        return StrategicAdjustment(
            adjustment_id=str(uuid.uuid4()),
            adjustment_type=AdjustmentType.REBALANCE_WEEKLY_THEME,
            reason=f"Focus misaligned: {change.explanation}",
            domain=change.domain,
            parameters={},
        )
    
    async def apply_cooldown(
        self,
        adjustments: List[StrategicAdjustment],
        recent_adjustments: List[StrategicAdjustment],
    ) -> List[StrategicAdjustment]:
        """Apply cooldown logic to prevent rapid oscillations."""
        
        # Filter out adjustments that happened recently
        filtered = []
        
        for adj in adjustments:
            # Check if similar adjustment was made recently
            is_duplicate = False
            for recent in recent_adjustments:
                if (recent.adjustment_type == adj.adjustment_type and
                    recent.domain == adj.domain):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(adj)
        
        return filtered


async def get_strategy_adjuster() -> StrategyAdjuster:
    """Get strategy adjuster instance."""
    return StrategyAdjuster()
