"""Recommendation Aggregator - BB-CORE-022

Collects and normalizes recommendations from all domains.
"""

from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.core.executive_council.council_models import (
    Domain,
    ChiefOfficer,
    DomainRecommendation,
    RecommendationSignal,
    RecommendationStatus,
    DOMAIN_TO_OFFICER,
)

logger = logging.getLogger(__name__)


class RecommendationAggregator:
    """Aggregates recommendations from all Chief Officers."""
    
    def __init__(self):
        self._recommendations: List[DomainRecommendation] = []
    
    def add_recommendation(
        self,
        domain: Domain,
        title: str,
        description: str,
        action_items: Optional[List[str]] = None,
        priority: str = "medium",
        confidence: float = 0.5,
        signals: Optional[List[Dict]] = None,
    ) -> DomainRecommendation:
        """Add a recommendation from a domain."""
        
        # Get chief officer for domain
        chief_officer = DOMAIN_TO_OFFICER.get(domain)
        
        # Convert signals
        recommendation_signals = []
        if signals:
            for sig in signals:
                recommendation_signals.append(RecommendationSignal(
                    source=sig.get("source", ""),
                    signal_type=sig.get("type", ""),
                    description=sig.get("description", ""),
                    strength=sig.get("strength", 0.5),
                ))
        
        # Calculate importance score
        importance = self._calculate_importance(priority, confidence, len(recommendation_signals))
        
        # Create recommendation
        recommendation = DomainRecommendation(
            recommendation_id=f"rec_{domain.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.utcnow(),
            domain=domain,
            chief_officer=chief_officer or ChiefOfficer.CFO,
            title=title,
            description=description,
            action_items=action_items or [],
            priority=priority,
            confidence=confidence,
            importance_score=importance,
            signals=recommendation_signals,
            status=RecommendationStatus.PENDING,
        )
        
        self._recommendations.append(recommendation)
        
        logger.info(f"Added recommendation: {title} from {domain.value}")
        
        return recommendation
    
    def _calculate_importance(
        self,
        priority: str,
        confidence: float,
        num_signals: int,
    ) -> float:
        """Calculate importance score (0-1)."""
        
        # Priority weight
        priority_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25,
        }
        
        priority_score = priority_weights.get(priority.lower(), 0.5)
        
        # Confidence weight
        confidence_score = confidence
        
        # Signal diversity weight (more signals = higher confidence)
        signal_score = min(1.0, num_signals / 5.0)
        
        # Combined score
        importance = (priority_score * 0.5) + (confidence_score * 0.35) + (signal_score * 0.15)
        
        return importance
    
    def aggregate(
        self,
        include_domains: Optional[List[Domain]] = None,
    ) -> List[DomainRecommendation]:
        """Aggregate all recommendations."""
        
        if include_domains:
            filtered = [r for r in self._recommendations if r.domain in include_domains]
            return filtered
        
        return self._recommendations
    
    def get_by_domain(self, domain: Domain) -> List[DomainRecommendation]:
        """Get recommendations for a specific domain."""
        return [r for r in self._recommendations if r.domain == domain]
    
    def get_pending(self) -> List[DomainRecommendation]:
        """Get all pending recommendations."""
        return [r for r in self._recommendations if r.status == RecommendationStatus.PENDING]
    
    def get_by_priority(self, priority: str) -> List[DomainRecommendation]:
        """Get recommendations by priority level."""
        return [r for r in self._recommendations if r.priority.value == priority]
    
    def clear(self) -> None:
        """Clear all recommendations."""
        self._recommendations.clear()
    
    def generate_demo_recommendations(self) -> List[DomainRecommendation]:
        """Generate demo recommendations for all domains."""
        
        recommendations = []
        
        # Finance recommendations
        recommendations.append(self.add_recommendation(
            domain=Domain.FINANCE,
            title="Deploy Selective Capital",
            description="Deploy capital selectively in high momentum securities during favorable regime",
            action_items=["Review top ranked opportunities", "Allocate 3% to momentum strategy", "Set stop losses"],
            priority="high",
            confidence=0.82,
            signals=[
                {"source": "regime_engine", "type": "trend_signal", "description": "Risk-On regime detected", "strength": 0.85},
                {"source": "strategy_lab", "type": "opportunity_signal", "description": "Top strategy Sharpe > 1.0", "strength": 0.78},
            ],
        ))
        
        # Health recommendations
        recommendations.append(self.add_recommendation(
            domain=Domain.HEALTH,
            title="Increase Sleep Duration",
            description="Increase nightly sleep by 1 hour to address accumulated sleep debt",
            action_items=["Set bedtime to 10:30 PM", "Limit evening screen time", "Track sleep quality"],
            priority="high",
            confidence=0.91,
            signals=[
                {"source": "health_tracker", "type": "deficit", "description": "Sleep debt > 5 hours", "strength": 0.9},
                {"source": "productivity_data", "type": "impact", "description": "Cognitive performance declining", "strength": 0.75},
            ],
        ))
        
        # Career recommendations
        recommendations.append(self.add_recommendation(
            domain=Domain.CAREER,
            title="Begin AI Engineering Course",
            description="Start advanced AI engineering program to maintain competitive edge",
            action_items=["Research available courses", "Set learning schedule", "Allocate 5 hours weekly"],
            priority="medium",
            confidence=0.78,
            signals=[
                {"source": "market_analysis", "type": "skill_demand", "description": "AI skills in high demand", "strength": 0.88},
                {"source": "career_trajectory", "type": "growth", "description": "Aligns with 5-year plan", "strength": 0.72},
            ],
        ))
        
        # Lifestyle recommendations
        recommendations.append(self.add_recommendation(
            domain=Domain.LIFESTYLE,
            title="Schedule Outdoor Recovery Day",
            description="Plan full day outdoors for mental recovery and stress management",
            action_items=["Block Saturday for outdoor activity", "Choose nature location", "Disconnect from work"],
            priority="medium",
            confidence=0.85,
            signals=[
                {"source": "stress_indicators", "type": "elevation", "description": "Cortisol levels elevated", "strength": 0.7},
                {"source": "lifestyle_balance", "type": "deficit", "description": "Outdoor time below target", "strength": 0.8},
            ],
        ))
        
        # Intelligence recommendations
        recommendations.append(self.add_recommendation(
            domain=Domain.INTELLIGENCE,
            title="Expand Knowledge Base",
            description="Read research papers on emerging financial technologies",
            action_items=["Subscribe to top journals", "Set weekly reading goal", "Take notes"],
            priority="low",
            confidence=0.65,
            signals=[
                {"source": "research_tracker", "type": "opportunity", "description": "New methodologies available", "strength": 0.6},
            ],
        ))
        
        # Relationships recommendations
        recommendations.append(self.add_recommendation(
            domain=Domain.RELATIONSHIPS,
            title="Schedule Quality Time",
            description="Plan dedicated time for meaningful relationship connections",
            action_items=["Contact close friends", "Plan weekend activity", "Limit phone during meals"],
            priority="medium",
            confidence=0.72,
            signals=[
                {"source": "social_indicators", "type": "isolation", "description": "Social interactions below baseline", "strength": 0.65},
            ],
        ))
        
        return recommendations


_aggregator: Optional[RecommendationAggregator] = None


def get_recommendation_aggregator() -> RecommendationAggregator:
    """Get the recommendation aggregator."""
    global _aggregator
    
    if _aggregator is None:
        _aggregator = RecommendationAggregator()
    
    return _aggregator
