"""Tests for Doctrine Manager."""
import pytest
from datetime import datetime

from app.state_engine import (
    DoctrineManager,
    StateRepository,
)
from app.state_engine.state_models import DoctrineEntry


class TestDoctrineManager:
    """Tests for DoctrineManager."""

    def setup_method(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.manager = DoctrineManager(repository=StateRepository(self.temp_dir))

    def test_add_doctrine_entry(self):
        """Test adding a doctrine entry."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[{"type": "test"}],
            origin_cycle="cycle_1",
            confidence_level=0.7,
        )
        assert doc_id is not None

    def test_get_doctrine(self):
        """Test retrieving a doctrine entry."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
        )
        
        doctrine = self.manager.get_doctrine(doc_id)
        assert doctrine is not None
        assert doctrine.strategic_rule == "Test rule"

    def test_get_active_doctrine(self):
        """Test getting active doctrine entries."""
        self.manager.add_doctrine_entry(
            strategic_rule="Active rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
        )
        
        active = self.manager.get_active_doctrine()
        assert len(active) >= 1

    def test_update_doctrine_confidence(self):
        """Test updating doctrine confidence."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
            confidence_level=0.5,
        )
        
        result = self.manager.update_doctrine_confidence(doc_id, 0.8)
        assert result is True
        
        doctrine = self.manager.get_doctrine(doc_id)
        assert doctrine.confidence_level == 0.8

    def test_add_evidence(self):
        """Test adding evidence to doctrine."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
        )
        
        result = self.manager.add_evidence(doc_id, {"type": "new_evidence"})
        assert result is True
        
        doctrine = self.manager.get_doctrine(doc_id)
        assert len(doctrine.supporting_evidence) == 1

    def test_evolve_doctrine(self):
        """Test evolving doctrine based on outcome."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
            confidence_level=0.5,
        )
        
        outcome = {"success": 0.8, "details": "Good outcome"}
        result = self.manager.evolve_doctrine(doc_id, outcome)
        assert result is True

    def test_deactivate_doctrine(self):
        """Test deactivating doctrine."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
        )
        
        result = self.manager.deactivate_doctrine(doc_id)
        assert result is True
        
        active = self.manager.get_active_doctrine()
        assert not any(d.doctrine_id == doc_id for d in active)

    def test_reactivate_doctrine(self):
        """Test reactivating doctrine."""
        doc_id = self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
        )
        
        self.manager.deactivate_doctrine(doc_id)
        result = self.manager.reactivate_doctrine(doc_id)
        assert result is True

    def test_search_doctrine(self):
        """Test searching doctrine."""
        self.manager.add_doctrine_entry(
            strategic_rule="Health is important",
            supporting_evidence=[],
            origin_cycle="cycle_1",
        )
        
        results = self.manager.search_doctrine("health")
        assert len(results) >= 1

    def test_get_doctrine_by_confidence(self):
        """Test getting doctrine by confidence level."""
        self.manager.add_doctrine_entry(
            strategic_rule="High confidence rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
            confidence_level=0.9,
        )
        self.manager.add_doctrine_entry(
            strategic_rule="Low confidence rule",
            supporting_evidence=[],
            origin_cycle="cycle_2",
            confidence_level=0.2,
        )
        
        high = self.manager.get_doctrine_by_confidence(0.8)
        assert len(high) >= 1

    def test_get_doctrine_stats(self):
        """Test getting doctrine statistics."""
        self.manager.add_doctrine_entry(
            strategic_rule="Test rule",
            supporting_evidence=[],
            origin_cycle="cycle_1",
            confidence_level=0.7,
        )
        
        stats = self.manager.get_doctrine_stats()
        assert "total" in stats
        assert "active" in stats
        assert "avg_confidence" in stats

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
