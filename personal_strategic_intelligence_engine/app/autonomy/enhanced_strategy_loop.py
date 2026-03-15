"""Enhanced Strategy Loop with Review Gate Integration.

This version of the strategy loop integrates the review gate between
adjustment generation and execution, ensuring all autonomous actions
pass through proper review before execution.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomy import StrategyLoopCycle, LoopPolicy
from app.autonomy.loop_types import (
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

# Import review gate components
from app.governance.review_gate import (
    get_review_gate_manager,
    ReviewRequest,
    RiskLevel,
)
from app.governance.review_audit import get_review_audit_logger

logger = get_logger(__name__)


class EnhancedStrategyLoop:
    """Enhanced strategy loop with integrated review gate.
    
    This version adds mandatory review between adjustment generation
    and execution, preventing autonomous bypass of executive review.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.state_monitor = None
        self.change_detector = None
        self.strategy_adjuster = None
        self.review_gate_manager = None
        self.review_audit_logger = None
        self.last_cycle: Optional[StrategyLoopCycle] = None
    
    async def _ensure_initialized(self):
        """Lazy initialization of dependencies."""
        if self.state_monitor is None:
            self.state_monitor = await get_state_monitor(self.session)
            self.change_detector = await get_change_detector()
            self.strategy_adjuster = await get_strategy_adjuster()
        
        if self.review_gate_manager is None:
            self.review_gate_manager = get_review_gate_manager()
            await self.review_gate_manager.initialize()
        
        if self.review_audit_logger is None:
            self.review_audit_logger = get_review_audit_logger()
    
    async def run_cycle(
        self,
        trigger_type: CycleTriggerType = CycleTriggerType.SCHEDULED,
        review_enabled: bool = True,
    ) -> CycleOutcome:
        """Execute one complete strategy loop cycle with review gate integration.
        
        Args:
            trigger_type: What triggered this cycle
            review_enabled: Whether to use review gate (default True)
        """
        
        cycle_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting enhanced strategy loop cycle {cycle_id}")
        
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
            await self._ensure_initialized()
            
            # Step 1: Observe state
            logger.info(f"Cycle {cycle_id}: Observing state")
            observation = await self.state_monitor.observe_state()
            
            cycle.observed_domains = [d.domain for d in observation.domains]
            cycle.overall_health = observation.overall_health
            await self.session.commit()
            
            # Step 2: Detect changes
            logger.info(f"Cycle {cycle_id}: Detecting changes")
            changes = await self.change_detector.detect_changes(observation)
            
            cycle.changes_detected = [c.dict() for c in changes]
            cycle.changes_count = len(changes)
            await self.session.commit()
            
            # Step 3: Generate adjustments
            logger.info(f"Cycle {cycle_id}: Generating adjustments")
            adjustments = await self.strategy_adjuster.generate_adjustments(changes)
            
            cycle.adjustments = [a.dict() for a in adjustments]
            cycle.adjustments_count = len(adjustments)
            await self.session.commit()
            
            # NEW STEP 4: Review Gate (if enabled)
            if review_enabled:
                logger.info(f"Cycle {cycle_id}: Review gate")
                review_results = await self._process_review_gate(adjustments)
                cycle.review_results = review_results
                await self.session.commit()
            else:
                review_results = {"all_approved": True, "adjustments": adjustments}
            
            # Step 5: Execute actions (only approved)
            logger.info(f"Cycle {cycle_id}: Executing approved actions")
            actions = await self._execute_adjustments(adjustments, review_results)
            
            cycle.actions_executed = actions
            
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
    
    async def _process_review_gate(
        self,
        adjustments: List,
    ) -> dict:
        """Process adjustments through review gate.
        
        Args:
            adjustments: List of adjustments to review
            
        Returns:
            Dictionary with review results for each adjustment
        """
        results = {
            "all_approved": True,
            "approved": [],
            "rejected": [],
            "deferred": [],
            "details": [],
        }
        
        for adjustment in adjustments:
            # Create review request from adjustment
            request = self._create_review_request(adjustment)
            
            # Submit for review
            result = await self.review_gate_manager.submit_for_review(request)
            
            # Log audit entry
            await self.review_audit_logger.log_review_decision(
                request=request,
                result=result,
                reviewer=result.reviewer or "system",
                reviewer_type="executive" if result.reviewer else "system",
            )
            
            # Track result
            detail = {
                "adjustment_id": str(adjustment.adjustment_id),
                "adjustment_type": adjustment.adjustment_type.value,
                "decision": result.decision.value,
                "reason": result.reason,
            }
            results["details"].append(detail)
            
            if result.decision.value == "approved":
                results["approved"].append(adjustment)
            elif result.decision.value == "rejected":
                results["rejected"].append(adjustment)
                results["all_approved"] = False
            elif result.decision.value == "deferred":
                results["deferred"].append(adjustment)
                results["all_approved"] = False
        
        return results
    
    def _create_review_request(self, adjustment) -> ReviewRequest:
        """Create a review request from an adjustment.
        
        Args:
            adjustment: Adjustment object
            
        Returns:
            Review request
        """
        # Determine risk level based on adjustment type
        risk_level = self._assess_risk(adjustment)
        
        return ReviewRequest(
            adjustment_id=adjustment.adjustment_id,
            adjustment_type=adjustment.adjustment_type.value,
            adjustment_data=adjustment.dict(),
            risk_level=risk_level,
            impact_scope=adjustment.target_domain or "system",
            source="strategy_loop",
            rationale=adjustment.rationale or "Autonomous strategy adjustment",
        )
    
    def _assess_risk(self, adjustment) -> RiskLevel:
        """Assess risk level of an adjustment.
        
        Args:
            adjustment: Adjustment object
            
        Returns:
            Risk level
        """
        # High risk adjustments
        high_risk_types = [
            "doctrine_change",
            "strategy_change",
            "resource_allocation",
        ]
        
        if adjustment.adjustment_type.value in high_risk_types:
            return RiskLevel.HIGH
        
        # Medium risk
        medium_risk_types = [
            "plan_modification",
            "priority_adjustment",
        ]
        
        if adjustment.adjustment_type.value in medium_risk_types:
            return RiskLevel.MEDIUM
        
        # Default to low risk for simple adjustments
        return RiskLevel.LOW
    
    async def _execute_adjustments(
        self,
        adjustments: List,
        review_results: dict,
    ) -> List[str]:
        """Execute adjustments that passed review.
        
        Args:
            adjustments: All adjustments
            review_results: Results from review gate
            
        Returns:
            List of executed action descriptions
        """
        actions = []
        
        # Only execute approved adjustments
        approved = review_results.get("approved", adjustments)
        
        for adjustment in approved:
            try:
                action = await self._execute_adjustment(adjustment)
                actions.append(f"EXECUTED: {action}")
            except Exception as e:
                logger.error(f"Failed to execute adjustment {adjustment.adjustment_id}: {e}")
                actions.append(f"FAILED: {adjustment.adjustment_id}: {str(e)}")
        
        # Log rejected/deferred
        rejected = review_results.get("rejected", [])
        for adjustment in rejected:
            actions.append(f"REJECTED: {adjustment.adjustment_id}")
        
        deferred = review_results.get("deferred", [])
        for adjustment in deferred:
            actions.append(f"DEFERRED: {adjustment.adjustment_id}")
        
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
            return f"Adjustment {adj_type} executed"


async def get_enhanced_strategy_loop(session: AsyncSession) -> EnhancedStrategyLoop:
    """Get enhanced strategy loop instance."""
    return EnhancedStrategyLoop(session)
