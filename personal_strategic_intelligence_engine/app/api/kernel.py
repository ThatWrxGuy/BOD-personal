"""Kernel API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.kernel.kernel_controller import get_kernel_controller
from app.kernel.state_model.state_model_engine import get_state_model_engine
from app.kernel.priorities.priority_engine import get_priority_engine
from app.kernel.policy.policy_engine import get_policy_engine
from app.kernel.decision_utility.decision_utility_engine import get_decision_utility_engine
from app.models.kernel import KernelMode
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/kernel", tags=["kernel"])


@router.get("/status")
async def kernel_status(session: AsyncSession = Depends(get_db)):
    """Get kernel status."""
    try:
        controller = await get_kernel_controller(session)
        status = await controller.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting kernel status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state")
async def get_state(session: AsyncSession = Depends(get_db)):
    """Get current system state."""
    try:
        engine = await get_state_model_engine(session)
        state = await engine.get_current_state()
        return {"state": state}
    except Exception as e:
        logger.error(f"Error getting state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state/snapshots")
async def get_state_snapshots(limit: int = 10, session: AsyncSession = Depends(get_db)):
    """Get state snapshots."""
    try:
        engine = await get_state_model_engine(session)
        snapshots = await engine.get_snapshots(limit)
        return {
            "snapshots": [
                {
                    "id": str(s.id),
                    "net_worth": s.net_worth,
                    "market_regime": s.market_regime,
                    "system_health_score": s.system_health_score,
                    "created_at": s.created_at.isoformat(),
                }
                for s in snapshots
            ]
        }
    except Exception as e:
        logger.error(f"Error getting snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/priorities")
async def get_priorities(session: AsyncSession = Depends(get_db)):
    """Get current strategic priorities."""
    try:
        engine = await get_priority_engine(session)
        priorities = await engine.get_active_priorities()
        return {"priorities": priorities}
    except Exception as e:
        logger.error(f"Error getting priorities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies")
async def get_policies(session: AsyncSession = Depends(get_db)):
    """Get active policies."""
    try:
        engine = await get_policy_engine(session)
        policies = await engine.get_active_policies()
        return {"policies": policies}
    except Exception as e:
        logger.error(f"Error getting policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/evaluate")
async def evaluate_decision(decision: dict, session: AsyncSession = Depends(get_db)):
    """Evaluate a decision against policies."""
    try:
        engine = await get_policy_engine(session)
        result = await engine.evaluate_decision(decision)
        return result
    except Exception as e:
        logger.error(f"Error evaluating decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decisions/evaluate")
async def evaluate_decision_get(
    decision_type: str,
    expected_value: float = 0.5,
    risk: float = 0.5,
    confidence: float = 0.5,
    session: AsyncSession = Depends(get_db),
):
    """Evaluate a decision using utility scoring."""
    try:
        engine = await get_decision_utility_engine(session)
        score = await engine.score_decision(
            decision_type=decision_type,
            decision_description="",
            expected_value=expected_value,
            risk_assessment=risk,
            confidence=confidence,
        )
        return {
            "utility_score": score.utility_score,
            "expected_value": score.expected_value,
            "risk_penalty": score.risk_penalty,
            "confidence_score": score.confidence_score,
            "alignment_score": score.alignment_score,
        }
    except Exception as e:
        logger.error(f"Error scoring decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-cycle")
async def run_cycle(session: AsyncSession = Depends(get_db)):
    """Run a kernel control cycle."""
    try:
        controller = await get_kernel_controller(session)
        result = await controller.run_cycle()
        return result
    except Exception as e:
        logger.error(f"Error running cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mode")
async def set_kernel_mode(mode: str, session: AsyncSession = Depends(get_db)):
    """Set kernel operation mode."""
    try:
        controller = await get_kernel_controller(session)
        controller.set_mode(mode)
        return {"mode": mode, "message": "Kernel mode updated"}
    except Exception as e:
        logger.error(f"Error setting mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mode")
async def get_kernel_mode(session: AsyncSession = Depends(get_db)):
    """Get current kernel mode."""
    try:
        controller = await get_kernel_controller(session)
        return {"mode": controller.mode}
    except Exception as e:
        logger.error(f"Error getting mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))
