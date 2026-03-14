"""Finance State Service - provides API-ready financial state outputs."""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models.financial_profile import FinancialProfile
from app.finance.models.asset import Asset
from app.finance.models.liability import Liability
from app.finance.models.cashflow_record import CashFlowRecord
from app.finance.models.financial_assumptions import FinancialAssumptions
from app.finance.models.financial_snapshot import FinancialSnapshot
from app.finance.engine.financial_state_engine import FinancialStateEngine


class FinanceStateService:
    """Service for managing financial state and snapshots."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_financial_state(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the current financial state for a profile.
        
        Args:
            profile_id: The profile ID
            
        Returns:
            Dictionary with financial state or None if profile not found
        """
        # Fetch profile
        profile = await self.session.get(FinancialProfile, profile_id)
        if not profile:
            return None

        # Fetch assets
        assets_result = await self.session.execute(
            select(Asset).where(Asset.profile_id == profile_id)
        )
        assets = list(assets_result.scalars().all())

        # Fetch liabilities
        liabilities_result = await self.session.execute(
            select(Liability).where(Liability.profile_id == profile_id)
        )
        liabilities = list(liabilities_result.scalars().all())

        # Fetch assumptions
        assumptions_result = await self.session.execute(
            select(FinancialAssumptions).where(FinancialAssumptions.profile_id == profile_id)
        )
        assumptions = list(assumptions_result.scalars().all())
        assumption = assumptions[0] if assumptions else None

        # Compute financial state
        state = FinancialStateEngine.compute_summary(profile, assets, liabilities, assumption)
        
        return state

    async def generate_financial_snapshot(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Generate and persist a financial snapshot.
        
        Args:
            profile_id: The profile ID
            
        Returns:
            Dictionary with snapshot data or None if profile not found
        """
        # Fetch current state
        state = await self.get_financial_state(profile_id)
        if not state:
            return None

        # Get assumptions version
        assumptions_result = await self.session.execute(
            select(FinancialAssumptions).where(FinancialAssumptions.profile_id == profile_id)
        )
        assumptions = list(assumptions_result.scalars().all())
        assumptions_version = None
        if assumptions:
            assumptions_version = f"v{assumptions[0].assumptions_id}"

        # Create snapshot
        snapshot = FinancialSnapshot.create_from_state(
            profile_id=profile_id,
            state=state,
            assumptions_version=assumptions_version,
        )

        # Persist snapshot
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)

        return snapshot.to_dict()

    async def get_financial_metrics(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Get financial metrics including health score breakdown.
        
        Args:
            profile_id: The profile ID
            
        Returns:
            Dictionary with financial metrics or None if profile not found
        """
        # Fetch profile
        profile = await self.session.get(FinancialProfile, profile_id)
        if not profile:
            return None

        # Fetch assets
        assets_result = await self.session.execute(
            select(Asset).where(Asset.profile_id == profile_id)
        )
        assets = list(assets_result.scalars().all())

        # Fetch liabilities
        liabilities_result = await self.session.execute(
            select(Liability).where(Liability.profile_id == profile_id)
        )
        liabilities = list(liabilities_result.scalars().all())

        # Fetch assumptions
        assumptions_result = await self.session.execute(
            select(FinancialAssumptions).where(FinancialAssumptions.profile_id == profile_id)
        )
        assumptions = list(assumptions_result.scalars().all())
        assumption = assumptions[0] if assumptions else None

        # Compute financial state
        state = FinancialStateEngine.compute(profile, assets, liabilities, assumption)

        return {
            "profile_id": profile_id,
            "net_worth": state.net_worth,
            "monthly_income": state.monthly_income,
            "monthly_expenses": state.monthly_expenses,
            "free_cash_flow": state.free_cash_flow,
            "total_assets": state.total_assets,
            "total_liabilities": state.total_liabilities,
            "liquid_assets": state.liquid_assets,
            "total_debt": state.total_debt,
            "debt_to_income_ratio": state.debt_to_income_ratio,
            "emergency_fund_months": state.emergency_fund_months,
            "financial_health_score": state.financial_health_score,
            "savings_rate": state.savings_rate,
            "liquidity_ratio": state.liquidity_ratio,
            "revolving_debt_balance": state.revolving_debt_balance,
            "secured_debt_balance": state.secured_debt_balance,
        }

    async def create_profile(
        self,
        monthly_income: float = 0.0,
        monthly_fixed_expenses: float = 0.0,
        monthly_variable_expenses: float = 0.0,
        risk_tolerance: str = "moderate",
        liquidity_preference: str = "medium",
        investment_horizon_years: int = 10,
        income_stability_score: str = "stable",
        user_id: Optional[int] = None,
    ) -> FinancialProfile:
        """
        Create a new financial profile.
        
        Args:
            monthly_income: Monthly income amount
            monthly_fixed_expenses: Monthly fixed expenses
            monthly_variable_expenses: Monthly variable expenses
            risk_tolerance: Risk tolerance level
            liquidity_preference: Liquidity preference level
            investment_horizon_years: Investment horizon in years
            income_stability_score: Income stability score
            user_id: Optional user ID to link to
            
        Returns:
            Created FinancialProfile
        """
        profile = FinancialProfile(
            user_id=user_id,
            monthly_income=monthly_income,
            monthly_fixed_expenses=monthly_fixed_expenses,
            monthly_variable_expenses=monthly_variable_expenses,
            risk_tolerance=risk_tolerance,
            liquidity_preference=liquidity_preference,
            investment_horizon_years=investment_horizon_years,
            income_stability_score=income_stability_score,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        return profile

    async def create_asset(
        self,
        profile_id: int,
        category: str,
        name: str,
        current_value: float,
        liquidity_score: float = 1.0,
        volatility_score: float = 0.0,
    ) -> Asset:
        """
        Create a new asset.
        
        Args:
            profile_id: Profile ID
            category: Asset category
            name: Asset name
            current_value: Current value
            liquidity_score: Liquidity score (0-1)
            volatility_score: Volatility score (0-1)
            
        Returns:
            Created Asset
        """
        asset = Asset(
            profile_id=profile_id,
            category=category,
            name=name,
            current_value=current_value,
            liquidity_score=liquidity_score,
            volatility_score=volatility_score,
            updated_at=datetime.utcnow(),
        )
        
        self.session.add(asset)
        await self.session.commit()
        await self.session.refresh(asset)
        
        return asset

    async def create_liability(
        self,
        profile_id: int,
        category: str,
        name: str,
        balance: float,
        minimum_payment: float = 0.0,
        interest_rate: float = 0.0,
        term_end_date: Optional[str] = None,
        secured_flag: bool = False,
    ) -> Liability:
        """
        Create a new liability.
        
        Args:
            profile_id: Profile ID
            category: Liability category
            name: Liability name
            balance: Current balance
            minimum_payment: Minimum monthly payment
            interest_rate: Annual interest rate
            term_end_date: End date of term (YYYY-MM-DD format)
            secured_flag: Whether liability is secured
            
        Returns:
            Created Liability
        """
        from datetime import datetime as dt
        
        term_date = None
        if term_end_date:
            term_date = dt.strptime(term_end_date, "%Y-%m-%d").date()
        
        liability = Liability(
            profile_id=profile_id,
            category=category,
            name=name,
            balance=balance,
            minimum_payment=minimum_payment,
            interest_rate=interest_rate,
            term_end_date=term_date,
            secured_flag=secured_flag,
            updated_at=datetime.utcnow(),
        )
        
        self.session.add(liability)
        await self.session.commit()
        await self.session.refresh(liability)
        
        return liability

    async def create_cashflow_record(
        self,
        profile_id: int,
        month: str,
        gross_income: float,
        net_income: float,
        fixed_expenses: float = 0.0,
        variable_expenses: float = 0.0,
        debt_payments: float = 0.0,
        savings_contributions: float = 0.0,
        investment_contributions: float = 0.0,
    ) -> CashFlowRecord:
        """
        Create a new cash flow record.
        
        Args:
            profile_id: Profile ID
            month: Month in YYYY-MM format
            gross_income: Gross income
            net_income: Net income
            fixed_expenses: Fixed expenses
            variable_expenses: Variable expenses
            debt_payments: Debt payments
            savings_contributions: Savings contributions
            investment_contributions: Investment contributions
            
        Returns:
            Created CashFlowRecord
        """
        record = CashFlowRecord(
            profile_id=profile_id,
            month=month,
            gross_income=gross_income,
            net_income=net_income,
            fixed_expenses=fixed_expenses,
            variable_expenses=variable_expenses,
            debt_payments=debt_payments,
            savings_contributions=savings_contributions,
            investment_contributions=investment_contributions,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        
        return record

    async def create_assumptions(
        self,
        profile_id: int,
        expected_market_return: float = 0.07,
        inflation_rate: float = 0.025,
        income_growth_rate: float = 0.03,
        emergency_fund_target_months: int = 6,
        tax_drag_estimate: float = 0.15,
        crypto_volatility_factor: float = 0.5,
        recession_probability: float = 0.2,
    ) -> FinancialAssumptions:
        """
        Create financial assumptions.
        
        Args:
            profile_id: Profile ID
            expected_market_return: Expected annual market return
            inflation_rate: Expected annual inflation rate
            income_growth_rate: Expected annual income growth rate
            emergency_fund_target_months: Target emergency fund months
            tax_drag_estimate: Tax drag estimate
            crypto_volatility_factor: Crypto volatility factor
            recession_probability: Recession probability
            
        Returns:
            Created FinancialAssumptions
        """
        assumptions = FinancialAssumptions(
            profile_id=profile_id,
            expected_market_return=expected_market_return,
            inflation_rate=inflation_rate,
            income_growth_rate=income_growth_rate,
            emergency_fund_target_months=emergency_fund_target_months,
            tax_drag_estimate=tax_drag_estimate,
            crypto_volatility_factor=crypto_volatility_factor,
            recession_probability=recession_probability,
            updated_at=datetime.utcnow(),
        )
        
        self.session.add(assumptions)
        await self.session.commit()
        await self.session.refresh(assumptions)
        
        return assumptions

    async def get_snapshots(self, profile_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get financial snapshots for a profile.
        
        Args:
            profile_id: The profile ID
            limit: Maximum number of snapshots to return
            
        Returns:
            List of snapshot dictionaries
        """
        result = await self.session.execute(
            select(FinancialSnapshot)
            .where(FinancialSnapshot.profile_id == profile_id)
            .order_by(FinancialSnapshot.timestamp.desc())
            .limit(limit)
        )
        snapshots = result.scalars().all()
        
        return [snapshot.to_dict() for snapshot in snapshots]
