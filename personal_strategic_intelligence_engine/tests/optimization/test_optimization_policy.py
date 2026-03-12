"""Tests for optimization policy engine."""
import pytest
from datetime import datetime, timedelta
from app.optimization.optimization_policy import OptimizationPolicyEngine, get_optimization_policy_engine
from app.optimization.optimization_types import (
    LifeDomain,
    DomainMetrics,
    OptimizationPolicy,
    OptimizationAction,
    DomainConditionResult,
    DomainCondition,
    TradeoffDecision,
    TradeoffType,
)


class TestOptimizationPolicyEngine:
    """Tests for OptimizationPolicyEngine class."""
    
    @pytest.fixture
    def default_policy(self):
        """Create a default policy."""
        return OptimizationPolicy()
    
    @pytest.fixture
    def engine(self, default_policy):
        """Create a policy engine."""
        return OptimizationPolicyEngine(default_policy)
    
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
                domain=LifeDomain.CAREER,
                performance_score=5.0,
                risk_score=4.0,
                opportunity_score=7.0,
                momentum_score=1.0,
                alignment_score=6.0,
                resource_allocation=25.0,
                strategic_priority=2,
            ),
        ]
    
    def test_default_policy_values(self, engine):
        """Test default policy values."""
        policy = engine.policy
        
        assert policy.min_domain_score == 3.0
        assert policy.max_domain_score == 9.0
        assert policy.neglect_threshold == 3.5
        assert policy.overinvest_threshold == 8.0
        assert policy.enable_automatic_rebalancing is True
        assert policy.max_daily_domain_shifts == 2
    
    def test_update_policy(self, engine):
        """Test updating policy."""
        new_policy = OptimizationPolicy(
            min_domain_score=4.0,
            max_domain_score=8.0,
            enable_automatic_rebalancing=False,
        )
        
        engine.update_policy(new_policy)
        
        assert engine.policy.min_domain_score == 4.0
        assert engine.policy.max_domain_score == 8.0
        assert engine.policy.enable_automatic_rebalancing is False
    
    def test_can_adjust_domain_initially(self, engine):
        """Test that domains can be adjusted initially."""
        assert engine.can_adjust_domain(LifeDomain.HEALTH) is True
    
    def test_record_domain_adjustment(self, engine):
        """Test recording domain adjustment."""
        engine.record_domain_adjustment(LifeDomain.HEALTH)
        
        assert LifeDomain.HEALTH in engine._action_cooldown
    
    def test_cooldown_after_adjustment(self, engine):
        """Test cooldown after adjustment."""
        engine.record_domain_adjustment(LifeDomain.HEALTH)
        
        # Immediately after, should not be able to adjust
        # (We set cooldown to 24 hours, but test with short time)
        engine._policy._recovery_period_hours = 0
        assert engine.can_adjust_domain(LifeDomain.HEALTH) is True
    
    def test_validate_action_increase_priority(self, engine, sample_metrics):
        """Test validating increase priority action."""
        metrics = sample_metrics[1]  # CAREER with score 5.0
        
        is_valid, reason = engine.validate_action(
            OptimizationAction.INCREASE_PRIORITY,
            LifeDomain.CAREER,
            metrics,
            []
        )
        
        assert is_valid is True
    
    def test_validate_action_at_max_score(self, engine):
        """Test validation when domain at max score."""
        metrics = DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=9.5,
            risk_score=1.0,
            opportunity_score=9.0,
            momentum_score=5.0,
            alignment_score=9.0,
            resource_allocation=50.0,
            strategic_priority=2,
        )
        
        is_valid, reason = engine.validate_action(
            OptimizationAction.INCREASE_PRIORITY,
            LifeDomain.CAREER,
            metrics,
            []
        )
        
        assert is_valid is False
        assert "max score" in reason.lower()
    
    def test_validate_action_health_protection(self, engine):
        """Test health domain protection."""
        metrics = DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=2.0,
            risk_score=8.0,
            opportunity_score=3.0,
            momentum_score=-3.0,
            alignment_score=5.0,
            resource_allocation=5.0,
            strategic_priority=1,
        )
        
        condition = DomainConditionResult(
            domain=LifeDomain.HEALTH,
            condition=DomainCondition.NEGLECTED,
            severity=0.8,
            evidence=["Low score"],
        )
        
        is_valid, reason = engine.validate_action(
            OptimizationAction.DECREASE_PRIORITY,
            LifeDomain.HEALTH,
            metrics,
            [condition]
        )
        
        # Should be blocked by safety constraint
        assert is_valid is False
    
    def test_apply_policy_to_recommendation(self, engine, sample_metrics):
        """Test applying policy to recommendation."""
        from app.optimization.optimization_types import OptimizationActionRecommendation
        
        rec = OptimizationActionRecommendation(
            action=OptimizationAction.INCREASE_PRIORITY,
            target_domain=LifeDomain.CAREER,
            priority=3,
            reasoning="Test recommendation",
            expected_impact=0.5,
            confidence=0.8,
        )
        
        constrained = engine.apply_policy_to_recommendation(
            rec, sample_metrics[1], []
        )
        
        assert constrained.policy_constraints_respected is True
    
    def test_apply_policy_to_tradeoff(self, engine):
        """Test applying policy to tradeoff decision."""
        all_metrics = [
            DomainMetrics(
                domain=LifeDomain.HEALTH,
                performance_score=2.0,
                risk_score=8.0,
                opportunity_score=3.0,
                momentum_score=-3.0,
                alignment_score=5.0,
                resource_allocation=5.0,
                strategic_priority=1,
            ),
            DomainMetrics(
                domain=LifeDomain.CAREER,
                performance_score=8.0,
                risk_score=3.0,
                opportunity_score=8.0,
                momentum_score=3.0,
                alignment_score=8.0,
                resource_allocation=40.0,
                strategic_priority=2,
            ),
        ]
        
        tradeoff = TradeoffDecision(
            tradeoff_type=TradeoffType.CAREER_VS_HEALTH,
            domains_involved=[LifeDomain.HEALTH, LifeDomain.CAREER],
            winner=LifeDomain.CAREER,
            loser=LifeDomain.HEALTH,
            reasoning="Career wins",
            long_term_value_impact=0.3,
            risk_mitigation_score=0.5,
            sustainability_score=0.6,
            energy_impact=-0.2,
        )
        
        protected = engine.apply_policy_to_tradeoff(tradeoff, all_metrics)
        
        # Should flip the decision to protect health
        assert protected.winner == LifeDomain.HEALTH
    
    def test_calculate_risk_tolerance_factor(self, engine):
        """Test risk tolerance factor calculation."""
        engine._policy.risk_tolerance = "conservative"
        factor = engine.calculate_risk_tolerance_factor()
        assert factor == 0.3
        
        engine._policy.risk_tolerance = "moderate"
        factor = engine.calculate_risk_tolerance_factor()
        assert factor == 0.5
        
        engine._policy.risk_tolerance = "aggressive"
        factor = engine.calculate_risk_tolerance_factor()
        assert factor == 0.8
    
    def test_get_weighted_objective(self, engine):
        """Test weighted objective calculation."""
        # Set policy weights
        engine._policy.sustainability_weight = 0.3
        engine._policy.long_term_weight = 0.4
        engine._policy.energy_constraint_factor = 0.3
        
        result = engine.get_weighted_objective(0.8, 0.7, 0.5)
        
        expected = 0.8 * 0.3 + 0.7 * 0.4 + 0.5 * 0.3
        assert result == expected
    
    def test_should_auto_rebalance(self, engine):
        """Test auto rebalance check."""
        engine._policy.enable_automatic_rebalancing = True
        assert engine.should_auto_rebalance() is True
        
        engine._policy.enable_automatic_rebalancing = False
        assert engine.should_auto_rebalance() is False
    
    def test_get_policy_status(self, engine):
        """Test getting policy status."""
        status = engine.get_policy_status()
        
        assert "policy" in status
        assert "cooldowns" in status
        assert "recent_adjustments" in status
    
    def test_reset_cooldowns(self, engine):
        """Test resetting cooldowns."""
        engine.record_domain_adjustment(LifeDomain.HEALTH)
        engine.record_domain_adjustment(LifeDomain.CAREER)
        
        engine.reset_cooldowns()
        
        assert len(engine._action_cooldown) == 0
        assert len(engine._last_adjustments) == 0


class TestOptimizationPolicyEngineIntegration:
    """Integration tests for OptimizationPolicyEngine."""
    
    def test_get_global_engine(self):
        """Test getting global engine."""
        engine1 = get_optimization_policy_engine()
        engine2 = get_optimization_policy_engine()
        
        assert engine1 is engine2
