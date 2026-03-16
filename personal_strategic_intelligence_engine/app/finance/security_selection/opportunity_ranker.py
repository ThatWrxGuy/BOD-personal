"""Opportunity Ranker.

This module ranks scored securities by attractiveness.
"""
from typing import Optional

from app.finance.security_selection.selection_models import (
    ConvictionLevel,
    RankedOpportunity,
    SecurityCategory,
    SecurityScore,
)


class OpportunityRanker:
    """Ranks securities by attractiveness."""
    
    # Score thresholds for conviction levels
    CONVICTION_THRESHOLDS = {
        ConvictionLevel.EXCEPTIONAL: 85.0,
        ConvictionLevel.HIGH: 70.0,
        ConvictionLevel.MODERATE: 50.0,
        ConvictionLevel.LOW: 0.0,
    }
    
    def __init__(self):
        """Initialize the ranker."""
        pass
    
    def rank(
        self,
        scores: list[SecurityScore],
        category: Optional[SecurityCategory] = None,
    ) -> list[RankedOpportunity]:
        """Rank securities by score.
        
        Args:
            scores: List of security scores
            category: Optional category filter
            
        Returns:
            Ranked opportunities
        """
        # Filter by category if specified
        if category:
            scores = [s for s in scores if s.category == category]
        
        # Sort by total score descending
        sorted_scores = sorted(scores, key=lambda s: s.total_score, reverse=True)
        
        # Create ranked opportunities
        opportunities = []
        for rank, score in enumerate(sorted_scores, 1):
            opportunity = self._create_opportunity(rank, score)
            opportunities.append(opportunity)
        
        return opportunities
    
    def rank_top_n(
        self,
        scores: list[SecurityScore],
        n: int = 10,
        category: Optional[SecurityCategory] = None,
    ) -> list[RankedOpportunity]:
        """Rank and return top N securities.
        
        Args:
            scores: List of security scores
            n: Number to return
            category: Optional category filter
            
        Returns:
            Top N ranked opportunities
        """
        ranked = self.rank(scores, category)
        return ranked[:n]
    
    def get_top_investment(self, scores: list[SecurityScore]) -> Optional[RankedOpportunity]:
        """Get top investment opportunity.
        
        Args:
            scores: List of security scores
            
        Returns:
            Top investment opportunity
        """
        investment_scores = [
            s for s in scores 
            if s.category in [SecurityCategory.INVESTMENT, SecurityCategory.CORE]
        ]
        
        if not investment_scores:
            return None
        
        ranked = self.rank(investment_scores)
        return ranked[0] if ranked else None
    
    def get_top_tactical(self, scores: list[SecurityScore]) -> Optional[RankedOpportunity]:
        """Get top tactical opportunity.
        
        Args:
            scores: List of security scores
            
        Returns:
            Top tactical opportunity
        """
        tactical_scores = [
            s for s in scores 
            if s.category == SecurityCategory.TACTICAL
        ]
        
        if not tactical_scores:
            return None
        
        ranked = self.rank(tactical_scores)
        return ranked[0] if ranked else None
    
    def get_top_options(self, scores: list[SecurityScore]) -> Optional[RankedOpportunity]:
        """Get top options opportunity.
        
        Args:
            scores: List of security scores
            
        Returns:
            Top options opportunity
        """
        options_scores = [
            s for s in scores 
            if s.category == SecurityCategory.OPTIONS
        ]
        
        if not options_scores:
            return None
        
        ranked = self.rank(options_scores)
        return ranked[0] if ranked else None
    
    def _create_opportunity(self, rank: int, score: SecurityScore) -> RankedOpportunity:
        """Create a ranked opportunity from a score."""
        # Determine conviction
        conviction = self._determine_conviction(score.total_score)
        
        # Determine allocation bucket
        bucket = self._determine_allocation_bucket(score.category)
        
        # Generate rationale
        rationale = self._generate_rationale(score)
        
        return RankedOpportunity(
            rank=rank,
            symbol=score.symbol,
            category=score.category,
            score=score.total_score,
            conviction=conviction,
            allocation_bucket=bucket,
            score_breakdown={
                f.factor_name: f.contribution for f in score.factor_scores
            },
            rationale=rationale,
        )
    
    def _determine_conviction(self, total_score: float) -> ConvictionLevel:
        """Determine conviction level from score."""
        if total_score >= self.CONVICTION_THRESHOLDS[ConvictionLevel.EXCEPTIONAL]:
            return ConvictionLevel.EXCEPTIONAL
        elif total_score >= self.CONVICTION_THRESHOLDS[ConvictionLevel.HIGH]:
            return ConvictionLevel.HIGH
        elif total_score >= self.CONVICTION_THRESHOLDS[ConvictionLevel.MODERATE]:
            return ConvictionLevel.MODERATE
        else:
            return ConvictionLevel.LOW
    
    def _determine_allocation_bucket(self, category: SecurityCategory) -> str:
        """Determine allocation bucket from category."""
        bucket_map = {
            SecurityCategory.CORE: "Investment",
            SecurityCategory.INVESTMENT: "Investment",
            SecurityCategory.TACTICAL: "Tactical",
            SecurityCategory.INCOME: "Income",
            SecurityCategory.OPTIONS: "Tactical",
            SecurityCategory.WATCHLIST: "Stability",
        }
        return bucket_map.get(category, "Investment")
    
    def _generate_rationale(self, score: SecurityScore) -> list[str]:
        """Generate rationale from factor scores."""
        rationale = []
        
        # Check each factor
        if score.trend_quality >= 70:
            rationale.append("Strong trend quality")
        elif score.trend_quality < 40:
            rationale.append("Weak trend quality")
        
        if score.momentum >= 70:
            rationale.append("Strong momentum")
        elif score.momentum < 40:
            rationale.append("Weak momentum")
        
        if score.relative_strength >= 70:
            rationale.append("Outperforming peers")
        elif score.relative_strength < 40:
            rationale.append("Underperforming peers")
        
        if score.liquidity >= 70:
            rationale.append("High liquidity")
        elif score.liquidity < 40:
            rationale.append("Limited liquidity")
        
        if score.risk_reward >= 70:
            rationale.append("Favorable risk/reward")
        
        if not rationale:
            rationale.append("Moderate overall characteristics")
        
        return rationale


# Global instance
_ranker: Optional[OpportunityRanker] = None


def get_ranker() -> OpportunityRanker:
    """Get the global opportunity ranker."""
    global _ranker
    
    if _ranker is None:
        _ranker = OpportunityRanker()
    
    return _ranker
