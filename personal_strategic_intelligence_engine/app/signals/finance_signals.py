"""Personal finance signal collector."""
import random

from app.models.strategic_signal import SignalCategory
from app.signals.signal_base import BaseSignalCollector, SignalData


class FinanceSignalCollector(BaseSignalCollector):
    """Collects signals from personal finance data."""

    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}

    @property
    def category(self) -> str:
        return SignalCategory.PERSONAL_FINANCE

    async def collect(self) -> list[SignalData]:
        """Collect personal finance signals."""
        signals = []

        # Example: Large transaction detected
        if random.random() > 0.7:
            is_income = random.random() > 0.5
            amount = random.uniform(1000, 10000)
            signals.append(SignalData(
                source="finance_tracker",
                title=f"Large {'Income' if is_income else 'Expense'} Detected",
                description=f"A transaction of ${amount:.2f} was {'received' if is_income}.",
                raw_data={
                    "amount": amount,
                    "direction": "up" if is_income else "down",
                    "change_percent": amount / 5000 * 100,
                    "signal_strength": min(10.0, amount / 1000),
                    "urgency": 3 if is_income else 6,
                    "confidence": 0.95,
                    "type": "large_transaction",
                },
                category=self.category,
            ))

        # Example: Budget threshold alert
        if random.random() > 0.8:
            category = random.choice(["food", "transport", "entertainment", "shopping"])
            pct = random.uniform(80, 100)
            signals.append(SignalData(
                source="budget_tracker",
                title=f"Budget Threshold Alert: {category.title()}",
                description=f"You've used {pct:.0f}% of your {category} budget this month.",
                raw_data={
                    "category": category,
                    "percentage_used": pct,
                    "signal_strength": 5.0 + (pct - 80) / 4,
                    "urgency": 7 if pct > 95 else 5,
                    "confidence": 0.9,
                    "type": "budget_alert",
                },
                category=self.category,
            ))

        return signals

    def get_interval_seconds(self) -> int:
        """Collect every 6 hours."""
        return 6 * 60 * 60
