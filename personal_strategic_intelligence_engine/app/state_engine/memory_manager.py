"""Memory manager for three-tier memory system."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.state_engine.state_models import MemoryEntry
from app.state_engine.state_types import MemoryTier
from app.state_engine.state_repository import StateRepository


class MemoryManager:
    """Manages three-tier memory system.
    
    Tiers:
    - SHORT_TERM: Last N system cycles for immediate adjustments
    - STRATEGIC: Medium-term historical states for forecasting/simulation
    - DOCTRINE: Long-term lessons and strategic insights
    """
    
    # Default limits for each tier
    DEFAULT_SHORT_TERM_LIMIT = 10
    DEFAULT_STRATEGIC_LIMIT = 100
    DEFAULT_DOCTRINE_LIMIT = 500
    
    def __init__(
        self,
        repository: Optional[StateRepository] = None,
        short_term_limit: int = DEFAULT_SHORT_TERM_LIMIT,
        strategic_limit: int = DEFAULT_STRATEGIC_LIMIT,
        doctrine_limit: int = DEFAULT_DOCTRINE_LIMIT,
    ):
        self.repository = repository or StateRepository()
        
        # Memory limits
        self.short_term_limit = short_term_limit
        self.strategic_limit = strategic_limit
        self.doctrine_limit = doctrine_limit
        
        # In-memory cache
        self._short_term_memory: List[MemoryEntry] = []
        self._strategic_memory: List[MemoryEntry] = []
    
    # ============= Store Operations =============
    
    def store_memory(
        self,
        memory_type: MemoryTier,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store a memory entry in the appropriate tier.
        
        Args:
            memory_type: Which tier to store in
            content: The content to store
            importance: Importance score (0-1)
            tags: Optional tags for categorization
            
        Returns:
            The entry ID
        """
        entry_id = f"mem_{memory_type.value[:3]}_{uuid.uuid4().hex[:12]}"
        
        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=memory_type.value,
            content=content,
            timestamp=datetime.utcnow(),
            importance=importance,
            tags=tags or [],
        )
        
        # Store in repository
        self.repository.store_memory(entry)
        
        # Add to in-memory cache for short-term
        if memory_type == MemoryTier.SHORT_TERM:
            self._short_term_memory.append(entry)
            self._enforce_limit(MemoryTier.SHORT_TERM)
        
        return entry_id
    
    def store_short_term(
        self,
        content: Dict[str, Any],
        importance: float = 0.5,
    ) -> str:
        """Store a short-term memory."""
        return self.store_memory(MemoryTier.SHORT_TERM, content, importance)
    
    def store_strategic(
        self,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store a strategic memory."""
        return self.store_memory(MemoryTier.STRATEGIC, content, importance, tags)
    
    def store_doctrine_memory(
        self,
        content: Dict[str, Any],
        importance: float = 0.7,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store a doctrine-level memory."""
        return self.store_memory(MemoryTier.DOCTRINE, content, importance, tags)
    
    # ============= Retrieve Operations =============
    
    def retrieve_memory(
        self,
        memory_type: MemoryTier,
        entry_id: str,
    ) -> Optional[MemoryEntry]:
        """Retrieve a specific memory entry.
        
        Args:
            memory_type: The tier to search in
            entry_id: The entry ID to retrieve
            
        Returns:
            The memory entry, or None if not found
        """
        # Check cache first for short-term
        if memory_type == MemoryTier.SHORT_TERM:
            for entry in self._short_term_memory:
                if entry.entry_id == entry_id:
                    return entry
        
        # Check repository
        return self.repository.get_memory(entry_id, memory_type.value)
    
    def retrieve_by_tier(
        self,
        memory_type: MemoryTier,
        limit: Optional[int] = None,
    ) -> List[MemoryEntry]:
        """Retrieve memories by tier.
        
        Args:
            memory_type: The tier to retrieve from
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries
        """
        if memory_type == MemoryTier.SHORT_TERM:
            # Return from cache
            entries = self._short_term_memory[-limit:] if limit else self._short_term_memory
            return list(reversed(entries))
        
        # Get from repository for other tiers
        limit = limit or {
            MemoryTier.STRATEGIC: self.strategic_limit,
            MemoryTier.DOCTRINE: self.doctrine_limit,
        }.get(memory_type, 100)
        
        return self.repository.get_memory_by_tier(memory_type, limit)
    
    def retrieve_recent(self, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve recent memories across all tiers.
        
        Args:
            limit: Maximum total entries to return
            
        Returns:
            Combined list of recent memories
        """
        all_memories = self.repository.get_all_memory(limit)
        return all_memories
    
    def search_memory(
        self,
        query: str,
        memory_type: Optional[MemoryTier] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """Search memory entries.
        
        Args:
            query: Search query (matches against content)
            memory_type: Optional tier to search in
            tags: Optional tags to filter by
            limit: Maximum results
            
        Returns:
            Matching memory entries
        """
        results = []
        
        tiers = [memory_type] if memory_type else list(MemoryTier)
        
        for tier in tiers:
            entries = self.retrieve_by_tier(tier, limit=100)
            
            for entry in entries:
                # Check tags
                if tags:
                    if not any(tag in entry.tags for tag in tags):
                        continue
                
                # Check content
                content_str = str(entry.content).lower()
                if query.lower() in content_str:
                    results.append(entry)
                
                if len(results) >= limit:
                    break
        
        return results[:limit]
    
    # ============= Summary Operations =============
    
    def summarize_memory(
        self,
        memory_type: Optional[MemoryTier] = None,
    ) -> Dict[str, Any]:
        """Summarize memory contents.
        
        Args:
            memory_type: Optional tier to summarize, or None for all
            
        Returns:
            Summary of memory contents
        """
        if memory_type:
            entries = self.retrieve_by_tier(memory_type)
            return {
                "tier": memory_type.value,
                "count": len(entries),
                "oldest": entries[0].timestamp.isoformat() if entries else None,
                "newest": entries[-1].timestamp.isoformat() if entries else None,
            }
        
        # Summarize all tiers
        summary = {}
        for tier in MemoryTier:
            entries = self.retrieve_by_tier(tier)
            summary[tier.value] = {
                "count": len(entries),
                "oldest": entries[0].timestamp.isoformat() if entries else None,
                "newest": entries[-1].timestamp.isoformat() if entries else None,
            }
        
        return summary
    
    def get_important_memories(self, threshold: float = 0.7) -> List[MemoryEntry]:
        """Get memories with importance above threshold.
        
        Args:
            threshold: Minimum importance score
            
        Returns:
            List of important memories
        """
        results = []
        
        for tier in MemoryTier:
            entries = self.retrieve_by_tier(tier, limit=500)
            for entry in entries:
                if entry.importance >= threshold:
                    results.append(entry)
        
        # Sort by importance
        results.sort(key=lambda x: x.importance, reverse=True)
        return results
    
    # ============= Delete Operations =============
    
    def delete_memory(
        self,
        memory_type: MemoryTier,
        entry_id: str,
    ) -> bool:
        """Delete a memory entry.
        
        Args:
            memory_type: The tier to delete from
            entry_id: The entry ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Remove from cache if short-term
        if memory_type == MemoryTier.SHORT_TERM:
            self._short_term_memory = [
                e for e in self._short_term_memory
                if e.entry_id != entry_id
            ]
        
        return self.repository.delete_memory(entry_id, memory_type.value)
    
    def clear_tier(self, memory_type: MemoryTier) -> int:
        """Clear all memories from a tier.
        
        Args:
            memory_type: The tier to clear
            
        Returns:
            Number of entries cleared
        """
        if memory_type == MemoryTier.SHORT_TERM:
            count = len(self._short_term_memory)
            self._short_term_memory.clear()
            return count
        
        # For persistent tiers, we'd need to iterate and delete
        return 0
    
    # ============= Utility =============
    
    def _enforce_limit(self, memory_type: MemoryTier):
        """Enforce memory limits for a tier."""
        if memory_type == MemoryTier.SHORT_TERM:
            while len(self._short_term_memory) > self.short_term_limit:
                self._short_term_memory.pop(0)
    
    def promote_to_strategic(self, entry_id: str) -> bool:
        """Promote a short-term memory to strategic tier.
        
        Args:
            entry_id: The entry to promote
            
        Returns:
            True if promoted, False if not found
        """
        entry = self.retrieve_memory(MemoryTier.SHORT_TERM, entry_id)
        if not entry:
            return False
        
        # Store in strategic tier
        self.store_strategic(
            content=entry.content,
            importance=entry.importance,
            tags=entry.tags + ["promoted"],
        )
        
        # Remove from short-term
        self.delete_memory(MemoryTier.SHORT_TERM, entry_id)
        return True
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "short_term": {
                "count": len(self._short_term_memory),
                "limit": self.short_term_limit,
            },
            "strategic": {
                "count": len(self.retrieve_by_tier(MemoryTier.STRATEGIC)),
                "limit": self.strategic_limit,
            },
            "doctrine": {
                "count": len(self.retrieve_by_tier(MemoryTier.DOCTRINE)),
                "limit": self.doctrine_limit,
            },
        }
