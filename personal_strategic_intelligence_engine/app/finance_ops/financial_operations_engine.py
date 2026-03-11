"""Financial operations engine."""
from datetime import date
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.finance_ops.bill_registry import get_bill_registry
from app.finance_ops.expense_tracker import get_expense_tracker
from app.finance_ops.cashflow_forecaster import (
    get_cashflow_forecaster,
    get_liquidity_monitor,
    get_subscription_detector,
)
from app.orchestration.event_types import DomainEvent, EventType
from app.orchestration.event_bus import get_event_bus
from app.core.logging import get_logger

logger = get_logger(__name__)


class FinancialOperationsEngine:
    """Main financial operations engine."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def run_financial_review(
        self,
        time_horizon_days: int = 30,
    ) -> Dict[str, Any]:
        """Run a complete financial operations review."""
        
        logger.info(f"Running financial operations review for {time_horizon_days} days")
        
        # Get bill data
        bill_registry = await get_bill_registry(self.session)
        upcoming_bills = await bill_registry.get_upcoming_bills(time_horizon_days)
        overdue_bills = await bill_registry.get_overdue_bills()
        bill_stats = await bill_registry.get_bill_statistics()
        
        # Get expense data
        expense_tracker = await get_expense_tracker(self.session)
        expense_summary = await expense_tracker.get_expense_summary()
        
        # Get subscription data
        subscription_detector = await get_subscription_detector(self.session)
        subscription_summary = await subscription_detector.get_subscription_summary()
        
        # Get cash flow forecast
        cashflow_forecaster = await get_cashflow_forecaster(self.session)
        cashflow_forecast = await cashflow_forecaster.forecast_cashflow(time_horizon_days)
        
        # Get liquidity status
        liquidity_monitor = await get_liquidity_monitor(self.session)
        liquidity_status = await liquidity_monitor.check_liquidity()
        
        # Publish event
        await self._publish_event("review_completed", {
            "time_horizon_days": time_horizon_days,
            "upcoming_bills": len(upcoming_bills),
            "total_obligations": bill_stats.get("monthly_total", 0),
            "liquidity_status": liquidity_status.get("status"),
        })
        
        return {
            "bills": {
                "upcoming_count": len(upcoming_bills),
                "overdue_count": len(overdue_bills),
                "monthly_total": bill_stats.get("monthly_total", 0),
            },
            "expenses": expense_summary,
            "subscriptions": subscription_summary,
            "cashflow": {
                "starting_balance": cashflow_forecast.get("starting_balance"),
                "ending_balance": cashflow_forecast.get("ending_balance"),
                "lowest_balance_date": cashflow_forecast.get("lowest_balance_date"),
            },
            "liquidity": liquidity_status,
        }
    
    async def _publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        """Publish financial operations event."""
        
        event_bus = get_event_bus(self.session)
        
        await event_bus.publish_event(
            DomainEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={
                    "event": event_type,
                    **payload,
                },
                source_module="financial_operations_engine",
            )
        )


async def get_financial_operations_engine(session: AsyncSession) -> FinancialOperationsEngine:
    """Get financial operations engine instance."""
    return FinancialOperationsEngine(session)
