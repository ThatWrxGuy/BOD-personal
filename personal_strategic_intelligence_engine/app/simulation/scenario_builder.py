"""Scenario Builder for creating realistic simulation scenarios."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.models.strategic_signal import SignalCategory
from app.models.strategic_goal import GoalCategory


class ScenarioBuilder:
    """Builds realistic simulation scenarios."""

    def __init__(self):
        pass

    def build_baseline_stability_scenario(self) -> dict:
        """Build a baseline stability scenario."""
        return {
            "name": "Baseline Stability",
            "description": "A stable period with minimal stressors",
            "goals": [
                {
                    "title": "Maintain Emergency Fund",
                    "category": GoalCategory.FINANCE,
                    "target_value": 20000,
                    "current_value": 18000,
                    "target_date": datetime.utcnow() + timedelta(days=60),
                    "priority": 8,
                },
                {
                    "title": "Weekly Exercise Goal",
                    "category": GoalCategory.HEALTH,
                    "target_value": 100,
                    "current_value": 75,
                    "target_date": datetime.utcnow() + timedelta(days=30),
                    "priority": 7,
                },
            ],
            "signals": self._generate_moderate_signals(7),
            "calendar_load": 0.4,
        }

    def build_stress_scenario(self) -> dict:
        """Build a high stress scenario."""
        return {
            "name": "High Stress Multi-Domain",
            "description": "Multiple concurrent stressors across domains",
            "goals": [
                {
                    "title": "Critical Project Deadline",
                    "category": GoalCategory.CAREER,
                    "target_value": 100,
                    "current_value": 60,
                    "target_date": datetime.utcnow() + timedelta(days=7),
                    "priority": 10,
                },
                {
                    "title": "Debt Payoff",
                    "category": GoalCategory.FINANCE,
                    "target_value": 10000,
                    "current_value": 8000,
                    "target_date": datetime.utcnow() + timedelta(days=14),
                    "priority": 9,
                },
            ],
            "signals": self._generate_stress_signals(14),
            "calendar_load": 0.9,
        }

    def build_recovery_scenario(self) -> dict:
        """Build a recovery scenario."""
        return {
            "name": "Recovery Scenario",
            "description": "Post-stress recovery with opportunity",
            "goals": [
                {
                    "title": "Career Transition",
                    "category": GoalCategory.CAREER,
                    "target_value": 100,
                    "current_value": 20,
                    "target_date": datetime.utcnow() + timedelta(days=90),
                    "priority": 8,
                },
            ],
            "signals": self._generate_recovery_signals(7),
            "calendar_load": 0.5,
        }

    def build_opportunity_scenario(self) -> dict:
        """Build an opportunity scenario."""
        return {
            "name": "Opportunity Scenario",
            "description": "Positive opportunities requiring strategic decision",
            "goals": [
                {
                    "title": "Investment Opportunity",
                    "category": GoalCategory.FINANCE,
                    "target_value": 50000,
                    "current_value": 30000,
                    "target_date": datetime.utcnow() + timedelta(days=180),
                    "priority": 7,
                },
            ],
            "signals": self._generate_opportunity_signals(7),
            "calendar_load": 0.6,
        }

    def build_mixed_life_pressure_scenario(self) -> dict:
        """Build the default mixed life pressure scenario."""
        return {
            "name": "Mixed Life Pressure",
            "description": "Realistic multi-domain pressure: moderate expenses, calendar fragmentation, health trend, goal deadline",
            "goals": [
                {
                    "title": "Save for Home Down Payment",
                    "category": GoalCategory.FINANCE,
                    "target_value": 80000,
                    "current_value": 52000,
                    "target_date": datetime.utcnow() + timedelta(days=45),
                    "priority": 9,
                },
                {
                    "title": "Complete Professional Certification",
                    "category": GoalCategory.CAREER,
                    "target_value": 100,
                    "current_value": 65,
                    "target_date": datetime.utcnow() + timedelta(days=21),
                    "priority": 8,
                },
                {
                    "title": "Improve Cardiovascular Health",
                    "category": GoalCategory.HEALTH,
                    "target_value": 100,
                    "current_value": 40,
                    "target_date": datetime.utcnow() + timedelta(days=90),
                    "priority": 7,
                },
            ],
            "signals": self._generate_mixed_pressure_signals(14),
            "calendar_load": 0.75,
        }

    def _generate_moderate_signals(self, days: int) -> list:
        """Generate moderate signals."""
        signals = []
        for i in range(days):
            signals.append({
                "day": i + 1,
                "category": SignalCategory.PERSONAL_FINANCE,
                "title": f"Regular expense {i+1}",
                "urgency": 3,
                "signal_strength": 3,
            })
        return signals

    def _generate_stress_signals(self, days: int) -> list:
        """Generate high stress signals."""
        signals = []
        for i in range(days):
            signals.append({
                "day": i + 1,
                "category": SignalCategory.PERSONAL_FINANCE if i % 3 == 0 else SignalCategory.CALENDAR,
                "title": f"Urgent issue {i+1}",
                "urgency": 8,
                "signal_strength": 8,
            })
        return signals

    def _generate_recovery_signals(self, days: int) -> list:
        """Generate recovery signals."""
        signals = []
        for i in range(days):
            urgency = max(2, 6 - i)
            signals.append({
                "day": i + 1,
                "category": SignalCategory.HEALTH,
                "title": f"Recovery indicator {i+1}",
                "urgency": urgency,
                "signal_strength": 5,
            })
        return signals

    def _generate_opportunity_signals(self, days: int) -> list:
        """Generate opportunity signals."""
        signals = []
        for i in range(days):
            signals.append({
                "day": i + 1,
                "category": SignalCategory.MARKET if i % 2 == 0 else SignalCategory.RESEARCH,
                "title": f"Opportunity signal {i+1}",
                "urgency": 6,
                "signal_strength": 7,
            })
        return signals

    def _generate_mixed_pressure_signals(self, days: int) -> list:
        """Generate mixed pressure signals."""
        signals = []
        
        # Financial pressure signals
        signals.append({"day": 1, "category": SignalCategory.PERSONAL_FINANCE, "title": "Unexpected car repair", "urgency": 7, "signal_strength": 7})
        signals.append({"day": 3, "category": SignalCategory.PERSONAL_FINANCE, "title": "Insurance premium due", "urgency": 6, "signal_strength": 5})
        signals.append({"day": 7, "category": SignalCategory.PERSONAL_FINANCE, "title": "Higher than expected expenses", "urgency": 5, "signal_strength": 6})
        
        # Calendar overload signals
        signals.append({"day": 2, "category": SignalCategory.CALENDAR, "title": "Back-to-back meetings all week", "urgency": 7, "signal_strength": 8})
        signals.append({"day": 5, "category": SignalCategory.CALENDAR, "title": "Multiple deadlines converging", "urgency": 8, "signal_strength": 7})
        signals.append({"day": 8, "category": SignalCategory.CALENDAR, "title": "No buffer time available", "urgency": 6, "signal_strength": 7})
        
        # Health deterioration signals
        signals.append({"day": 4, "category": SignalCategory.HEALTH, "title": "Sleep quality declining", "urgency": 6, "signal_strength": 6})
        signals.append({"day": 9, "category": SignalCategory.HEALTH, "title": "Missed workout streak", "urgency": 5, "signal_strength": 5})
        
        # Macro stress
        signals.append({"day": 6, "category": SignalCategory.MACRO, "title": "Economic uncertainty news", "urgency": 5, "signal_strength": 5})
        
        # Market opportunity
        signals.append({"day": 10, "category": SignalCategory.MARKET, "title": "Investment opportunity identified", "urgency": 6, "signal_strength": 7})
        
        return signals

    def get_scenario(self, scenario_type: str) -> dict:
        """Get a scenario by type."""
        scenarios = {
            "baseline": self.build_baseline_stability_scenario,
            "stress": self.build_stress_scenario,
            "recovery": self.build_recovery_scenario,
            "opportunity": self.build_opportunity_scenario,
            "mixed": self.build_mixed_life_pressure_scenario,
            "mixed_life_pressure": self.build_mixed_life_pressure_scenario,
        }
        
        builder = scenarios.get(scenario_type, self.build_mixed_life_pressure_scenario)
        return builder()


def get_scenario_builder() -> ScenarioBuilder:
    """Get a scenario builder instance."""
    return ScenarioBuilder()
