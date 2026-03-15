"""Entity registry for knowledge graph."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import KnowledgeEntity
from app.knowledge.knowledge_types import EntityType, KnowledgeDomain
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class EntityRegistry:
    """Manages entities in the knowledge graph."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_entity(
        self,
        entity_type: str,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None,
    ) -> KnowledgeEntity:
        """Create a new entity."""
        
        entity = KnowledgeEntity(
            entity_type=entity_type,
            name=name,
            attributes=attributes or {},
            domain=domain,
            valid_from=datetime.utcnow(),
        )
        
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        
        increment("entities_created", domain=MetricDomain.SYSTEM)
        
        logger.info(f"Created entity {entity.id} of type {entity_type}")
        
        return entity
    
    async def update_entity(
        self,
        entity_id: uuid.UUID,
        attributes: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> KnowledgeEntity:
        """Update an entity."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.id == entity_id)
        )
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")
        
        if attributes:
            entity.attributes = {**(entity.attributes or {}), **attributes}
        
        if name:
            entity.name = name
        
        if status:
            entity.status = status
        
        entity.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(entity)
        
        return entity
    
    async def delete_entity(
        self,
        entity_id: uuid.UUID,
    ) -> bool:
        """Delete an entity."""
        
        from sqlalchemy import select, delete
        
        result = await self.session.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.id == entity_id)
        )
        entity = result.scalar_one_or_none()
        
        if not entity:
            return False
        
        # Delete related relationships first
        await self.session.execute(
            delete(KnowledgeRelationship).where(
                (KnowledgeRelationship.source_entity_id == entity_id) |
                (KnowledgeRelationship.target_entity_id == entity_id)
            )
        )
        
        await self.session.delete(entity)
        await self.session.commit()
        
        return True
    
    async def get_entity(
        self,
        entity_id: uuid.UUID,
    ) -> Optional[KnowledgeEntity]:
        """Get an entity by ID."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_entities(
        self,
        entity_type: Optional[str] = None,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[KnowledgeEntity]:
        """Get entities with filters."""
        
        from sqlalchemy import select
        
        query = select(KnowledgeEntity).limit(limit)
        
        if entity_type:
            query = query.where(KnowledgeEntity.entity_type == entity_type)
        
        if domain:
            query = query.where(KnowledgeEntity.domain == domain)
        
        if status:
            query = query.where(KnowledgeEntity.status == status)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_entity_count(self) -> Dict[str, int]:
        """Get count of entities by type."""
        
        from sqlalchemy import select, func
        
        result = await self.session.execute(
            select(KnowledgeEntity.entity_type, func.count(KnowledgeEntity.id))
            .group_by(KnowledgeEntity.entity_type)
        )
        
        return {row[0]: row[1] for row in result.all()}


async def get_entity_registry(session: AsyncSession) -> EntityRegistry:
    """Get entity registry instance."""
    return EntityRegistry(session)
