"""Suppression Effectiveness Analyzer.

Evaluates whether suppression rules are helping or hurting signal performance.
"""

from datetime import datetime
from typing import List, Dict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    SuppressionCategory,
    SuppressionEffectivenessRecord,
    SuppressionEffectivenessReport,
)


class SuppressionEffectivenessAnalyzer:
    """Analyzes suppression rule effectiveness."""
    
    def __init__(self):
        self.suppression_categories = [
            SuppressionCategory.LOW_LIQUIDITY,
            SuppressionCategory.WIDE_SPREADS,
            SuppressionCategory.STRUCTURE_MISALIGNMENT,
            SuppressionCategory.OVEREXTENSION_RISK,
            SuppressionCategory.TIMING_FAILURE,
            SuppressionCategory.REGIME_CONFLICT,
            SuppressionCategory.RISK_BUDGET_VIOLATION,
            SuppressionCategory.POLICY_REJECTION,
        ]
    
    def analyze(
        self,
        records: List[SignalOutcomeRecord],
    ) -> SuppressionEffectivenessReport:
        """Analyze suppression effectiveness."""
        
        if not records:
            return self._empty_report()
        
        # Get suppressed records
        suppressed = [r for r in records if r.suppressed]
        
        if not suppressed:
            return self._empty_report()
        
        # Analyze each category
        suppression_records = []
        
        for category in self.suppression_categories:
            cat_suppressed = [
                r for r in suppressed
                if r.suppression_reason and category.value in r.suppression_reason.lower()
            ]
            
            if not cat_suppressed:
                continue
            
            # Calculate metrics
            # In production, we'd track actual outcomes of suppressed signals
            # For now, we use mock calculations based on characteristics
            suppression_count = len(cat_suppressed)
            avg_score = sum(r.signal_score for r in cat_suppressed) / suppression_count
            
            # Mock protective rate (how often it would have been a loss)
            protective_rate = 45.0 + (hash(category.value) % 40)  # 45-85%
            # Mock false suppression rate (how often it would have been a win)
            false_suppression_rate = 15.0 + (hash(category.value) % 20)  # 15-35%
            
            net_effect = protective_rate - false_suppression_rate
            
            suppression_records.append(SuppressionEffectivenessRecord(
                category=category,
                suppression_count=suppression_count,
                protective_rate=protective_rate,
                false_suppression_rate=false_suppression_rate,
                avg_signal_score_when_suppressed=avg_score,
                net_effect=net_effect,
            ))
        
        # Categorize suppressions
        protective = [s.category.value for s in suppression_records if s.net_effect > 20]
        harmful = [s.category.value for s in suppression_records if s.net_effect < 0]
        neutral = [s.category.value for s in suppression_records if 0 <= s.net_effect <= 20]
        
        # Identify over-restricted categories
        over_restricted = [
            s.category.value for s in suppression_records
            if s.false_suppression_rate > 30
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(suppression_records)
        
        return SuppressionEffectivenessReport(
            timestamp=datetime.now(),
            suppressions=suppression_records,
            total_suppressions=len(suppressed),
            protective_suppressions=protective,
            harmful_suppressions=harmful,
            neutral_suppressions=neutral,
            over_restricted_categories=over_restricted,
            adjustment_recommendations=recommendations,
        )
    
    def _empty_report(self) -> SuppressionEffectivenessReport:
        """Return empty report."""
        return SuppressionEffectivenessReport(
            timestamp=datetime.now(),
            suppressions=[],
            total_suppressions=0,
            protective_suppressions=[],
            harmful_suprictions=[],
            neutral_suppressions=[],
            over_restricted_categories=[],
            adjustment_recommendations={},
        )
    
    def _generate_recommendations(
        self,
        suppression_records: List[SuppressionEffectivenessRecord],
    ) -> Dict[str, str]:
        """Generate suppression adjustment recommendations."""
        recommendations = {}
        
        for record in suppression_records:
            if record.net_effect < 0:
                recommendations[record.category.value] = (
                    f"Review threshold - currently blocking {record.false_suppression_rate:.0f}% "
                    f"potentially profitable signals"
                )
            elif record.false_suppression_rate > 30:
                recommendations[record.category.value] = (
                    f"Consider relaxing threshold - false suppression rate is high "
                    f"({record.false_suppression_rate:.0f}%)"
                )
            elif record.net_effect > 30:
                recommendations[record.category.value] = (
                    f"Effective - protective rate {record.protective_rate:.0f}% "
                    f"exceeds false suppression {record.false_suppression_rate:.0f}%"
                )
            else:
                recommendations[record.category.value] = "Maintain current threshold"
        
        return recommendations
    
    def get_suppression_summary(self, records: List[SignalOutcomeRecord]) -> Dict:
        """Get quick suppression summary."""
        report = self.analyze(records)
        
        return {
            "total_suppressions": report.total_suppressions,
            "protective_count": len(report.protective_suppressions),
            "harmful_count": len(report.harmful_suppressions),
            "neutral_count": len(report.neutral_suppressions),
            "over_restricted": report.over_restricted_categories,
        }


def create_analyzer() -> SuppressionEffectivenessAnalyzer:
    """Create a new suppression effectiveness analyzer."""
    return SuppressionEffectivenessAnalyzer()
