"""Expense tracker for recording and categorizing expenses."""
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.finance_ops import ExpenseRecord
from app.finance_ops.finance_types import ExpenseCategory
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExpenseTracker:
    """Track and categorize expenses."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def record_expense(
        self,
        category: str,
        amount: float,
        transaction_date: date,
        merchant: Optional[str] = None,
        description: Optional[str] = None,
        is_recurring: bool = False,
        bill_id: Optional[uuid.UUID] = None,
    ) -> ExpenseRecord:
        """Record an expense."""
        
        expense = ExpenseRecord(
            category=category,
            amount=amount,
            transaction_date=transaction_date,
            merchant=merchant,
            description=description,
            is_recurring=is_recurring,
            bill_id=bill_id,
        )
        
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        
        increment("expenses_recorded", domain=MetricDomain.SYSTEM)
        
        return expense
    
    async def get_expenses(
        self,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_recurring: Optional[bool] = None,
        limit: int = 100,
    ) -> List[ExpenseRecord]:
        """Get expenses with filters."""
        
        query = select(ExpenseRecord).order_by(ExpenseRecord.transaction_date.desc()).limit(limit)
        
        if category:
            query = query.where(ExpenseRecord.category == category)
        
        if start_date:
            query = query.where(ExpenseRecord.transaction_date >= start_date)
        
        if end_date:
            query = query.where(ExpenseRecord.transaction_date <= end_date)
        
        if is_recurring is not None:
            query = query.where(ExpenseRecord.is_recurring == is_recurring)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_expense_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get expense summary by category."""
        
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        expenses = await self.get_expenses(start_date=start_date, end_date=end_date, limit=1000)
        
        # Group by category
        by_category = {}
        total = 0.0
        
        for expense in expenses:
            cat = expense.category
            if cat not in by_category:
                by_category[cat] = {"count": 0, "total": 0.0}
            
            by_category[cat]["count"] += 1
            by_category[cat]["total"] += expense.amount
            total += expense.amount
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_expenses": total,
            "by_category": by_category,
            "expense_count": len(expenses),
            "average_expense": total / len(expenses) if expenses else 0,
        }
    
    async def get_monthly_totals(
        self,
        months: int = 6,
    ) -> List[Dict[str, Any]]:
        """Get monthly expense totals."""
        
        monthly_totals = []
        
        for i in range(months):
            # Calculate month range
            today = date.today()
            month_start = date(today.year, today.month - i, 1) if today.month > i else date(today.year - 1, 12 + today.month - i, 1)
            
            if today.month - i <= 0:
                month_end = date(today.year, today.month - i + 12, 1) - timedelta(days=1)
            else:
                next_month = date(today.year, today.month - i + 1, 1) if today.month - i + 1 <= 12 else date(today.year + 1, 1, 1)
                month_end = next_month - timedelta(days=1)
            
            summary = await self.get_expense_summary(start_date=month_start, end_date=month_end)
            
            monthly_totals.append({
                "month": month_start.strftime("%Y-%m"),
                "total": summary["total_expenses"],
                "count": summary["expense_count"],
            })
        
        return monthly_totals
    
    async def get_recurring_expenses(self) -> List[ExpenseRecord]:
        """Get all recurring expenses."""
        
        result = await self.session.execute(
            select(ExpenseRecord)
            .where(ExpenseRecord.is_recurring == True)
            .order_by(ExpenseRecord.category)
        )
        
        return list(result.scalars().all())
    
    async def get_expense_count(self) -> int:
        """Get total expense count."""
        
        result = await self.session.execute(
            select(func.count(ExpenseRecord.id))
        )
        
        return result.scalar() or 0


async def get_expense_tracker(session: AsyncSession) -> ExpenseTracker:
    """Get expense tracker instance."""
    return ExpenseTracker(session)
