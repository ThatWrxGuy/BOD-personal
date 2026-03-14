"""Strategic review engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import StrategicReview, ReviewDecisionProposal
from app.models.strategic_insight import StrategicInsight
from app.reviews.review_types import (
    ReviewType,
    ReviewStatus,
    REVIEW_TYPE_CONFIG,
)
from app.reviews.review_scheduler import get_review_scheduler
from app.reviews.domain_analyzer import get_domain_analyzer
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategicReviewEngine:
    """Engine for running strategic reviews."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.scheduler = None
        self.analyzer = None
    
    async def _get_scheduler(self):
        if self.scheduler is None:
            self.scheduler = await get_review_scheduler(self.session)
        return self.scheduler
    
    async def _get_analyzer(self):
        if self.analyzer is None:
            self.analyzer = await get_domain_analyzer(self.session)
        return self.analyzer
    
    async def run_review(
        self,
        review_type: str,
        time_range_days: int = 30,
    ) -> StrategicReview:
        """Run a strategic review."""
        
        # Get config
        config = REVIEW_TYPE_CONFIG.get(review_type)
        if not config:
            raise ValueError(f"Unknown review type: {review_type}")
        
        # Create review record
        review = StrategicReview(
            review_type=review_type,
            status=ReviewStatus.RUNNING,
            started_at=datetime.utcnow(),
            domains_analyzed=config.get("domains", []),
            agents_involved=config.get("agents", []),
        )
        
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        
        logger.info(f"Starting review {review_type} (id: {review.id})")
        
        try:
            # Step 1: Analyze domains
            analyzer = await self._get_analyzer()
            domains = config.get("domains", [])
            domain_results = await analyzer.analyze_all_domains(domains, time_range_days)
            
            # Step 2: Generate insights
            insights = await self._generate_insights(review.id, domain_results)
            
            # Step 3: Generate decision proposals
            proposals = await self._generate_proposals(review.id, insights)
            
            # Step 4: Generate summary
            summary = self._generate_summary(review_type, domain_results, insights, proposals)
            
            # Complete the review
            review.status = ReviewStatus.COMPLETED
            review.completed_at = datetime.utcnow()
            review.summary = summary
            review.metrics_snapshot = {
                "domains_analyzed": len(domain_results),
                "insights_generated": len(insights),
                "proposals_generated": len(proposals),
            }
            
            await self.session.commit()
            await self.session.refresh(review)
            
            # Publish completion event
            event_bus = get_event_bus(self.session)
            await event_bus.publish_event(
                DomainEvent(
                    event_type=EventType.WORKFLOW_COMPLETED,
                    payload={
                        "review_id": str(review.id),
                        "review_type": review_type,
                        "insights_count": len(insights),
                        "proposals_count": len(proposals),
                    },
                    source_module="strategic_review_engine",
                    correlation_id=review.correlation_id,
                )
            )
            
            logger.info(f"Completed review {review_type} (id: {review.id})")
            
            return review
            
        except Exception as e:
            logger.error(f"Review failed: {e}")
            review.status = ReviewStatus.FAILED
            review.completed_at = datetime.utcnow()
            review.error_message = str(e)
            await self.session.commit()
            raise
    
    async def _generate_insights(
        self,
        review_id: uuid.UUID,
        domain_results: Dict[str, Any],
    ) -> List[StrategicInsight]:
        """Generate strategic insights from domain analysis."""
        
        insights = []
        
        for domain, result in domain_results.items():
            if "error" in result:
                continue
            
            # Extract insights from domain results
            domain_insights = result.get("insights", [])
            
            for insight_data in domain_insights:
                insight = StrategicInsight(
                    review_id=review_id,
                    domain=domain,
                    insight_type=insight_data.get("type", "observation"),
                    title=insight_data.get("description", "")[:200],
                    description=insight_data.get("description", ""),
                    confidence_score=insight_data.get("confidence", 0.8),
                    priority=insight_data.get("priority", "medium"),
                )
                self.session.add(insight)
                insights.append(insight)
            
            # Generate additional insights based on metrics
            metrics = result.get("metrics", {})
            
            if metrics.get("financial_focus_percentage", 0) < 10:
                insight = StrategicInsight(
                    review_id=review_id,
                    domain=domain,
                    insight_type="improvement",
                    title="Low financial decision activity",
                    description="Consider focusing more on financial planning and decisions",
                    confidence_score=0.7,
                    priority="medium",
                )
                self.session.add(insight)
                insights.append(insight)
        
        await self.session.commit()
        
        return insights
    
    async def _generate_proposals(
        self,
        review_id: uuid.UUID,
        insights: List[StrategicInsight],
    ) -> List[ReviewDecisionProposal]:
        """Generate decision proposals from insights."""
        
        proposals = []
        
        # Generate proposals based on insights
        for insight in insights:
            if insight.priority in ["high", "critical"]:
                proposal = ReviewDecisionProposal(
                    review_id=review_id,
                    decision_type=f"address_{insight.insight_type}",
                    title=f"Address: {insight.title}",
                    description=f"Based on strategic insight: {insight.description}",
                    priority=insight.priority,
                    expected_impact="Improve strategic position",
                )
                self.session.add(proposal)
                proposals.append(proposal)
        
        await self.session.commit()
        
        return proposals
    
    def _generate_summary(
        self,
        review_type: str,
        domain_results: Dict[str, Any],
        insights: List[StrategicInsight],
        proposals: List[ReviewDecisionProposal],
    ) -> str:
        """Generate review summary."""
        
        config = REVIEW_TYPE_CONFIG.get(review_type, {})
        name = config.get("name", review_type)
        
        summary_parts = [
            f"## {name}",
            "",
            f"**Domains Analyzed:** {', '.join(domain_results.keys())}",
            f"**Insights Generated:** {len(insights)}",
            f"**Proposals Created:** {len(proposals)}",
            "",
        ]
        
        # Add key insights
        if insights:
            summary_parts.append("### Key Insights")
            summary_parts.append("")
            for insight in insights[:5]:
                summary_parts.append(f"- **{insight.title}** ({insight.insight_type})")
            summary_parts.append("")
        
        # Add proposals
        if proposals:
            summary_parts.append("### Recommended Actions")
            summary_parts.append("")
            for proposal in proposals:
                summary_parts.append(f"- {proposal.title}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    async def get_review(self, review_id: uuid.UUID) -> Optional[StrategicReview]:
        """Get a review by ID."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicReview).where(StrategicReview.id == review_id)
        )
        return result.scalar_one_or_none()
    
    async def get_reviews(
        self,
        review_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[StrategicReview]:
        """Get reviews with optional filters."""
        
        from sqlalchemy import select, desc
        
        query = select(StrategicReview).order_by(desc(StrategicReview.created_at)).limit(limit)
        
        if review_type:
            query = query.where(StrategicReview.review_type == review_type)
        
        if status:
            query = query.where(StrategicReview.status == status)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_review_insights(self, review_id: uuid.UUID) -> List[StrategicInsight]:
        """Get insights for a review."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(StrategicInsight)
            .where(StrategicInsight.review_id == review_id)
            .order_by(StrategicInsight.priority.desc())
        )
        return list(result.scalars().all())
    
    async def get_review_proposals(self, review_id: uuid.UUID) -> List[ReviewDecisionProposal]:
        """Get decision proposals for a review."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(ReviewDecisionProposal)
            .where(ReviewDecisionProposal.review_id == review_id)
            .order_by(ReviewDecisionProposal.priority.desc())
        )
        return list(result.scalars().all())


async def get_strategic_review_engine(session: AsyncSession) -> StrategicReviewEngine:
    """Get strategic review engine instance."""
    return StrategicReviewEngine(session)
