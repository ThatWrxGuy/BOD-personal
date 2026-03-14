"""Cash Flow Analyzer - computes monthly income, expenses, free cash flow, savings rate, and debt service ratio."""
from dataclasses import dataclass
from typing import List, Optional

from app.finance.models.cashflow_record import CashFlowRecord
from app.finance.models.financial_profile import FinancialProfile


@dataclass
class CashFlowResult:
    """Result of cash flow analysis."""
    monthly_income: float
    monthly_expenses: float
    free_cash_flow: float
    savings_rate: float
    debt_service_ratio: float
    gross_income: float
    net_income: float
    fixed_expenses: float
    variable_expenses: float
    debt_payments: float
    savings_contributions: float
    investment_contributions: float


class CashFlowAnalyzer:
    """Analyzes cash flow from financial profile and cash flow records."""

    @staticmethod
    def calculate_from_profile(
        profile: FinancialProfile,
        monthly_debt_payments: float = 0.0,
        monthly_savings: float = 0.0,
        monthly_investments: float = 0.0,
    ) -> CashFlowResult:
        """
        Calculate cash flow from a financial profile.

        Args:
            profile: FinancialProfile object
            monthly_debt_payments: Monthly debt payments
            monthly_savings: Monthly savings contributions
            monthly_investments: Monthly investment contributions

        Returns:
            CashFlowResult with computed values
        """
        gross_income = profile.monthly_income
        # Assume net income is ~80% of gross (simplified)
        net_income = gross_income * 0.8
        
        fixed_expenses = profile.monthly_fixed_expenses
        variable_expenses = profile.monthly_variable_expenses
        
        # Total expenses
        monthly_expenses = fixed_expenses + variable_expenses + monthly_debt_payments
        
        # Free cash flow = net income - all outflows
        free_cash_flow = net_income - monthly_expenses - monthly_savings - monthly_investments
        
        # Savings rate = (savings + investments) / gross income
        savings_rate = (monthly_savings + monthly_investments) / gross_income if gross_income > 0 else 0.0
        
        # Debt service ratio = debt payments / gross income
        debt_service_ratio = monthly_debt_payments / gross_income if gross_income > 0 else 0.0

        return CashFlowResult(
            monthly_income=net_income,
            monthly_expenses=monthly_expenses,
            free_cash_flow=free_cash_flow,
            savings_rate=savings_rate,
            debt_service_ratio=debt_service_ratio,
            gross_income=gross_income,
            net_income=net_income,
            fixed_expenses=fixed_expenses,
            variable_expenses=variable_expenses,
            debt_payments=monthly_debt_payments,
            savings_contributions=monthly_savings,
            investment_contributions=monthly_investments,
        )

    @staticmethod
    def calculate_from_records(
        records: List[CashFlowRecord],
        latest_only: bool = True,
    ) -> Optional[CashFlowResult]:
        """
        Calculate cash flow from cash flow records.

        Args:
            records: List of CashFlowRecord objects
            latest_only: If True, use only the most recent record

        Returns:
            CashFlowResult with computed values, or None if no records
        """
        if not records:
            return None

        if latest_only:
            # Sort by month and get the latest
            sorted_records = sorted(records, key=lambda r: r.month, reverse=True)
            record = sorted_records[0]
        else:
            # Average across all records
            record = records[-1]  # Use last record for now

        gross_income = record.gross_income
        net_income = record.net_income
        
        total_expenses = record.fixed_expenses + record.variable_expenses + record.debt_payments
        free_cash_flow = net_income - total_expenses - record.savings_contributions - record.investment_contributions
        
        # Savings rate = (savings + investments) / gross income
        savings_rate = (record.savings_contributions + record.investment_contributions) / gross_income if gross_income > 0 else 0.0
        
        # Debt service ratio = debt payments / gross income
        debt_service_ratio = record.debt_payments / gross_income if gross_income > 0 else 0.0

        return CashFlowResult(
            monthly_income=net_income,
            monthly_expenses=total_expenses,
            free_cash_flow=free_cash_flow,
            savings_rate=savings_rate,
            debt_service_ratio=debt_service_ratio,
            gross_income=gross_income,
            net_income=net_income,
            fixed_expenses=record.fixed_expenses,
            variable_expenses=record.variable_expenses,
            debt_payments=record.debt_payments,
            savings_contributions=record.savings_contributions,
            investment_contributions=record.investment_contributions,
        )

    @staticmethod
    def calculate_summary(
        profile: FinancialProfile,
        monthly_debt_payments: float = 0.0,
        monthly_savings: float = 0.0,
        monthly_investments: float = 0.0,
    ) -> dict:
        """
        Calculate cash flow and return as dictionary.

        Args:
            profile: FinancialProfile object
            monthly_debt_payments: Monthly debt payments
            monthly_savings: Monthly savings contributions
            monthly_investments: Monthly investment contributions

        Returns:
            Dictionary with cash flow summary
        """
        result = CashFlowAnalyzer.calculate_from_profile(
            profile, monthly_debt_payments, monthly_savings, monthly_investments
        )
        return {
            "monthly_income": result.monthly_income,
            "monthly_expenses": result.monthly_expenses,
            "free_cash_flow": result.free_cash_flow,
            "savings_rate": result.savings_rate,
            "debt_service_ratio": result.debt_service_ratio,
            "gross_income": result.gross_income,
            "net_income": result.net_income,
            "fixed_expenses": result.fixed_expenses,
            "variable_expenses": result.variable_expenses,
            "debt_payments": result.debt_payments,
            "savings_contributions": result.savings_contributions,
            "investment_contributions": result.investment_contributions,
        }
