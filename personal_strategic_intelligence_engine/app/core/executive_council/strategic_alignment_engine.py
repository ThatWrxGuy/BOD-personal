"""Strategic Alignment Engine - BB-CORE-022

Ensures recommendations align with long-term strategic goals.
"""

from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.core.executive_council.council_models import (
    Domain,
    DomainRecommendation,
    StrategicGoal,
    AlignmentScore,
)

logger = logging.getLogger(__name__)


class StrategicAlignmentEngine:
    """Evaluates alignment of recommendations with strategic goals."""
    
    def __init__(self):
        # Define default strategic goals by domain
        self._default_goals = self._initialize_goals()
    
    def _initialize_goals(self) -> Dict[Domain, List[StrategicGoal]]:
        """Initialize default strategic goals."""
        
        goals = {
            Domain.FINANCE: [
                StrategicGoal(
                    goal_id="fin_1",
                    title="Financial Security",
                    description="Build emergency fund and retirement savings",
                    domain=Domain.FINANCE,
                    progress=0.4,
                ),
                StrategicGoal(
                    goal_id="fin_2",
                    title="Passive Income",
                    description="Develop passive income streams",
                    domain=Domain.FINANCE,
                    progress=0.25,
                ),
            ],
            Domain.HEALTH: [
                StrategicGoal(
                    goal_id="health_1",
                    title="Physical Longevity",
                    description="Maintain healthy weight and exercise routine",
                    domain=Domain.HEALTH,
                    progress=0.6,
                ),
                StrategicGoal(
                    goal_id="health_2",
                    title="Mental Clarity",
                    description="Achieve consistent sleep and stress management",
                    domain=Domain.HEALTH,
                    progress=0.35,
                ),
            ],
            Domain.CAREER: [
                StrategicGoal(
                    goal_id="career_1",
                    title="Expertise Mastery",
                    description="Become recognized expert in AI/ML",
                    domain=Domain.CAREER,
                    progress=0.45,
                ),
                StrategicGoal(
                    goal_id="career_2",
                    title="Leadership Growth",
                    description="Develop management and leadership skills",
                    domain=Domain.CAREER,
                    progress=0.3,
                ),
            ],
            Domain.LIFESTYLE: [
                StrategicGoal(
                    goal_id="life_1",
                    title="Work-Life Balance",
                    description="Maintain sustainable work hours",
                    domain=Domain.LIFESTYLE,
                    progress=0.4,
                ),
                StrategicGoal(
                    goal_id="life_2",
                    title="Meaningful Experiences",
                    description="Pursue hobbies and experiences that bring joy",
                    domain=Domain.LIFESTYLE,
                    progress=0.35,
                ),
            ],
            Domain.INTELLIGENCE: [
                StrategicGoal(
                    goal_id="intel_1",
                    title="Continuous Learning",
                    description="Read and study consistently",
                    domain=Domain.INTELLIGENCE,
                    progress=0.5,
                ),
            ],
            Domain.RELATIONSHIPS: [
                StrategicGoal(
                    goal_id="rel_1",
                    title="Strong Network",
                    description="Maintain close relationships with family and friends",
                    domain=Domain.RELATIONSHIPS,
                    progress=0.55,
                ),
            ],
        }
        
        return goals
    
    def evaluate_alignment(
        self,
        recommendations: List[DomainRecommendation],
        goals: Optional[List[StrategicGoal]] = None,
    ) -> List[AlignmentScore]:
        """Evaluate alignment of recommendations with strategic goals."""
        
        # Use default goals if not provided
        if goals is None:
            goals = []
            for domain_goals in self._default_goals.values():
                goals.extend(domain_goals)
        
        # Calculate alignment scores by domain
        alignment_scores = []
        domains_seen = set()
        
        for rec in recommendations:
            if rec.domain in domains_seen:
                continue
            
            domains_seen.add(rec.domain)
            
            # Get relevant goals for this domain
            domain_goals = [g for g in goals if g.domain == rec.domain]
            
            if not domain_goals:
                # Use default goals
                domain_goals = self._default_goals.get(rec.domain, [])
            
            # Calculate alignment
            score, factors, concerns = self._calculate_alignment(rec, domain_goals)
            
            alignment_scores.append(AlignmentScore(
                domain=rec.domain,
                score=score,
                contributing_factors=factors,
                concerns=concerns,
            ))
        
        logger.info(f"Evaluated alignment for {len(alignment_scores)} domains")
        
        return alignment_scores
    
    def _calculate_alignment(
        self,
        rec: DomainRecommendation,
        goals: List[StrategicGoal],
    ) -> tuple:
        """Calculate alignment score for a recommendation against goals."""
        
        if not goals:
            return 0.5, [], ["No strategic goals defined"]
        
        contributing = []
        concerns = []
        
        # Keywords that indicate alignment
        alignment_keywords = {
            "increase": 0.1,
            "build": 0.15,
            "develop": 0.15,
            "maintain": 0.1,
            "improve": 0.15,
            "grow": 0.1,
            "expand": 0.1,
            "achieve": 0.15,
        }
        
        # Keywords that might indicate concern
        concern_keywords = {
            "reduce": -0.1,
            "decrease": -0.1,
            "limit": -0.05,
            "cut": -0.15,
            "stop": -0.2,
            "pause": -0.1,
        }
        
        text = (rec.title + " " + rec.description).lower()
        
        # Calculate alignment score
        score = 0.5  # Base score
        
        for keyword, impact in alignment_keywords.items():
            if keyword in text:
                score += impact
                contributing.append(f"'{keyword}' indicates progress toward goal")
        
        for keyword, impact in concern_keywords.items():
            if keyword in text:
                score += impact
                concerns.append(f"'{keyword}' may impact goal progress")
        
        # Adjust for goal progress (lower progress = higher need)
        avg_progress = sum(g.progress for g in goals) / len(goals)
        if avg_progress < 0.3:
            score += 0.15
            contributing.append("Low goal progress increases priority")
        elif avg_progress < 0.5:
            score += 0.05
        elif avg_progress > 0.7:
            score -= 0.1
            concerns.append("High goal progress - maintain vs. new initiatives")
        
        # Adjust for confidence
        score += (rec.confidence - 0.5) * 0.2
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        return score, contributing, concerns
    
    def get_goals_by_domain(self, domain: Domain) -> List[StrategicGoal]:
        """Get strategic goals for a specific domain."""
        return self._default_goals.get(domain, [])
    
    def update_goal_progress(self, goal_id: str, progress: float) -> None:
        """Update progress for a specific goal."""
        
        for domain_goals in self._default_goals.values():
            for goal in domain_goals:
                if goal.goal_id == goal_id:
                    goal.progress = max(0.0, min(1.0, progress))
                    logger.info(f"Updated goal {goal_id} progress to {progress:.1%}")
                    return


_alignment_engine: Optional[StrategicAlignmentEngine] = None


def get_strategic_alignment_engine() -> StrategicAlignmentEngine:
    """Get the strategic alignment engine."""
    global _alignment_engine
    
    if _alignment_engine is None:
        _alignment_engine = StrategicAlignmentEngine()
    
    return _alignment_engine
