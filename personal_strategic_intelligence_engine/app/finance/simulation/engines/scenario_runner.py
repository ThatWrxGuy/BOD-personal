"""Scenario Runner - central orchestrator for executing financial simulations."""
from typing import Any, Dict, Optional

from app.finance.simulation.models.scenario_definition import ScenarioDefinition, ScenarioType
from app.finance.simulation.models.scenario_parameters import ScenarioParameters
from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.engines.debt_payoff_simulator import DebtPayoffSimulator
from app.finance.simulation.engines.liquidity_stress_tester import LiquidityStressTester
from app.finance.simulation.engines.income_shock_simulator import IncomeShockSimulator
from app.finance.simulation.engines.expense_shock_simulator import ExpenseShockSimulator
from app.finance.simulation.engines.allocation_projection_engine import AllocationProjectionEngine


class ScenarioRunner:
    """
    Central orchestrator responsible for executing financial simulations.
    
    Responsibilities:
    - Call appropriate simulation engine
    - Capture simulation results
    - Normalize output data
    - Generate scenario result object
    """

    @staticmethod
    def run(
        financial_state: Dict[str, Any],
        scenario_definition: ScenarioDefinition,
        parameters: ScenarioParameters,
    ) -> ScenarioResult:
        """
        Run a simulation based on scenario definition and parameters.

        Args:
            financial_state: Current financial state
            scenario_definition: Scenario type and description
            parameters: Simulation parameters

        Returns:
            ScenarioResult with simulation output
        """
        # Route to appropriate simulator
        if scenario_definition.scenario_type == ScenarioType.DEBT_PAYOFF:
            result = ScenarioRunner._run_debt_payoff(financial_state, parameters)
        elif scenario_definition.scenario_type == ScenarioType.LIQUIDITY_STRESS:
            result = ScenarioRunner._run_liquidity_stress(financial_state, parameters)
        elif scenario_definition.scenario_type == ScenarioType.INCOME_SHOCK:
            result = ScenarioRunner._run_income_shock(financial_state, parameters)
        elif scenario_definition.scenario_type == ScenarioType.EXPENSE_SHOCK:
            result = ScenarioRunner._run_expense_shock(financial_state, parameters)
        elif scenario_definition.scenario_type == ScenarioType.INVESTMENT_ALLOCATION:
            result = ScenarioRunner._run_allocation_projection(financial_state, parameters)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_definition.scenario_type}")
        
        # Set scenario ID
        result.scenario_id = scenario_definition.scenario_id
        
        return result

    @staticmethod
    def _run_debt_payoff(
        financial_state: Dict[str, Any],
        parameters: ScenarioParameters,
    ) -> ScenarioResult:
        """Run debt payoff simulation."""
        return DebtPayoffSimulator.simulate(
            financial_state=financial_state,
            extra_payment_amount=parameters.extra_payment_amount or 0,
            simulation_horizon_months=parameters.simulation_horizon_months,
            inflation_rate=parameters.inflation_rate or 0.03,
        )

    @staticmethod
    def _run_liquidity_stress(
        financial_state: Dict[str, Any],
        parameters: ScenarioParameters,
    ) -> ScenarioResult:
        """Run liquidity stress test simulation."""
        # Use income reduction as proxy for income interruption months
        # (reusing the percentage field for duration)
        income_interruption_months = int(parameters.income_reduction_percentage * 12) if parameters.income_reduction_percentage else 3
        
        return LiquidityStressTester.simulate(
            financial_state=financial_state,
            income_interruption_months=income_interruption_months,
            expense_shock_amount=parameters.expense_increase_amount or 0,
            simulation_horizon_months=parameters.simulation_horizon_months,
        )

    @staticmethod
    def _run_income_shock(
        financial_state: Dict[str, Any],
        parameters: ScenarioParameters,
    ) -> ScenarioResult:
        """Run income shock simulation."""
        return IncomeShockSimulator.simulate(
            financial_state=financial_state,
            income_reduction_percentage=parameters.income_reduction_percentage or 0.25,
            income_shock_duration_months=parameters.income_shock_duration_months or 6,
            simulation_horizon_months=parameters.simulation_horizon_months,
        )

    @staticmethod
    def _run_expense_shock(
        financial_state: Dict[str, Any],
        parameters: ScenarioParameters,
    ) -> ScenarioResult:
        """Run expense shock simulation."""
        return ExpenseShockSimulator.simulate(
            financial_state=financial_state,
            expense_shock_amount=parameters.expense_increase_amount or 5000,
            expense_type=parameters.expense_shock_type or "one_time",
            recovery_contribution=parameters.extra_payment_amount or 0,
            simulation_horizon_months=parameters.simulation_horizon_months,
        )

    @staticmethod
    def _run_allocation_projection(
        financial_state: Dict[str, Any],
        parameters: ScenarioParameters,
    ) -> ScenarioResult:
        """Run investment allocation projection."""
        return AllocationProjectionEngine.simulate(
            financial_state=financial_state,
            target_allocation=parameters.target_allocation,
            market_return_rate=parameters.market_return_rate or 0.07,
            inflation_rate=parameters.inflation_rate or 0.03,
            simulation_horizon_months=parameters.simulation_horizon_months,
        )

    @staticmethod
    def get_available_scenarios() -> Dict[str, str]:
        """
        Get available scenario types with descriptions.
        
        Returns:
            Dictionary of scenario types and their descriptions
        """
        return {
            "debt_payoff": "Evaluate accelerated debt payoff strategies",
            "income_shock": "Model effects of reduced income",
            "expense_shock": "Model unexpected financial obligations",
            "liquidity_stress": "Evaluate resilience to financial disruption",
            "investment_allocation": "Project asset growth under different allocations",
        }
