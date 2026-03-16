"""Executive Council Engine - BB-CORE-022

Main orchestration for the Executive Council Intelligence Engine.
"""

from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.core.executive_council.council_models import (
    Domain,
    DomainRecommendation,
    CouncilCycleResult,
    CouncilState,
)

from app.core.executive_council.recommendation_aggregator import (
    RecommendationAggregator,
    get_recommendation_aggregator,
)
from app.core.executive_council.priority_resolution_engine import (
    PriorityResolutionEngine,
    get_priority_resolution_engine,
)
from app.core.executive_council.conflict_resolution_engine import (
    ConflictResolutionEngine,
    get_conflict_resolution_engine,
)
from app.core.executive_council.strategic_alignment_engine import (
    StrategicAlignmentEngine,
    get_strategic_alignment_engine,
)
from app.core.executive_council.executive_brief_generator import (
    ExecutiveBriefGenerator,
    get_executive_brief_generator,
)

logger = logging.getLogger(__name__)


class ExecutiveCouncilEngine:
    """Orchestrates the full Executive Council decision process."""
    
    def __init__(self):
        self.aggregator = get_recommendation_aggregator()
        self.priority_engine = get_priority_resolution_engine()
        self.conflict_engine = get_conflict_resolution_engine()
        self.alignment_engine = get_strategic_alignment_engine()
        self.brief_generator = get_executive_brief_generator()
        
        self._state = CouncilState()
        self._last_result: Optional[CouncilCycleResult] = None
    
    def run_council_cycle(
        self,
        recommendations: Optional[List[DomainRecommendation]] = None,
        finance_context: Optional[Dict] = None,
    ) -> CouncilCycleResult:
        """Run a complete council decision cycle."""
        
        start_time = datetime.utcnow()
        
        # Step 1: Aggregate recommendations
        if recommendations:
            # Use provided recommendations
            domain_recs = recommendations
        else:
            # Generate demo recommendations
            domain_recs = self.aggregator.generate_demo_recommendations()
        
        # Update state
        self._state.pending_recommendations = {}
        for rec in domain_recs:
            if rec.domain not in self._state.pending_recommendations:
                self._state.pending_recommendations[rec.domain] = []
            self._state.pending_recommendations[rec.domain].append(rec)
        
        # Step 2: Resolve priorities
        ranked = self.priority_engine.resolve_priorities(domain_recs)
        
        # Step 3: Detect and resolve conflicts
        conflicts = self.conflict_engine.detect_conflicts(domain_recs)
        resolved_conflicts = self.conflict_engine.resolve_conflicts(conflicts, ranked)
        
        # Step 4: Evaluate strategic alignment
        alignment_scores = self.alignment_engine.evaluate_alignment(domain_recs)
        
        # Step 5: Generate executive brief
        result = self.brief_generator.generate_brief(
            ranked=ranked,
            conflicts=resolved_conflicts,
            alignment_scores=alignment_scores,
            finance_context=finance_context,
        )
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.cycle_duration_ms = duration
        
        # Update state
        self._state.is_active = True
        self._state.last_cycle = datetime.utcnow()
        self._last_result = result
        
        logger.info(f"Council cycle complete: {duration:.1f}ms, {len(ranked)} recommendations processed")
        
        return result
    
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
        """Add a recommendation to the council."""
        
        return self.aggregator.add_recommendation(
            domain=domain,
            title=title,
            description=description,
            action_items=action_items,
            priority=priority,
            confidence=confidence,
            signals=signals,
        )
    
    def get_state(self) -> CouncilState:
        """Get current council state."""
        return self._state
    
    def get_last_result(self) -> Optional[CouncilCycleResult]:
        """Get last council cycle result."""
        return self._last_result
    
    def format_brief_text(
        self,
        result: Optional[CouncilCycleResult] = None,
        finance_context: Optional[Dict] = None,
    ) -> str:
        """Format the executive brief as readable text."""
        
        if result is None:
            result = self._last_result
        
        if result is None:
            return "No brief available. Run council cycle first."
        
        return self.brief_generator.format_brief_text(result, finance_context)
    
    def get_recommendations_by_domain(self, domain: Domain) -> List[DomainRecommendation]:
        """Get recommendations for a specific domain."""
        return self.aggregator.get_by_domain(domain)
    
    def clear_recommendations(self) -> None:
        """Clear all pending recommendations."""
        self.aggregator.clear()
        self._state.pending_recommendations = {}


# Global instance
_council_engine: Optional[ExecutiveCouncilEngine] = None


def get_executive_council_engine() -> ExecutiveCouncilEngine:
    """Get the executive council engine."""
    global _council_engine
    
    if _council_engine is None:
        _council_engine = ExecutiveCouncilEngine()
    
    return _council_engine
