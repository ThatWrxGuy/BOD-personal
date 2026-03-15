"""Debt Analyzer - computes total debt, revolving/secured debt balances, weighted interest rate, and debt-to-income ratio."""
from dataclasses import dataclass
from typing import List

from app.finance.models.liability import Liability


@dataclass
class DebtResult:
    """Result of debt analysis."""
    total_debt_balance: float
    revolving_debt_balance: float
    secured_debt_balance: float
    unsecured_debt_balance: float
    weighted_interest_rate: float
    debt_to_income_ratio: float
    monthly_minimum_payments: float
    debt_count: int


class DebtAnalyzer:
    """Analyzes debt position."""

    @staticmethod
    def calculate(
        liabilities: List[Liability],
        monthly_income: float,
    ) -> DebtResult:
        """
        Calculate debt metrics.

        Args:
            liabilities: List of Liability objects
            monthly_income: Monthly income amount

        Returns:
            DebtResult with computed values
        """
        # Total debt
        total_debt = sum(liability.balance for liability in liabilities)

        # Revolving debt (credit cards, etc.)
        revolving_debt_balance = sum(
            liability.balance for liability in liabilities if liability.is_revolving()
        )

        # Secured debt (mortgages, auto loans, etc.)
        secured_debt_balance = sum(
            liability.balance for liability in liabilities if liability.is_secured()
        )

        # Unsecured debt
        unsecured_debt_balance = total_debt - secured_debt_balance

        # Weighted interest rate
        weighted_interest_rate = DebtAnalyzer._calculate_weighted_interest_rate(liabilities)

        # Monthly minimum payments
        monthly_minimum_payments = sum(
            liability.minimum_payment for liability in liabilities
        )

        # Debt to income ratio (monthly debt payments / monthly income)
        # This is the standard back-end DTI calculation
        debt_to_income_ratio = (
            monthly_minimum_payments / monthly_income if monthly_income > 0 else 0.0
        )

        # Debt count
        debt_count = len(liabilities)

        return DebtResult(
            total_debt_balance=total_debt,
            revolving_debt_balance=revolving_debt_balance,
            secured_debt_balance=secured_debt_balance,
            unsecured_debt_balance=unsecured_debt_balance,
            weighted_interest_rate=weighted_interest_rate,
            debt_to_income_ratio=debt_to_income_ratio,
            monthly_minimum_payments=monthly_minimum_payments,
            debt_count=debt_count,
        )

    @staticmethod
    def _calculate_weighted_interest_rate(liabilities: List[Liability]) -> float:
        """
        Calculate weighted average interest rate based on balances.

        Args:
            liabilities: List of Liability objects

        Returns:
            Weighted average interest rate
        """
        if not liabilities:
            return 0.0

        total_balance = sum(liability.balance for liability in liabilities)
        if total_balance == 0:
            return 0.0

        weighted_sum = sum(
            liability.balance * liability.interest_rate for liability in liabilities
        )
        return weighted_sum / total_balance

    @staticmethod
    def calculate_summary(
        liabilities: List[Liability],
        monthly_income: float,
    ) -> dict:
        """
        Calculate debt metrics and return as dictionary.

        Args:
            liabilities: List of Liability objects
            monthly_income: Monthly income amount

        Returns:
            Dictionary with debt summary
        """
        result = DebtAnalyzer.calculate(liabilities, monthly_income)
        return {
            "total_debt": result.total_debt_balance,
            "revolving_debt_balance": result.revolving_debt_balance,
            "secured_debt_balance": result.secured_debt_balance,
            "unsecured_debt_balance": result.unsecured_debt_balance,
            "weighted_interest_rate": result.weighted_interest_rate,
            "debt_to_income_ratio": result.debt_to_income_ratio,
            "monthly_minimum_payments": result.monthly_minimum_payments,
            "debt_count": result.debt_count,
        }

    @staticmethod
    def is_high_debt_to_income(liabilities: List[Liability], monthly_income: float, threshold: float = 0.36) -> bool:
        """
        Check if debt-to-income ratio is high (typically > 36% is considered high).

        Args:
            liabilities: List of Liability objects
            monthly_income: Monthly income amount
            threshold: Threshold for high DTI (default 36%)

        Returns:
            True if debt-to-income ratio is high
        """
        result = DebtAnalyzer.calculate(liabilities, monthly_income)
        return result.debt_to_income_ratio > threshold
