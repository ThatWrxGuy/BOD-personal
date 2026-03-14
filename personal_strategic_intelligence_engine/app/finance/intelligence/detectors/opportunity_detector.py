"""Opportunity Detector - detects conditions where the user's financial position can be improved."""
from typing import Any, Dict, List

from app.finance.intelligence.models.financial_opportunity import FinancialOpportunity, OpportunityType


class OpportunityDetector:
    """
    Detects conditions where the user's financial position can be improved.
    """

    # Opportunity thresholds
    EXCESS_CASH_FLOW_THRESHOLD = 500  # $500+ excess
    RESERVE_EXCESS_MULTIPLIER = 1.5  # 1.5x target
    DEBT_PAYOFF_BENEFIT_THRESHOLD = 0.15  # 15%+ interest savings
    
    # Minimum debt balance to consider for payoff
    MIN_DEBT_FOR_PAYOFF = 1000

    @staticmethod
    def detect(
        financial_state: Dict[str, Any],
        financial_metrics: Dict[str, Any],
    ) -> List[FinancialOpportunity]:
        """
        Detect opportunities from financial state and metrics.

        Args:
            financial_state: The canonical financial state
            financial_metrics: Additional financial metrics

        Returns:
            List of FinancialOpportunity objects
        """
        opportunities = []
        profile_id = financial_state.get("profile_id", 0)

        # Check for Excess Cash Flow opportunity
        excess_cash = OpportunityDetector._check_excess_cash_flow(
            financial_state, profile_id
        )
        opportunities.extend(excess_cash)

        # Check for Reserve Optimization opportunity
        reserve_ops = OpportunityDetector._check_reserve_optimization(
            financial_state, profile_id
        )
        opportunities.extend(reserve_ops)

        # Check for Debt Acceleration opportunity
        debt_ops = OpportunityDetector._check_debt_acceleration(
            financial_state, profile_id
        )
        opportunities.extend(debt_ops)

        # Check for Allocation Rebalance opportunity
        allocation_ops = OpportunityDetector._check_allocation_rebalance(
            financial_state, profile_id
        )
        opportunities.extend(allocation_ops)

        # Check for High Yield Savings opportunity
        savings_ops = OpportunityDetector._check_high_yield_savings(
            financial_state, profile_id
        )
        opportunities.extend(savings_ops)

        return opportunities

    @staticmethod
    def _check_excess_cash_flow(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialOpportunity]:
        """Check for excess cash flow that could be used for investments or debt payoff."""
        opportunities = []
        fcf = financial_state.get("free_cash_flow", 0)
        total_debt = financial_state.get("total_debt", 0)
        
        if fcf > OpportunityDetector.EXCESS_CASH_FLOW_THRESHOLD:
            # Determine best use of excess cash
            if total_debt > OpportunityDetector.MIN_DEBT_FOR_PAYOFF:
                # Recommend debt payoff
                opportunities.append(FinancialOpportunity.create(
                    profile_id=profile_id,
                    opportunity_type=OpportunityType.ACCELERATED_DEBT_PAYOFF,
                    description=f"Free cash flow of ${fcf:,.2f} per month provides opportunity to accelerate debt payoff.",
                    trigger_metric="free_cash_flow",
                    trigger_value=fcf,
                    expected_benefit=f"Using excess cash flow for debt reduction could save ${fcf * 12:,.2f} annually in interest and accelerate payoff."
                ))
            else:
                # Recommend investment
                opportunities.append(FinancialOpportunity.create(
                    profile_id=profile_id,
                    opportunity_type=OpportunityType.EXCESS_CASH_FLOW_INVESTMENT,
                    description=f"Free cash flow of ${fcf:,.2f} per month can be invested for long-term growth.",
                    trigger_metric="free_cash_flow",
                    trigger_value=fcf,
                    expected_benefit=f"Investing ${fcf:,.2f} monthly could yield significant long-term returns."
                ))

        return opportunities

    @staticmethod
    def _check_reserve_optimization(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialOpportunity]:
        """Check if liquid reserves exceed emergency fund target."""
        opportunities = []
        
        emergency_months = financial_state.get("emergency_fund_months", 0)
        target_months = 6  # Default target
        
        # Check if emergency fund significantly exceeds target
        if emergency_months > target_months * OpportunityDetector.RESERVE_EXCESS_MULTIPLIER:
            excess_months = emergency_months - target_months
            monthly_expenses = financial_state.get("monthly_expenses", 0)
            excess_amount = excess_months * monthly_expenses
            
            opportunities.append(FinancialOpportunity.create(
                profile_id=profile_id,
                opportunity_type=OpportunityType.RESERVE_OPTIMIZATION,
                description=f"Emergency fund of {emergency_months:.1f} months exceeds target of {target_months} months by approximately ${excess_amount:,.2f}.",
                trigger_metric="emergency_fund_months",
                trigger_value=emergency_months,
                expected_benefit=f"Reallocating ${excess_amount:,.2f} of excess reserves to investments could generate additional returns."
            ))

        return opportunities

    @staticmethod
    def _check_debt_acceleration(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialOpportunity]:
        """Check for opportunities to accelerate debt payoff."""
        opportunities = []
        
        revolving_debt = financial_state.get("revolving_debt_balance", 0)
        free_cash_flow = financial_state.get("free_cash_flow", 0)
        
        # If there's revolving debt and positive cash flow
        if revolving_debt > OpportunityDetector.MIN_DEBT_FOR_PAYOFF and free_cash_flow > 0:
            opportunities.append(FinancialOpportunity.create(
                profile_id=profile_id,
                opportunity_type=OpportunityType.ACCELERATED_DEBT_PAYOFF,
                description=f"Revolving debt of ${revolving_debt:,.2f} with available free cash flow of ${free_cash_flow:,.2f} presents opportunity for accelerated payoff.",
                trigger_metric="revolving_debt_balance",
                trigger_value=revolving_debt,
                expected_benefit="Accelerating debt payoff could reduce interest costs and improve cash flow faster."
            ))

        return opportunities

    @staticmethod
    def _check_allocation_rebalance(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialOpportunity]:
        """Check for asset allocation rebalancing opportunities."""
        opportunities = []
        
        assets_by_category = financial_state.get("assets_by_category", {})
        total_assets = financial_state.get("total_assets", 0)
        
        if total_assets > 0:
            # Check for significant cash position
            cash_categories = ["cash", "checking", "savings"]
            cash_total = sum(
                assets_by_category.get(cat, 0) for cat in cash_categories
            )
            cash_ratio = cash_total / total_assets
            
            # If more than 30% in cash, suggest investment
            if cash_ratio > 0.30 and total_assets > 10000:
                opportunities.append(FinancialOpportunity.create(
                    profile_id=profile_id,
                    opportunity_type=OpportunityType.ALLOCATION_REBALANCE,
                    description=f"Cash holdings represent {cash_ratio:.1%} of total assets, which may be over-allocated to low-yield assets.",
                    trigger_metric="cash_ratio",
                    trigger_value=cash_ratio,
                    expected_benefit="Reallocating excess cash to investments could improve long-term returns."
                ))

        return opportunities

    @staticmethod
    def _check_high_yield_savings(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialOpportunity]:
        """Check if savings accounts could be optimized for higher yields."""
        opportunities = []
        
        assets_by_category = financial_state.get("assets_by_category", {})
        savings_balance = assets_by_category.get("savings", 0)
        
        # If significant savings balance exists
        if savings_balance > 10000:
            opportunities.append(FinancialOpportunity.create(
                profile_id=profile_id,
                opportunity_type=OpportunityType.HIGH_YIELD_SAVINGS,
                description=f"Savings balance of ${savings_balance:,.2f} may benefit from higher-yield alternatives.",
                trigger_metric="savings_balance",
                trigger_value=savings_balance,
                expected_benefit="Moving to high-yield savings or money market accounts could increase annual returns."
            ))

        return opportunities
