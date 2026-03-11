"""Relationship manager for knowledge graph."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.knowledge.knowledge_types import KnowledgeRelationship, RelationshipType
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class RelationshipManager:
    """Manages relationships in the knowledge graph."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_relationship(
        self,
        source_entity_id: uuid.UUID,
        target_entity_id: uuid.UUID,
        relationship_type: str,
        weight: float = 1.0,
        confidence: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None,
        source: str = "manual",
    ) -> KnowledgeRelationship:
        """Create a new relationship."""
        
        # Validate that entities exist
        from app.knowledge.knowledge_types import KnowledgeEntity
        
        source_result = await self.session.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.id == source_entity_id)
        )
        source_entity = source_result.scalar_one_or_none()
        
        if not source_entity:
            raise ValueError(f"Source entity not found: {source_entity_id}")
        
        target_result = await self.session.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.id == target_entity_id)
        )
        target_entity = target_result.scalar_one_or_none()
        
        if not target_entity:
            raise ValueError(f"Target entity not found: {target_entity_id}")
        
        relationship = KnowledgeRelationship(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            weight=weight,
            confidence=confidence,
            attributes=attributes,
            source=source,
        )
        
        self.session.add(relationship)
        await self.session.commit()
        await self.session.refresh(relationship)
        
        increment("relationships_created", domain=MetricDomain.SYSTEM)
        
        logger.info(f"Created relationship {relationship.id}: {source_entity_id} -> {target_entity_id}")
        
        return relationship
    
    async def update_relationship(
        self,
        relationship_id: uuid.UUID,
        weight: Optional[float] = None,
        confidence: Optional[float] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeRelationship:
        """Update a relationship."""
        
        result = await self.session.execute(
            select(KnowledgeRelationship).where(KnowledgeRelationship.id == relationship_id)
        )
        relationship = result.scalar_one_or_none()
        
        if not relationship:
            raise ValueError(f"Relationship not found: {relationship_id}")
        
        if weight is not None:
            relationship.weight = weight
        
        if confidence is not None:
            relationship.confidence = confidence
        
        if attributes:
            relationship.attributes = {**(relationship.attributes or {}), **attributes}
        
        await self.session.commit()
        await self.session.refresh(relationship)
        
        return relationship
    
    async def delete_relationship(
        self,
        relationship_id: uuid.UUID,
    ) -> bool:
        """Delete a relationship."""
        
        result = await self.session.execute(
            select(KnowledgeRelationship).where(KnowledgeRelationship.id == relationship_id)
        )
        relationship = result.scalar_one_or_none()
        
        if not relationship:
            return False
        
        await self.session.delete(relationship)
        await self.session.commit()
        
        return True
    
    async def get_relationships(
        self,
        entity_id: Optional[uuid.UUID] = None,
        relationship_type: Optional[str] = None,
        source_entity_id: Optional[uuid.UUID] = None,
        target_entity_id: Optional[uuid.UUID] = None,
        limit: int = 100,
    ) -> List[KnowledgeRelationship]:
        """Get relationships with filters."""
        
        query = select(KnowledgeRelationship).limit(limit)
        
        if entity_id:
            query = query.where(
                (KnowledgeRelationship.source_entity_id == entity_id) |
                (KnowledgeRelationship.target_entity_id == entity_id)
            )
        
        if relationship_type:
            query = query.where(KnowledgeRelationship.relationship_type == relationship_type)
        
        if source_entity_id:
            query = query.where(KnowledgeRelationship.source_entity_id == source_entity_id)
        
        if target_entity_id:
            query = query.where(KnowledgeRelationship.target_entity_id == target_entity_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_outgoing_relationships(
        self,
        entity_id: uuid.UUID,
    ) -> List[KnowledgeRelationship]:
        """Get all outgoing relationships from an entity."""
        
        result = await self.session.execute(
            select(KnowledgeRelationship)
            .where(KnowledgeRelationship.source_entity_id == entity_id)
        )
        return list(result.scalars().all())
    
    async def get_incoming_relationships(
        self,
        entity_id: uuid.UUID,
    ) -> List[KnowledgeRelationship]:
        """Get all incoming relationships to an entity."""
        
        result = await self.session.execute(
            select(KnowledgeRelationship)
            .where(KnowledgeRelationship.target_entity_id == entity_id)
        )
        return list(result.scalars().all())
    
    async def find_related_entities(
        self,
        entity_id: uuid.UUID,
        relationship_types: Optional[List[str]] = None,
    ) -> List[uuid.UUID]:
        """Find all entities related to a given entity."""
        
        relationships = await self.get_relationships(entity_id=entity_id)
        
        related_ids = []
        
        for rel in relationships:
            if relationship_types and rel.relationship_type not in relationship_types:
                continue
            
            if rel.source_entity_id == entity_id:
                related_ids.append(rel.target_entity_id)
            else:
                related_ids.append(rel.source_entity_id)
        
        return related_ids


async def get_relationship_manager(session: AsyncSession) -> RelationshipManager:
    """Get relationship manager instance."""
    return RelationshipManager(session)
