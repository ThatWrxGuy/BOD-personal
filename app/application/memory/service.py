"""
BB-APP-002: Memory Service

Per BB-APP-002 Section 8.6 - Memory Integration.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.read_models import (
    MemoryEntryReadModel,
    MemoryEntityLink,
)


class MemoryService:
    """Service for memory/knowledge base."""
    
    # Mock memory store
    _memories = {
        "memory-1": {
            "id": "memory-1",
            "title": "Q4 Goals Review",
            "content": "Completed major career milestones: promotion achieved, salary increased by 15%, new responsibilities assumed. Financial goals on track with retirement contributions at 15% of income.",
            "memory_type": "reflection",
            "tags": ["Career", "Goals", "Q4"],
            "domains": ["Career", "Finance"],
            "linked_entities": [
                {"entity_type": "action", "entity_id": "action-2"},
                {"entity_type": "brief", "entity_id": "brief-001"},
            ],
            "created_at": datetime.now() - timedelta(days=7),
            "updated_at": datetime.now() - timedelta(days=7),
        },
        "memory-2": {
            "id": "memory-2",
            "title": "Investment Strategy Notes",
            "content": "Discussed portfolio rebalancing with financial advisor. Maintained 80/20 stocks/bonds allocation. Increased emergency fund to cover 6 months expenses.",
            "memory_type": "insight",
            "tags": ["Finance", "Investment"],
            "domains": ["Finance"],
            "linked_entities": [
                {"entity_type": "recommendation", "entity_id": "rec-1"},
            ],
            "created_at": datetime.now() - timedelta(days=10),
            "updated_at": datetime.now() - timedelta(days=10),
        },
        "memory-3": {
            "id": "memory-3",
            "title": "Health Check Results",
            "content": "Annual physical showed improvements in cardiovascular health. BMI in healthy range. Recommended to maintain sleep consistency and increase exercise frequency.",
            "memory_type": "insight",
            "tags": ["Health", "Medical"],
            "domains": ["Health"],
            "linked_entities": [
                {"entity_type": "recommendation", "entity_id": "rec-3"},
                {"entity_type": "action", "entity_id": "action-4"},
            ],
            "created_at": datetime.now() - timedelta(days=14),
            "updated_at": datetime.now() - timedelta(days=14),
        },
    }
    
    async def list_memories(
        self,
        user_id: str,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[MemoryEntryReadModel]:
        """List memories with optional filters."""
        results = []
        
        for memory in self._memories.values():
            # Apply domain filter
            if domain and not any(d.lower() == domain.lower() for d in memory["domains"]):
                continue
            
            # Apply tag filter
            if tags and not any(t.lower() in [tag.lower() for tag in memory["tags"]] for t in tags):
                continue
            
            linked_entities = [
                MemoryEntityLink(**entity)
                for entity in memory["linked_entities"]
            ]
            
            results.append(MemoryEntryReadModel(
                id=memory["id"],
                title=memory["title"],
                content=memory["content"],
                memory_type=memory["memory_type"],
                tags=memory["tags"],
                domains=memory["domains"],
                linked_entities=linked_entities,
                created_at=memory["created_at"],
                updated_at=memory["updated_at"],
            ))
        
        # Sort by most recent
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results[:limit]
    
    async def get_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> Optional[MemoryEntryReadModel]:
        """Get detailed memory entry."""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        linked_entities = [
            MemoryEntityLink(**entity)
            for entity in memory["linked_entities"]
        ]
        
        return MemoryEntryReadModel(
            id=memory["id"],
            title=memory["title"],
            content=memory["content"],
            memory_type=memory["memory_type"],
            tags=memory["tags"],
            domains=memory["domains"],
            linked_entities=linked_entities,
            created_at=memory["created_at"],
            updated_at=memory["updated_at"],
        )
    
    async def create_memory(
        self,
        user_id: str,
        title: str,
        content: str,
        memory_type: str = "general",
        tags: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        linked_entities: Optional[List[dict]] = None
    ) -> str:
        """Create a new memory entry."""
        import uuid
        memory_id = str(uuid.uuid4())
        
        self._memories[memory_id] = {
            "id": memory_id,
            "title": title,
            "content": content,
            "memory_type": memory_type,
            "tags": tags or [],
            "domains": domains or [],
            "linked_entities": linked_entities or [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        return memory_id
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[MemoryEntryReadModel]:
        """Search memories by query."""
        results = []
        query_lower = query.lower()
        
        for memory in self._memories.values():
            # Search in title and content
            if query_lower in memory["title"].lower() or query_lower in memory["content"].lower():
                linked_entities = [
                    MemoryEntityLink(**entity)
                    for entity in memory["linked_entities"]
                ]
                
                results.append(MemoryEntryReadModel(
                    id=memory["id"],
                    title=memory["title"],
                    content=memory["content"],
                    memory_type=memory["memory_type"],
                    tags=memory["tags"],
                    domains=memory["domains"],
                    linked_entities=linked_entities,
                    created_at=memory["created_at"],
                    updated_at=memory["updated_at"],
                ))
        
        return results[:limit]


# Singleton instance
memory_service = MemoryService()
