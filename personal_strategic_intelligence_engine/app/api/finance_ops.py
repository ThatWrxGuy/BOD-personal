"""Financial operations API routes."""
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.finance_ops.bill_registry import get_bill_registry
from app.finance_ops.expense_tracker import get_expense_tracker
from app.finance_ops.cashflow_forecaster import (
    get_cashflow_forecaster,
    get_liquidity_monitor,
    get_subscription_detector,
)
from app.finance_ops.financial_operations_engine import get_financial_operations_engine
from app.models.finance_ops import Bill, SubscriptionRecord

router = APIRouter(prefix="/finance-ops", tags=["finance-ops"])


# ===================
# Bills
# ===================

@router.get("/bills")
async def list_bills(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    days_ahead: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """List bills."""
    
    registry = await get_bill_registry(session)
    bills = await registry.get_bills(status, category, days_ahead, limit)
    
    return {
        "bills": [
            {
                "id": str(b.id),
                "name": b.name,
                "category": b.category,
                "amount": b.amount,
                "due_date": b.due_date.isoformat(),
                "recurrence": b.recurrence,
                "status": b.status,
                "autopay_enabled": b.autopay_enabled,
                "priority": b.priority,
            }
            for b in bills
        ]
    }


@router.get("/bills/{bill_id}")
async def get_bill(
    bill_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get bill details."""
    
    registry = await get_bill_registry(session)
    bill = await registry.get_bill(bill_id)
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return {
        "id": str(bill.id),
        "name": bill.name,
        "category": bill.category,
        "amount": bill.amount,
        "due_date": bill.due_date.isoformat(),
        "recurrence": bill.recurrence,
        "status": bill.status,
        "autopay_enabled": bill.autopay_enabled,
        "priority": bill.priority,
        "source_account": bill.source_account,
        "notes": bill.notes,
    }


@router.post("/bills")
async def create_bill(
    name: str = Query(...),
    category: str = Query(...),
    amount: float = Query(...),
    due_date: str = Query(...),
    recurrence: str = Query("one_time"),
    autopay_enabled: bool = Query(False),
    priority: str = Query("medium"),
    source_account: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """Create a new bill."""
    
    registry = await get_bill_registry(session)
    
    bill = await registry.create_bill(
        name=name,
        category=category,
        amount=amount,
        due_date=date.fromisoformat(due_date),
        recurrence=recurrence,
        autopay_enabled=autopay_enabled,
        priority=priority,
        source_account=source_account,
        notes=notes,
    )
    
    return {
        "id": str(bill.id),
        "name": bill.name,
        "message": "Bill created",
    }


@router.post("/bills/{bill_id}/mark-paid")
async def mark_bill_paid(
    bill_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Mark a bill as paid."""
    
    registry = await get_bill_registry(session)
    
    try:
        bill = await registry.mark_paid(bill_id)
        return {"id": str(bill.id), "status": bill.status, "message": "Bill marked as paid"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===================
# Expenses
# ===================

@router.get("/expenses")
async def list_expenses(
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """List expenses."""
    
    tracker = await get_expense_tracker(session)
    
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    expenses = await tracker.get_expenses(category, start, end, limit=limit)
    
    return {
        "expenses": [
            {
                "id": str(e.id),
                "category": e.category,
                "amount": e.amount,
                "merchant": e.merchant,
                "transaction_date": e.transaction_date.isoformat(),
                "is_recurring": e.is_recurring,
            }
            for e in expenses
        ]
    }


@router.post("/expenses")
async def record_expense(
    category: str = Query(...),
    amount: float = Query(...),
    transaction_date: str = Query(...),
    merchant: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    is_recurring: bool = Query(False),
    session: AsyncSession = Depends(get_db),
):
    """Record an expense."""
    
    tracker = await get_expense_tracker(session)
    
    expense = await tracker.record_expense(
        category=category,
        amount=amount,
        transaction_date=date.fromisoformat(transaction_date),
        merchant=merchant,
        description=description,
        is_recurring=is_recurring,
    )
    
    return {
        "id": str(expense.id),
        "message": "Expense recorded",
    }


@router.get("/expenses/summary")
async def get_expense_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """Get expense summary."""
    
    tracker = await get_expense_tracker(session)
    
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    summary = await tracker.get_expense_summary(start, end)
    return summary


# ===================
# Subscriptions
# ===================

@router.get("/subscriptions")
async def list_subscriptions(
    session: AsyncSession = Depends(get_db),
):
    """List subscriptions."""
    
    from sqlalchemy import select
    
    result = await session.execute(
        select(SubscriptionRecord).where(SubscriptionRecord.is_active == True)
    )
    subscriptions = list(result.scalars().all())
    
    return {
        "subscriptions": [
            {
                "id": str(s.id),
                "name": s.name,
                "amount": s.amount,
                "billing_cycle": s.billing_cycle,
                "is_active": s.is_active,
                "is_essential": s.is_essential,
                "usage_frequency": s.usage_frequency,
            }
            for s in subscriptions
        ]
    }


@router.get("/subscriptions/summary")
async def get_subscription_summary(
    session: AsyncSession = Depends(get_db),
):
    """Get subscription summary."""
    
    detector = await get_subscription_detector(session)
    summary = await detector.get_subscription_summary()
    return summary


# ===================
# Cash Flow
# ===================

@router.get("/cashflow/forecast")
async def get_cashflow_forecast(
    time_horizon_days: int = Query(30, ge=1, le=365),
    starting_balance: Optional[float] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """Get cash flow forecast."""
    
    forecaster = await get_cashflow_forecaster(session)
    forecast = await forecaster.forecast_cashflow(time_horizon_days, starting_balance)
    return forecast


# ===================
# Liquidity
# ===================

@router.get("/liquidity")
async def get_liquidity(
    minimum_balance: float = Query(1000.0),
    session: AsyncSession = Depends(get_db),
):
    """Get liquidity status."""
    
    monitor = await get_liquidity_monitor(session)
    status = await monitor.check_liquidity(minimum_balance)
    return status


@router.get("/alerts")
async def get_alerts(
    unresolved_only: bool = Query(True),
    session: AsyncSession = Depends(get_db),
):
    """Get liquidity alerts."""
    
    monitor = await get_liquidity_monitor(session)
    alerts = await monitor.get_alerts(unresolved_only)
    
    return {
        "alerts": [
            {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "projected_date": a.projected_date.isoformat() if a.projected_date else None,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]
    }


# ===================
# Reviews
# ===================

@router.post("/run-review")
async def run_financial_review(
    time_horizon_days: int = Query(30),
    session: AsyncSession = Depends(get_db),
):
    """Run financial operations review."""
    
    engine = await get_financial_operations_engine(session)
    result = await engine.run_financial_review(time_horizon_days)
    return result
