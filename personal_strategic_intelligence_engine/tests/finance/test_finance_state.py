"""Finance Module Tests - State Layer."""
import pytest

from app.finance.models.financial_profile import FinancialProfile
from app.finance.models.asset import Asset
from app.finance.models.liability import Liability
from app.finance.engine.financial_state_engine import FinancialStateEngine


class TestFinancialStateEngine:
    """Tests for FinancialStateEngine."""

    @pytest.fixture
    def sample_profile(self):
        """Create a sample financial profile."""
        return FinancialProfile(
            profile_id=1,
            monthly_income=6400,
            monthly_fixed_expenses=3000,
            monthly_variable_expenses=3150,
        )

    @pytest.fixture
    def sample_assets(self):
        """Create sample assets."""
        return [
            Asset(asset_id=1, profile_id=1, category='checking', name='Main Checking', 
                  current_value=10000, liquidity_score=1.0, volatility_score=0.0),
            Asset(asset_id=2, profile_id=1, category='savings', name='Emergency Fund', 
                  current_value=20000, liquidity_score=1.0, volatility_score=0.0),
            Asset(asset_id=3, profile_id=1, category='investment', name='Brokerage', 
                  current_value=50000, liquidity_score=0.8, volatility_score=0.3),
            Asset(asset_id=4, profile_id=1, category='retirement', name='401k', 
                  current_value=100000, liquidity_score=0.3, volatility_score=0.5),
        ]

    @pytest.fixture
    def sample_liabilities(self):
        """Create sample liabilities."""
        return [
            Liability(liability_id=1, profile_id=1, category='mortgage', name='Home Loan', 
                     balance=250000, minimum_payment=1500, interest_rate=0.065),
            Liability(liability_id=2, profile_id=1, category='credit_card', name='Credit Card', 
                     balance=5000, minimum_payment=150, interest_rate=0.18),
        ]

    def test_compute_net_worth(self, sample_profile, sample_assets, sample_liabilities):
        """Test net worth calculation."""
        state = FinancialStateEngine.compute(sample_profile, sample_assets, sample_liabilities)
        
        assert state.total_assets == 180000
        assert state.total_liabilities == 255000
        assert state.net_worth == -75000

    def test_compute_liquid_assets(self, sample_profile, sample_assets, sample_liabilities):
        """Test liquid assets calculation."""
        state = FinancialStateEngine.compute(sample_profile, sample_assets, sample_liabilities)
        
        # All assets are considered liquid in this test
        assert state.liquid_assets == 180000

    def test_compute_debt_to_income(self, sample_profile, sample_assets, sample_liabilities):
        """Test debt-to-income ratio calculation."""
        state = FinancialStateEngine.compute(sample_profile, sample_assets, sample_liabilities)
        
        # 255000 / 6400 = ~40 months, ratio should reflect monthly debt payments vs income
        assert state.debt_to_income_ratio > 0

    def test_compute_emergency_fund_months(self, sample_profile, sample_assets, sample_liabilities):
        """Test emergency fund months calculation."""
        state = FinancialStateEngine.compute(sample_profile, sample_assets, sample_liabilities)
        
        # Liquid assets / monthly expenses
        assert state.emergency_fund_months > 0


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_income(self):
        """Test handling of zero income."""
        profile = FinancialProfile(
            profile_id=1, monthly_income=0, monthly_fixed_expenses=1000, monthly_variable_expenses=500
        )
        assets = [
            Asset(asset_id=1, profile_id=1, category='checking', name='Checking', 
                  current_value=5000, liquidity_score=1.0, volatility_score=0.0)
        ]
        liabilities = []
        
        state = FinancialStateEngine.compute(profile, assets, liabilities)
        
        assert state.net_worth == 5000
        assert state.debt_to_income_ratio == 0

    def test_no_liabilities(self):
        """Test handling of no liabilities."""
        profile = FinancialProfile(
            profile_id=1, monthly_income=5000, monthly_fixed_expenses=2000, monthly_variable_expenses=1500
        )
        assets = [
            Asset(asset_id=1, profile_id=1, category='savings', name='Savings', 
                  current_value=50000, liquidity_score=1.0, volatility_score=0.0)
        ]
        liabilities = []
        
        state = FinancialStateEngine.compute(profile, assets, liabilities)
        
        assert state.total_liabilities == 0
        assert state.debt_to_income_ratio == 0

    def test_empty_portfolio(self):
        """Test handling of empty portfolio."""
        profile = FinancialProfile(
            profile_id=1, monthly_income=5000, monthly_fixed_expenses=2000, monthly_variable_expenses=1500
        )
        assets = []
        liabilities = []
        
        state = FinancialStateEngine.compute(profile, assets, liabilities)
        
        assert state.net_worth == 0
        assert state.total_assets == 0
        assert state.total_liabilities == 0
