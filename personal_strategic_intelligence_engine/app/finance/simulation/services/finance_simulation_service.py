"""Finance Simulation Service - coordinates scenario creation and execution."""
from typing import Any, Dict, List, Optional

from app.finance.services.finance_state_service import FinanceStateService
from app.finance.simulation.models.scenario_definition import ScenarioDefinition, ScenarioType
from app.finance.simulation.models.scenario_parameters import ScenarioParameters
from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.models.scenario_comparison import ScenarioComparison
from app.finance.simulation.engines.scenario_runner import ScenarioRunner


class FinanceSimulationService:
    """
    Coordinates scenario creation and execution.
    
    Functions:
    - run_scenario(profile_id, scenario_type, parameters)
    - get_scenario_results(profile_id)
    - compare_scenarios(base_scenario_id, comparison_scenario_id)
    """

    def __init__(self, finance_state_service: FinanceStateService):
        self.finance_state_service = finance_state_service
        
        # In-memory storage for scenarios (would be database in production)
        self._scenario_results: Dict[str, ScenarioResult] = {}

    async def run_scenario(
        self,
        profile_id: int,
        scenario_type: ScenarioType,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ScenarioResult:
        """
        Run a financial simulation scenario.

        Args:
            profile_id: The profile ID
            scenario_type: Type of scenario to run
            parameters: Scenario parameters

        Returns:
            ScenarioResult with simulation output
        """
        # Get financial state
        financial_state = await self.finance_state_service.get_financial_state(profile_id)
        if not financial_state:
            # Use mock data for demo
            financial_state = self._get_demo_financial_state(profile_id)

        # Create scenario definition
        scenario_def = ScenarioDefinition.create(
            profile_id=profile_id,
            scenario_type=scenario_type,
            description=f"Simulation of {scenario_type.value}",
        )

        # Create parameters
        params_dict = parameters or {}
        scenario_params = ScenarioParameters.create(
            scenario_id=scenario_def.scenario_id,
            extra_payment_amount=params_dict.get("extra_payment_amount"),
            extra_payment_frequency=params_dict.get("extra_payment_frequency", "monthly"),
            income_reduction_percentage=params_dict.get("income_reduction_percentage"),
            income_shock_duration_months=params_dict.get("income_shock_duration_months"),
            expense_increase_amount=params_dict.get("expense_increase_amount"),
            expense_shock_type=params_dict.get("expense_shock_type", "one_time"),
            market_return_rate=params_dict.get("market_return_rate"),
            inflation_rate=params_dict.get("inflation_rate"),
            simulation_horizon_months=params_dict.get("simulation_horizon_months", 60),
            confidence_level=params_dict.get("confidence_level", 0.90),
            target_allocation=params_dict.get("target_allocation"),
            current_allocation=params_dict.get("current_allocation"),
        )

        # Run simulation
        result = ScenarioRunner.run(financial_state, scenario_def, scenario_params)

        # Store result
        self._scenario_results[result.result_id] = result

        return result

    async def get_scenario_results(self, profile_id: int) -> List[ScenarioResult]:
        """
        Get all scenario results for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of ScenarioResult objects
        """
        return [
            result for result in self._scenario_results.values()
            if result.profile_id == profile_id
        ]

    async def get_scenario_by_id(self, scenario_id: str) -> Optional[ScenarioResult]:
        """
        Get a specific scenario result by ID.

        Args:
            scenario_id: The scenario result ID

        Returns:
            ScenarioResult or None
        """
        return self._scenario_results.get(scenario_id)

    async def compare_scenarios(
        self,
        base_scenario_id: str,
        comparison_scenario_id: str,
    ) -> Optional[ScenarioComparison]:
        """
        Compare two scenario results.

        Args:
            base_scenario_id: ID of the base scenario
            comparison_scenario_id: ID of the scenario to compare

        Returns:
            ScenarioComparison object
        """
        base_result = self._scenario_results.get(base_scenario_id)
        comparison_result = self._scenario_results.get(comparison_scenario_id)

        if not base_result or not comparison_result:
            return None

        return ScenarioComparison.create(
            base_scenario_id=base_scenario_id,
            comparison_scenario_id=comparison_scenario_id,
            base_result=base_result,
            comparison_result=comparison_result,
        )

    def _get_demo_financial_state(self, profile_id: int) -> Dict[str, Any]:
        """Get demo financial state for testing."""
        return {
            "profile_id": profile_id,
            "net_worth": -75000,
            "total_assets": 180000,
            "total_liabilities": 255000,
            "monthly_income": 6400,
            "monthly_expenses": 6150,
            "free_cash_flow": -1350,
            "liquid_assets": 30000,
            "total_debt": 255000,
            "debt_to_income_ratio": 0.2062,
            "emergency_fund_months": 29.3,
            "revolving_debt_balance": 5000,
            "secured_debt_balance": 250000,
            "assets_by_category": {
                "checking": 10000,
                "savings": 20000,
                "investment": 50000,
                "retirement": 100000,
            },
            "liabilities_by_category": {
                "mortgage": 250000,
                "credit_card": 5000,
            },
            "liabilities": [
                {"name": "mortgage", "balance": 250000, "rate": 0.065, "minimum_payment": 1500},
                {"name": "credit_card", "balance": 5000, "rate": 0.18, "minimum_payment": 150},
            ],
        }
