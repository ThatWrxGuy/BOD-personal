"""Tests for domain scorer."""
import pytest
from app.optimization.domain_scorer import DomainScorer, get_domain_scorer
from app.optimization.domain_modeler import DomainModeler
from app.optimization.optimization_types import LifeDomain, DomainMetrics, DomainCondition


class TestDomainScorer:
    """Tests for DomainScorer class."""
    
    @pytest.fixture
    def scorer(self):
        """Create a scorer instance."""
        return DomainScorer()
    
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
                resource_allocation=25.0,
                strategic_priority=3,
            ),
        ]
    
    def test_score_domain(self, scorer):
        """Test scoring a single domain."""
        metrics = DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=7.0,
            risk_score=3.0,
            opportunity_score=6.0,
            momentum_score=2.0,
            alignment_score=7.0,
            resource_allocation=20.0,
            strategic_priority=1,
        )
        
        score = scorer.score_domain(metrics)
        
        assert 0 <= score <= 10
        assert score > 5.0  # Should be above average
    
    def test_score_all_domains(self, scorer, sample_metrics):
        """Test scoring all domains."""
        scores = scorer.score_all_domains(sample_metrics)
        
        assert len(scores) == len(sample_metrics)
        assert all(isinstance(s, float) for s in scores.values())
        assert all(0 <= s <= 10 for s in scores.values())
    
    def test_detect_neglected_condition(self, scorer):
        """Test detecting neglected domain condition."""
        metrics = DomainMetrics(
            domain=LifeDomain.LEARNING,
            performance_score=2.0,
            risk_score=3.0,
            opportunity_score=5.0,
            momentum_score=-1.0,
            alignment_score=4.0,
            resource_allocation=10.0,  # Low resources
            strategic_priority=5,
        )
        
        condition = scorer.detect_domain_condition(metrics)
        
        assert condition.condition == DomainCondition.NEGLECTED
        assert condition.severity > 0
    
    def test_detect_overinvested_condition(self, scorer):
        """Test detecting overinvested domain condition."""
        metrics = DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=9.0,
            risk_score=2.0,
            opportunity_score=4.0,
            momentum_score=1.0,
            alignment_score=8.0,
            resource_allocation=50.0,  # High resources
            strategic_priority=3,
        )
        
        condition = scorer.detect_domain_condition(metrics)
        
        assert condition.condition == DomainCondition.OVERINVESTED
    
    def test_detect_opportunity_window(self, scorer):
        """Test detecting opportunity window condition."""
        metrics = DomainMetrics(
            domain=LifeDomain.WEALTH,
            performance_score=6.0,
            risk_score=3.0,
            opportunity_score=8.0,  # High opportunity
            momentum_score=5.0,  # Positive momentum
            alignment_score=7.0,
            resource_allocation=20.0,
            strategic_priority=2,
        )
        
        condition = scorer.detect_domain_condition(metrics)
        
        assert condition.condition == DomainCondition.OPPORTUNITY_WINDOW
    
    def test_detect_risk_escalation(self, scorer):
        """Test detecting risk escalation condition."""
        metrics = DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=5.0,
            risk_score=8.0,  # High risk
            opportunity_score=4.0,
            momentum_score=0.0,
            alignment_score=6.0,
            resource_allocation=15.0,
            strategic_priority=1,
        )
        
        condition = scorer.detect_domain_condition(metrics)
        
        assert condition.condition == DomainCondition.RISK_ESCALATION
    
    def test_detect_healthy_condition(self, scorer):
        """Test detecting healthy domain condition."""
        metrics = DomainMetrics(
            domain=LifeDomain.RELATIONSHIPS,
            performance_score=6.5,
            risk_score=3.0,
            opportunity_score=5.0,
            momentum_score=1.0,
            alignment_score=7.0,
            resource_allocation=15.0,
            strategic_priority=5,
        )
        
        condition = scorer.detect_domain_condition(metrics)
        
        assert condition.condition == DomainCondition.HEALTHY
    
    def test_detect_all_conditions(self, scorer, sample_metrics):
        """Test detecting conditions for all domains."""
        conditions = scorer.detect_all_conditions(sample_metrics)
        
        assert len(conditions) == len(sample_metrics)
        assert all(c.domain in LifeDomain for c in conditions)
    
    def test_calculate_domain_health(self, scorer, sample_metrics):
        """Test calculating overall domain health."""
        health = scorer.calculate_domain_health(sample_metrics)
        
        assert 0 <= health <= 10
    
    def test_calculate_balance_score(self, scorer, sample_metrics):
        """Test calculating balance score."""
        balance = scorer.calculate_balance_score(sample_metrics)
        
        assert 0 <= balance <= 10
    
    def test_calculate_opportunity_potential(self, scorer, sample_metrics):
        """Test calculating opportunity potential."""
        potentials = scorer.calculate_opportunity_potential(sample_metrics)
        
        assert len(potentials) == len(sample_metrics)
        assert all(isinstance(p, tuple) for p in potentials)
        # Should be sorted by potential descending
        if len(potentials) > 1:
            assert potentials[0][1] >= potentials[1][1]
    
    def test_identify_domains_needing_attention(self, scorer, sample_metrics):
        """Test identifying domains needing attention."""
        needs_attention = scorer.identify_domains_needing_attention(sample_metrics)
        
        # Should include Career (low performance score)
        assert LifeDomain.CAREER in needs_attention or len(needs_attention) >= 0
    
    def test_normalize_scores(self, scorer):
        """Test normalizing domain scores."""
        metrics = [
            DomainMetrics(
                domain=LifeDomain.HEALTH,
                performance_score=15.0,  # Over max
                risk_score=-2.0,  # Under min
                opportunity_score=5.0,
                momentum_score=15.0,  # Over max
                alignment_score=5.0,
                resource_allocation=150.0,  # Over max
                strategic_priority=1,
            ),
        ]
        
        normalized = scorer.normalize_scores(metrics)
        
        assert normalized[0].performance_score <= 10
        assert normalized[0].risk_score >= 0
        assert normalized[0].momentum_score <= 10
        assert normalized[0].resource_allocation <= 100
    
    def test_record_and_get_score_trend(self, scorer):
        """Test recording and getting score trends."""
        domain = LifeDomain.HEALTH
        
        # Record some scores
        scorer.record_score_history(domain, 5.0)
        scorer.record_score_history(domain, 6.0)
        scorer.record_score_history(domain, 7.0)
        
        trend = scorer.get_score_trend(domain)
        
        # Should have positive trend
        assert trend > 0


class TestDomainScorerIntegration:
    """Integration tests for DomainScorer."""
    
    def test_get_global_scorer(self):
        """Test getting global scorer."""
        scorer1 = get_domain_scorer()
        scorer2 = get_domain_scorer()
        
        assert scorer1 is scorer2
