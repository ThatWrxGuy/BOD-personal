"""Tests for Memory Manager."""
import pytest

from app.state_engine import (
    MemoryManager,
    StateRepository,
    MemoryTier,
)
from app.state_engine.state_models import MemoryEntry


class TestMemoryManager:
    """Tests for MemoryManager."""

    def setup_method(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MemoryManager(
            repository=StateRepository(self.temp_dir),
            short_term_limit=5,
            strategic_limit=10,
        )

    def test_store_short_term_memory(self):
        """Test storing short-term memory."""
        entry_id = self.manager.store_short_term({"data": "test"}, importance=0.5)
        assert entry_id is not None
        
        memories = self.manager.retrieve_by_tier(MemoryTier.SHORT_TERM)
        assert len(memories) == 1

    def test_store_strategic_memory(self):
        """Test storing strategic memory."""
        entry_id = self.manager.store_strategic({"data": "test"}, importance=0.7)
        assert entry_id is not None

    def test_store_doctrine_memory(self):
        """Test storing doctrine memory."""
        entry_id = self.manager.store_doctrine_memory({"data": "test"}, importance=0.9)
        assert entry_id is not None

    def test_retrieve_memory(self):
        """Test retrieving memory."""
        entry_id = self.manager.store_short_term({"key": "value"})
        memory = self.manager.retrieve_memory(MemoryTier.SHORT_TERM, entry_id)
        assert memory is not None
        assert memory.content["key"] == "value"

    def test_search_memory(self):
        """Test searching memory."""
        self.manager.store_short_term({"content": "important data"})
        results = self.manager.search_memory("important")
        assert len(results) >= 1

    def test_summarize_memory(self):
        """Test summarizing memory."""
        self.manager.store_short_term({"data": "test"})
        summary = self.manager.summarize_memory()
        assert "short_term" in summary

    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        self.manager.store_short_term({"data": "test"})
        stats = self.manager.get_memory_stats()
        assert "short_term" in stats

    def test_short_term_limit(self):
        """Test that short-term memory enforces limit."""
        for i in range(10):
            self.manager.store_short_term({"index": i})
        
        memories = self.manager.retrieve_by_tier(MemoryTier.SHORT_TERM)
        # Should be limited to 5 (short_term_limit)
        assert len(memories) <= 5

    def test_get_important_memories(self):
        """Test getting important memories."""
        self.manager.store_short_term({"data": "low"}, importance=0.3)
        self.manager.store_short_term({"data": "high"}, importance=0.8)
        
        important = self.manager.get_important_memories(threshold=0.7)
        assert len(important) >= 1

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestMemoryTiers:
    """Tests for memory tier operations."""

    def setup_method(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MemoryManager(repository=StateRepository(self.temp_dir))

    def test_retrieve_by_tier(self):
        """Test retrieving by tier."""
        self.manager.store_short_term({"data": "short"})
        self.manager.store_strategic({"data": "strategic"})
        
        short = self.manager.retrieve_by_tier(MemoryTier.SHORT_TERM)
        strategic = self.manager.retrieve_by_tier(MemoryTier.STRATEGIC)
        
        assert len(short) >= 1
        assert len(strategic) >= 1

    def test_retrieve_recent(self):
        """Test retrieving recent memories."""
        self.manager.store_short_term({"data": "1"})
        self.manager.store_short_term({"data": "2"})
        
        recent = self.manager.retrieve_recent(limit=5)
        assert len(recent) >= 2

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
