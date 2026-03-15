"""Finance Module Tests - Simulation Layer."""
import pytest

from app.finance.simulation.engines.debt_payoff_simulator import DebtPayoffSimulator
from app.finance.simulation.engines.liquidity_stress_tester import LiquidityStressTester
from app.finance.simulation.engines.income_shock_simulator import IncomeShockSimulator
from app.finance.simulation.engines.allocation_projection_engine import AllocationProjectionEngine
from app.finance.simulation.engines.scenario_runner import ScenarioRunner
from app.finance.simulation.models.scenario_definition import ScenarioType


class TestDebtPayoffSimulator:
    """Tests for DebtPayoffSimulator."""

    @pytest.fixture
    def state_with_debt(self):
        """Create a state with debt."""
        return {
            'profile_id': 1,
            'total_assets': 100000,
            'liquid_assets': 30000,
            'monthly_income': 5000,
            'monthly_expenses': 4000,
            'total_debt': 80000,
            'liabilities': [
                {'name': 'mortgage', 'balance': 70000, 'rate': 0.065, 'minimum_payment': 1000},
                {'name': 'credit_card', 'balance': 10000, 'rate': 0.18, 'minimum_payment': 300},
            ],
            'liabilities_by_category': {'mortgage': 70000, 'credit_card': 10000},
        }

    def test_simulate_with_extra_payment(self, state_with_debt):
        """Test debt payoff with extra payment."""
        result = DebtPayoffSimulator.simulate(state_with_debt, extra_payment_amount=500)
        
        assert result.payoff_timeline_months > 0
        assert result.interest_paid_total > 0

    def test_simulate_no_extra_payment(self, state_with_debt):
        """Test debt payoff without extra payment."""
        result = DebtPayoffSimulator.simulate(state_with_debt, extra_payment_amount=0)
        
        assert result.payoff_timeline_months > 0


class TestLiquidityStressTester:
    """Tests for LiquidityStressTester."""

    @pytest.fixture
    def state_with_reserves(self):
        """Create a state with reserves."""
        return {
            'profile_id': 1,
            'liquid_assets': 30000,
            'monthly_income': 5000,
            'monthly_expenses': 4000,
        }

    def test_stress_with_income_interruption(self, state_with_reserves):
        """Test liquidity stress with income interruption."""
        result = LiquidityStressTester.simulate(
            state_with_reserves, 
            income_interruption_months=3
        )
        
        assert result.survival_months > 0
        assert result.survival_months < float('inf')

    def test_stress_with_expense_shock(self, state_with_reserves):
        """Test liquidity stress with expense shock."""
        result = LiquidityStressTester.simulate(
            state_with_reserves,
            expense_shock_amount=10000
        )
        
        assert result.survival_months > 0


class TestIncomeShockSimulator:
    """Tests for IncomeShockSimulator."""

    @pytest.fixture
    def state_with_income(self):
        """Create a state with income."""
        return {
            'profile_id': 1,
            'monthly_income': 5000,
            'monthly_expenses': 4000,
            'liquid_assets': 20000,
            'total_debt': 50000,
        }

    def test_shock_25_percent(self, state_with_income):
        """Test 25% income shock."""
        result = IncomeShockSimulator.simulate(
            state_with_income,
            income_reduction_percentage=0.25,
            income_shock_duration_months=6
        )
        
        assert result.survival_months > 0

    def test_shock_50_percent(self, state_with_income):
        """Test 50% income shock."""
        result = IncomeShockSimulator.simulate(
            state_with_income,
            income_reduction_percentage=0.50,
            income_shock_duration_months=6
        )
        
        assert result.survival_months > 0


class TestAllocationProjectionEngine:
    """Tests for AllocationProjectionEngine."""

    @pytest.fixture
    def state_with_assets(self):
        """Create a state with assets."""
        return {
            'profile_id': 1,
            'total_assets': 100000,
            'liquid_assets': 50000,
            'monthly_income': 5000,
            'assets_by_category': {'stocks': 50000, 'bonds': 30000, 'cash': 20000},
        }

    def test_projection_default_allocation(self, state_with_assets):
        """Test allocation projection with default allocation."""
        result = AllocationProjectionEngine.simulate(state_with_assets)
        
        assert result.projected_net_worth > 0
        assert result.confidence_score > 0

    def test_projection_custom_allocation(self, state_with_assets):
        """Test allocation projection with custom allocation."""
        result = AllocationProjectionEngine.simulate(
            state_with_assets,
            target_allocation={'stocks': 0.7, 'bonds': 0.2, 'cash': 0.1}
        )
        
        assert result.projected_net_worth > 0


class TestScenarioRunner:
    """Tests for ScenarioRunner."""

    def test_get_available_scenarios(self):
        """Test getting available scenarios."""
        scenarios = ScenarioRunner.get_available_scenarios()
        
        assert 'debt_payoff' in scenarios
        assert 'income_shock' in scenarios
        assert 'liquidity_stress' in scenarios
