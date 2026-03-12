"""Report Builder V2 - Generates final structured simulation report."""
import json
import logging
from datetime import datetime
from typing import Any, Optional

from app.simulation.simulation_types_v2 import (
    SimulationResults,
    SimulationReport,
    SimulationMetadata,
)
from app.simulation.results_analyzer import ResultsAnalyzer

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Builds final simulation reports."""
    
    def __init__(self):
        self.analyzer = ResultsAnalyzer()
    
    def build_report(self, results: SimulationResults) -> SimulationReport:
        """Build a complete simulation report."""
        
        # Analyze results
        analysis_scores = self.analyzer.analyze(results)
        patterns = self.analyzer.detect_patterns(results)
        
        # Build metadata
        metadata = results.metadata
        
        # Build initial conditions
        initial_conditions = {
            "personal_profile": results.initial_profile.model_dump() if results.initial_profile else {},
            "financial_state": results.initial_financial.model_dump() if results.initial_financial else {},
            "goals": [g.model_dump() for g in results.initial_goals] if results.initial_goals else [],
            "habits": [h.model_dump() for h in results.initial_habits] if results.initial_habits else [],
            "domain_states": [d.model_dump() for d in results.initial_domains] if results.initial_domains else [],
        }
        
        # Build major events
        major_events = self._extract_major_events(results)
        
        # Build system behavior
        system_behavior = self._build_system_behavior(results, patterns)
        
        # Build scorecard
        scorecard = analysis_scores
        
        # Identify weaknesses
        weaknesses = self._identify_weaknesses(analysis_scores, patterns, results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis_scores, patterns, results)
        
        # Build final state
        final_state = self._build_final_state(results)
        
        report = SimulationReport(
            metadata=metadata,
            initial_conditions=initial_conditions,
            major_events=major_events,
            system_behavior=system_behavior,
            scorecard=scorecard,
            weaknesses=weaknesses,
            recommendations=recommendations,
            final_state=final_state,
            generated_at=datetime.utcnow(),
        )
        
        logger.info(f"Simulation report built: {metadata.simulation_id}")
        
        return report
    
    def _extract_major_events(self, results: SimulationResults) -> list[dict]:
        """Extract major events from simulation."""
        
        events = []
        
        # Collect all events
        all_events = []
        for day in results.daily_summaries:
            for event_desc in day.events_triggered:
                all_events.append({
                    "day": day.day,
                    "description": event_desc,
                    "severity": self._estimate_severity(event_desc),
                })
        
        # Sort by severity
        all_events.sort(key=lambda e: e["severity"], reverse=True)
        
        # Take top events
        major_events = all_events[:20]
        
        return major_events
    
    def _estimate_severity(self, event_desc: str) -> float:
        """Estimate event severity from description."""
        
        high_keywords = ["crisis", "critical", "major", "severe", "collapse"]
        medium_keywords = ["stress", "spike", "increase", "surge"]
        
        desc_lower = event_desc.lower()
        
        if any(kw in desc_lower for kw in high_keywords):
            return 0.9
        elif any(kw in desc_lower for kw in medium_keywords):
            return 0.6
        else:
            return 0.5
    
    def _build_system_behavior(
        self, 
        results: SimulationResults,
        patterns: dict
    ) -> dict:
        """Build system behavior summary."""
        
        total_events = sum(len(d.events_triggered) for d in results.daily_summaries)
        total_shifts = sum(len(d.priority_shifts) for d in results.daily_summaries)
        
        return {
            "total_events_processed": total_events,
            "total_priority_shifts": total_shifts,
            "days_simulated": len(results.daily_summaries),
            "weeks_simulated": len(results.weekly_summaries),
            "patterns_detected": {
                "overreaction_count": len(patterns.get("overreaction", [])),
                "oscillations": len(patterns.get("oscillating_priorities", [])),
                "neglect_cases": len(patterns.get("domain_neglect", [])),
            },
        }
    
    def _identify_weaknesses(
        self,
        scores: dict,
        patterns: dict,
        results: SimulationResults
    ) -> list[str]:
        """Identify system weaknesses."""
        
        weaknesses = []
        
        if scores.get("strategic_stability", 5) < 4:
            weaknesses.append("Low strategic stability")
        
        if scores.get("domain_balance", 5) < 4:
            weaknesses.append("Significant domain imbalance")
        
        if patterns.get("oscillating_priorities"):
            weaknesses.append("Oscillating priorities detected")
        
        return weaknesses
    
    def _generate_recommendations(
        self,
        scores: dict,
        patterns: dict,
        results: SimulationResults
    ) -> list[str]:
        """Generate recommendations."""
        
        recommendations = []
        
        if scores.get("strategic_stability", 5) < 5:
            recommendations.append("Implement priority smoothing")
        
        if scores.get("domain_balance", 5) < 5:
            recommendations.append("Implement domain rebalancing")
        
        if not recommendations:
            recommendations.append("System performing within acceptable parameters")
        
        return recommendations
    
    def _build_final_state(self, results: SimulationResults) -> dict:
        """Build final state snapshot."""
        
        if not results.final_domains:
            return {}
        
        domain_summary = []
        for d in results.final_domains:
            domain_summary.append({
                "domain": d.domain,
                "performance": round(d.performance_score, 2),
                "risk": round(d.risk_score, 2),
            })
        
        return {
            "domain_summary": domain_summary,
        }
    
    def export_report_json(self, report: SimulationReport) -> str:
        """Export report as JSON."""
        return report.model_dump_json(indent=2)
    
    def export_report_dict(self, report: SimulationReport) -> dict:
        """Export report as dictionary."""
        return report.model_dump()


def create_report_builder() -> ReportBuilder:
    """Create a report builder."""
    return ReportBuilder()
