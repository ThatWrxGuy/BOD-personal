"""Conflict Resolution Engine - BB-CORE-022

Resolves conflicts between domain recommendations.
"""

from datetime import datetime
from typing import List, Dict, Optional, Set
import logging

from app.core.executive_council.council_models import (
    Domain,
    DomainRecommendation,
    RankedRecommendation,
    Conflict,
)

logger = logging.getLogger(__name__)


class ConflictResolutionEngine:
    """Resolves conflicts between domain recommendations."""
    
    def __init__(self):
        # Define conflicting domain pairs
        self._conflict_patterns = {
            (Domain.FINANCE, Domain.HEALTH): {
                "pattern": "intense_focus_vs_rest",
                "resolution": "prioritize_health",
                "reason": "Health is foundational - without it, other achievements are diminished",
            },
            (Domain.CAREER, Domain.HEALTH): {
                "pattern": "workload_vs_recovery",
                "resolution": "prioritize_health",
                "reason": "Chronic health neglect leads to burnout and reduced productivity",
            },
            (Domain.CAREER, Domain.LIFESTYLE): {
                "pattern": "work_vs_recovery",
                "resolution": "balance_with_boundaries",
                "reason": "Sustainable productivity requires lifestyle balance",
            },
            (Domain.FINANCE, Domain.LIFESTYLE): {
                "pattern": "aggressive_vs_enjoyment",
                "resolution": "balance_investment",
                "reason": "Financial security should enhance, not replace, life enjoyment",
            },
            (Domain.FINANCE, Domain.RELATIONSHIPS): {
                "pattern": "work_vs_connection",
                "resolution": "schedule_quality_time",
                "reason": "Relationships require intentional time investment",
            },
            (Domain.CAREER, Domain.RELATIONSHIPS): {
                "pattern": "work_vs_connection",
                "resolution": "protect_relationship_time",
                "reason": "Neglected relationships degrade over time",
            },
        }
        
        self._resolved_conflicts: List[Conflict] = []
    
    def detect_conflicts(
        self,
        recommendations: List[DomainRecommendation],
    ) -> List[Conflict]:
        """Detect conflicts between recommendations."""
        
        conflicts = []
        
        # Check each pair of recommendations
        for i, rec_a in enumerate(recommendations):
            for rec_b in recommendations[i + 1:]:
                conflict = self._check_pair(rec_a, rec_b)
                if conflict:
                    conflicts.append(conflict)
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        
        return conflicts
    
    def _check_pair(
        self,
        rec_a: DomainRecommendation,
        rec_b: DomainRecommendation,
    ) -> Optional[Conflict]:
        """Check if two recommendations conflict."""
        
        # Get conflict pattern
        pattern = self._conflict_patterns.get((rec_a.domain, rec_b.domain))
        if not pattern:
            pattern = self._conflict_patterns.get((rec_b.domain, rec_a.domain))
        
        if not pattern:
            return None
        
        # Check if recommendations actually conflict
        if self._is_conflicting(rec_a, rec_b, pattern["pattern"]):
            conflict = Conflict(
                conflict_id=f"conf_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(self._resolved_conflicts)}",
                timestamp=datetime.utcnow(),
                domain_a=rec_a.domain,
                domain_b=rec_b.domain,
                recommendation_a=rec_a.title,
                recommendation_b=rec_b.title,
                description=f"Conflict between {rec_a.domain.value} and {rec_b.domain.value}",
            )
            
            return conflict
        
        return None
    
    def _is_conflicting(
        self,
        rec_a: DomainRecommendation,
        rec_b: DomainRecommendation,
        pattern: str,
    ) -> bool:
        """Determine if recommendations actually conflict based on pattern."""
        
        # Keywords that indicate conflicting focus
        intense_keywords = ["aggressive", "intense", "maximum", "full", "deploy", "expand"]
        rest_keywords = ["rest", "recovery", "sleep", "reduce", "limit", "relax"]
        
        text_a = (rec_a.title + " " + rec_a.description).lower()
        text_b = (rec_b.title + " " + rec_b.description).lower()
        
        if pattern == "intense_focus_vs_rest":
            # Check if one recommends intensity and other recommends rest
            a_intense = any(kw in text_a for kw in intense_keywords)
            b_intense = any(kw in text_b for kw in intense_keywords)
            a_rest = any(kw in text_a for kw in rest_keywords)
            b_rest = any(kw in text_b for kw in rest_keywords)
            
            return (a_intense and b_rest) or (b_intense and a_rest)
        
        if pattern == "workload_vs_recovery":
            # Check if career recommends more work and health recommends rest
            a_career = rec_a.domain == Domain.CAREER
            b_career = rec_b.domain == Domain.CAREER
            a_health = rec_a.domain == Domain.HEALTH
            b_health = rec_b.domain == Domain.HEALTH
            
            if a_career and b_health:
                return "increase" in text_a and ("rest" in text_b or "sleep" in text_b)
            if b_career and a_health:
                return "increase" in text_b and ("rest" in text_a or "sleep" in text_a)
        
        if pattern == "work_vs_recovery":
            a_career = rec_a.domain == Domain.CAREER
            b_lifestyle = rec_b.domain == Domain.LIFESTYLE
            
            return a_career or b_lifestyle  # General potential conflict
        
        return False
    
    def resolve_conflicts(
        self,
        conflicts: List[Conflict],
        ranked: List[RankedRecommendation],
    ) -> List[Conflict]:
        """Resolve detected conflicts."""
        
        for conflict in conflicts:
            resolution = self._resolve_single_conflict(conflict, ranked)
            conflict.resolved = True
            conflict.resolution = resolution["action"]
            conflict.resolution_reason = resolution["reason"]
            
            self._resolved_conflicts.append(conflict)
        
        logger.info(f"Resolved {len(conflicts)} conflicts")
        
        return conflicts
    
    def _resolve_single_conflict(
        self,
        conflict: Conflict,
        ranked: List[RankedRecommendation],
    ) -> Dict:
        """Resolve a single conflict."""
        
        # Get priority scores for both domains
        domain_a_score = self._get_domain_score(ranked, conflict.domain_a)
        domain_b_score = self._get_domain_score(ranked, conflict.domain_b)
        
        # Get conflict pattern
        pattern = self._conflict_patterns.get((conflict.domain_a, conflict.domain_b))
        if not pattern:
            pattern = self._conflict_patterns.get((conflict.domain_b, conflict.domain_a))
        
        if not pattern:
            # Default: use priority scores
            if domain_a_score >= domain_b_score:
                return {
                    "action": f"Prioritize {conflict.domain_a.value}",
                    "reason": "Higher strategic priority",
                }
            else:
                return {
                    "action": f"Prioritize {conflict.domain_b.value}",
                    "reason": "Higher strategic priority",
                }
        
        # Use pattern-based resolution
        resolution = pattern["resolution"]
        
        if resolution == "prioritize_health":
            # Health always wins
            return {
                "action": f"Prioritize {conflict.domain_b.value if conflict.domain_a != Domain.HEALTH else conflict.domain_a.value}",
                "reason": pattern["reason"],
            }
        
        if resolution == "balance_with_boundaries":
            return {
                "action": "Implement balanced schedule with clear boundaries",
                "reason": pattern["reason"],
            }
        
        if resolution == "balance_investment":
            return {
                "action": "Maintain balanced investment approach",
                "reason": pattern["reason"],
            }
        
        if resolution == "schedule_quality_time":
            return {
                "action": "Schedule dedicated quality time",
                "reason": pattern["reason"],
            }
        
        if resolution == "protect_relationship_time":
            return {
                "action": "Protect dedicated relationship time",
                "reason": pattern["reason"],
            }
        
        return {
            "action": "Review and balance priorities",
            "reason": "General conflict resolution",
        }
    
    def _get_domain_score(
        self,
        ranked: List[RankedRecommendation],
        domain: Domain,
    ) -> float:
        """Get priority score for a domain from ranked recommendations."""
        
        for r in ranked:
            if r.recommendation.domain == domain:
                return r.priority_score
        
        return 0.0
    
    def get_unresolved_conflicts(self) -> List[Conflict]:
        """Get unresolved conflicts."""
        return [c for c in self._resolved_conflicts if not c.resolved]
    
    def get_resolved_conflicts(self) -> List[Conflict]:
        """Get resolved conflicts."""
        return [c for c in self._resolved_conflicts if c.resolved]


_conflict_engine: Optional[ConflictResolutionEngine] = None


def get_conflict_resolution_engine() -> ConflictResolutionEngine:
    """Get the conflict resolution engine."""
    global _conflict_engine
    
    if _conflict_engine is None:
        _conflict_engine = ConflictResolutionEngine()
    
    return _conflict_engine
