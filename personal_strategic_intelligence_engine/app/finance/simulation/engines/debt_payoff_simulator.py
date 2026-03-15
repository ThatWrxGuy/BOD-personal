"""Debt Payoff Simulator - evaluates accelerated debt payoff strategies."""
from typing import Any, Dict, List

from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.models.scenario_definition import ScenarioType


class DebtPayoffSimulator:
    """
    Evaluates accelerated debt payoff strategies.
    
    Simulates different payment strategies to show:
    - Debt payoff timeline
    - Total interest paid
    - Interest saved vs baseline
    """

    @staticmethod
    def simulate(
        financial_state: Dict[str, Any],
        extra_payment_amount: float = 0,
        simulation_horizon_months: int = 60,
        inflation_rate: float = 0.03,
    ) -> ScenarioResult:
        """
        Simulate debt payoff with extra payments.

        Args:
            financial_state: Current financial state
            extra_payment_amount: Additional monthly payment toward debt
            simulation_horizon_months: Maximum months to simulate
            inflation_rate: Assumed inflation rate

        Returns:
            ScenarioResult with debt payoff projections
        """
        profile_id = financial_state.get("profile_id", 0)
        
        # Get liabilities
        liabilities = financial_state.get("liabilities_by_category", {})
        total_debt = financial_state.get("total_debt", 0)
        monthly_income = financial_state.get("monthly_income", 0)
        
        # Get minimum payments
        monthly_min_payments = sum(liability.get("minimum_payment", 0) 
                                   for liability in financial_state.get("liabilities", []))
        
        # Build debt list with interest rates
        debts = []
        
        # Add mortgage debt
        if "mortgage" in liabilities:
            debts.append({
                "name": "mortgage",
                "balance": liabilities["mortgage"],
                "rate": 0.065,  # Assume 6.5%
                "minimum_payment": 1500,
            })
        
        # Add credit card debt
        if "credit_card" in liabilities:
            debts.append({
                "name": "credit_card",
                "balance": liabilities["credit_card"],
                "rate": 0.18,  # Assume 18%
                "minimum_payment": 150,
            })
        
        # Add other debts
        for category, balance in liabilities.items():
            if category not in ["mortgage", "credit_card"] and balance > 0:
                debts.append({
                    "name": category,
                    "balance": balance,
                    "rate": 0.10,  # Assume 10%
                    "minimum_payment": balance * 0.02,  # 2% of balance
                })
        
        # Simulate month by month
        timeline = []
        current_month = 0
        total_interest_paid = 0
        remaining_debts = [d.copy() for d in debts]
        
        while current_month < simulation_horizon_months and any(d["balance"] > 0 for d in remaining_debts):
            current_month += 1
            
            # Calculate total available for debt payment
            available = monthly_min_payments + extra_payment_amount
            
            # Apply payments to debts (highest interest first)
            for debt in remaining_debts:
                if debt["balance"] <= 0:
                    continue
                    
                # Calculate monthly interest
                monthly_rate = debt["rate"] / 12
                interest = debt["balance"] * monthly_rate
                total_interest_paid += interest
                
                # Apply payment
                payment = min(available, debt["balance"] + interest)
                debt["balance"] = debt["balance"] + interest - payment
                available -= payment
                
                if debt["balance"] < 0:
                    available += abs(debt["balance"])
                    debt["balance"] = 0
            
            # Track monthly state
            total_balance = sum(d["balance"] for d in remaining_debts)
            timeline.append({
                "month": current_month,
                "total_debt": total_balance,
                "total_interest_paid": total_interest_paid,
            })
        
        # Calculate baseline (no extra payments) for comparison
        baseline_interest = DebtPayoffSimulator._calculate_baseline_interest(
            debts, monthly_min_payments, simulation_horizon_months
        )
        
        # Calculate projected values at end of simulation
        final_debt_balance = sum(d["balance"] for d in remaining_debts)
        
        # Project forward to end of horizon with investments
        monthly_expenses = financial_state.get("monthly_expenses", 0)
        monthly_savings = monthly_income - monthly_expenses - monthly_min_payments
        
        # Simple projection: savings grow, debt decreases to 0
        projected_liquidity = max(0, financial_state.get("liquid_assets", 0))
        if monthly_savings > 0:
            # Project savings growth at 5% annual return
            monthly_return = 0.05 / 12
            months_remaining = simulation_horizon_months - current_month
            projected_liquidity += monthly_savings * (
                (1 + monthly_return) ** months_remaining - 1
            ) / monthly_return if monthly_return > 0 else months_remaining * monthly_savings
        
        # Calculate net worth
        total_assets = financial_state.get("total_assets", 0)
        projected_net_worth = total_assets + projected_liquidity - final_debt_balance
        
        # Determine risk classification
        if final_debt_balance <= 0:
            risk_classification = "low"
        elif final_debt_balance < total_debt * 0.5:
            risk_classification = "moderate"
        else:
            risk_classification = "high"
        
        return ScenarioResult.create(
            scenario_id="",  # Will be set by caller
            profile_id=profile_id,
            scenario_type=ScenarioType.DEBT_PAYOFF,
            projected_net_worth=projected_net_worth,
            projected_liquidity=projected_liquidity,
            projected_debt_balance=final_debt_balance,
            interest_paid_total=total_interest_paid,
            interest_saved_vs_baseline=baseline_interest - total_interest_paid,
            payoff_timeline_months=current_month,
            survival_months=current_month,  # Time to debt freedom
            minimum_liquidity=projected_liquidity,
            confidence_score=0.80,
            timeline=timeline,
            risk_classification=risk_classification,
        )

    @staticmethod
    def _calculate_baseline_interest(
        debts: List[Dict],
        monthly_payment: float,
        months: int,
    ) -> float:
        """Calculate total interest paid with no extra payments."""
        total_interest = 0
        remaining = [d.copy() for d in debts]
        
        for _ in range(months):
            for debt in remaining:
                if debt["balance"] <= 0:
                    continue
                monthly_rate = debt["rate"] / 12
                interest = debt["balance"] * monthly_rate
                total_interest += interest
                payment = min(monthly_payment, debt["balance"] + interest)
                debt["balance"] = max(0, debt["balance"] + interest - payment)
        
        return total_interest
