"""Report Builder for generating audit reports."""
from datetime import datetime
from typing import Optional

from app.simulation.audit_evaluator import AuditEvaluator
from app.simulation.metrics_collector import MetricsCollector
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportBuilder:
    """Builds the final audit report."""

    def __init__(self, evaluator: AuditEvaluator, metrics: MetricsCollector):
        self.evaluator = evaluator
        self.metrics = metrics

    def build_report(
        self,
        simulation_name: str,
        scenario_description: str,
        simulated_days: int,
    ) -> dict:
        """Build the complete audit report."""
        
        # Get evaluation results
        evaluation = self.evaluator.evaluate_all()
        summary = self.metrics.get_summary()
        
        # Generate executive summary
        overall_score = evaluation["overall_score"]
        if overall_score >= 80:
            readiness = "HIGH - System ready for expanded operations"
        elif overall_score >= 60:
            readiness = "MEDIUM - System functional with areas for improvement"
        elif overall_score >= 40:
            readiness = "LOW - Significant hardening required"
        else:
            readiness = "CRITICAL - Major redesign needed before expansion"
        
        executive_summary = f"""
System Readiness: {readiness}

Overall Score: {overall_score}/100

The Personal Strategic Intelligence Engine simulation ran for {simulated_days} days using the '{simulation_name}' scenario. 
The system demonstrated {'strong' if overall_score >= 70 else 'moderate' if overall_score >= 50 else 'limited'} operational capability across major components.

Key findings:
- {summary.get('signals_ingested', 0)} signals were processed
- {summary.get('triggers_fired', 0)} governance triggers fired
- {summary.get('meetings_executed', 0)} board meetings were executed
- {summary.get('component_failures', 0)} component failures occurred

{'The system is recommended for continued development.' if overall_score >= 60 else 'The system requires significant hardening before further expansion.'}
        """.strip()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(evaluation)
        
        # Build full report
        report = {
            "executive_summary": executive_summary,
            "system_readiness_score": overall_score,
            "component_scores": evaluation["component_scores"],
            "strengths": evaluation["strengths"],
            "weaknesses": evaluation["weaknesses"],
            "failures": evaluation["failures"],
            "recommendations": recommendations,
            "simulation_summary": {
                "name": simulation_name,
                "description": scenario_description,
                "days": simulated_days,
                "metrics": summary,
            },
            "sections": {
                "signals_and_triggers": {
                    "signals_ingested": summary.get("signals_ingested", 0),
                    "high_urgency_signals": summary.get("high_urgency_signals", 0),
                    "triggers_fired": summary.get("triggers_fired", 0),
                },
                "governance": {
                    "meetings_executed": summary.get("meetings_executed", 0),
                    "agent_responses": summary.get("agent_responses", 0),
                },
                "goals_and_plans": {
                    "goals_updated": summary.get("goals_updated", 0),
                },
                "forecasting": {
                    "forecasts_generated": summary.get("forecasts_generated", 0),
                },
            },
        }
        
        return report

    def _generate_recommendations(self, evaluation: dict) -> list:
        """Generate prioritized recommendations."""
        recommendations = []
        
        scores = evaluation.get("component_scores", {})
        
        # Priority 1: Critical components
        if scores.get("board_deliberation", 0) < 60:
            recommendations.append({
                "priority": 1,
                "component": "board_deliberation",
                "recommendation": "Strengthen board meeting execution and agent response generation",
            })
        
        if scores.get("signal_layer", 0) < 60:
            recommendations.append({
                "priority": 1,
                "component": "signal_layer",
                "recommendation": "Enhance signal ingestion and variety",
            })
        
        # Priority 2: Important components
        if scores.get("trigger_engine", 0) < 60:
            recommendations.append({
                "priority": 2,
                "component": "trigger_engine",
                "recommendation": "Expand trigger conditions and automation",
            })
        
        if scores.get("goal_plan_systems", 0) < 60:
            recommendations.append({
                "priority": 2,
                "component": "goal_plan_systems",
                "recommendation": "Improve goal progress tracking and plan analysis",
            })
        
        # Priority 3: Enhancement
        if scores.get("forecasting", 0) < 60:
            recommendations.append({
                "priority": 3,
                "component": "forecasting",
                "recommendation": "Integrate forecasting into board meeting context",
            })
        
        # General recommendations
        recommendations.append({
            "priority": 3,
            "component": "general",
            "recommendation": "Add more realistic seed data for improved simulation quality",
        })
        
        return recommendations


def get_report_builder(
    evaluator: AuditEvaluator,
    metrics: MetricsCollector,
) -> ReportBuilder:
    """Get a report builder instance."""
    return ReportBuilder(evaluator, metrics)
