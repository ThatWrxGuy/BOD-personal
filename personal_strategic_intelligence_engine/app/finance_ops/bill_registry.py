"""Bill registry for managing bills and payments."""
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.finance_ops import Bill
from app.finance_ops.finance_types import BillStatus, RecurrenceType
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class BillRegistry:
    """Manage bills and payment tracking."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_bill(
        self,
        name: str,
        category: str,
        amount: float,
        due_date: date,
        recurrence: str = "one_time",
        autopay_enabled: bool = False,
        priority: str = "medium",
        source_account: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Bill:
        """Create a new bill."""
        
        bill = Bill(
            name=name,
            category=category,
            amount=amount,
            due_date=due_date,
            recurrence=recurrence,
            autopay_enabled=autopay_enabled,
            priority=priority,
            source_account=source_account,
            notes=notes,
        )
        
        self.session.add(bill)
        await self.session.commit()
        await self.session.refresh(bill)
        
        increment("bills_created", domain=MetricDomain.SYSTEM)
        
        logger.info(f"Created bill: {name} - ${amount} due {due_date}")
        
        return bill
    
    async def update_bill(
        self,
        bill_id: uuid.UUID,
        **kwargs,
    ) -> Bill:
        """Update a bill."""
        
        result = await self.session.execute(
            select(Bill).where(Bill.id == bill_id)
        )
        bill = result.scalar_one_or_none()
        
        if not bill:
            raise ValueError(f"Bill not found: {bill_id}")
        
        for key, value in kwargs.items():
            if hasattr(bill, key):
                setattr(bill, key, value)
        
        await self.session.commit()
        await self.session.refresh(bill)
        
        return bill
    
    async def mark_paid(
        self,
        bill_id: uuid.UUID,
    ) -> Bill:
        """Mark a bill as paid."""
        
        result = await self.session.execute(
            select(Bill).where(Bill.id == bill_id)
        )
        bill = result.scalar_one_or_none()
        
        if not bill:
            raise ValueError(f"Bill not found: {bill_id}")
        
        bill.status = BillStatus.PAID.value
        bill.paid_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(bill)
        
        increment("bills_paid", domain=MetricDomain.SYSTEM)
        
        logger.info(f"Marked bill as paid: {bill.name}")
        
        return bill
    
    async def get_bill(
        self,
        bill_id: uuid.UUID,
    ) -> Optional[Bill]:
        """Get a bill by ID."""
        
        result = await self.session.execute(
            select(Bill).where(Bill.id == bill_id)
        )
        return result.scalar_one_or_none()
    
    async def get_bills(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        days_ahead: Optional[int] = None,
        limit: int = 100,
    ) -> List[Bill]:
        """Get bills with filters."""
        
        query = select(Bill).order_by(Bill.due_date).limit(limit)
        
        if status:
            query = query.where(Bill.status == status)
        
        if category:
            query = query.where(Bill.category == category)
        
        if days_ahead is not None:
            future_date = date.today() + timedelta(days=days_ahead)
            query = query.where(Bill.due_date <= future_date)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_upcoming_bills(
        self,
        days_ahead: int = 30,
    ) -> List[Bill]:
        """Get bills due within the specified days."""
        
        return await self.get_bills(
            status=BillStatus.PENDING.value,
            days_ahead=days_ahead,
        )
    
    async def get_overdue_bills(self) -> List[Bill]:
        """Get overdue bills."""
        
        today = date.today()
        
        result = await self.session.execute(
            select(Bill)
            .where(Bill.due_date < today)
            .where(Bill.status == BillStatus.PENDING.value)
            .order_by(Bill.due_date)
        )
        
        return list(result.scalars().all())
    
    async def get_bills_due_soon(
        self,
        days_ahead: int = 7,
    ) -> List[Bill]:
        """Get bills due within specified days."""
        
        today = date.today()
        future = today + timedelta(days=days_ahead)
        
        result = await self.session.execute(
            select(Bill)
            .where(Bill.due_date >= today)
            .where(Bill.due_date <= future)
            .where(Bill.status == BillStatus.PENDING.value)
            .order_by(Bill.due_date)
        )
        
        return list(result.scalars().all())
    
    async def get_total_upcoming(
        self,
        days_ahead: int = 30,
    ) -> float:
        """Get total amount of upcoming bills."""
        
        bills = await self.get_upcoming_bills(days_ahead)
        return sum(bill.amount for bill in bills)
    
    async def get_monthly_bill_total(self) -> float:
        """Get estimated monthly bill total (normalized)."""
        
        bills = await self.get_bills(status=BillStatus.PENDING.value)
        
        monthly_total = 0.0
        
        for bill in bills:
            recurrence = bill.recurrence
            
            if recurrence == RecurrenceType.MONTHLY.value:
                monthly_total += bill.amount
            elif recurrence == RecurrenceType.YEARLY.value:
                monthly_total += bill.amount / 12
            elif recurrence == RecurrenceType.QUARTERLY.value:
                monthly_total += bill.amount / 3
            elif recurrence == RecurrenceType.BIWEEKLY.value:
                monthly_total += bill.amount * 2
            elif recurrence == RecurrenceType.WEEKLY.value:
                monthly_total += bill.amount * 4
        
        return monthly_total
    
    async def get_bill_statistics(self) -> Dict[str, Any]:
        """Get bill statistics."""
        
        all_bills = await self.get_bills(limit=1000)
        pending = [b for b in all_bills if b.status == BillStatus.PENDING.value]
        paid = [b for b in all_bills if b.status == BillStatus.PAID.value]
        overdue = await self.get_overdue_bills()
        
        # Calculate totals
        pending_total = sum(b.amount for b in pending)
        overdue_total = sum(b.amount for b in overdue)
        
        return {
            "total_bills": len(all_bills),
            "pending_count": len(pending),
            "paid_count": len(paid),
            "overdue_count": len(overdue),
            "pending_total": pending_total,
            "overdue_total": overdue_total,
            "monthly_total": await self.get_monthly_bill_total(),
        }


async def get_bill_registry(session: AsyncSession) -> BillRegistry:
    """Get bill registry instance."""
    return BillRegistry(session)
