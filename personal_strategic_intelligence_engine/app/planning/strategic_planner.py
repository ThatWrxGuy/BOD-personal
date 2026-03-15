"""Strategic planner for cross-domain planning."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.planning import StrategicPlan, PlanAction, PlanOutcome
from app.planning.plan_types import (
    PlanStatus,
    ActionStatus,
    PlanType,
)
from app.planning.domain_relationship_mapper import get_domain_relationship_mapper, get_tradeoff_analyzer
from app.planning.strategy_generator import get_strategy_generator
from app.reviews.strategic_review_engine import get_strategic_review_engine
from app.detection.detection_engine import get_detection_engine
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategicPlanner:
    """Main strategic planner for cross-domain planning."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def generate_plan(
        self,
        scope: str = "monthly",
        domains: Optional[List[str]] = None,
    ) -> StrategicPlan:
        """Generate a strategic plan."""
        
        # Default domains
        if domains is None:
            domains = ["financial", "health", "productivity"]
        
        logger.info(f"Generating {scope} plan for domains: {domains}")
        
        # Aggregate insights from reviews and detection
        insights = await self._aggregate_insights(domains)
        
        # Generate the plan
        generator = await get_strategy_generator(self.session)
        plan = await generator.generate_plan(scope, domains, insights)
        
        # Update status
        plan.status = PlanStatus.UNDER_REVIEW
        await self.session.commit()
        
        # Publish event
        await self._publish_plan_event(plan, "generated")
        
        # Track metrics
        increment("plans_generated", domain=MetricDomain.SYSTEM)
        
        return plan
    
    async def _aggregate_insights(
        self,
        domains: List[str],
    ) -> List[Dict[str, Any]]:
        """Aggregate insights from reviews and detection."""
        
        all_insights = []
        
        # Get insights from recent reviews
        try:
            review_engine = await get_strategic_review_engine(self.session)
            reviews = await review_engine.get_reviews(status="completed", limit=5)
            
            for review in reviews:
                insights = await review_engine.get_review_insights(review.id)
                all_insights.extend([
                    {
                        "title": i.title,
                        "description": i.description,
                        "domain": i.domain,
                        "type": i.insight_type,
                        "confidence": i.confidence_score,
                        "source": "review",
                    }
                    for i in insights
                ])
        except Exception as e:
            logger.warning(f"Error getting review insights: {e}")
        
        # Get detection events
        try:
            detection_engine = await get_detection_engine(self.session)
            events = await detection_engine.get_detection_events(
                domain=None,
                limit=20,
            )
            
            all_insights.extend([
                {
                    "title": e.title,
                    "description": e.description,
                    "domain": e.domain,
                    "type": e.event_type,
                    "confidence": e.confidence_score,
                    "severity": e.severity,
                    "source": "detection",
                }
                for e in events
            ])
        except Exception as e:
            logger.warning(f"Error getting detection events: {e}")
        
        return all_insights
    
    async def approve_plan(
        self,
        plan_id: uuid.UUID,
    ) -> StrategicPlan:
        """Approve a strategic plan."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicPlan).where(StrategicPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan.status = PlanStatus.APPROVED
        await self.session.commit()
        
        # Publish event
        await self._publish_plan_event(plan, "approved")
        
        # Track metrics
        increment("plans_approved", domain=MetricDomain.SYSTEM)
        
        return plan
    
    async def reject_plan(
        self,
        plan_id: uuid.UUID,
    ) -> StrategicPlan:
        """Reject a strategic plan."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicPlan).where(StrategicPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan.status = PlanStatus.REJECTED
        await self.session.commit()
        
        # Publish event
        await self._publish_plan_event(plan, "rejected")
        
        # Track metrics
        increment("plans_rejected", domain=MetricDomain.SYSTEM)
        
        return plan
    
    async def get_plan(
        self,
        plan_id: uuid.UUID,
    ) -> Optional[StrategicPlan]:
        """Get a plan by ID."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicPlan).where(StrategicPlan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    async def get_plans(
        self,
        status: Optional[str] = None,
        plan_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[StrategicPlan]:
        """Get plans with filters."""
        
        from sqlalchemy import select, desc
        
        query = select(StrategicPlan).order_by(desc(StrategicPlan.created_at)).limit(limit)
        
        if status:
            query = query.where(StrategicPlan.status == status)
        if plan_type:
            query = query.where(StrategicPlan.plan_type == plan_type)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_plan_actions(
        self,
        plan_id: uuid.UUID,
    ) -> List[PlanAction]:
        """Get actions for a plan."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(PlanAction)
            .where(PlanAction.plan_id == plan_id)
            .order_by(PlanAction.priority.desc())
        )
        return list(result.scalars().all())
    
    async def update_action_status(
        self,
        action_id: uuid.UUID,
        status: str,
    ) -> PlanAction:
        """Update action status."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(PlanAction).where(PlanAction.id == action_id)
        )
        action = result.scalar_one_or_none()
        
        if not action:
            raise ValueError(f"Action not found: {action_id}")
        
        action.status = status
        
        if status == ActionStatus.COMPLETED:
            action.completed_at = datetime.utcnow()
        
        await self.session.commit()
        
        return action
    
    async def record_outcome(
        self,
        plan_id: uuid.UUID,
        action_id: Optional[uuid.UUID],
        outcome_type: str,
        description: str,
        success_metric: Optional[float] = None,
    ) -> PlanOutcome:
        """Record an outcome for a plan."""
        
        outcome = PlanOutcome(
            plan_id=plan_id,
            action_id=action_id,
            outcome_type=outcome_type,
            description=description,
            success_metric=success_metric,
            measured_at=datetime.utcnow(),
        )
        
        self.session.add(outcome)
        await self.session.commit()
        
        return outcome
    
    async def _publish_plan_event(
        self,
        plan: StrategicPlan,
        event_type_suffix: str,
    ) -> None:
        """Publish a plan event to the event bus."""
        
        event_bus = get_event_bus(self.session)
        
        await event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={
                    "plan_id": str(plan.id),
                    "plan_type": plan.plan_type,
                    "event": event_type_suffix,
                },
                source_module="strategic_planner",
                correlation_id=plan.correlation_id,
            )
        )


async def get_strategic_planner(session: AsyncSession) -> StrategicPlanner:
    """Get strategic planner instance."""
    return StrategicPlanner(session)
