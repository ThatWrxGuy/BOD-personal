"""Knowledge graph main module."""
import uuid
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge.entity_registry import get_entity_registry
from app.knowledge.relationship_manager import get_relationship_manager
from app.knowledge.knowledge_types import EntityType, RelationshipType, KnowledgeEntity, KnowledgeRelationship, KnowledgeDomain
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class KnowledgeGraph:
    """Main knowledge graph interface."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.entity_registry = None
        self.relationship_manager = None
    
    async def _get_entity_registry(self):
        if self.entity_registry is None:
            self.entity_registry = await get_entity_registry(self.session)
        return self.entity_registry
    
    async def _get_relationship_manager(self):
        if self.relationship_manager is None:
            self.relationship_manager = await get_relationship_manager(self.session)
        return self.relationship_manager
    
    # ===================
    # Entity Operations
    # ===================
    
    async def create_entity(
        self,
        entity_type: str,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None,
    ) -> KnowledgeEntity:
        """Create a new entity in the knowledge graph."""
        
        registry = await self._get_entity_registry()
        return await registry.create_entity(entity_type, name, attributes, domain)
    
    async def get_entity(
        self,
        entity_id: uuid.UUID,
    ) -> Optional[KnowledgeEntity]:
        """Get an entity by ID."""
        
        registry = await self._get_entity_registry()
        return await registry.get_entity(entity_id)
    
    async def get_entities(
        self,
        entity_type: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 100,
    ) -> List[KnowledgeEntity]:
        """Get entities with filters."""
        
        registry = await self._get_entity_registry()
        return await registry.get_entities(entity_type, domain, limit=limit)
    
    async def update_entity(
        self,
        entity_id: uuid.UUID,
        attributes: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ) -> KnowledgeEntity:
        """Update an entity."""
        
        registry = await self._get_entity_registry()
        return await registry.update_entity(entity_id, attributes, name)
    
    # ===================
    # Relationship Operations
    # ===================
    
    async def create_relationship(
        self,
        source_entity_id: uuid.UUID,
        target_entity_id: uuid.UUID,
        relationship_type: str,
        weight: float = 1.0,
        confidence: float = 1.0,
    ) -> KnowledgeRelationship:
        """Create a relationship between entities."""
        
        manager = await self._get_relationship_manager()
        return await manager.create_relationship(
            source_entity_id, target_entity_id, relationship_type,
            weight, confidence, source="system"
        )
    
    async def get_relationships(
        self,
        entity_id: Optional[uuid.UUID] = None,
        relationship_type: Optional[str] = None,
    ) -> List[KnowledgeRelationship]:
        """Get relationships."""
        
        manager = await self._get_relationship_manager()
        return await manager.get_relationships(entity_id, relationship_type)
    
    # ===================
    # Domain-Specific Queries
    # ===================
    
    async def find_goals_related_to_project(
        self,
        project_id: uuid.UUID,
    ) -> List[KnowledgeEntity]:
        """Find goals related to a project."""
        
        manager = await self._get_relationship_manager()
        registry = await self._get_entity_registry()
        
        # Find relationships from project to goals
        relationships = await manager.get_relationships(
            source_entity_id=project_id,
            relationship_type=RelationshipType.PROJECT_AFFECTS_GOAL.value,
        )
        
        goals = []
        for rel in relationships:
            goal = await registry.get_entity(rel.target_entity_id)
            if goal:
                goals.append(goal)
        
        return goals
    
    async def find_projects_for_goal(
        self,
        goal_id: uuid.UUID,
    ) -> List[KnowledgeEntity]:
        """Find projects that support a goal."""
        
        manager = await self._get_relationship_manager()
        registry = await self._get_entity_registry()
        
        relationships = await manager.get_relationships(
            target_entity_id=goal_id,
            relationship_type=RelationshipType.GOAL_REQUIRES_PROJECT.value,
        )
        
        projects = []
        for rel in relationships:
            project = await registry.get_entity(rel.source_entity_id)
            if project:
                projects.append(project)
        
        return projects
    
    async def find_risks_affecting_goal(
        self,
        goal_id: uuid.UUID,
    ) -> List[KnowledgeEntity]:
        """Find risks that threaten a goal."""
        
        manager = await self._get_relationship_manager()
        registry = await self._get_entity_registry()
        
        relationships = await manager.get_relationships(
            target_entity_id=goal_id,
            relationship_type=RelationshipType.RISK_THREATENS_GOAL.value,
        )
        
        risks = []
        for rel in relationships:
            risk = await registry.get_entity(rel.source_entity_id)
            if risk:
                risks.append(risk)
        
        return risks
    
    async def find_opportunities_for_goal(
        self,
        goal_id: uuid.UUID,
    ) -> List[KnowledgeEntity]:
        """Find opportunities that support a goal."""
        
        manager = await self._get_relationship_manager()
        registry = await self._get_entity_registry()
        
        relationships = await manager.get_relationships(
            target_entity_id=goal_id,
            relationship_type=RelationshipType.OPPORTUNITY_SUPPORTS_GOAL.value,
        )
        
        opportunities = []
        for rel in relationships:
            opp = await registry.get_entity(rel.source_entity_id)
            if opp:
                opportunities.append(opp)
        
        return opportunities
    
    async def find_related_entities(
        self,
        entity_id: uuid.UUID,
        relationship_types: Optional[List[str]] = None,
    ) -> List[KnowledgeEntity]:
        """Find all entities related to a given entity."""
        
        manager = await self._get_relationship_manager()
        registry = await self._get_entity_registry()
        
        related_ids = await manager.find_related_entities(entity_id, relationship_types)
        
        entities = []
        for rel_id in related_ids:
            entity = await registry.get_entity(rel_id)
            if entity:
                entities.append(entity)
        
        return entities
    
    # ===================
    # Graph Statistics
    # ===================
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        
        registry = await self._get_entity_registry()
        manager = await self._get_relationship_manager()
        
        entity_counts = await registry.get_entity_count()
        
        # Count relationships by type
        from sqlalchemy import select, func
        result = await self.session.execute(
            select(KnowledgeRelationship.relationship_type, func.count(KnowledgeRelationship.id))
            .group_by(KnowledgeRelationship.relationship_type)
        )
        relationship_counts = {row[0]: row[1] for row in result.all()}
        
        # Total counts
        total_entities = sum(entity_counts.values())
        total_relationships = sum(relationship_counts.values())
        
        return {
            "entities_by_type": entity_counts,
            "relationships_by_type": relationship_counts,
            "total_entities": total_entities,
            "total_relationships": total_relationships,
        }
    
    # ===================
    # Query Interface
    # ===================
    
    async def query(
        self,
        query_type: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a named query."""
        
        params = params or {}
        
        if query_type == "goals_for_project":
            project_id = uuid.UUID(params["project_id"])
            goals = await self.find_goals_related_to_project(project_id)
            return [{"id": str(g.id), "name": g.name, "type": g.entity_type} for g in goals]
        
        elif query_type == "projects_for_goal":
            goal_id = uuid.UUID(params["goal_id"])
            projects = await self.find_projects_for_goal(goal_id)
            return [{"id": str(p.id), "name": p.name, "type": p.entity_type} for p in projects]
        
        elif query_type == "risks_for_goal":
            goal_id = uuid.UUID(params["goal_id"])
            risks = await self.find_risks_affecting_goal(goal_id)
            return [{"id": str(r.id), "name": r.name, "type": r.entity_type} for r in risks]
        
        elif query_type == "opportunities_for_goal":
            goal_id = uuid.UUID(params["goal_id"])
            opportunities = await self.find_opportunities_for_goal(goal_id)
            return [{"id": str(o.id), "name": o.name, "type": o.entity_type} for o in opportunities]
        
        elif query_type == "related_entities":
            entity_id = uuid.UUID(params["entity_id"])
            entities = await self.find_related_entities(entity_id)
            return [{"id": str(e.id), "name": e.name, "type": e.entity_type} for e in entities]
        
        elif query_type == "statistics":
            return await self.get_graph_statistics()
        
        else:
            raise ValueError(f"Unknown query type: {query_type}")
    
    # ===================
    # Auto-linking
    # ===================
    
    async def auto_link_detection_event(
        self,
        event_id: uuid.UUID,
        event_type: str,
        domain: str,
        title: str,
    ) -> Optional[KnowledgeEntity]:
        """Automatically create and link a detection event entity."""
        
        # Create entity for the event
        entity = await self.create_entity(
            entity_type=event_type,
            name=title,
            attributes={"event_id": str(event_id), "domain": domain},
            domain=domain,
        )
        
        # Link to related goals if it's a risk or opportunity
        if event_type in [EntityType.RISK.value, EntityType.OPPORTUNITY.value]:
            goals = await self.get_entities(entity_type=EntityType.GOAL.value, domain=domain)
            
            rel_type = (
                RelationshipType.RISK_THREATENS_GOAL.value 
                if event_type == EntityType.RISK.value 
                else RelationshipType.OPPORTUNITY_SUPPORTS_GOAL.value
            )
            
            for goal in goals:
                await self.create_relationship(
                    source_entity_id=entity.id,
                    target_entity_id=goal.id,
                    relationship_type=rel_type,
                )
        
        increment("knowledge_updates", domain=MetricDomain.SYSTEM)
        
        return entity
    
    async def auto_link_strategic_plan(
        self,
        plan_id: uuid.UUID,
        plan_type: str,
        domains: List[str],
        title: str,
    ) -> Optional[KnowledgeEntity]:
        """Automatically create and link a strategic plan entity."""
        
        # Create entity for the plan
        entity = await self.create_entity(
            entity_type=EntityType.STRATEGIC_PLAN.value,
            name=title,
            attributes={"plan_id": str(plan_id), "plan_type": plan_type, "domains": domains},
            domain="strategic",
        )
        
        # Link to related goals and risks
        for domain in domains:
            # Link to risks that this plan might address
            risks = await self.get_entities(entity_type=EntityType.RISK.value, domain=domain)
            
            for risk in risks:
                await self.create_relationship(
                    source_entity_id=entity.id,
                    target_entity_id=risk.id,
                    relationship_type=RelationshipType.PLAN_ADDRESSES_RISK.value,
                )
            
            # Link to goals
            goals = await self.get_entities(entity_type=EntityType.GOAL.value, domain=domain)
            
            for goal in goals:
                await self.create_relationship(
                    source_entity_id=entity.id,
                    target_entity_id=goal.id,
                    relationship_type=RelationshipType.PLAN_LEADS_TO_GOAL.value,
                )
        
        increment("knowledge_updates", domain=MetricDomain.SYSTEM)
        
        return entity


async def get_knowledge_graph(session: AsyncSession) -> KnowledgeGraph:
    """Get knowledge graph instance."""
    return KnowledgeGraph(session)
