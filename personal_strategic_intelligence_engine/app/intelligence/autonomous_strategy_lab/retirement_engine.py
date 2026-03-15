"""Retirement Engine.

Retires weak, unstable, or degraded variants.
"""

from typing import List, Optional
from dataclasses import dataclass

from app.intelligence.autonomous_strategy_lab.lab_models import VariantPerformance


@dataclass
class RetirementDecision:
    """Retirement decision."""
    variant_id: str
    reason: str
    severity: str
    action: str


class RetirementEngine:
    """Retires poor performing variants."""
    
    def __init__(self):
        self.decisions = []
    
    def evaluate_retirement(
        self,
        variant_id: str,
        performance: VariantPerformance,
        historical_performance: Optional[VariantPerformance] = None,
    ) -> Optional[RetirementDecision]:
        """Evaluate whether to retire a variant."""
        
        # Check for degradation
        if historical_performance:
            expectancy_change = (performance.expectancy - historical_performance.expectancy) / abs(historical_performance.expectancy) * 100 if historical_performance.expectancy != 0 else 0
            
            if expectancy_change < -30:
                self.decisions.append(RetirementDecision(
                    variant_id=variant_id,
                    reason=f"Expectancy dropped by {abs(expectancy_change):.1f}%",
                    severity="high",
                    action="retire",
                ))
                return self.decisions[-1]
        
        # Check absolute performance
        if performance.expectancy < -10:
            self.decisions.append(RetirementDecision(
                variant_id=variant_id,
                reason="Consistently negative expectancy",
                severity="critical",
                action="retire",
            ))
            return self.decisions[-1]
        
        if performance.stability_score < 0.3:
            self.decisions.append(RetirementDecision(
                variant_id=variant_id,
                reason="Very low stability",
                severity="high",
                action="retire",
            ))
            return self.decisions[-1]
        
        if performance.drawdown > 25:
            self.decisions.append(RetirementDecision(
                variant_id=variant_id,
                reason=f"Drawdown {performance.drawdown:.1f}% exceeds limit",
                severity="high",
                action="retire",
            ))
            return self.decisions[-1]
        
        return None
    
    def get_retired_variants(self) -> List[RetirementDecision]:
        """Get list of retired variants."""
        
        return [d for d in self.decisions if d.action == "retire"]


def create_engine() -> RetirementEngine:
    """Create retirement engine."""
    return RetirementEngine()
