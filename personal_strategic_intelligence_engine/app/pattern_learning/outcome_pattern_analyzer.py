"""Outcome Pattern Analyzer.

Analyzes results across decision patterns.
"""
from typing import Any, Dict, List, Optional
from collections import defaultdict

from app.pattern_learning.pattern_models import (
    DecisionPattern,
    PatternOutcomeSummary,
    StrategyFamily,
)


class OutcomePatternAnalyzer:
    """Analyzes outcomes across decision patterns."""
    
    # Minimum sample size for reliable statistics
    MIN_SAMPLE_SIZE = 5
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 20
    MEDIUM_CONFIDENCE_THRESHOLD = 10
    
    def __init__(self):
        self._pattern_summaries: Dict[str, PatternOutcomeSummary] = {}
    
    def analyze_pattern(
        self,
        pattern: DecisionPattern,
    ) -> PatternOutcomeSummary:
        """Analyze outcomes for a single pattern."""
        
        # Count outcomes
        outcome_counts = defaultdict(int)
        total_impact = 0.0
        
        for outcome in pattern.observed_outcomes:
            outcome_counts[outcome] += 1
            
            # Estimate impact
            if outcome in ["improvement", "stabilization"]:
                total_impact += 1.0
            elif outcome == "deterioration":
                total_impact -= 1.0
        
        total = len(pattern.observed_outcomes)
        
        # Calculate rates
        improvements = outcome_counts.get("improvement", 0)
        stabilizations = outcome_counts.get("stabilization", 0)
        deteriorations = outcome_counts.get("deterioration", 0)
        
        success_count = improvements + stabilizations
        success_rate = success_count / total if total > 0 else 0.0
        failure_rate = deteriorations / total if total > 0 else 0.0
        
        # Calculate confidence
        confidence = self._calculate_confidence(total)
        
        # Calculate average impact
        avg_impact = total_impact / total if total > 0 else 0.0
        
        summary = PatternOutcomeSummary(
            pattern_id=pattern.pattern_id,
            total_decisions=total,
            improvements=improvements,
            stabilizations=stabilizations,
            deteriorations=deteriorations,
            success_rate=success_rate,
            failure_rate=failure_rate,
            avg_impact_score=avg_impact,
            confidence=confidence,
            sample_size_adequate=total >= self.MIN_SAMPLE_SIZE,
        )
        
        self._pattern_summaries[pattern.pattern_id] = summary
        
        return summary
    
    def analyze_patterns(
        self,
        patterns: List[DecisionPattern],
    ) -> Dict[str, PatternOutcomeSummary]:
        """Analyze outcomes for multiple patterns."""
        
        summaries = {}
        
        for pattern in patterns:
            summary = self.analyze_pattern(pattern)
            summaries[pattern.pattern_id] = summary
        
        return summaries
    
    def analyze_by_strategy_family(
        self,
        patterns: List[DecisionPattern],
    ) -> Dict[StrategyFamily, PatternOutcomeSummary]:
        """Analyze outcomes grouped by strategy family."""
        
        # Group patterns by family
        family_patterns = defaultdict(list)
        
        for pattern in patterns:
            family = pattern.recommendation_family
            family_patterns[family].append(pattern)
        
        # Aggregate by family
        family_summaries = {}
        
        for family, fam_patterns in family_patterns.items():
            # Aggregate statistics
            total = sum(p.total_count for p in fam_patterns)
            successes = sum(p.success_count for p in fam_patterns)
            failures = sum(p.failure_count for p in fam_patterns)
            
            success_rate = successes / total if total > 0 else 0.0
            failure_rate = failures / total if total > 0 else 0.0
            
            family_summaries[family] = PatternOutcomeSummary(
                pattern_id=f"family_{family.value}",
                total_decisions=total,
                improvements=successes,
                deteriorations=failures,
                success_rate=success_rate,
                failure_rate=failure_rate,
                confidence=self._calculate_confidence(total),
                sample_size_adequate=total >= self.MIN_SAMPLE_SIZE,
            )
        
        return family_summaries
    
    def analyze_by_cluster(
        self,
        patterns: List[DecisionPattern],
        cluster_assignments: Dict[str, str],
    ) -> Dict[str, PatternOutcomeSummary]:
        """Analyze outcomes grouped by context cluster."""
        
        # Group patterns by cluster
        cluster_patterns = defaultdict(list)
        
        for pattern in patterns:
            cluster_id = cluster_assignments.get(pattern.pattern_id)
            if cluster_id:
                cluster_patterns[cluster_id].append(pattern)
        
        # Aggregate by cluster
        cluster_summaries = {}
        
        for cluster_id, cl_patterns in cluster_patterns.items():
            total = sum(p.total_count for p in cl_patterns)
            successes = sum(p.success_count for p in cl_patterns)
            failures = sum(p.failure_count for p in cl_patterns)
            
            success_rate = successes / total if total > 0 else 0.0
            
            cluster_summaries[cluster_id] = PatternOutcomeSummary(
                pattern_id=cluster_id,
                total_decisions=total,
                improvements=successes,
                deteriorations=failures,
                success_rate=success_rate,
                confidence=self._calculate_confidence(total),
                sample_size_adequate=total >= self.MIN_SAMPLE_SIZE,
            )
        
        return cluster_summaries
    
    def identify_strong_strategies(
        self,
        patterns: List[DecisionPattern],
    ) -> List[tuple]:
        """Identify strategies with high success rates."""
        
        family_summaries = self.analyze_by_strategy_family(patterns)
        
        # Sort by success rate
        strong = [
            (family, summary.success_rate, summary.total_decisions)
            for family, summary in family_summaries.items()
            if summary.sample_size_adequate
        ]
        
        strong.sort(key=lambda x: x[1], reverse=True)
        
        return strong
    
    def identify_weak_strategies(
        self,
        patterns: List[DecisionPattern],
    ) -> List[tuple]:
        """Identify strategies with high failure rates."""
        
        family_summaries = self.analyze_by_strategy_family(patterns)
        
        # Sort by failure rate
        weak = [
            (family, summary.failure_rate, summary.total_decisions)
            for family, summary in family_summaries.items()
            if summary.sample_size_adequate
        ]
        
        weak.sort(key=lambda x: x[1], reverse=True)
        
        return weak
    
    def _calculate_confidence(self, sample_size: int) -> float:
        """Calculate confidence based on sample size."""
        
        if sample_size >= self.HIGH_CONFIDENCE_THRESHOLD:
            return 0.9
        elif sample_size >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return 0.7
        elif sample_size >= self.MIN_SAMPLE_SIZE:
            return 0.5
        else:
            return 0.3


# Global analyzer instance
_outcome_pattern_analyzer: Optional[OutcomePatternAnalyzer] = None


def get_outcome_pattern_analyzer() -> OutcomePatternAnalyzer:
    """Get the global outcome pattern analyzer instance."""
    global _outcome_pattern_analyzer
    if _outcome_pattern_analyzer is None:
        _outcome_pattern_analyzer = OutcomePatternAnalyzer()
    return _outcome_pattern_analyzer
