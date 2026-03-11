"""Cash flow forecaster and liquidity monitor."""
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.finance_ops.finance_types import (
    CashFlowForecast,
    LiquidityAlert,
    AccountBalance,
    AlertSeverity,
    Bill,
    BillStatus,
)
from app.finance_ops.bill_registry import get_bill_registry
from app.finance_ops.expense_tracker import get_expense_tracker
from app.observability import increment
from app.observability.metrics_service import MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)


class CashFlowForecaster:
    """Forecast cash flow."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def forecast_cashflow(
        self,
        time_horizon_days: int = 30,
        starting_balance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate cash flow forecast."""
        
        # Get current balance or use provided
        if starting_balance is None:
            starting_balance = await self._get_current_cash_balance()
        
        # Get upcoming bills
        bill_registry = await get_bill_registry(self.session)
        upcoming_bills = await bill_registry.get_upcoming_bills(time_horizon_days)
        
        # Get recent expenses for recurring pattern
        expense_tracker = await get_expense_tracker(self.session)
        
        # Calculate daily projections
        daily_projections = []
        current_balance = starting_balance
        
        for day_offset in range(time_horizon_days):
            forecast_date = date.today() + timedelta(days=day_offset)
            
            # Bills due on this day
            bills_due = [b for b in upcoming_bills if b.due_date == forecast_date]
            bills_total = sum(b.amount for b in bills_due)
            
            # Estimated daily expenses (rough estimate)
            daily_expenses = starting_balance * 0.01  # Rough 1% of balance
            
            # Update balance
            current_balance = current_balance - bills_total - daily_expenses
            
            daily_projections.append({
                "date": forecast_date.isoformat(),
                "projected_balance": round(current_balance, 2),
                "bills_due": len(bills_due),
                "bills_amount": bills_total,
            })
        
        # Find key dates
        lowest_balance_date = min(daily_projections, key=lambda x: x["projected_balance"])
        
        # Generate forecast record
        forecast = CashFlowForecast(
            forecast_date=date.today(),
            projected_balance=current_balance,
            time_horizon_days=time_horizon_days,
            projected_expenses=sum(p["bills_amount"] for p in daily_projections),
            forecast_data={"daily_projections": daily_projections},
        )
        
        self.session.add(forecast)
        await self.session.commit()
        
        increment("cashflow_forecasts_generated", domain=MetricDomain.SYSTEM)
        
        return {
            "starting_balance": starting_balance,
            "ending_balance": round(current_balance, 2),
            "time_horizon_days": time_horizon_days,
            "lowest_balance_date": lowest_balance_date,
            "daily_projections": daily_projections,
            "upcoming_bills_count": len(upcoming_bills),
            "upcoming_bills_total": sum(b.amount for b in upcoming_bills),
        }
    
    async def _get_current_cash_balance(self) -> float:
        """Get current cash balance from accounts."""
        
        result = await self.session.execute(
            select(AccountBalance)
            .where(AccountBalance.account_type.in_(["checking", "savings"]))
            .order_by(AccountBalance.as_of_date.desc())
            .limit(1)
        )
        
        account = result.scalar_one_or_none()
        
        if account:
            return account.balance
        
        # Default balance if no accounts configured
        return 0.0


class LiquidityMonitor:
    """Monitor liquidity and generate alerts."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def check_liquidity(
        self,
        minimum_balance: float = 1000.0,
    ) -> Dict[str, Any]:
        """Check liquidity status and generate alerts."""
        
        # Get current balance
        forecaster = CashFlowForecaster(self.session)
        current_balance = await forecaster._get_current_cash_balance()
        
        # Get upcoming bills
        bill_registry = await get_bill_registry(self.session)
        bills_7_days = await bill_registry.get_bills_due_soon(7)
        bills_30_days = await bill_registry.get_upcoming_bills(30)
        
        # Calculate obligations
        obligations_7 = sum(b.amount for b in bills_7_days)
        obligations_30 = sum(b.amount for b in bills_30_days)
        
        # Generate alerts
        alerts = []
        
        # Check for overdue bills
        overdue = await bill_registry.get_overdue_bills()
        if overdue:
            alert = await self._create_alert(
                alert_type="bills_overdue",
                severity=AlertSeverity.HIGH,
                message=f"{len(overdue)} bill(s) overdue - total ${sum(b.amount for b in overdue):.2f}",
            )
            alerts.append(alert)
        
        # Check for low balance
        if current_balance < minimum_balance:
            alert = await self._create_alert(
                alert_type="low_balance",
                severity=AlertSeverity.HIGH if current_balance < minimum_balance / 2 else AlertSeverity.MEDIUM,
                message=f"Current balance ${current_balance:.2f} below minimum ${minimum_balance:.2f}",
                projected_balance=current_balance,
            )
            alerts.append(alert)
        
        # Check for upcoming pressure
        if obligations_7 > current_balance * 0.5:
            alert = await self._create_alert(
                alert_type="upcoming_pressure",
                severity=AlertSeverity.MEDIUM,
                message=f"${obligations_7:.2f} due in 7 days may stress liquidity",
                projected_date=date.today() + timedelta(days=7),
            )
            alerts.append(alert)
        
        # Days of coverage
        bill_registry = await get_bill_registry(self.session)
        monthly_bills = await bill_registry.get_monthly_bill_total()
        days_of_coverage = (current_balance / monthly_bills * 30) if monthly_bills > 0 else float('inf')
        
        if days_of_coverage < 14:
            alert = await self._create_alert(
                alert_type="low_coverage",
                severity=AlertSeverity.CRITICAL,
                message=f"Only {days_of_coverage:.0f} days of bill coverage remaining",
            )
            alerts.append(alert)
        
        increment("liquidity_alerts_triggered", domain=MetricDomain.SYSTEM)
        
        return {
            "current_balance": current_balance,
            "minimum_balance": minimum_balance,
            "obligations_7_days": obligations_7,
            "obligations_30_days": obligations_30,
            "days_of_coverage": round(days_of_coverage, 1),
            "alerts": alerts,
            "status": "critical" if days_of_coverage < 14 else "warning" if days_of_coverage < 30 else "healthy",
        }
    
    async def _create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        projected_date: Optional[date] = None,
        projected_balance: Optional[float] = None,
    ) -> LiquidityAlert:
        """Create a liquidity alert."""
        
        alert = LiquidityAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            projected_date=projected_date,
            projected_balance=projected_balance,
        )
        
        self.session.add(alert)
        await self.session.commit()
        
        return alert
    
    async def get_alerts(
        self,
        unresolved_only: bool = True,
        limit: int = 50,
    ) -> List[LiquidityAlert]:
        """Get liquidity alerts."""
        
        query = select(LiquidityAlert).order_by(LiquidityAlert.created_at.desc()).limit(limit)
        
        if unresolved_only:
            query = query.where(LiquidityAlert.is_resolved == False)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SubscriptionDetector:
    """Detect and track subscriptions."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_subscription_summary(self) -> Dict[str, Any]:
        """Get subscription summary."""
        
        from app.finance_ops.finance_types import SubscriptionRecord
        
        result = await self.session.execute(
            select(SubscriptionRecord).where(SubscriptionRecord.is_active == True)
        )
        subscriptions = list(result.scalars().all())
        
        # Calculate totals
        monthly_total = 0.0
        yearly_total = 0.0
        
        for sub in subscriptions:
            if sub.billing_cycle == "monthly":
                monthly_total += sub.amount
                yearly_total += sub.amount * 12
            elif sub.billing_cycle == "yearly":
                monthly_total += sub.amount / 12
                yearly_total += sub.amount
            elif sub.billing_cycle == "weekly":
                monthly_total += sub.amount * 4
                yearly_total += sub.amount * 52
        
        # Identify potential issues
        underused = [s for s in subscriptions if s.usage_frequency == "rarely"]
        
        return {
            "total_subscriptions": len(subscriptions),
            "monthly_total": round(monthly_total, 2),
            "yearly_total": round(yearly_total, 2),
            "underused_count": len(underused),
            "subscriptions": [
                {
                    "name": s.name,
                    "amount": s.amount,
                    "billing_cycle": s.billing_cycle,
                    "is_essential": s.is_essential,
                    "usage_frequency": s.usage_frequency,
                }
                for s in subscriptions
            ],
        }


async def get_cashflow_forecaster(session: AsyncSession) -> CashFlowForecaster:
    """Get cash flow forecaster instance."""
    return CashFlowForecaster(session)


async def get_liquidity_monitor(session: AsyncSession) -> LiquidityMonitor:
    """Get liquidity monitor instance."""
    return LiquidityMonitor(session)


async def get_subscription_detector(session: AsyncSession) -> SubscriptionDetector:
    """Get subscription detector instance."""
    return SubscriptionDetector(session)
