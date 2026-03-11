"""Research engine for autonomous research."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.research.research_types import (
    ResearchTask,
    ResearchReport,
    ResearchSourceResult,
    ResearchStatus,
    ResearchPriority,
    ResearchScope,
)
from app.research.research_sources import get_source_manager
from app.research.research_analyzer import get_research_analyzer
from app.knowledge.knowledge_graph import get_knowledge_graph
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResearchEngine:
    """Main research engine for autonomous research."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def run_research(
        self,
        topic: str,
        scope: str = "standard",
        priority: str = "medium",
        description: Optional[str] = None,
        trigger_source: Optional[str] = None,
        trigger_id: Optional[uuid.UUID] = None,
    ) -> ResearchTask:
        """Run a research task."""
        
        logger.info(f"Starting research on: {topic}")
        
        # Create research task
        task = ResearchTask(
            topic=topic,
            description=description,
            status=ResearchStatus.RUNNING,
            priority=priority,
            scope=scope,
            trigger_source=trigger_source,
            trigger_id=trigger_id,
            started_at=datetime.utcnow(),
            current_step="initializing",
        )
        
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        
        try:
            # Publish event
            await self._publish_event(task, "triggered")
            
            # Run research
            result = await self._execute_research(task)
            
            # Generate report
            report = await self._generate_report(task, result)
            
            # Update task status
            task.status = ResearchStatus.COMPLETED
            task.progress = 100.0
            task.completed_at = datetime.utcnow()
            
            # Update knowledge graph
            await self._update_knowledge_graph(report)
            
            # Publish completion event
            await self._publish_event(task, "completed")
            
            # Track metrics
            increment("research_tasks_completed", domain=MetricDomain.SYSTEM)
            
            await self.session.commit()
            
            logger.info(f"Research completed: {topic}")
            
            return task
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            task.status = ResearchStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self.session.commit()
            raise
    
    async def _execute_research(
        self,
        task: ResearchTask,
    ) -> Dict[str, Any]:
        """Execute the research task."""
        
        topic = task.topic
        scope = task.scope
        
        # Determine sources based on scope
        source_manager = get_source_manager()
        
        task.current_step = "gathering_data"
        task.progress = 20.0
        await self.session.commit()
        
        # Get available sources
        available_sources = source_manager.get_available_sources()
        
        # Query sources
        task.current_step = "querying_sources"
        task.progress = 40.0
        await self.session.commit()
        
        # Determine which sources to query based on topic
        sources_to_query = self._determine_sources(topic, available_sources)
        
        source_results = await source_manager.query_with_timeout(
            query=topic,
            source_types=sources_to_query,
            timeout_seconds=self._get_timeout(scope),
        )
        
        # Store source results
        for result in source_results:
            source_result = ResearchSourceResult(
                task_id=task.id,
                source_name=result.get("source", "unknown"),
                query=topic,
                results=result.get("data"),
                success=result.get("success", False),
                error=result.get("error"),
            )
            self.session.add(source_result)
        
        task.sources_queried = sources_to_query
        task.data_collected = {"sources": sources_to_query, "results_count": len(source_results)}
        
        task.current_step = "analyzing"
        task.progress = 70.0
        await self.session.commit()
        
        # Analyze results
        analyzer = await get_research_analyzer()
        analysis = await analyzer.analyze(topic, source_results)
        
        task.current_step = "completed"
        task.progress = 100.0
        
        return {
            "source_results": source_results,
            "analysis": analysis,
        }
    
    def _determine_sources(
        self,
        topic: str,
        available_sources: List[str],
    ) -> List[str]:
        """Determine which sources to query based on topic."""
        
        topic_lower = topic.lower()
        
        # Default sources to always include
        sources = ["knowledge_base"]  # Always include internal knowledge
        
        # Add LLM if available
        if "llm" in available_sources:
            sources.append("llm")
        
        # Add topic-specific sources
        if any(keyword in topic_lower for keyword in ["financial", "investment", "stock", "market", "portfolio"]):
            if "financial" in available_sources:
                sources.append("financial")
        
        if any(keyword in topic_lower for keyword in ["economic", "gdp", "inflation", "economy"]):
            if "economic" in available_sources:
                sources.append("economic")
        
        return sources
    
    def _get_timeout(self, scope: str) -> int:
        """Get timeout based on scope."""
        
        timeouts = {
            "quick": 60,
            "standard": 180,
            "deep": 600,
        }
        
        return timeouts.get(scope, 180)
    
    async def _generate_report(
        self,
        task: ResearchTask,
        result: Dict[str, Any],
    ) -> ResearchReport:
        """Generate a research report."""
        
        analysis = result.get("analysis", {})
        
        # Generate summary
        analyzer = await get_research_analyzer()
        summary = analyzer._generate_summary(task.topic, analysis.get("key_findings", []))
        
        report = ResearchReport(
            task_id=task.id,
            topic=task.topic,
            summary=summary,
            key_findings=analysis.get("key_findings", []),
            supporting_evidence=analysis.get("supporting_evidence", []),
            risk_analysis=analysis.get("risk_analysis", {}),
            recommended_actions=analysis.get("recommended_actions", []),
            confidence_score=analysis.get("confidence_score", 0.5),
            sources_count=len(result.get("source_results", [])),
            research_scope=task.scope,
            completed_at=datetime.utcnow(),
        )
        
        self.session.add(report)
        await self.session.commit()
        
        increment("research_reports_generated", domain=MetricDomain.SYSTEM)
        
        return report
    
    async def _update_knowledge_graph(
        self,
        report: ResearchReport,
    ) -> None:
        """Update knowledge graph with research results."""
        
        try:
            graph = await get_knowledge_graph(self.session)
            
            # Create entity for the report
            entity = await graph.create_entity(
                entity_type="research_report",
                name=f"Research: {report.topic[:50]}",
                attributes={
                    "report_id": str(report.id),
                    "topic": report.topic,
                    "confidence": report.confidence_score,
                    "summary": report.summary[:200],
                },
                domain="strategic",
            )
            
            # Update report with linked entity
            report.linked_entities = [str(entity.id)]
            
            await self.session.commit()
            
        except Exception as e:
            logger.warning(f"Failed to update knowledge graph: {e}")
    
    async def _publish_event(
        self,
        task: ResearchTask,
        event_suffix: str,
    ) -> None:
        """Publish research event to event bus."""
        
        event_bus = get_event_bus(self.session)
        
        await event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={
                    "task_id": str(task.id),
                    "topic": task.topic,
                    "event": event_suffix,
                },
                source_module="research_engine",
            )
        )
    
    async def get_task(
        self,
        task_id: uuid.UUID,
    ) -> Optional[ResearchTask]:
        """Get a research task."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(ResearchTask).where(ResearchTask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[ResearchTask]:
        """Get research tasks."""
        
        from sqlalchemy import select, desc
        
        query = select(ResearchTask).order_by(desc(ResearchTask.created_at)).limit(limit)
        
        if status:
            query = query.where(ResearchTask.status == status)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_report(
        self,
        report_id: uuid.UUID,
    ) -> Optional[ResearchReport]:
        """Get a research report."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(ResearchReport).where(ResearchReport.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_reports(
        self,
        limit: int = 20,
    ) -> List[ResearchReport]:
        """Get research reports."""
        
        from sqlalchemy import select, desc
        
        result = await self.session.execute(
            select(ResearchReport).order_by(desc(ResearchReport.created_at)).limit(limit)
        )
        return list(result.scalars().all())
    
    async def cancel_task(
        self,
        task_id: uuid.UUID,
    ) -> ResearchTask:
        """Cancel a research task."""
        
        task = await self.get_task(task_id)
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        if task.status == ResearchStatus.RUNNING:
            task.status = ResearchStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            await self.session.commit()
        
        return task


async def get_research_engine(session: AsyncSession) -> ResearchEngine:
    """Get research engine instance."""
    return ResearchEngine(session)
