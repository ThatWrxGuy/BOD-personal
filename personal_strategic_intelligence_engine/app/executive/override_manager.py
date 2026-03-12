"""Override manager - handles operator overrides."""
import uuid
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.executive.command_types import OverrideLog, AutonomyOverride
from app.core.logging import get_logger

logger = get_logger(__name__)


class OverrideManager:
    """Manages operator overrides."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def pause_autonomy(self, issued_by: str = "operator") -> Dict[str, Any]:
        """Pause autonomous strategy loop."""
        
        # Check if already paused
        from sqlalchemy import select
        result = await self.session.execute(
            select(AutonomyOverride)
            .where(AutonomyOverride.is_active == True)
            .where(AutonomyOverride.override_type == "pause_autonomy")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return {"status": "already_paused", "override_id": str(existing.id)}
        
        # Create pause override
        override = AutonomyOverride(
            override_type="pause_autonomy",
            is_active=True,
            started_at=datetime.utcnow(),
            issued_by=issued_by,
            reason="Operator requested pause",
        )
        self.session.add(override)
        
        # Log the override
        log = OverrideLog(
            override_id=str(uuid.uuid4()),
            override_type="pause_autonomy",
            issued_by=issued_by,
            reason="Operator requested pause",
            status="applied",
        )
        self.session.add(log)
        
        await self.session.commit()
        
        logger.info(f"Autonomy paused by {issued_by}")
        
        return {
            "status": "paused",
            "override_id": str(override.id),
            "issued_by": issued_by,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def resume_autonomy(self, issued_by: str = "operator") -> Dict[str, Any]:
        """Resume autonomous strategy loop."""
        
        # Find active pause override
        from sqlalchemy import select, update
        result = await self.session.execute(
            select(AutonomyOverride)
            .where(AutonomyOverride.is_active == True)
            .where(AutonomyOverride.override_type == "pause_autonomy")
        )
        override = result.scalar_one_or_none()
        
        if not override:
            return {"status": "not_paused"}
        
        # End the override
        override.is_active = False
        override.ended_at = datetime.utcnow()
        
        # Log the override
        log = OverrideLog(
            override_id=str(uuid.uuid4()),
            override_type="resume_autonomy",
            issued_by=issued_by,
            reason="Operator requested resume",
            status="applied",
        )
        self.session.add(log)
        
        await self.session.commit()
        
        logger.info(f"Autonomy resumed by {issued_by}")
        
        return {
            "status": "resumed",
            "override_id": str(override.id),
            "issued_by": issued_by,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def force_strategy_cycle(self, issued_by: str = "operator") -> Dict[str, Any]:
        """Force immediate strategy cycle."""
        
        from app.autonomy.strategy_loop import get_strategy_loop
        from app.autonomy.loop_types import CycleTriggerType
        
        loop = await get_strategy_loop(self.session)
        result = await loop.run_cycle(trigger_type=CycleTriggerType.MANUAL)
        
        # Log the override
        log = OverrideLog(
            override_id=str(uuid.uuid4()),
            override_type="force_cycle",
            issued_by=issued_by,
            reason="Operator forced strategy cycle",
            status="completed",
        )
        self.session.add(log)
        await self.session.commit()
        
        return {
            "status": "completed",
            "cycle_id": result.cycle_id,
            "changes": len(result.changes),
            "adjustments": len(result.adjustments),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def is_autonomy_paused(self) -> bool:
        """Check if autonomy is currently paused."""
        
        from sqlalchemy import select
        result = await self.session.execute(
            select(AutonomyOverride)
            .where(AutonomyOverride.is_active == True)
            .where(AutonomyOverride.override_type == "pause_autonomy")
        )
        return result.scalar_one_or_none() is not None
    
    async def get_override_history(self, limit: int = 20) -> Dict[str, Any]:
        """Get override history."""
        
        from sqlalchemy import select, desc
        
        result = await self.session.execute(
            select(OverrideLog)
            .order_by(desc(OverrideLog.created_at))
            .limit(limit)
        )
        logs = list(result.scalars().all())
        
        return {
            "overrides": [
                {
                    "id": str(l.id),
                    "override_type": l.override_type,
                    "issued_by": l.issued_by,
                    "reason": l.reason,
                    "status": l.status,
                    "timestamp": l.created_at.isoformat(),
                }
                for l in logs
            ]
        }


async def get_override_manager(session: AsyncSession) -> OverrideManager:
    """Get override manager instance."""
    return OverrideManager(session)
