"""Tests for domain modeler."""
import pytest
from app.optimization.domain_modeler import DomainModeler, get_domain_modeler
from app.optimization.optimization_types import LifeDomain, DomainDataInput


class TestDomainModeler:
    """Tests for DomainModeler class."""
    
    def test_create_default_domain_metrics(self):
        """Test creating default domain metrics."""
        modeler = DomainModeler()
        
        metrics = modeler.create_default_domain_metrics(
            domain=LifeDomain.HEALTH,
            strategic_priority=1
        )
        
        assert metrics.domain == LifeDomain.HEALTH
        assert metrics.performance_score == 5.0
        assert metrics.risk_score == 3.0
        assert metrics.opportunity_score == 5.0
        assert metrics.momentum_score == 0.0
        assert metrics.alignment_score == 5.0
        assert metrics.resource_allocation == 12.5
        assert metrics.strategic_priority == 1
    
    def test_create_domain_metrics_from_data(self):
        """Test creating domain metrics from input data."""
        modeler = DomainModeler()
        
        data = DomainDataInput(
            domain=LifeDomain.HEALTH,
            goal_progress=0.8,
            task_completion_rate=0.9,
            quality_indicators=[0.8, 0.9],
            recent_progress=0.5,
            trend_direction=0.3,
            strategic_alignment=0.8,
            goal_alignment=0.7,
            time_invested_hours=10,
            energy_invested=0.7,
        )
        
        metrics = modeler.create_domain_metrics(
            domain=LifeDomain.HEALTH,
            data=data,
            strategic_priority=2
        )
        
        assert metrics.domain == LifeDomain.HEALTH
        assert metrics.performance_score > 5.0  # Should be higher with good data
        assert metrics.strategic_priority == 2
    
    def test_composite_score_calculation(self):
        """Test composite score calculation."""
        modeler = DomainModeler()
        
        metrics = modeler.create_default_domain_metrics(LifeDomain.HEALTH)
        
        # With default values, composite should be around 5.0
        # performance 5 * 0.30 = 1.5
        # opportunity 5 * 0.20 = 1.0
        # momentum 0 * 0.15 = 0
        # alignment 5 * 0.25 = 1.25
        # (10 - risk 3) * 0.10 = 0.7
        # Total = 4.45
        assert 4.0 < metrics.composite_score < 5.0
    
    def test_health_status_property(self):
        """Test health status property."""
        modeler = DomainModeler()
        
        # Test thriving
        metrics = modeler.create_default_domain_metrics(LifeDomain.HEALTH)
        metrics._performance_score = 8.0
        assert metrics.health_status == "thriving"
        
        # Test critical
        metrics._performance_score = 2.0
        assert metrics.health_status == "critical"
    
    def test_get_all_domain_metrics(self):
        """Test getting all domain metrics."""
        modeler = DomainModeler()
        
        all_metrics = modeler.get_all_domain_metrics()
        
        assert len(all_metrics) == len(LifeDomain)
        assert all(m.domain in LifeDomain for m in all_metrics)
    
    def test_get_cache_status(self):
        """Test cache status."""
        modeler = DomainModeler()
        
        status = modeler.get_cache_status()
        
        assert "cached_domains" in status
        assert "last_update" in status
        assert "domains" in status
    
    def test_reset_domain(self):
        """Test resetting a domain."""
        modeler = DomainModeler()
        
        # First get a domain
        metrics = modeler.get_domain_metrics(LifeDomain.HEALTH)
        assert metrics is not None
        
        # Reset it
        modeler.reset_domain(LifeDomain.HEALTH)
        
        # Should create a new default
        metrics2 = modeler.get_domain_metrics(LifeDomain.HEALTH)
        assert metrics2 is not None


class TestDomainModelerIntegration:
    """Integration tests for DomainModeler."""
    
    def test_get_global_modeler(self):
        """Test getting global modeler."""
        modeler1 = get_domain_modeler()
        modeler2 = get_domain_modeler()
        
        # Should return the same instance
        assert modeler1 is modeler2
