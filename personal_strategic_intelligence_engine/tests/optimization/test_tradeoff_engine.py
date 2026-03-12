"""Tests for tradeoff engine."""
import pytest
from app.optimization.tradeoff_engine import TradeoffEngine, get_tradeoff_engine
from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    OptimizationPolicy,
    TradeoffType,
)


class TestTradeoffEngine:
    """Tests for TradeoffEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create a tradeoff engine instance."""
        return TradeoffEngine()
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample domain metrics for tradeoff testing."""
        return [
            DomainMetrics(
                domain=LifeDomain.HEALTH,
                performance_score=7.0,
                risk_score=3.0,
                opportunity_score=6.0,
                momentum_score=2.0,
                alignment_score=7.0,
                resource_allocation=20.0,
                strategic_priority=1,
            ),
            DomainMetrics(
                domain=LifeDomain.CAREER,
                performance_score=8.0,
                risk_score=4.0,
                opportunity_score=8.0,
                momentum_score=3.0,
                alignment_score=8.0,
                resource_allocation=35.0,
                strategic_priority=2,
            ),
        ]
    
    @pytest.fixture
    def policy(self):
        """Create a test policy."""
        return OptimizationPolicy()
    
    def test_detect_conflicts(self, engine, sample_metrics):
        """Test detecting conflicts between domains."""
        conflicts = engine.detect_conflicts(sample_metrics)
        
        assert isinstance(conflicts, list)
    
    def test_detect_conflicts_resource_imbalance(self, engine):
        """Test detecting resource imbalance conflicts."""
        # Create metrics with resource imbalance
        metrics = [
            DomainMetrics(
                domain=LifeDomain.HEALTH,
                performance_score=7.0,
                risk_score=3.0,
                opportunity_score=6.0,
                momentum_score=2.0,
                alignment_score=7.0,
                resource_allocation=50.0,  # High
                strategic_priority=1,
            ),
            DomainMetrics(
                domain=LifeDomain.WEALTH,
                performance_score=6.0,
                risk_score=4.0,
                opportunity_score=7.0,
                momentum_score=1.0,
                alignment_score=6.0,
                resource_allocation=45.0,  # High
                strategic_priority=2,
            ),
            DomainMetrics(
                domain=LifeDomain.CAREER,
                performance_score=8.0,
                risk_score=3.0,
                opportunity_score=8.0,
                momentum_score=2.0,
                alignment_score=8.0,
                resource_allocation=40.0,  # High
                strategic_priority=3,
            ),
            DomainMetrics(
                domain=LifeDomain.LEARNING,
                performance_score=4.0,
                risk_score=5.0,
                opportunity_score=5.0,
                momentum_score=-1.0,
                alignment_score=5.0,
                resource_allocation=10.0,  # Low
                strategic_priority=4,
            ),
            DomainMetrics(
                domain=LifeDomain.RELATIONSHIPS,
                performance_score=3.0,
                risk_score=4.0,
                opportunity_score=4.0,
                momentum_score=-2.0,
                alignment_score=6.0,
                resource_allocation=8.0,  # Low
                strategic_priority=5,
            ),
        ]
        
        conflicts = engine.detect_conflicts(metrics)
        
        # Should detect resource imbalance
        assert any(c.get("type") == "resource_imbalance" for c in conflicts)
    
    def test_resolve_tradeoff(self, engine, sample_metrics, policy):
        """Test resolving a tradeoff between domains."""
        decision = engine.resolve_tradeoff(
            domain_a=LifeDomain.HEALTH,
            domain_b=LifeDomain.CAREER,
            metrics_a=sample_metrics[0],
            metrics_b=sample_metrics[1],
            policy=policy
        )
        
        assert decision.winner is not None
        assert decision.loser is not None
        assert decision.winner != decision.loser
        assert -1 <= decision.long_term_value_impact <= 1
        assert 0 <= decision.risk_mitigation_score <= 1
        assert 0 <= decision.sustainability_score <= 1
    
    def test_tradeoff_reasoning_generation(self, engine, sample_metrics, policy):
        """Test that tradeoff reasoning is generated."""
        decision = engine.resolve_tradeoff(
            domain_a=LifeDomain.HEALTH,
            domain_b=LifeDomain.CAREER,
            metrics_a=sample_metrics[0],
            metrics_b=sample_metrics[1],
            policy=policy
        )
        
        assert len(decision.reasoning) > 0
        assert "prioritized" in decision.reasoning.lower()
    
    def test_resolve_all_tradeoffs(self, engine, sample_metrics, policy):
        """Test resolving all tradeoffs."""
        decisions = engine.resolve_all_tradeoffs(sample_metrics, policy)
        
        assert isinstance(decisions, list)
    
    def test_tradeoff_type_classification(self, engine):
        """Test tradeoff type classification."""
        # Test career vs health
        m1 = DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=7.0,
            risk_score=4.0,
            opportunity_score=7.0,
            momentum_score=2.0,
            alignment_score=7.0,
            resource_allocation=20.0,
            strategic_priority=3,
        )
        m2 = DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=6.0,
            risk_score=3.0,
            opportunity_score=5.0,
            momentum_score=1.0,
            alignment_score=8.0,
            resource_allocation=15.0,
            strategic_priority=1,
        )
        
        policy = OptimizationPolicy()
        decision = engine.resolve_tradeoff(
            LifeDomain.CAREER, LifeDomain.HEALTH, m1, m2, policy
        )
        
        assert decision.tradeoff_type == TradeoffType.CAREER_VS_HEALTH
    
    def test_get_active_tradeoffs(self, engine):
        """Test getting active tradeoff types."""
        tradeoffs = engine.get_active_tradeoffs()
        
        assert isinstance(tradeoffs, list)
    
    def test_get_tradeoff_statistics(self, engine, sample_metrics, policy):
        """Test getting tradeoff statistics."""
        # First make some tradeoffs
        engine.resolve_all_tradeoffs(sample_metrics, policy)
        
        stats = engine.get_tradeoff_statistics()
        
        assert "total_decisions" in stats
        assert "by_type" in stats
        assert "win_distribution" in stats
    
    def test_clear_history(self, engine):
        """Test clearing tradeoff history."""
        # Add some data
        metrics = [
            DomainMetrics(
                domain=LifeDomain.HEALTH,
                performance_score=7.0,
                risk_score=3.0,
                opportunity_score=6.0,
                momentum_score=2.0,
                alignment_score=7.0,
                resource_allocation=20.0,
                strategic_priority=1,
            ),
            DomainMetrics(
                domain=LifeDomain.CAREER,
                performance_score=8.0,
                risk_score=4.0,
                opportunity_score=8.0,
                momentum_score=3.0,
                alignment_score=8.0,
                resource_allocation=30.0,
                strategic_priority=2,
            ),
        ]
        policy = OptimizationPolicy()
        engine.resolve_all_tradeoffs(metrics, policy)
        
        # Clear history
        engine.clear_history()
        
        stats = engine.get_tradeoff_statistics()
        assert stats["total_decisions"] == 0


class TestTradeoffEngineIntegration:
    """Integration tests for TradeoffEngine."""
    
    def test_get_global_engine(self):
        """Test getting global engine."""
        engine1 = get_tradeoff_engine()
        engine2 = get_tradeoff_engine()
        
        assert engine1 is engine2
