"""Strategic Priority Engine - Dynamic priority management."""
import uuid
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.kernel import StrategicPriority, PriorityType
from app.kernel.state_model.state_model_engine import StateModelEngine
from app.core.logging import get_logger

logger = get_logger(__name__)


class PriorityEngine:
    """Manages dynamic strategic priorities."""
    
    DEFAULT_PRIORITIES = [
        {
            "name": "preserve_liquidity",
            "type": PriorityType.PRESERVATION,
            "weight": 0.3,
            "description": "Maintain adequate cash reserves",
        },
        {
            "name": "reduce_debt_pressure",
            "type": PriorityType.PRESERVATION,
            "weight": 0.25,
            "description": "Pay down high-interest debt",
        },
        {
            "name": "grow_capital_base",
            "type": PriorityType.GROWTH,
            "weight": 0.2,
            "description": "Increase investment and savings",
        },
        {
            "name": "improve_efficiency",
            "type": PriorityType.EFFICIENCY,
            "weight": 0.15,
            "description": "Optimize operational processes",
        },
        {
            "name": "protect_wellbeing",
            "type": PriorityType.PROTECTION,
            "weight": 0.1,
            "description": "Maintain health and cognitive bandwidth",
        },
    ]
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.state_engine = StateModelEngine(session)
        self._current_priorities: List[Dict[str, Any]] = []
    
    async def initialize_priorities(self) -> None:
        """Initialize default priorities if none exist."""
        
        result = await self.session.execute(select(StrategicPriority))
        existing = list(result.scalars().all())
        
        if not existing:
            for i, p in enumerate(self.DEFAULT_PRIORITIES):
                priority = StrategicPriority(
                    priority_name=p["name"],
                    priority_type=p["type"],
                    priority_weight=p["weight"],
                    priority_order=i,
                    is_active=True,
                )
                self.session.add(priority)
            
            await self.session.commit()
            logger.info("Initialized default priorities")
    
    async def update_priorities(self) -> List[Dict[str, Any]]:
        """Update priorities based on current state."""
        
        state = await self.state_engine.get_current_state()
        
        # Adjust weights based on state
        adjustments = self._calculate_adjustments(state)
        
        result = await self.session.execute(
            select(StrategicPriority).order_by(StrategicPriority.priority_order)
        )
        priorities = list(result.scalars().all())
        
        updated = []
        for priority in priorities:
            adjustment = adjustments.get(priority.priority_name, 0)
            new_weight = max(0.05, min(1.0, priority.priority_weight + adjustment))
            priority.priority_weight = new_weight
            
            updated.append({
                "name": priority.priority_name,
                "type": priority.priority_type,
                "weight": new_weight,
                "is_active": priority.is_active,
            })
        
        await self.session.commit()
        
        self._current_priorities = updated
        logger.info("Updated strategic priorities")
        
        return updated
    
    def _calculate_adjustments(self, state: Dict[str, Any]) -> Dict[str, float]:
        """Calculate priority weight adjustments based on state."""
        
        adjustments = {}
        
        # Financial state adjustments
        financial = state.get("financial", {})
        net_worth = financial.get("net_worth", 0)
        savings_rate = financial.get("savings_rate", 0)
        
        if net_worth < 10000:
            adjustments["preserve_liquidity"] = 0.15
            adjustments["reduce_debt_pressure"] = 0.1
            adjustments["grow_capital_base"] = -0.15
        elif net_worth < 50000:
            adjustments["preserve_liquidity"] = 0.05
            adjustments["grow_capital_base"] = 0.05
        else:
            adjustments["grow_capital_base"] = 0.1
        
        # Debt pressure
        debt = state.get("debt", {})
        dti = debt.get("debt_to_income", 0)
        
        if dti > 0.4:
            adjustments["reduce_debt_pressure"] = 0.2
            adjustments["grow_capital_base"] = -0.1
        elif dti > 0.2:
            adjustments["reduce_debt_pressure"] = 0.1
        
        # Market conditions
        market = state.get("market", {})
        regime = market.get("regime", "NEUTRAL")
        
        if regime == "BEAR" or regime == "VOLATILE":
            adjustments["preserve_liquidity"] = adjustments.get("preserve_liquidity", 0) + 0.1
            adjustments["protect_wellbeing"] = adjustments.get("protect_wellbeing", 0) + 0.05
        elif regime == "BULL":
            adjustments["grow_capital_base"] = adjustments.get("grow_capital_base", 0) + 0.1
        
        return adjustments
    
    async def get_active_priorities(self) -> List[Dict[str, Any]]:
        """Get currently active priorities."""
        
        if self._current_priorities:
            return self._current_priorities
        
        result = await self.session.execute(
            select(StrategicPriority)
            .where(StrategicPriority.is_active == True)
            .order_by(StrategicPriority.priority_weight.desc())
        )
        
        priorities = list(result.scalars().all())
        
        self._current_priorities = [
            {
                "name": p.priority_name,
                "type": p.priority_type,
                "weight": p.priority_weight,
                "order": p.priority_order,
            }
            for p in priorities
        ]
        
        return self._current_priorities
    
    async def get_top_priority(self) -> Dict[str, Any]:
        """Get the current top priority."""
        
        priorities = await self.get_active_priorities()
        
        if priorities:
            return priorities[0]
        
        return {"name": "maintain_stability", "weight": 0.5}


async def get_priority_engine(session: AsyncSession) -> PriorityEngine:
    """Get priority engine instance."""
    engine = PriorityEngine(session)
    await engine.initialize_priorities()
    return engine
