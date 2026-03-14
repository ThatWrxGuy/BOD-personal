"""Knowledge graph API routes."""
import uuid
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.knowledge.knowledge_graph import get_knowledge_graph
from app.models.knowledge import KnowledgeEntity, KnowledgeRelationship

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/entities")
async def list_entities(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """List knowledge graph entities."""
    
    graph = await get_knowledge_graph(session)
    entities = await graph.get_entities(entity_type, domain, limit)
    
    return {
        "entities": [
            {
                "id": str(e.id),
                "entity_type": e.entity_type,
                "name": e.name,
                "domain": e.domain,
                "status": e.status,
                "attributes": e.attributes,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entities
        ]
    }


@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get entity details."""
    
    graph = await get_knowledge_graph(session)
    entity = await graph.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Get related entities
    relationships = await graph.get_relationships(entity_id)
    
    return {
        "id": str(entity.id),
        "entity_type": entity.entity_type,
        "name": entity.name,
        "domain": entity.domain,
        "status": entity.status,
        "attributes": entity.attributes,
        "created_at": entity.created_at.isoformat() if entity.created_at else None,
        "relationships": [
            {
                "id": str(r.id),
                "source_id": str(r.source_entity_id),
                "target_id": str(r.target_entity_id),
                "relationship_type": r.relationship_type,
                "weight": r.weight,
            }
            for r in relationships
        ]
    }


@router.get("/relationships")
async def list_relationships(
    entity_id: Optional[uuid.UUID] = Query(None, description="Filter by entity ID"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """List knowledge graph relationships."""
    
    graph = await get_knowledge_graph(session)
    relationships = await graph.get_relationships(entity_id, relationship_type)
    
    return {
        "relationships": [
            {
                "id": str(r.id),
                "source_entity_id": str(r.source_entity_id),
                "target_entity_id": str(r.target_entity_id),
                "relationship_type": r.relationship_type,
                "weight": r.weight,
                "confidence": r.confidence,
                "source": r.source,
            }
            for r in relationships[:limit]
        ]
    }


@router.post("/entities")
async def create_entity(
    entity_type: str = Query(..., description="Entity type"),
    name: str = Query(..., description="Entity name"),
    domain: Optional[str] = Query(None, description="Domain"),
    attributes: Optional[Dict[str, Any]] = Body(None, description="Entity attributes"),
    session: AsyncSession = Depends(get_db),
):
    """Create a new entity."""
    
    graph = await get_knowledge_graph(session)
    
    try:
        entity = await graph.create_entity(entity_type, name, attributes, domain)
        
        return {
            "id": str(entity.id),
            "entity_type": entity.entity_type,
            "name": entity.name,
            "message": "Entity created",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationships")
async def create_relationship(
    source_entity_id: uuid.UUID = Query(..., description="Source entity ID"),
    target_entity_id: uuid.UUID = Query(..., description="Target entity ID"),
    relationship_type: str = Query(..., description="Relationship type"),
    weight: float = Query(1.0, description="Relationship weight"),
    confidence: float = Query(1.0, description="Confidence"),
    session: AsyncSession = Depends(get_db),
):
    """Create a new relationship."""
    
    graph = await get_knowledge_graph(session)
    
    try:
        relationship = await graph.create_relationship(
            source_entity_id,
            target_entity_id,
            relationship_type,
            weight,
            confidence,
        )
        
        return {
            "id": str(relationship.id),
            "message": "Relationship created",
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def execute_query(
    query_type: str = Query(..., description="Query type"),
    params: Optional[Dict[str, Any]] = Body(None, description="Query parameters"),
    session: AsyncSession = Depends(get_db),
):
    """Execute a knowledge graph query."""
    
    graph = await get_knowledge_graph(session)
    
    try:
        results = await graph.query(query_type, params)
        return {"results": results}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(
    session: AsyncSession = Depends(get_db),
):
    """Get knowledge graph statistics."""
    
    graph = await get_knowledge_graph(session)
    stats = await graph.get_graph_statistics()
    
    return stats


@router.delete("/entities/{entity_id}")
async def delete_entity(
    entity_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Delete an entity and its relationships."""
    
    from app.knowledge.entity_registry import get_entity_registry
    
    registry = await get_entity_registry(session)
    
    try:
        success = await registry.delete_entity(entity_id)
        
        if success:
            return {"message": "Entity deleted"}
        else:
            raise HTTPException(status_code=404, detail="Entity not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
