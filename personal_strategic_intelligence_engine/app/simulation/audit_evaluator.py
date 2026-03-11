"""Audit Evaluator for scoring system performance."""
import uuid
from typing import Optional

from app.simulation.metrics_collector import MetricsCollector
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditEvaluator:
    """Evaluates system performance after simulation."""

    # Weighted scoring model
    WEIGHTS = {
        "signal_layer": 0.15,
        "trigger_engine": 0.15,
        "governance_scheduler": 0.10,
        "goal_plan_systems": 0.15,
        "board_deliberation": 0.20,
        "decision_logging": 0.10,
        "forecasting": 0.10,
        "reporting": 0.05,
    }

    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics

    def evaluate_signal_layer(self) -> dict:
        """Evaluate signal layer performance."""
        m = self.metrics.get_metrics()
        
        score = 50.0  # Base
        
        if m["signals_ingested"] >= 10:
            score += 20
        elif m["signals_ingested"] >= 5:
            score += 10
        
        if m["high_urgency_signals"] >= 3:
            score += 15
        elif m["high_urgency_signals"] >= 1:
            score += 10
        
        score = min(100, score)
        
        return {
            "score": score,
            "strengths": ["Signal ingestion working", "Urgency detection functional"] if score >= 70 else [],
            "weaknesses": ["Limited signal variety", "Insufficient historical data"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_trigger_engine(self) -> dict:
        """Evaluate trigger engine performance."""
        m = self.metrics.get_metrics()
        
        score = 50.0
        
        if m["triggers_fired"] >= 1:
            score += 30
        elif m["triggers_fired"] >= 0:
            score += 15
        
        # Check for trigger failures
        trigger_failures = [e for e in m["exceptions"] if "trigger" in e.get("component", "").lower()]
        if trigger_failures:
            score -= 20
        
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "strengths": ["Trigger evaluation functional"] if score >= 70 else [],
            "weaknesses": ["Limited trigger variety", "No complex trigger conditions"] if score < 70 else [],
            "defects": [f["error"] for f in trigger_failures],
        }

    def evaluate_governance_scheduler(self) -> dict:
        """Evaluate governance scheduler."""
        m = self.metrics.get_metrics()
        
        score = 50.0
        
        # Governance depends on triggers and meetings
        if m["meetings_executed"] >= 1:
            score += 30
        elif m["meetings_executed"] >= 0:
            score += 15
        
        score = min(100, score)
        
        return {
            "score": score,
            "strengths": ["Scheduler operational"] if score >= 70 else [],
            "weaknesses": ["Limited scheduling logic"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_goal_plan_systems(self) -> dict:
        """Evaluate goal and plan systems."""
        m = self.metrics.get_metrics()
        
        score = 60.0
        
        if m["goals_updated"] >= 1:
            score += 20
        
        if m["goals_updated"] == 0:
            score -= 20
        
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "strengths": ["Goal tracking functional"] if score >= 70 else [],
            "weaknesses": ["Limited progress updates", "No plan analysis"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_board_deliberation(self) -> dict:
        """Evaluate board deliberation quality."""
        m = self.metrics.get_metrics()
        
        score = 40.0
        
        if m["meetings_executed"] >= 1:
            score += 30
        
        if m["agent_responses"] >= 3:
            score += 20
        elif m["agent_responses"] >= 1:
            score += 10
        
        score = min(100, score)
        
        return {
            "score": score,
            "strengths": ["Board meeting execution functional"] if score >= 70 else [],
            "weaknesses": ["Limited agent responses", "No synthesis generation"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_decision_logging(self) -> dict:
        """Evaluate decision logging."""
        m = self.metrics.get_metrics()
        
        score = 50.0
        
        if m["decisions_logged"] >= 1:
            score += 30
        elif m["decisions_logged"] >= 0:
            score += 15
        
        score = min(100, score)
        
        return {
            "score": score,
            "strengths": ["Decision logging functional"] if score >= 70 else [],
            "weaknesses": ["Limited decision tracking"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_forecasting(self) -> dict:
        """Evaluate forecasting layer."""
        m = self.metrics.get_metrics()
        
        score = 40.0
        
        if m["forecasts_generated"] >= 1:
            score += 30
        
        if m["forecasts_generated"] == 0:
            score -= 10
        
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "strengths": ["Forecasting engine present"] if score >= 70 else [],
            "weaknesses": ["No forecasts generated during simulation"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_reporting(self) -> dict:
        """Evaluate reporting and explainability."""
        m = self.metrics.get_metrics()
        
        score = 60.0
        
        if m["component_failures"] > 3:
            score -= 20
        
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "strengths": ["Basic reporting available"] if score >= 70 else [],
            "weaknesses": ["Limited dashboard features"] if score < 70 else [],
            "defects": [],
        }

    def evaluate_all(self) -> dict:
        """Evaluate all components and calculate overall score."""
        component_scores = {
            "signal_layer": self.evaluate_signal_layer(),
            "trigger_engine": self.evaluate_trigger_engine(),
            "governance_scheduler": self.evaluate_governance_scheduler(),
            "goal_plan_systems": self.evaluate_goal_plan_systems(),
            "board_deliberation": self.evaluate_board_deliberation(),
            "decision_logging": self.evaluate_decision_logging(),
            "forecasting": self.evaluate_forecasting(),
            "reporting": self.evaluate_reporting(),
        }
        
        # Calculate weighted overall score
        overall_score = 0.0
        for component, score_data in component_scores.items():
            weight = self.WEIGHTS.get(component, 0)
            overall_score += score_data["score"] * weight
        
        # Collect all strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        all_failures = []
        
        for component, score_data in component_scores.items():
            all_strengths.extend([f"{component}: {s}" for s in score_data.get("strengths", [])])
            all_weaknesses.extend([f"{component}: {w}" for w in score_data.get("weaknesses", [])])
            all_failures.extend([f"{component}: {f}" for f in score_data.get("defects", [])])
        
        return {
            "overall_score": round(overall_score, 1),
            "component_scores": {k: v["score"] for k, v in component_scores.items()},
            "strengths": all_strengths[:10],  # Top 10
            "weaknesses": all_weaknesses[:10],
            "failures": all_failures,
            "details": component_scores,
        }


def get_audit_evaluator(metrics: MetricsCollector) -> AuditEvaluator:
    """Get an audit evaluator instance."""
    return AuditEvaluator(metrics)
