"""Tests for domain optimizer."""
import pytest
from app.optimization.domain_optimizer import DomainOptimizer, get_domain_optimizer
from app.optimization.domain_modeler import DomainModeler
from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    OptimizationAction,
    DomainCondition,
)


class TestDomainOptimizer:
    """Tests for DomainOptimizer class."""
    
    @pytest.fixture
    def optimizer(self):
        """Create an optimizer instance."""
        return DomainOptimizer()
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample domain metrics."""
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
                domain=LifeDomain.WEALTH,
                performance_score=5.0,
                risk_score=5.0,
                opportunity_score=7.0,
                momentum_score=1.0,
                alignment_score=6.0,
                resource_allocation=15.0,
                strategic_priority=2,
            ),
            DomainMetrics(
                domain=LifeDomain.CAREER,
                performance_score=3.0,
                risk_score=4.0,
                opportunity_score=8.0,
                momentum_score=-2.0,
                alignment_score=5.0,
                resource_allocation=30.0,
                strategic_priority=3,
            ),
            DomainMetrics(
                domain=LifeDomain.LEARNING,
                performance_score=6.0,
                risk_score=3.0,
                opportunity_score=5.0,
                momentum_score=3.0,
                alignment_score=7.0,
                resource_allocation=10.0,
                strategic_priority=4,
            ),
            DomainMetrics(
                domain=LifeDomain.RELATIONSHIPS,
                performance_score=4.0,
                risk_score=3.0,
                opportunity_score=4.0,
                momentum_score=-1.0,
                alignment_score=6.0,
                resource_allocation=8.0,
                strategic_priority=5,
            ),
            DomainMetrics(
                domain=LifeDomain.PERSONAL_DEVELOPMENT,
                performance_score=6.0,
                risk_score=2.0,
                opportunity_score=6.0,
                momentum_score=2.0,
                alignment_score=7.0,
                resource_allocation=10.0,
                strategic_priority=6,
            ),
            DomainMetrics(
                domain=LifeDomain.OPERATIONS,
                performance_score=5.0,
                risk_score=4.0,
                opportunity_score=3.0,
                momentum_score=0.0,
                alignment_score=5.0,
                resource_allocation=12.0,
                strategic_priority=7,
            ),
            DomainMetrics(
                domain=LifeDomain.STRATEGIC_PROJECTS,
                performance_score=7.0,
                risk_score=3.0,
                opportunity_score=8.0,
                momentum_score=4.0,
                alignment_score=8.0,
                resource_allocation=20.0,
                strategic_priority=8,
            ),
        ]
    
    def test_run_optimization_cycle(self, optimizer, sample_metrics):
        """Test running a complete optimization cycle."""
        cycle = optimizer.run_optimization_cycle(sample_metrics)
        
        assert cycle.cycle_id is not None
        assert len(cycle.domain_metrics) == len(sample_metrics)
        assert len(cycle.detected_conditions) > 0
        assert isinstance(cycle.overall_balance_score, float)
        assert 0 <= cycle.overall_balance_score <= 10
    
    def test_run_optimization_cycle_default_metrics(self, optimizer):
        """Test running optimization cycle with default metrics."""
        cycle = optimizer.run_optimization_cycle()
        
        assert cycle.cycle_id is not None
        assert cycle.execution_status == "completed"
    
    def test_generate_recommendations(self, optimizer, sample_metrics):
        """Test generating recommendations."""
        conditions = optimizer.scorer.detect_all_conditions(sample_metrics)
        tradeoffs = optimizer.tradeoff_engine.resolve_all_tradeoffs(
            sample_metrics, optimizer.policy_engine.policy
        )
        
        recommendations = optimizer._generate_recommendations(
            sample_metrics, conditions, tradeoffs
        )
        
        assert isinstance(recommendations, list)
    
    def test_recommend_neglected_domain(self, optimizer):
        """Test recommending action for neglected domain."""
        from app.optimization.optimization_types import DomainConditionResult
        
        condition = DomainConditionResult(
            domain=LifeDomain.LEARNING,
            condition=DomainCondition.NEGLECTED,
            severity=0.8,
            evidence=["Low composite score with minimal resources"],
        )
        
        rec = optimizer._recommend_neglected_domain(condition)
        
        assert rec is not None
        assert rec.action == OptimizationAction.INCREASE_PRIORITY
        assert rec.target_domain == LifeDomain.LEARNING
    
    def test_recommend_health_neglect_higher_priority(self, optimizer):
        """Test that health neglect gets highest priority."""
        from app.optimization.optimization_types import DomainConditionResult
        
        condition = DomainConditionResult(
            domain=LifeDomain.HEALTH,
            condition=DomainCondition.NEGLECTED,
            severity=0.9,
            evidence=["Health critical"],
        )
        
        rec = optimizer._recommend_neglected_domain(condition)
        
        assert rec is not None
        assert rec.priority == 1
    
    def test_recommend_overinvested_domain(self, optimizer):
        """Test recommending action for overinvested domain."""
        from app.optimization.optimization_types import DomainConditionResult
        
        condition = DomainConditionResult(
            domain=LifeDomain.CAREER,
            condition=DomainCondition.OVERINVESTED,
            severity=0.5,
            evidence=["High allocation with diminishing returns"],
        )
        
        rec = optimizer._recommend_overinvested_domain(condition)
        
        assert rec is not None
        assert rec.action == OptimizationAction.DECREASE_PRIORITY
    
    def test_recommend_opportunity_window(self, optimizer):
        """Test recommending action for opportunity window."""
        from app.optimization.optimization_types import DomainConditionResult
        
        condition = DomainConditionResult(
            domain=LifeDomain.STRATEGIC_PROJECTS,
            condition=DomainCondition.OPPORTUNITY_WINDOW,
            severity=0.7,
            evidence=["Strong opportunity with positive momentum"],
        )
        
        rec = optimizer._recommend_opportunity_window(condition)
        
        assert rec is not None
        assert rec.action == OptimizationAction.ESCALATE_TO_STRATEGIC
    
    def test_recommend_risk_escalation(self, optimizer):
        """Test recommending action for risk escalation."""
        from app.optimization.optimization_types import DomainConditionResult
        
        condition = DomainConditionResult(
            domain=LifeDomain.WEALTH,
            condition=DomainCondition.RISK_ESCALATION,
            severity=0.6,
            evidence=["Elevated risk exposure"],
        )
        
        rec = optimizer._recommend_risk_escalation(condition)
        
        assert rec is not None
        assert rec.action == OptimizationAction.TRIGGER_HABIT_INTERVENTION
    
    def test_apply_policy_constraints(self, optimizer, sample_metrics):
        """Test applying policy constraints."""
        from app.optimization.optimization_types import OptimizationActionRecommendation
        
        # Create a recommendation that might be blocked
        recommendations = [
            OptimizationActionRecommendation(
                action=OptimizationAction.INCREASE_PRIORITY,
                target_domain=LifeDomain.CAREER,
                priority=3,
                reasoning="Test",
                expected_impact=0.5,
                confidence=0.8,
            ),
        ]
        
        conditions = optimizer.scorer.detect_all_conditions(sample_metrics)
        
        constrained = optimizer._apply_policy_constraints(
            recommendations, sample_metrics, conditions
        )
        
        assert isinstance(constrained, list)
    
    def test_apply_optimization(self, optimizer, sample_metrics):
        """Test applying optimization recommendations."""
        cycle = optimizer.run_optimization_cycle(sample_metrics)
        
        result = optimizer.apply_optimization(cycle)
        
        assert "status" in result
        assert result["status"] in ["completed", "no_optimization_needed"]
    
    def test_calculate_domain_shifts(self, optimizer, sample_metrics):
        """Test calculating domain shifts."""
        current = sample_metrics[:4]
        
        # Create target metrics with different allocations
        target = [
            DomainMetrics(
                domain=dm.domain,
                performance_score=dm.performance_score,
                risk_score=dm.risk_score,
                opportunity_score=dm.opportunity_score,
                momentum_score=dm.momentum_score,
                alignment_score=dm.alignment_score,
                resource_allocation=dm.resource_allocation + 10,  # Increase
                strategic_priority=dm.strategic_priority,
            )
            for dm in current
        ]
        
        shifts = optimizer.calculate_domain_shifts(current, target)
        
        assert isinstance(shifts, list)
    
    def test_get_optimization_summary(self, optimizer):
        """Test getting optimization summary."""
        summary = optimizer.get_optimization_summary()
        
        assert "overall_health" in summary
        assert "balance_score" in summary
        assert "domains_needing_attention" in summary
        assert "top_opportunities" in summary
        assert "active_tradeoffs" in summary
        assert "pending_recommendations" in summary
    
    def test_optimization_cycle_handles_empty_metrics(self, optimizer):
        """Test optimization cycle handles empty metrics gracefully."""
        cycle = optimizer.run_optimization_cycle([])
        
        assert cycle.cycle_id is not None
        assert cycle.execution_status in ["completed", "failed"]


class TestDomainOptimizerIntegration:
    """Integration tests for DomainOptimizer."""
    
    def test_get_global_optimizer(self):
        """Test getting global optimizer."""
        optimizer1 = get_domain_optimizer()
        optimizer2 = get_domain_optimizer()
        
        assert optimizer1 is optimizer2
    
    def test_full_optimization_workflow(self):
        """Test complete optimization workflow."""
        optimizer = get_domain_optimizer()
        
        # Run cycle
        cycle = optimizer.run_optimization_cycle()
        assert cycle.execution_status == "completed"
        
        # Get summary
        summary = optimizer.get_optimization_summary()
        assert "overall_health" in summary
        
        # Apply recommendations if any
        if cycle.recommendations:
            result = optimizer.apply_optimization(cycle)
            assert "status" in result
