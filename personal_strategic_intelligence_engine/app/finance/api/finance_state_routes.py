"""Financial State API routes - canonical financial state for the platform."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.finance.services.finance_state_service import FinanceStateService


router = APIRouter(prefix="/finance", tags=["finance"])


# ===================
# Pydantic Models
# ===================

class FinancialProfileCreate(BaseModel):
    """Model for creating a financial profile."""
    monthly_income: float = 0.0
    monthly_fixed_expenses: float = 0.0
    monthly_variable_expenses: float = 0.0
    risk_tolerance: str = "moderate"
    liquidity_preference: str = "medium"
    investment_horizon_years: int = 10
    income_stability_score: str = "stable"
    user_id: Optional[int] = None


class AssetCreate(BaseModel):
    """Model for creating an asset."""
    profile_id: int
    category: str
    name: str
    current_value: float
    liquidity_score: float = 1.0
    volatility_score: float = 0.0


class LiabilityCreate(BaseModel):
    """Model for creating a liability."""
    profile_id: int
    category: str
    name: str
    balance: float
    minimum_payment: float = 0.0
    interest_rate: float = 0.0
    term_end_date: Optional[str] = None
    secured_flag: bool = False


class CashFlowRecordCreate(BaseModel):
    """Model for creating a cash flow record."""
    profile_id: int
    month: str  # YYYY-MM format
    gross_income: float
    net_income: float
    fixed_expenses: float = 0.0
    variable_expenses: float = 0.0
    debt_payments: float = 0.0
    savings_contributions: float = 0.0
    investment_contributions: float = 0.0


class FinancialAssumptionsCreate(BaseModel):
    """Model for creating financial assumptions."""
    profile_id: int
    expected_market_return: float = 0.07
    inflation_rate: float = 0.025
    income_growth_rate: float = 0.03
    emergency_fund_target_months: int = 6
    tax_drag_estimate: float = 0.15
    crypto_volatility_factor: float = 0.5
    recession_probability: float = 0.2


# ===================
# Endpoints
# ===================

@router.get("/state")
async def get_financial_state(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get the current financial state for a profile.
    
    Returns the canonical financial state object containing:
    - net_worth, monthly_income, monthly_expenses, free_cash_flow
    - total_assets, total_liabilities, liquid_assets
    - total_debt, debt_to_income_ratio, emergency_fund_months
    - financial_health_score
    """
    service = FinanceStateService(session)
    state = await service.get_financial_state(profile_id)
    
    if state is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return state


@router.get("/metrics")
async def get_financial_metrics(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get detailed financial metrics including health score breakdown.
    """
    service = FinanceStateService(session)
    metrics = await service.get_financial_metrics(profile_id)
    
    if metrics is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return metrics


@router.get("/snapshots")
async def get_financial_snapshots(
    profile_id: int = Query(..., description="Profile ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of snapshots"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get financial snapshots for a profile.
    
    Returns a list of historical snapshots for audit trails.
    """
    service = FinanceStateService(session)
    snapshots = await service.get_snapshots(profile_id, limit)
    
    return {"snapshots": snapshots}


@router.post("/snapshots")
async def create_financial_snapshot(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Generate and persist a new financial snapshot.
    """
    service = FinanceStateService(session)
    snapshot = await service.generate_financial_snapshot(profile_id)
    
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return snapshot


@router.post("/profile")
async def create_financial_profile(
    data: FinancialProfileCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new financial profile.
    """
    service = FinanceStateService(session)
    profile = await service.create_profile(
        monthly_income=data.monthly_income,
        monthly_fixed_expenses=data.monthly_fixed_expenses,
        monthly_variable_expenses=data.monthly_variable_expenses,
        risk_tolerance=data.risk_tolerance,
        liquidity_preference=data.liquidity_preference,
        investment_horizon_years=data.investment_horizon_years,
        income_stability_score=data.income_stability_score,
        user_id=data.user_id,
    )
    
    return profile.to_dict()


@router.post("/assets")
async def create_asset(
    data: AssetCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new asset for a profile.
    """
    service = FinanceStateService(session)
    asset = await service.create_asset(
        profile_id=data.profile_id,
        category=data.category,
        name=data.name,
        current_value=data.current_value,
        liquidity_score=data.liquidity_score,
        volatility_score=data.volatility_score,
    )
    
    return asset.to_dict()


@router.post("/liabilities")
async def create_liability(
    data: LiabilityCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new liability for a profile.
    """
    service = FinanceStateService(session)
    liability = await service.create_liability(
        profile_id=data.profile_id,
        category=data.category,
        name=data.name,
        balance=data.balance,
        minimum_payment=data.minimum_payment,
        interest_rate=data.interest_rate,
        term_end_date=data.term_end_date,
        secured_flag=data.secured_flag,
    )
    
    return liability.to_dict()


@router.post("/cashflow")
async def create_cashflow_record(
    data: CashFlowRecordCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new cash flow record for a profile.
    """
    service = FinanceStateService(session)
    record = await service.create_cashflow_record(
        profile_id=data.profile_id,
        month=data.month,
        gross_income=data.gross_income,
        net_income=data.net_income,
        fixed_expenses=data.fixed_expenses,
        variable_expenses=data.variable_expenses,
        debt_payments=data.debt_payments,
        savings_contributions=data.savings_contributions,
        investment_contributions=data.investment_contributions,
    )
    
    return record.to_dict()


@router.post("/assumptions")
async def create_assumptions(
    data: FinancialAssumptionsCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create financial assumptions for a profile.
    """
    service = FinanceStateService(session)
    assumptions = await service.create_assumptions(
        profile_id=data.profile_id,
        expected_market_return=data.expected_market_return,
        inflation_rate=data.inflation_rate,
        income_growth_rate=data.income_growth_rate,
        emergency_fund_target_months=data.emergency_fund_target_months,
        tax_drag_estimate=data.tax_drag_estimate,
        crypto_volatility_factor=data.crypto_volatility_factor,
        recession_probability=data.recession_probability,
    )
    
    return assumptions.to_dict()
