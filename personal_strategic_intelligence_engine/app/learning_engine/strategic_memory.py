"""Strategic Memory Store - maintains long-term system memory.

The Strategic Memory Store preserves signals, strategies, decisions, and executions
as long-term knowledge that can be retrieved for future reasoning cycles.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning_engine.memory_models import (
    MemoryCategory,
    MemoryRecord,
    SourceType,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategicMemoryStore:
    """
    Maintains long-term system memory.
    
    Responsibilities:
    - Store signals, strategies, decisions, and executions
    - Retrieve similar historical cases
    - Provide context to agents during reasoning cycles
    - Preserve institutional system knowledge
    """
    
    def __init__(self):
        # Primary storage: id -> MemoryRecord
        self._memory: Dict[str, MemoryRecord] = {}
        
        # Indexes for efficient retrieval
        self._by_source: Dict[str, List[str]] = {}  # source_id -> [record_ids]
        self._by_category: Dict[str, List[str]] = {}  # category -> [record_ids]
        self._by_source_type: Dict[str, List[str]] = {}  # source_type -> [record_ids]
        self._by_tag: Dict[str, List[str]] = {}  # tag -> [record_ids]
    
    def store(
        self,
        source_type: SourceType,
        source_id: str,
        category: MemoryCategory,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> MemoryRecord:
        """Store a new memory record."""
        record = MemoryRecord(
            source_type=source_type,
            source_id=source_id,
            category=category,
            summary=summary,
            metadata=metadata or {},
            tags=tags or [],
        )
        
        self._memory[record.id] = record
        
        # Update indexes
        self._update_indexes(record)
        
        logger.info(f"Stored memory record: {record.id} ({category})")
        
        return record
    
    def _update_indexes(self, record: MemoryRecord) -> None:
        """Update all indexes for a record."""
        # By source_id
        if record.source_id not in self._by_source:
            self._by_source[record.source_id] = []
        self._by_source[record.source_id].append(record.id)
        
        # By category
        category_key = record.category.value if hasattr(record.category, 'value') else str(record.category)
        if category_key not in self._by_category:
            self._by_category[category_key] = []
        self._by_category[category_key].append(record.id)
        
        # By source_type
        source_key = record.source_type.value if hasattr(record.source_type, 'value') else str(record.source_type)
        if source_key not in self._by_source_type:
            self._by_source_type[source_key] = []
        self._by_source_type[source_key].append(record.id)
        
        # By tags
        for tag in record.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(record.id)
    
    def get(self, record_id: str) -> Optional[MemoryRecord]:
        """Retrieve a memory record by ID."""
        return self._memory.get(record_id)
    
    def get_by_source(self, source_id: str) -> List[MemoryRecord]:
        """Get all records from a specific source."""
        record_ids = self._by_source.get(source_id, [])
        return [self._memory[rid] for rid in record_ids if rid in self._memory]
    
    def get_by_category(self, category: MemoryCategory) -> List[MemoryRecord]:
        """Get all records of a specific category."""
        category_key = category.value if hasattr(category, 'value') else str(category)
        record_ids = self._by_category.get(category_key, [])
        return [self._memory[rid] for rid in record_ids if rid in self._memory]
    
    def get_by_source_type(self, source_type: SourceType) -> List[MemoryRecord]:
        """Get all records from a specific source type."""
        source_key = source_type.value if hasattr(source_type, 'value') else str(source_type)
        record_ids = self._by_source_type.get(source_key, [])
        return [self._memory[rid] for rid in record_ids if rid in self._memory]
    
    def get_by_tag(self, tag: str) -> List[MemoryRecord]:
        """Get all records with a specific tag."""
        record_ids = self._by_tag.get(tag, [])
        return [self._memory[rid] for rid in record_ids if rid in self._memory]
    
    def get_recent(self, limit: int = 50) -> List[MemoryRecord]:
        """Get the most recent memory records."""
        sorted_records = sorted(
            self._memory.values(),
            key=lambda r: r.timestamp,
            reverse=True,
        )
        return sorted_records[:limit]
    
    def find_similar(
        self,
        category: Optional[MemoryCategory] = None,
        source_type: Optional[SourceType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryRecord]:
        """Find similar memory records based on criteria."""
        candidates = list(self._memory.values())
        
        # Filter by category
        if category:
            category_key = category.value if hasattr(category, 'value') else str(category)
            candidates = [r for r in candidates if r.category == category_key]
        
        # Filter by source_type
        if source_type:
            source_key = source_type.value if hasattr(source_type, 'value') else str(source_type)
            candidates = [r for r in candidates if r.source_type == source_key]
        
        # Filter by tags
        if tags:
            candidates = [r for r in candidates if any(tag in r.tags for tag in tags)]
        
        # Return most recent
        sorted_candidates = sorted(
            candidates,
            key=lambda r: r.timestamp,
            reverse=True,
        )
        return sorted_candidates[:limit]
    
    def search(self, query: str, limit: int = 50) -> List[MemoryRecord]:
        """Search memory records by query string."""
        results = []
        query_lower = query.lower()
        
        for record in self._memory.values():
            if query_lower in record.summary.lower():
                results.append(record)
            elif record.metadata and query_lower in str(record.metadata).lower():
                results.append(record)
        
        # Return most recent
        sorted_results = sorted(
            results,
            key=lambda r: r.timestamp,
            reverse=True,
        )
        return sorted_results[:limit]
    
    def delete(self, record_id: str) -> bool:
        """Delete a memory record."""
        if record_id in self._memory:
            del self._memory[record_id]
            # Note: indexes are not cleaned up in this simple implementation
            logger.info(f"Deleted memory record: {record_id}")
            return True
        return False
    
    def clear_category(self, category: MemoryCategory) -> int:
        """Clear all records of a specific category."""
        category_key = category.value if hasattr(category, 'value') else str(category)
        record_ids = self._by_category.get(category_key, [])
        count = len(record_ids)
        
        for rid in record_ids:
            if rid in self._memory:
                del self._memory[rid]
        
        logger.info(f"Cleared {count} records from category {category}")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_records": len(self._memory),
            "by_category": {
                k: len(v) for k, v in self._by_category.items()
            },
            "by_source_type": {
                k: len(v) for k, v in self._by_source_type.items()
            },
            "by_tag": {
                k: len(v) for k, v in self._by_tag.items()
            },
        }


# Singleton instance
_strategic_memory: Optional[StrategicMemoryStore] = None


def get_strategic_memory() -> StrategicMemoryStore:
    """Get the global strategic memory store instance."""
    global _strategic_memory
    if _strategic_memory is None:
        _strategic_memory = StrategicMemoryStore()
    return _strategic_memory


def reset_strategic_memory() -> None:
    """Reset the strategic memory (for testing)."""
    global _strategic_memory
    _strategic_memory = None
