"""Cycle logger - records every strategy loop cycle."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.autonomy.loop_types import StrategyLoopCycle
from app.core.logging import get_logger

logger = get_logger(__name__)


class CycleLogger:
    """Records every strategy loop cycle."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_cycle(
        self,
        cycle_id: str,
        trigger_type: str,
        status: str,
        observation_summary: dict,
        changes_count: int,
        adjustments_count: int,
        actions: List[str],
        runtime_ms: int,
        error: Optional[str] = None,
    ) -> None:
        """Log a completed cycle."""
        
        logger.info(
            f"Cycle {cycle_id} logged: {status}, "
            f"changes={changes_count}, adjustments={adjustments_count}, "
            f"runtime={runtime_ms}ms"
        )
    
    async def get_cycle(
        self,
        cycle_id: str,
    ) -> Optional[StrategyLoopCycle]:
        """Get a specific cycle."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategyLoopCycle)
            .where(StrategyLoopCycle.id == cycle_id)
        )
        return result.scalar_one_or_none()
    
    async def get_recent_cycles(
        self,
        limit: int = 20,
    ) -> List[StrategyLoopCycle]:
        """Get recent cycles."""
        
        from sqlalchemy import select, desc
        
        result = await self.session.execute(
            select(StrategyLoopCycle)
            .order_by(desc(StrategyLoopCycle.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_cycle_logger(session: AsyncSession) -> CycleLogger:
    """Get cycle logger instance."""
    return CycleLogger(session)
