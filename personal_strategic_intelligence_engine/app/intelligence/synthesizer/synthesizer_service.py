"""Synthesizer Service - Main orchestration engine for strategic intelligence."""
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.intelligence.synthesizer.insight_models import (
    StrategicIntelligenceReport,
    StrategicInsight,
    StrategicRecommendation,
    IntelligenceConflict,
    PredictionSnapshot,
)
from app.intelligence.synthesizer.signal_extractor import get_signal_extractor
from app.intelligence.synthesizer.conflict_detector import get_conflict_detector
from app.intelligence.synthesizer.insight_ranker import get_insight_ranker
from app.intelligence.synthesizer.strategy_advisor import get_strategy_advisor


class SynthesizerService:
    """Main orchestration engine for strategic intelligence synthesis."""
    
    def __init__(self):
        self.signal_extractor = get_signal_extractor()
        self.conflict_detector = get_conflict_detector()
        self.insight_ranker = get_insight_ranker()
        self.strategy_advisor = get_strategy_advisor()
        
        # History
        self.reports: List[StrategicIntelligenceReport] = []
    
    def generate_report(
        self,
        forecast_data: Optional[Dict[str, Any]] = None,
        simulation_data: Optional[Dict[str, Any]] = None,
        monte_carlo_data: Optional[Dict[str, Any]] = None,
    ) -> StrategicIntelligenceReport:
        """Generate a complete strategic intelligence report."""
        
        start_time = time.time()
        
        # Convert dict data to PredictionSnapshots
        forecast_snapshot = self._dict_to_snapshot(forecast_data, "forecast") if forecast_data else None
        sim_snapshot = self._dict_to_snapshot(simulation_data, "simulation") if simulation_data else None
        mc_snapshot = self._dict_to_snapshot(monte_carlo_data, "monte_carlo") if monte_carlo_data else None
        
        # Step 1: Extract signals
        insights = self.signal_extractor.extract_all(
            forecast_data=forecast_snapshot,
            simulation_data=sim_snapshot,
            monte_carlo_data=mc_snapshot,
        )
        
        # Step 2: Detect conflicts
        conflicts = self.conflict_detector.check_all_conflicts(
            forecast=forecast_snapshot,
            simulation=sim_snapshot,
            monte_carlo=mc_snapshot,
        )
        
        # Adjust insight confidence for conflicts
        for insight in insights:
            insight.confidence_score = self.conflict_detector.adjust_confidence_for_conflict(
                insight.confidence_score, conflicts
            )
        
        # Step 3: Rank insights
        ranked_insights = self.insight_ranker.rank_insights(insights)
        
        # Step 4: Generate recommendations
        recommendations = self.strategy_advisor.generate_recommendations(ranked_insights)
        
        # Build report
        critical_count = sum(
            1 for i in ranked_insights 
            if i.urgency.value in ["high", "critical"]
        )
        
        report = StrategicIntelligenceReport(
            report_id=str(uuid.uuid4())[:8],
            timestamp=datetime.utcnow(),
            insights=ranked_insights,
            recommendations=recommendations,
            conflicts=conflicts,
            total_insights=len(ranked_insights),
            total_recommendations=len(recommendations),
            critical_issues=critical_count,
            forecast_summary=forecast_data or {},
            simulation_summary=simulation_data or {},
            monte_carlo_summary=monte_carlo_data or {},
            engines_used=self._get_active_engines(
                forecast_data, simulation_data, monte_carlo_data
            ),
            processing_time_ms=int((time.time() - start_time) * 1000),
        )
        
        # Store report
        self.reports.append(report)
        
        return report
    
    def _dict_to_snapshot(
        self,
        data: Dict[str, Any],
        engine_name: str,
    ) -> PredictionSnapshot:
        """Convert dictionary data to PredictionSnapshot."""
        
        return PredictionSnapshot(
            engine_name=engine_name,
            timestamp=datetime.utcnow(),
            domain_predictions=data.get("domain_predictions", {}),
            risk_predictions=data.get("risk_predictions", {}),
            goal_probabilities=data.get("goal_probabilities", {}),
            strategy_rankings=data.get("strategy_rankings", {}),
            raw_data=data.get("raw_data", {}),
        )
    
    def _get_active_engines(
        self,
        forecast: Optional[Dict],
        simulation: Optional[Dict],
        monte_carlo: Optional[Dict],
    ) -> List[str]:
        """Get list of active engines."""
        
        engines = []
        
        if forecast:
            engines.append("forecast")
        if simulation:
            engines.append("simulation")
        if monte_carlo:
            engines.append("monte_carlo")
        
        return engines
    
    def get_latest_report(self) -> Optional[StrategicIntelligenceReport]:
        """Get the most recent intelligence report."""
        
        if self.reports:
            return self.reports[-1]
        return None
    
    def get_report_history(
        self,
        limit: int = 10,
    ) -> List[StrategicIntelligenceReport]:
        """Get recent intelligence reports."""
        
        return self.reports[-limit:]
    
    def get_top_insights(
        self,
        limit: int = 5,
    ) -> List[StrategicInsight]:
        """Get top insights from the latest report."""
        
        report = self.get_latest_report()
        
        if report:
            return self.insight_ranker.get_top_insights(report.insights, limit)
        
        return []
    
    def get_critical_recommendations(
        self,
    ) -> List[StrategicRecommendation]:
        """Get critical recommendations from the latest report."""
        
        report = self.get_latest_report()
        
        if report:
            return [
                r for r in report.recommendations
                if r.risk_level.value in ["high", "critical"]
            ]
        
        return []
    
    def get_conflicts(self) -> List[IntelligenceConflict]:
        """Get unresolved conflicts from the latest report."""
        
        report = self.get_latest_report()
        
        if report:
            return [c for c in report.conflicts if not c.resolved]
        
        return []


# Global service
_synthesizer: Optional[SynthesizerService] = None


def get_synthesizer_service() -> SynthesizerService:
    """Get the global synthesizer service."""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = SynthesizerService()
    return _synthesizer
