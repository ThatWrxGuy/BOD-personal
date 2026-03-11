"""State Model Engine - Maintains system state representation."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.kernel import SystemStateSnapshot
from app.core.logging import get_logger

logger = get_logger(__name__)


class StateModelEngine:
    """Maintains system state representation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._current_state: Optional[Dict[str, Any]] = None
    
    async def capture_snapshot(self) -> SystemStateSnapshot:
        """Capture current system state as a snapshot."""
        
        state = await self.get_current_state()
        
        snapshot = SystemStateSnapshot(
            net_worth=state.get("financial", {}).get("net_worth"),
            total_assets=state.get("financial", {}).get("total_assets"),
            total_liabilities=state.get("financial", {}).get("total_liabilities"),
            cash_reserves=state.get("financial", {}).get("cash_reserves"),
            monthly_income=state.get("financial", {}).get("monthly_income"),
            monthly_expenses=state.get("financial", {}).get("monthly_expenses"),
            risk_tolerance=state.get("risk", {}).get("tolerance"),
            current_risk_exposure=state.get("risk", {}).get("exposure"),
            volatility_index=state.get("risk", {}).get("volatility"),
            market_regime=state.get("market", {}).get("regime"),
            market_sentiment=state.get("market", {}).get("sentiment"),
            goal_progress=state.get("goals", {}),
            system_health_score=state.get("system", {}).get("health_score"),
            active_agents=state.get("system", {}).get("active_agents", 0),
            raw_state=state,
        )
        
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        
        logger.info(f"Captured state snapshot: {snapshot.id}")
        
        return snapshot
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current system state."""
        
        if self._current_state:
            return self._current_state
        
        # Build state from various sources
        self._current_state = {
            "financial": await self._get_financial_state(),
            "risk": await self._get_risk_state(),
            "market": await self._get_market_state(),
            "goals": await self._get_goals_state(),
            "system": await self._get_system_state(),
            "portfolio": await self._get_portfolio_state(),
            "liquidity": await self._get_liquidity_state(),
            "debt": await self._get_debt_state(),
        }
        
        return self._current_state
    
    async def update_state(self, domain: str, updates: Dict[str, Any]) -> None:
        """Update specific domain in state."""
        
        if self._current_state is None:
            await self.get_current_state()
        
        if domain in self._current_state:
            self._current_state[domain].update(updates)
        else:
            self._current_state[domain] = updates
        
        logger.info(f"Updated state domain: {domain}")
    
    async def _get_financial_state(self) -> Dict[str, Any]:
        """Get financial state."""
        
        return {
            "total_assets": 0.0,
            "total_liabilities": 0.0,
            "net_worth": 0.0,
            "cash_reserves": 0.0,
            "monthly_income": 0.0,
            "monthly_expenses": 0.0,
            "savings_rate": 0.0,
        }
    
    async def _get_risk_state(self) -> Dict[str, Any]:
        """Get risk state."""
        
        return {
            "tolerance": 0.5,
            "exposure": 0.0,
            "volatility": 0.2,
            "max_drawdown": 0.0,
            "var_95": 0.0,
        }
    
    async def _get_market_state(self) -> Dict[str, Any]:
        """Get market state."""
        
        return {
            "regime": "NEUTRAL",  # BULL, BEAR, NEUTRAL, VOLATILE
            "sentiment": "NEUTRAL",  # BULLISH, BEARISH, NEUTRAL
            "volatility": 0.2,
            "trend": "SIDEWAYS",
        }
    
    async def _get_goals_state(self) -> Dict[str, Any]:
        """Get goals progress state."""
        
        return {
            "active_goals": 0,
            "completed_goals": 0,
            "overall_progress": 0.0,
        }
    
    async def _get_system_state(self) -> Dict[str, Any]:
        """Get system health state."""
        
        return {
            "health_score": 1.0,
            "active_agents": 6,
            "last_cycle_time": None,
            "uptime_percent": 100.0,
        }
    
    async def _get_portfolio_state(self) -> Dict[str, Any]:
        """Get portfolio state."""
        
        return {
            "total_value": 0.0,
            "positions": [],
            "allocation": {},
            "performance": 0.0,
        }
    
    async def _get_liquidity_state(self) -> Dict[str, Any]:
        """Get liquidity state."""
        
        return {
            "available_cash": 0.0,
            "liquid_assets": 0.0,
            "illiquid_assets": 0.0,
            "liquidity_ratio": 0.0,
        }
    
    async def _get_debt_state(self) -> Dict[str, Any]:
        """Get debt state."""
        
        return {
            "total_debt": 0.0,
            "debt_to_income": 0.0,
            "debt_service_ratio": 0.0,
            "credit_available": 0.0,
        }
    
    async def get_latest_snapshot(self) -> Optional[SystemStateSnapshot]:
        """Get the most recent state snapshot."""
        
        result = await self.session.execute(
            select(SystemStateSnapshot)
            .order_by(SystemStateSnapshot.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_snapshots(self, limit: int = 10) -> list[SystemStateSnapshot]:
        """Get recent state snapshots."""
        
        result = await self.session.execute(
            select(SystemStateSnapshot)
            .order_by(SystemStateSnapshot.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_state_model_engine(session: AsyncSession) -> StateModelEngine:
    """Get state model engine instance."""
    return StateModelEngine(session)
