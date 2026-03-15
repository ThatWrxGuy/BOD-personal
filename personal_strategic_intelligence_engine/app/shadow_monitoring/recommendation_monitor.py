"""Recommendation monitor for tracking recommendation patterns over time.

Monitors recommendation frequency, domains, urgency, and detects spam or underproduction.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict

from app.shadow_monitoring.monitoring_models import (
    MonitoringWindow,
    RecommendationActivitySummary,
    ShadowCycleRecord,
)


class RecommendationMonitor:
    """Monitor for tracking recommendation patterns."""
    
    def __init__(self):
        """Initialize recommendation monitor."""
        self.recommendation_history: List[Dict[str, Any]] = []
        self.domain_counts: Dict[str, int] = defaultdict(int)
        self.urgency_counts: Dict[str, int] = defaultdict(int)
        self.repeated_recommendations: Dict[str, int] = defaultdict(int)
    
    def record_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        cycle_number: int,
    ) -> None:
        """Record recommendations from a cycle."""
        for rec in recommendations:
            rec_id = rec.get("recommendation_id", "unknown")
            domain = rec.get("domain", "unknown")
            urgency = rec.get("priority", "normal")
            
            # Track counts
            self.domain_counts[domain] += 1
            self.urgency_counts[urgency] += 1
            
            # Track repeated recommendations
            self.repeated_recommendations[rec_id] += 1
            
            # Store history
            self.recommendation_history.append({
                "recommendation_id": rec_id,
                "domain": domain,
                "urgency": urgency,
                "cycle_number": cycle_number,
                "timestamp": datetime.utcnow(),
            })
        
        # Trim history if too large
        if len(self.recommendation_history) > 10000:
            self.recommendation_history = self.recommendation_history[-5000:]
    
    def get_summary(
        self,
        cycles: List[ShadowCycleRecord],
    ) -> RecommendationActivitySummary:
        """Get recommendation activity summary."""
        if not cycles:
            return RecommendationActivitySummary()
        
        total_recs = sum(c.recommendations_generated for c in cycles)
        
        # Aggregate by domain
        domain_counts: Dict[str, int] = defaultdict(int)
        urgency_counts: Dict[str, int] = defaultdict(int)
        
        for cycle in cycles:
            for domain, count in cycle.recommendations_by_domain.items():
                domain_counts[domain] += count
            for urgency, count in cycle.recommendations_by_urgency.items():
                urgency_counts[urgency] += count
        
        # Calculate repeated rate
        repeated_count = sum(
            1 for rec in self.recommendation_history[-1000:]
            if self.repeated_recommendations.get(rec["recommendation_id"], 0) > 1
        )
        
        repeated_rate = repeated_count / max(1, len(self.recommendation_history[-1000:]))
        
        # Calculate average per cycle
        avg_per_cycle = total_recs / len(cycles)
        
        # Determine trend
        if len(cycles) >= 10:
            first_half = sum(c.recommendations_generated for c in cycles[:len(cycles)//2])
            second_half = sum(c.recommendations_generated for c in cycles[len(cycles)//2:])
            
            if second_half > first_half * 1.2:
                trend = "increasing"
                trend_magnitude = (second_half - first_half) / max(1, first_half)
            elif second_half < first_half * 0.8:
                trend = "decreasing"
                trend_magnitude = (first_half - second_half) / max(1, first_half)
            else:
                trend = "stable"
                trend_magnitude = 0.0
        else:
            trend = "stable"
            trend_magnitude = 0.0
        
        return RecommendationActivitySummary(
            total_recommendations=total_recs,
            recommendations_by_domain=dict(domain_counts),
            recommendations_by_urgency=dict(urgency_counts),
            avg_recommendations_per_cycle=avg_per_cycle,
            repeated_recommendation_rate=repeated_rate,
            trend_direction=trend,
            trend_magnitude=trend_magnitude,
        )
    
    def detect_spam(self, threshold: int = 20) -> Optional[Dict[str, Any]]:
        """Detect recommendation spam (too many recommendations)."""
        recent = self.recommendation_history[-100:]
        
        if len(recent) >= threshold:
            return {
                "detected": True,
                "count": len(recent),
                "threshold": threshold,
                "domains": list(set(r["domain"] for r in recent)),
            }
        
        return {"detected": False}
    
    def detect_underproduction(self, min_expected: int = 1) -> Optional[Dict[str, Any]]:
        """Detect recommendation underproduction."""
        recent = self.recommendation_history[-50:]
        
        if len(recent) < min_expected * 10:  # 10 cycles
            return {
                "detected": True,
                "count": len(recent),
                "min_expected": min_expected * 10,
            }
        
        return {"detected": False}
    
    def get_domain_distribution(self) -> Dict[str, float]:
        """Get domain distribution of recommendations."""
        if not self.recommendation_history:
            return {}
        
        total = len(self.recommendation_history)
        domain_counts: Dict[str, int] = defaultdict(int)
        
        for rec in self.recommendation_history:
            domain_counts[rec["domain"]] += 1
        
        return {
            domain: count / total
            for domain, count in domain_counts.items()
        }
    
    def reset(self) -> None:
        """Reset monitor state."""
        self.recommendation_history = []
        self.domain_counts = defaultdict(int)
        self.urgency_counts = defaultdict(int)
        self.repeated_recommendations = defaultdict(int)


def create_recommendation_monitor() -> RecommendationMonitor:
    """Factory function to create a recommendation monitor."""
    return RecommendationMonitor()
