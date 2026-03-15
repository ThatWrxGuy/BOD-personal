"""Finance Module Tests - Governance Layer."""
import pytest

from app.finance.governance.engines.recommendation_classifier import RecommendationClassifier
from app.finance.governance.engines.approval_router import ApprovalRouter
from app.finance.governance.engines.board_brief_generator import BoardBriefGenerator
from app.finance.governance.engines.financial_audit_logger import FinancialAuditLogger
from app.finance.governance.models.financial_decision_request import DecisionClass
from app.finance.intelligence.models.financial_recommendation import Priority, ActionClass


class TestRecommendationClassifier:
    """Tests for RecommendationClassifier."""

    def test_classify_critical_priority(self):
        """Test classification of critical priority recommendations."""
        from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation
        
        rec = FinancialRecommendation(
            recommendation_id='r1',
            profile_id=1,
            title='Major Portfolio Rebalance',
            summary='Significant allocation change needed',
            rationale='Strategic shift required',
            priority=Priority.CRITICAL,
            confidence_score=0.80,
            expected_benefit='Improved returns',
            downside_risk='Market timing risk',
            action_class=ActionClass.ADVISORY,
        )
        
        classification = RecommendationClassifier.classify(rec)
        
        assert classification == DecisionClass.BOARD_REVIEW

    def test_classify_debt_recommendation(self):
        """Test classification of debt-related recommendations."""
        from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation
        
        rec = FinancialRecommendation(
            recommendation_id='r2',
            profile_id=1,
            title='Accelerate Debt Payoff',
            summary='Pay off debt faster',
            rationale='Reduce interest costs',
            priority=Priority.HIGH,
            confidence_score=0.85,
            expected_benefit='Interest savings',
            downside_risk='Less liquidity',
            action_class=ActionClass.ADVISORY,
        )
        
        classification = RecommendationClassifier.classify(rec)
        
        assert classification == DecisionClass.USER_APPROVAL

    def test_classify_informational(self):
        """Test classification of informational recommendations."""
        from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation
        
        rec = FinancialRecommendation(
            recommendation_id='r3',
            profile_id=1,
            title='Review Budget',
            summary='Consider reviewing monthly expenses',
            rationale='General financial health',
            priority=Priority.LOW,
            confidence_score=0.90,
            expected_benefit='Awareness',
            downside_risk='None',
            action_class=ActionClass.ADVISORY,
        )
        
        classification = RecommendationClassifier.classify(rec)
        
        assert classification == DecisionClass.INFORMATIONAL

    def test_batch_classification(self):
        """Test batch classification."""
        from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation
        
        recommendations = [
            FinancialRecommendation('r1', 1, 'Test1', 'Summary', 'Rationale', 
                                Priority.CRITICAL, 0.8, 'Benefit', 'Risk', ActionClass.ADVISORY),
            FinancialRecommendation('r2', 1, 'Test2', 'Summary', 'Rationale', 
                                Priority.HIGH, 0.8, 'Benefit', 'Risk', ActionClass.ADVISORY),
        ]
        
        summary = RecommendationClassifier.get_approval_summary(recommendations)
        
        assert 'informational' in summary
        assert 'user_approval_required' in summary
        assert 'board_review_required' in summary


class TestApprovalRouter:
    """Tests for ApprovalRouter."""

    def test_create_decision_request(self):
        """Test creating a decision request."""
        from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation
        
        router = ApprovalRouter()
        
        rec = FinancialRecommendation(
            recommendation_id='rec-1',
            profile_id=1,
            title='Test Recommendation',
            summary='Test summary',
            rationale='Test rationale',
            priority=Priority.HIGH,
            confidence_score=0.80,
            expected_benefit='Test benefit',
            downside_risk='Test risk',
            action_class=ActionClass.ADVISORY,
        )
        
        decision = router.create_decision_request(rec)
        
        assert decision.decision_id is not None
        assert decision.recommendation_id == 'rec-1'
        assert decision.profile_id == 1

    def test_get_pending_decisions(self):
        """Test getting pending decisions."""
        router = ApprovalRouter()
        
        pending = router.get_pending_decisions(1)
        
        assert isinstance(pending, list)


class TestBoardBriefGenerator:
    """Tests for BoardBriefGenerator."""

    @pytest.fixture
    def sample_state(self):
        """Create sample financial state."""
        return {
            'profile_id': 1,
            'net_worth': 50000,
            'total_assets': 150000,
            'total_liabilities': 100000,
            'monthly_income': 8000,
            'monthly_expenses': 5000,
            'free_cash_flow': 2000,
            'liquid_assets': 40000,
            'total_debt': 100000,
            'debt_to_income_ratio': 0.20,
            'emergency_fund_months': 8,
        }

    def test_generate_board_brief(self, sample_state):
        """Test board brief generation."""
        brief = BoardBriefGenerator.generate(sample_state)
        
        assert brief.profile_id == 1
        assert brief.net_worth == 50000
        assert brief.free_cash_flow == 2000

    def test_executive_summary(self, sample_state):
        """Test executive summary generation."""
        brief = BoardBriefGenerator.generate(sample_state)
        
        summary = BoardBriefGenerator.generate_executive_summary(brief)
        
        assert 'FINANCIAL INTELLIGENCE BRIEF' in summary
        assert 'NET WORTH' in summary.upper()


class TestFinancialAuditLogger:
    """Tests for FinancialAuditLogger."""

    def test_log_recommendation_generated(self):
        """Test logging recommendation generation."""
        logger = FinancialAuditLogger()
        
        event = logger.log_recommendation_generated(1, 'rec-1', 'Test Recommendation')
        
        assert event.event_type.value == 'recommendation_generated'
        assert event.event_reference == 'rec-1'

    def test_log_decision_requested(self):
        """Test logging decision request."""
        logger = FinancialAuditLogger()
        
        event = logger.log_decision_requested(1, 'dec-1', 'Test Decision', 'user_approval')
        
        assert event.event_type.value == 'decision_requested'

    def test_get_audit_log(self):
        """Test getting audit log."""
        logger = FinancialAuditLogger()
        
        logger.log_recommendation_generated(1, 'rec-1', 'Test 1')
        logger.log_recommendation_generated(1, 'rec-2', 'Test 2')
        
        events = logger.get_audit_log(1)
        
        assert len(events) == 2
