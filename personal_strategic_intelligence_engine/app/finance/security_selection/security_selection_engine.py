"""Security Selection Engine.

This is the main orchestration engine for security selection.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.finance.security_selection.selection_models import (
    ConvictionLevel,
    RankedOpportunity,
    ScreenResult,
    ScreeningResult,
    SecurityCategory,
    SecurityProfile,
    SecurityRecommendation,
    SelectionReport,
)


class SecuritySelectionEngine:
    """Main security selection orchestration engine."""
    
    def __init__(self):
        """Initialize the security selection engine."""
        self._universe_manager = None
        self._screener = None
        self._scoring_engine = None
        self._ranker = None
        self._conviction_engine = None
        self._recommendation_engine = None
        
    @property
    def universe_manager(self):
        """Lazy load universe manager."""
        if self._universe_manager is None:
            from app.finance.security_selection.universe_manager import get_universe_manager
            self._universe_manager = get_universe_manager()
        return self._universe_manager
    
    @property
    def screener(self):
        """Lazy load screener."""
        if self._screener is None:
            from app.finance.security_selection.security_screener import get_screener
            self._screener = get_screener()
        return self._screener
    
    @property
    def scoring_engine(self):
        """Lazy load scoring engine."""
        if self._scoring_engine is None:
            from app.finance.security_selection.factor_scoring_engine import get_scoring_engine
            self._scoring_engine = get_scoring_engine()
        return self._scoring_engine
    
    @property
    def ranker(self):
        """Lazy load ranker."""
        if self._ranker is None:
            from app.finance.security_selection.opportunity_ranker import get_ranker
            self._ranker = get_ranker()
        return self._ranker
    
    @property
    def conviction_engine(self):
        """Lazy load conviction engine."""
        if self._conviction_engine is None:
            from app.finance.security_selection.conviction_engine import get_conviction_engine
            self._conviction_engine = get_conviction_engine()
        return self._conviction_engine
    
    @property
    def recommendation_engine(self):
        """Lazy load recommendation engine."""
        if self._recommendation_engine is None:
            from app.finance.security_selection.recommendation_engine import get_recommendation_engine
            self._recommendation_engine = get_recommendation_engine()
        return self._recommendation_engine
    
    def run_selection(
        self,
        symbols: list[str],
        market_data: dict,
        categories: Optional[list[SecurityCategory]] = None,
    ) -> SelectionReport:
        """Run full security selection process.
        
        Args:
            symbols: List of symbols to analyze
            market_data: Market data for scoring
            categories: Optional category filter
            
        Returns:
            Selection report
        """
        # Step 1: Create profiles (would fetch real data in production)
        profiles = self._create_profiles(symbols)
        
        # Step 2: Screen
        passed_profiles, screen_results = self.screener.screen_batch(profiles)
        
        # Step 3: Score
        scores = self.scoring_engine.score_batch(passed_profiles, market_data)
        
        # Step 4: Rank
        ranked = self.ranker.rank_top_n(scores, n=20, category=None)
        
        # Step 5: Create recommendations
        recommendations = self.recommendation_engine.create_recommendations(ranked, market_data)
        
        # Build report
        report = SelectionReport(
            timestamp=datetime.now(),
            universe_size=len(symbols),
            screened_size=len(passed_profiles),
            ranked_opportunities=ranked,
        )
        
        # Set top picks
        report.top_investment = self.ranker.get_top_investment(scores)
        report.top_tactical = self.ranker.get_top_tactical(scores)
        
        # Calculate stats
        if ranked:
            report.average_score = sum(o.score for o in ranked) / len(ranked)
            report.high_conviction_count = sum(
                1 for o in ranked 
                if o.conviction in [ConvictionLevel.HIGH, ConvictionLevel.EXCEPTIONAL]
            )
        
        return report
    
    def get_recommendations(
        self,
        bucket: Optional[str] = None,
        min_conviction: ConvictionLevel = ConvictionLevel.MODERATE,
    ) -> list[SecurityRecommendation]:
        """Get current recommendations.
        
        Args:
            bucket: Allocation bucket filter
            min_conviction: Minimum conviction level
            
        Returns:
            Filtered recommendations
        """
        recs = self.recommendation_engine.get_top_recommendations(n=50)
        
        # Filter by conviction
        conviction_order = [
            ConvictionLevel.LOW,
            ConvictionLevel.MODERATE,
            ConvictionLevel.HIGH,
            ConvictionLevel.EXCEPTIONAL,
        ]
        min_index = conviction_order.index(min_conviction)
        
        filtered = [
            r for r in recs
            if conviction_order.index(r.conviction) >= min_index
        ]
        
        # Filter by bucket
        if bucket:
            filtered = [r for r in filtered if r.allocation_bucket == bucket]
        
        return filtered
    
    def should_activate_tactical(self) -> tuple[bool, str]:
        """Determine if SPY 0DTE agent should be activated.
        
        Returns:
            Tuple of (should_activate, reason)
        """
        report = self._last_report
        
        if not report or not report.top_tactical:
            return False, "No tactical opportunities"
        
        # Check if SPY is top tactical
        if report.top_tactical.symbol == "SPY":
            if report.top_tactical.score >= 70:
                return True, f"SPY top tactical with score {report.top_tactical.score}"
            elif report.top_tactical.score >= 50:
                return True, f"SPY qualified tactical with score {report.top_tactical.score}"
        
        return False, "SPY not top tactical candidate"
    
    def get_selection_summary(self) -> dict:
        """Get selection summary."""
        recs = self.recommendation_engine.get_top_recommendations(n=20)
        
        return {
            "total_recommendations": len(recs),
            "by_bucket": {
                bucket: len([r for r in recs if r.allocation_bucket == bucket])
                for bucket in ["Investment", "Tactical", "Income", "Stability"]
            },
            "by_conviction": {
                c.value: len([r for r in recs if r.conviction == c])
                for c in ConvictionLevel
            },
            "conviction_accuracy": self.conviction_engine.get_conviction_accuracy(),
        }
    
    def _create_profiles(self, symbols: list[str]) -> list[SecurityProfile]:
        """Create security profiles from symbols."""
        # In production, would fetch real market data
        profiles = []
        
        for symbol in symbols:
            # Determine category based on symbol
            category = self._categorize_symbol(symbol)
            
            profile = SecurityProfile(
                symbol=symbol,
                name=symbol,
                category=category,
                price=Decimal("100.00"),
                change_percent=0.5,
                volume=1_000_000,
                avg_volume=800_000,
                market_cap=100_000_000_000,
            )
            
            profiles.append(profile)
        
        return profiles
    
    def _categorize_symbol(self, symbol: str) -> SecurityCategory:
        """Categorize symbol into security category."""
        core = ["SPY", "QQQ", "DIA", "IWM", "VOO", "VTI"]
        tactical = ["SPY", "QQQ", "IWM", "TLT", "GLD", "SLV"]
        
        if symbol in core:
            return SecurityCategory.CORE
        elif symbol in tactical:
            return SecurityCategory.TACTICAL
        else:
            return SecurityCategory.INVESTMENT
    
    # Store last report
    _last_report: Optional[SelectionReport] = None


# Global instance
_selection_engine: Optional[SecuritySelectionEngine] = None


def get_security_selection_engine() -> SecuritySelectionEngine:
    """Get the global security selection engine."""
    global _selection_engine
    
    if _selection_engine is None:
        _selection_engine = SecuritySelectionEngine()
    
    return _selection_engine
