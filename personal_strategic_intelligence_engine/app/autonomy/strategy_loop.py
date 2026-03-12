"""Main strategy loop orchestration engine."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.autonomy.loop_types import (
    StrategyLoopCycle,
    CycleStatus,
    CycleTriggerType,
    CycleOutcome,
    ChangeSeverity,
)
from app.autonomy.state_monitor import get_state_monitor
from app.autonomy.change_detector import get_change_detector
from app.autonomy.strategy_adjuster import get_strategy_adjuster
from app.core.logging import get_logger
from app.observability import increment
from app.observability.metrics_service import MetricDomain

logger = get_logger(__name__)


class StrategyLoop:
    """Main strategy loop orchestration engine."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.state_monitor = await get_state_monitor(session)
        self.change_detector = await get_change_detector()
        self.strategy_adjuster = await get_strategy_adjuster()
        self.last_cycle: Optional[StrategyLoopCycle] = None
    
    async def run_cycle(
        self,
        trigger_type: CycleTriggerType = CycleTriggerType.SCHEDULED,
    ) -> CycleOutcome:
        """Execute one complete strategy loop cycle."""
        
        cycle_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting strategy loop cycle {cycle_id}")
        
        # Create cycle record
        cycle = StrategyLoopCycle(
            id=uuid.UUID(cycle_id),
            trigger_type=trigger_type,
            status=CycleStatus.RUNNING,
            started_at=start_time,
        )
        self.session.add(cycle)
        await self.session.commit()
        
        try:
            # Step 1: Observe state
            logger.info(f"Cycle {cycle_id}: Observing state")
            observation = await self.state_monitor.observe_state()
            
            # Update cycle
            cycle.observed_domains = [d.domain for d in observation.domains]
            cycle.overall_health = observation.overall_health
            await self.session.commit()
            
            # Step 2: Detect changes
            logger.info(f"Cycle {cycle_id}: Detecting changes")
            changes = await self.change_detector.detect_changes(observation)
            
            # Update cycle
            cycle.changes_detected = [c.dict() for c in changes]
            cycle.changes_count = len(changes)
            await self.session.commit()
            
            # Step 3: Generate adjustments
            logger.info(f"Cycle {cycle_id}: Generating adjustments")
            adjustments = await self.strategy_adjuster.generate_adjustments(changes)
            
            # Update cycle
            cycle.adjustments = [a.dict() for a in adjustments]
            cycle.adjustments_count = len(adjustments)
            await self.session.commit()
            
            # Step 4: Execute actions
            logger.info(f"Cycle {cycle_id}: Executing actions")
            actions = await self._execute_adjustments(adjustments)
            
            # Update cycle
            cycle.actions_executed = actions
            await self.session.commit()
            
            # Complete cycle
            end_time = datetime.utcnow()
            runtime_ms = int((end_time - start_time).total_seconds() * 1000)
            
            cycle.status = CycleStatus.COMPLETED
            cycle.completed_at = end_time
            cycle.runtime_ms = runtime_ms
            
            await self.session.commit()
            
            self.last_cycle = cycle
            
            # Track metric
            increment("strategy_cycles_completed", domain=MetricDomain.SYSTEM)
            
            logger.info(f"Cycle {cycle_id} completed in {runtime_ms}ms")
            
            return CycleOutcome(
                cycle_id=cycle_id,
                status=CycleStatus.COMPLETED,
                trigger_type=trigger_type,
                observation=observation,
                changes=changes,
                adjustments=adjustments,
                actions_executed=actions,
                runtime_ms=runtime_ms,
            )
            
        except Exception as e:
            logger.error(f"Cycle {cycle_id} failed: {e}")
            
            cycle.status = CycleStatus.FAILED
            cycle.error_message = str(e)
            cycle.completed_at = datetime.utcnow()
            
            await self.session.commit()
            
            return CycleOutcome(
                cycle_id=cycle_id,
                status=CycleStatus.FAILED,
                trigger_type=trigger_type,
                error_message=str(e),
                runtime_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            )
    
    async def _execute_adjustments(
        self,
        adjustments: List,
    ) -> List[str]:
        """Execute adjustments."""
        
        actions = []
        
        for adjustment in adjustments:
            try:
                action = await self._execute_adjustment(adjustment)
                actions.append(action)
            except Exception as e:
                logger.error(f"Failed to execute adjustment {adjustment.adjustment_id}: {e}")
                actions.append(f"FAILED: {adjustment.adjustment_id}: {str(e)}")
        
        return actions
    
    async def _execute_adjustment(self, adjustment) -> str:
        """Execute a single adjustment."""
        
        adj_type = adjustment.adjustment_type.value
        
        if adj_type == "regenerate_daily_plan":
            from app.rhythm.daily_planner import get_daily_planner
            
            planner = await get_daily_planner(self.session)
            plan = await planner.generate_plan()
            return f"Regenerated daily plan: {plan['id']}"
        
        elif adj_type == "regenerate_weekly_plan":
            from app.rhythm.weekly_planner import get_weekly_planner
            
            planner = await get_weekly_planner(self.session)
            plan = await planner.generate_plan()
            return f"Regenerated weekly plan: {plan['id']}"
        
        elif adj_type == "increase_risk_mitigation":
            return "Increased risk mitigation focus"
        
        elif adj_type == "increase_opportunity_response":
            return "Increased opportunity response focus"
        
        elif adj_type == "increase_recovery":
            return "Increased recovery time"
        
        elif adj_type == "reduce_priority":
            return "Reduced execution priority"
        
        elif adj_type == "no_action":
            return "No action required"
        
        else:
            return f"Adjustment {adj_type} logged"
    
    async def get_last_cycle(self) -> Optional[CycleOutcome]:
        """Get the last completed cycle."""
        
        if not self.last_cycle:
            return None
        
        return CycleOutcome(
            cycle_id=str(self.last_cycle.id),
            status=self.last_cycle.status,
            trigger_type=self.last_cycle.trigger_type,
            runtime_ms=self.last_cycle.runtime_ms,
        )
    
    async def get_cycle_history(self, limit: int = 20) -> List[CycleOutcome]:
        """Get cycle history."""
        
        from sqlalchemy import select, desc
        
        result = await self.session.execute(
            select(StrategyLoopCycle)
            .order_by(desc(StrategyLoopCycle.created_at))
            .limit(limit)
        )
        cycles = list(result.scalars().all())
        
        return [
            CycleOutcome(
                cycle_id=str(c.id),
                status=c.status,
                trigger_type=c.trigger_type,
                changes_count=c.changes_count,
                adjustments_count=c.adjustments_count,
                runtime_ms=c.runtime_ms,
            )
            for c in cycles
        ]


async def get_strategy_loop(session: AsyncSession) -> StrategyLoop:
    """Get strategy loop instance."""
    return StrategyLoop(session)
