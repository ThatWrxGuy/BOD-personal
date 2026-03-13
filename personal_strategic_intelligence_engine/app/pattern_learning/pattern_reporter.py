"""Pattern Reporter.

Generates pattern learning insight reports.
"""
from typing import Any, Dict, List, Optional

from app.pattern_learning.pattern_models import (
    ContextCluster,
    DecisionPattern,
    PatternLearningSummary,
    StrategyFamily,
)


class PatternReporter:
    """Generates pattern learning insight reports."""
    
    def __init__(self):
        pass
    
    def generate_summary(
        self,
        patterns: List[DecisionPattern],
        clusters: List[ContextCluster],
    ) -> PatternLearningSummary:
        """Generate a summary of pattern learning."""
        
        # Count
        total_patterns = len(patterns)
        total_clusters = len(clusters)
        
        # Get domains
        domains = set()
        for pattern in patterns:
            domains.update(pattern.context.domains)
        
        # Calculate average success rate
        if patterns:
            total_success = sum(p.success_count for p in patterns)
            total = sum(p.total_count for p in patterns)
            avg_success = total_success / total if total > 0 else 0.0
        else:
            avg_success = 0.0
        
        return PatternLearningSummary(
            total_patterns=total_patterns,
            total_clusters=total_clusters,
            total_families=len(StrategyFamily),
            domains_covered=list(domains),
            avg_success_rate=avg_success,
            avg_confidence=0.5,
        )
    
    def generate_cluster_report(
        self,
        clusters: List[ContextCluster],
    ) -> Dict[str, Any]:
        """Generate a report on context clusters."""
        
        return {
            "total_clusters": len(clusters),
            "clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "cluster_name": c.cluster_name,
                    "primary_domain": c.primary_domain,
                    "member_count": c.member_count,
                }
                for c in clusters
            ],
        }
    
    def generate_strategy_report(
        self,
        patterns: List[DecisionPattern],
    ) -> Dict[str, Any]:
        """Generate a report on strategy effectiveness."""
        
        # Group by strategy family
        family_stats = {}
        
        for pattern in patterns:
            family = pattern.recommendation_family
            
            if family not in family_stats:
                family_stats[family] = {
                    "total": 0,
                    "successes": 0,
                    "failures": 0,
                }
            
            family_stats[family]["total"] += pattern.total_count
            family_stats[family]["successes"] += pattern.success_count
            family_stats[family]["failures"] += pattern.failure_count
        
        # Calculate success rates
        strategies = []
        
        for family, stats in family_stats.items():
            total = stats["total"]
            successes = stats["successes"]
            
            if total > 0:
                success_rate = successes / total
            else:
                success_rate = 0.0
            
            strategies.append({
                "strategy": family.value,
                "total_attempts": total,
                "success_rate": success_rate,
                "is_reliable": total >= 10,
            })
        
        # Sort by success rate
        strategies.sort(key=lambda s: s["success_rate"], reverse=True)
        
        return {
            "total_strategies": len(strategies),
            "strategies": strategies,
            "strongest": strategies[0] if strategies else None,
            "weakest": strategies[-1] if strategies else None,
        }
    
    def generate_domain_report(
        self,
        patterns: List[DecisionPattern],
    ) -> Dict[str, Any]:
        """Generate a report on domain coverage."""
        
        domain_stats = {}
        
        for pattern in patterns:
            for domain in pattern.context.domains:
                if domain not in domain_stats:
                    domain_stats[domain] = {
                        "pattern_count": 0,
                        "success_count": 0,
                        "total_count": 0,
                    }
                
                domain_stats[domain]["pattern_count"] += 1
                domain_stats[domain]["success_count"] += pattern.success_count
                domain_stats[domain]["total_count"] += pattern.total_count
        
        # Calculate success rates
        domains = []
        
        for domain, stats in domain_stats.items():
            total = stats["total_count"]
            successes = stats["success_count"]
            
            if total > 0:
                success_rate = successes / total
            else:
                success_rate = 0.0
            
            domains.append({
                "domain": domain,
                "pattern_count": stats["pattern_count"],
                "success_rate": success_rate,
            })
        
        return {
            "total_domains": len(domains),
            "domains": domains,
        }
    
    def generate_full_report(
        self,
        patterns: List[DecisionPattern],
        clusters: List[ContextCluster],
    ) -> Dict[str, Any]:
        """Generate a comprehensive pattern learning report."""
        
        return {
            "summary": self.generate_summary(patterns, clusters).model_dump(),
            "clusters": self.generate_cluster_report(clusters),
            "strategies": self.generate_strategy_report(patterns),
            "domains": self.generate_domain_report(patterns),
        }


# Global reporter instance
_pattern_reporter: Optional[PatternReporter] = None


def get_pattern_reporter() -> PatternReporter:
    """Get the global pattern reporter instance."""
    global _pattern_reporter
    if _pattern_reporter is None:
        _pattern_reporter = PatternReporter()
    return _pattern_reporter
