"""Results Analyzer - Evaluates how the platform behaved during simulation."""
import logging
from typing import Any

from app.simulation.simulation_types_v2 import (
    SimulationResults,
    DailySummary,
    WeeklySummary,
)

logger = logging.getLogger(__name__)


class ResultsAnalyzer:
    """Analyzes simulation results and produces scores."""
    
    def analyze(self, results: SimulationResults) -> dict[str, float]:
        """Analyze simulation results and return scores."""
        
        scores = {}
        
        # Strategic Stability Score
        scores["strategic_stability"] = self._calculate_stability(results)
        
        # Responsiveness Score
        scores["responsiveness"] = self._calculate_responsiveness(results)
        
        # Noise Sensitivity Score
        scores["noise_sensitivity"] = self._calculate_noise_sensitivity(results)
        
        # Recovery Score
        scores["recovery"] = self._calculate_recovery(results)
        
        # Domain Balance Score
        scores["domain_balance"] = self._calculate_balance(results)
        
        # Execution Quality Score
        scores["execution_quality"] = self._calculate_execution_quality(results)
        
        # Policy Compliance Score
        scores["policy_compliance"] = self._calculate_policy_compliance(results)
        
        logger.info(f"Analysis complete: {len(scores)} scores generated")
        
        return scores
    
    def _calculate_stability(self, results: SimulationResults) -> float:
        """Calculate strategic stability score."""
        
        if not results.daily_summaries:
            return 5.0
        
        # Calculate variance in domain scores over time
        domain_performance_over_time = {}
        
        for day in results.daily_summaries:
            for domain, state in day.morning_state.items():
                if domain not in domain_performance_over_time:
                    domain_performance_over_time[domain] = []
                domain_performance_over_time[domain].append(state.get("performance", 5))
        
        # Calculate average variance
        variances = []
        for domain, perfs in domain_performance_over_time.items():
            if len(perfs) > 1:
                avg = sum(perfs) / len(perfs)
                var = sum((p - avg) ** 2 for p in perfs) / len(perfs)
                variances.append(var ** 0.5)  # Standard deviation
        
        if variances:
            avg_std = sum(variances) / len(variances)
            # Lower variance = higher stability
            return max(0, min(10, 10 - avg_std))
        
        return 5.0
    
    def _calculate_responsiveness(self, results: SimulationResults) -> float:
        """Calculate responsiveness score."""
        
        if not results.daily_summaries:
            return 0.0
        
        total_shifts = sum(len(d.priority_shifts) for d in results.daily_summaries)
        days = len(results.daily_summaries)
        
        # Higher shifts per day = more responsive
        ratio = total_shifts / days
        
        return min(10, ratio * 3)
    
    def _calculate_noise_sensitivity(self, results: SimulationResults) -> float:
        """Calculate noise sensitivity score."""
        
        if not results.daily_summaries:
            return 5.0
        
        # Count how often the system reacts to minor events
        minor_events = 0
        for day in results.daily_summaries:
            for event in day.events_triggered:
                if "minor" in event.lower() or "small" in event.lower():
                    minor_events += 1
        
        days = len(results.daily_summaries)
        
        # Lower sensitivity to noise is better
        sensitivity = minor_events / days if days > 0 else 0
        
        return max(0, min(10, 10 - sensitivity * 5))
    
    def _calculate_recovery(self, results: SimulationResults) -> float:
        """Calculate recovery score."""
        
        if not results.final_domains or not results.initial_domains:
            return 5.0
        
        recovery_points = 0
        total_checked = 0
        
        for final, initial in zip(results.final_domains, results.initial_domains):
            if initial.performance_score < 4:
                total_checked += 1
                if final.performance_score > initial.performance_score:
                    recovery_points += 1
                elif final.performance_score >= 5:
                    recovery_points += 0.5  # Partial credit
        
        if total_checked > 0:
            return min(10, (recovery_points / total_checked) * 10)
        
        return 5.0
    
    def _calculate_balance(self, results: SimulationResults) -> float:
        """Calculate domain balance score."""
        
        if not results.final_domains:
            return 0.0
        
        perfs = [d.performance_score for d in results.final_domains]
        avg = sum(perfs) / len(perfs)
        
        # Calculate variance
        variance = sum((p - avg) ** 2 for p in perfs) / len(perfs)
        std_dev = variance ** 0.5
        
        # Lower std dev = better balance
        return max(0, min(10, 10 - std_dev))
    
    def _calculate_execution_quality(self, results: SimulationResults) -> float:
        """Calculate execution quality score."""
        
        if not results.daily_summaries:
            return 0.0
        
        # Based on how well events were handled
        handled_events = sum(len(d.events_triggered) for d in results.daily_summaries)
        
        # Base score on event handling
        base_score = min(10, handled_events / 2)
        
        return base_score
    
    def _calculate_policy_compliance(self, results: SimulationResults) -> float:
        """Calculate policy compliance score."""
        
        if not results.recommendations:
            return 7.0  # Default assumption
        
        # Check how many recommendations were followed
        # For simulation, we assume recommendations are tracked
        compliance = 8.0  # Placeholder
        
        return compliance
    
    def detect_patterns(self, results: SimulationResults) -> dict[str, list[str]]:
        """Detect behavior patterns."""
        
        patterns = {
            "overreaction": [],
            "underreaction": [],
            "oscillating_priorities": [],
            "domain_neglect": [],
            "strategic_drift": [],
        }
        
        if not results.daily_summaries:
            return patterns
        
        # Detect oscillating priorities
        shift_counts = [len(d.priority_shifts) for d in results.daily_summaries]
        if len(shift_counts) > 5:
            # Count consecutive days with shifts
            oscillating_days = sum(
                1 for i in range(len(shift_counts) - 1)
                if shift_counts[i] > 0 and shift_counts[i + 1] > 0
            )
            if oscillating_days > 3:
                patterns["oscillating_priorities"].append(
                    "Multiple priority changes in consecutive days"
                )
        
        # Detect domain neglect
        if results.final_domains:
            for d in results.final_domains:
                if d.performance_score < 3:
                    patterns["domain_neglect"].append(
                        f"Domain {d.domain} at critical level: {d.performance_score:.1f}"
                    )
        
        # Detect strategic drift
        if results.final_domains and results.initial_domains:
            drift = sum(
                abs(f.performance_score - i.performance_score)
                for f, i in zip(results.final_domains, results.initial_domains)
            )
            if drift > 15:
                patterns["strategic_drift"].append(
                    f"Significant strategic drift: {drift:.1f}"
                )
        
        # Detect overreaction
        for day in results.daily_summaries:
            if len(day.priority_shifts) > 2:
                patterns["overreaction"].append(
                    f"Day {day.day}: {len(day.priority_shifts)} priority shifts"
                )
        
        return patterns


def create_results_analyzer() -> ResultsAnalyzer:
    """Create a results analyzer."""
    return ResultsAnalyzer()
