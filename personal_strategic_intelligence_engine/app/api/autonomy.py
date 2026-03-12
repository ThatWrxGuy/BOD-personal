"""Autonomy API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.autonomy.strategy_loop import get_strategy_loop
from app.autonomy.loop_types import CycleTriggerType

router = APIRouter(prefix="/autonomy", tags=["autonomy"])


@router.get("/status")
async def get_autonomy_status(
    session: AsyncSession = Depends(get_db),
):
    """Get current autonomous system status."""
    
    loop = await get_strategy_loop(session)
    last = await loop.get_last_cycle()
    
    return {
        "autonomy_enabled": True,
        "last_cycle": {
            "cycle_id": last.cycle_id if last else None,
            "status": last.status if last else None,
            "runtime_ms": last.runtime_ms if last else None,
        } if last else None,
    }


@router.post("/run-cycle")
async def run_cycle(
    trigger: str = Query("scheduled", description="Trigger type: scheduled, manual, event_driven"),
    session: AsyncSession = Depends(get_db),
):
    """Trigger immediate strategy loop execution."""
    
    trigger_type = CycleTriggerType(trigger)
    
    loop = await get_strategy_loop(session)
    result = await loop.run_cycle(trigger_type)
    
    return {
        "cycle_id": result.cycle_id,
        "status": result.status,
        "changes_count": len(result.changes),
        "adjustments_count": len(result.adjustments),
        "actions_executed": result.actions_executed,
        "runtime_ms": result.runtime_ms,
    }


@router.get("/last-cycle")
async def get_last_cycle(
    session: AsyncSession = Depends(get_db),
):
    """Get results from the most recent cycle."""
    
    loop = await get_strategy_loop(session)
    last = await loop.get_last_cycle()
    
    if not last:
        return {"message": "No cycles recorded yet"}
    
    return {
        "cycle_id": last.cycle_id,
        "status": last.status,
        "trigger_type": last.trigger_type,
        "runtime_ms": last.runtime_ms,
    }


@router.get("/cycle-history")
async def get_cycle_history(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Get historical cycle records."""
    
    loop = await get_strategy_loop(session)
    cycles = await loop.get_cycle_history(limit)
    
    return {
        "cycles": [
            {
                "cycle_id": c.cycle_id,
                "status": c.status,
                "trigger_type": c.trigger_type,
                "changes_count": c.changes_count if hasattr(c, 'changes_count') else 0,
                "adjustments_count": c.adjustments_count if hasattr(c, 'adjustments_count') else 0,
                "runtime_ms": c.runtime_ms,
            }
            for c in cycles
        ],
        "count": len(cycles),
    }
