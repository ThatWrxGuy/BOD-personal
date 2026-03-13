"""Monitoring reporter for producing structured shadow monitoring reports.

Generates comprehensive reports of shadow operation behavior.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    ApprovalBurdenSnapshot,
    ConfidenceDriftEvent,
    GovernanceLoadSnapshot,
    LongHorizonReadinessAssessment,
    MonitoringAnomaly,
    MonitoringWindow,
    MonitoringStatus,
    RecommendationActivitySummary,
    ShadowCycleRecord,
    ShadowOperationReport,
    SignalReliabilitySnapshot,
)


class MonitoringReporter:
    """Reporter for shadow monitoring results."""
    
    def __init__(self):
        """Initialize monitoring reporter."""
        pass
    
    def generate_report(
        self,
        window: MonitoringWindow,
        cycles: List[ShadowCycleRecord],
        anomalies: List[MonitoringAnomaly],
        confidence_drift_events: List[ConfidenceDriftEvent],
    ) -> ShadowOperationReport:
        """Generate a shadow operation report."""
        now = datetime.utcnow()
        
        # Calculate time window
        window_hours = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        hours = window_hours.get(window, 24)
        start_time = now - timedelta(hours=hours)
        
        # Filter cycles to window
        window_cycles = [c for c in cycles if c.timestamp >= start_time]
        
        # Calculate summary stats
        total_cycles = len(window_cycles)
        cycles_completed = sum(1 for c in window_cycles if c.cycle_duration_ms > 0)
        cycles_failed = total_cycles - cycles_completed
        
        avg_duration = (
            sum(c.cycle_duration_ms for c in window_cycles) / total_cycles
            if total_cycles > 0 else 0.0
        )
        
        signals_processed = sum(c.signals_processed for c in window_cycles)
        recommendations_generated = sum(c.recommendations_generated for c in window_cycles)
        execution_intents_generated = sum(c.execution_intents_generated for c in window_cycles)
        
        # Count anomalies by severity
        critical = sum(1 for a in anomalies if a.severity.value == "critical")
        high = sum(1 for a in anomalies if a.severity.value == "high")
        
        # Calculate health score
        health_score = self._calculate_health_score(
            total_cycles,
            len(anomalies),
            critical,
            high,
        )
        
        # Determine readiness level
        readiness = self._determine_readiness(health_score, total_cycles)
        
        return ShadowOperationReport(
            window=window,
            start_time=start_time,
            end_time=now,
            total_cycles=total_cycles,
            cycles_completed=cycles_completed,
            cycles_failed=cycles_failed,
            avg_cycle_duration_ms=avg_duration,
            signals_processed=signals_processed,
            recommendations_generated=recommendations_generated,
            execution_intents_generated=execution_intents_generated,
            recommendation_summary=self._generate_recommendation_summary(window_cycles),
            confidence_drift_events=confidence_drift_events,
            anomalies_detected=anomalies,
            critical_anomalies=critical,
            high_severity_anomalies=high,
            overall_health_score=health_score,
            readiness_level=readiness,
        )
    
    def _generate_recommendation_summary(
        self,
        cycles: List[ShadowCycleRecord],
    ) -> RecommendationActivitySummary:
        """Generate recommendation summary."""
        if not cycles:
            return RecommendationActivitySummary()
        
        total = sum(c.recommendations_generated for c in cycles)
        
        # Aggregate by domain
        domain_counts: Dict[str, int] = {}
        for cycle in cycles:
            for domain, count in cycle.recommendations_by_domain.items():
                domain_counts[domain] = domain_counts.get(domain, 0) + count
        
        return RecommendationActivitySummary(
            total_recommendations=total,
            recommendations_by_domain=domain_counts,
            avg_recommendations_per_cycle=total / len(cycles) if cycles else 0,
        )
    
    def _calculate_health_score(
        self,
        total_cycles: int,
        anomaly_count: int,
        critical_count: int,
        high_count: int,
    ) -> float:
        """Calculate overall health score."""
        score = 1.0
        
        # Penalize for no cycles
        if total_cycles == 0:
            return 0.0
        
        # Penalize for anomalies
        score -= (critical_count * 0.2)
        score -= (high_count * 0.1)
        score -= (anomaly_count * 0.02)
        
        # Penalize for low cycle count
        if total_cycles < 10:
            score *= 0.5
        elif total_cycles < 50:
            score *= 0.8
        
        return max(0.0, min(1.0, score))
    
    def _determine_readiness(self, health_score: float, total_cycles: int) -> str:
        """Determine readiness level."""
        if health_score < 0.3 or total_cycles < 10:
            return "not_ready"
        elif health_score < 0.7 or total_cycles < 50:
            return "developing"
        else:
            return "ready"
    
    def generate_readiness_assessment(
        self,
        window: MonitoringWindow,
        cycles: List[ShadowCycleRecord],
        recommendation_summary: RecommendationActivitySummary,
        governance_load: Optional[GovernanceLoadSnapshot],
        approval_burden: Optional[ApprovalBurdenSnapshot],
        signal_reliability: Optional[SignalReliabilitySnapshot],
        simulation_stability: float = 0.8,
    ) -> LongHorizonReadinessAssessment:
        """Generate long-horizon readiness assessment."""
        # Calculate component scores
        stability = self._calculate_stability_score(cycles)
        recommendation_quality = self._calculate_recommendation_quality(recommendation_summary)
        governance_efficiency = self._calculate_governance_efficiency(governance_load)
        operator_burden = self._calculate_operator_burden_score(approval_burden)
        signal_quality = self._calculate_signal_quality(signal_reliability)
        
        # Overall score (weighted)
        overall = (
            stability * 0.25 +
            recommendation_quality * 0.20 +
            governance_efficiency * 0.20 +
            operator_burden * 0.20 +
            signal_quality * 0.15
        )
        
        # Determine readiness
        if overall < 0.3:
            readiness = "not_ready"
        elif overall < 0.7:
            readiness = "developing"
        else:
            readiness = "ready"
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        recommendations = []
        
        if stability >= 0.7:
            strengths.append("Stable system behavior")
        else:
            weaknesses.append("Unstable system behavior detected")
            recommendations.append("Review governance stability")
        
        if recommendation_quality >= 0.6:
            strengths.append("Good recommendation quality")
        else:
            weaknesses.append("Recommendation quality below threshold")
            recommendations.append("Improve recommendation generation")
        
        if governance_efficiency >= 0.7:
            strengths.append("Efficient governance")
        else:
            weaknesses.append("Governance efficiency below target")
            recommendations.append("Optimize governance thresholds")
        
        if operator_burden >= 0.7:
            strengths.append("Low operator burden")
        else:
            weaknesses.append("High operator burden")
            recommendations.append("Reduce manual review requirements")
        
        if signal_quality >= 0.7:
            strengths.append("Good signal quality")
        else:
            weaknesses.append("Signal quality below threshold")
            recommendations.append("Improve signal sources")
        
        # Compare with simulation
        deviation = abs(stability - simulation_stability)
        matches_simulation = deviation < 0.2
        
        deviations = []
        if not matches_simulation:
            deviations.append(f"Real stability ({stability:.2f}) deviates from simulation ({simulation_stability:.2f})")
        
        return LongHorizonReadinessAssessment(
            window=window,
            stability_score=stability,
            recommendation_quality_score=recommendation_quality,
            governance_efficiency_score=governance_efficiency,
            operator_burden_score=operator_burden,
            signal_quality_score=signal_quality,
            overall_readiness_score=overall,
            readiness_level=readiness,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            matches_simulation_expectations=matches_simulation,
            simulation_deviations=deviations,
        )
    
    def _calculate_stability_score(self, cycles: List[ShadowCycleRecord]) -> float:
        """Calculate stability score from cycles."""
        if not cycles:
            return 0.0
        
        # Check confidence variance
        confidences = [c.confidence_score for c in cycles]
        avg = sum(confidences) / len(confidences)
        variance = sum((c - avg) ** 2 for c in confidences) / len(confidences)
        
        # Stability is inverse of variance
        return max(0.0, 1.0 - (variance * 4))
    
    def _calculate_recommendation_quality(
        self,
        summary: RecommendationActivitySummary,
    ) -> float:
        """Calculate recommendation quality score."""
        if summary.total_recommendations == 0:
            return 0.5
        
        # Penalize high repeated rate
        quality = 1.0 - summary.repeated_recommendation_rate
        
        # Penalize extreme recommendation volume
        if summary.avg_recommendations_per_cycle > 10:
            quality *= 0.7
        
        return max(0.0, min(1.0, quality))
    
    def _calculate_governance_efficiency(
        self,
        load: Optional[GovernanceLoadSnapshot],
    ) -> float:
        """Calculate governance efficiency score."""
        if not load:
            return 0.5
        
        # Inverse of load
        return 1.0 - load.avg_governance_load
    
    def _calculate_operator_burden_score(
        self,
        burden: Optional[ApprovalBurdenSnapshot],
    ) -> float:
        """Calculate operator burden score."""
        if not burden:
            return 0.5
        
        # Inverse of burden
        burden_scores = {
            "minimal": 1.0,
            "low": 0.8,
            "moderate": 0.6,
            "high": 0.3,
            "critical": 0.1,
        }
        
        return burden_scores.get(burden.burden_level, 0.5)
    
    def _calculate_signal_quality(
        self,
        reliability: Optional[SignalReliabilitySnapshot],
    ) -> float:
        """Calculate signal quality score."""
        if not reliability:
            return 0.5
        
        return reliability.overall_reliability
    
    def generate_text_report(self, report: ShadowOperationReport) -> str:
        """Generate human-readable text report."""
        lines = []
        
        lines.append("=" * 60)
        lines.append("SHADOW OPERATION MONITORING REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"Window: {report.window.value}")
        lines.append(f"Period: {report.start_time.isoformat()} to {report.end_time.isoformat()}")
        lines.append(f"Generated: {report.generated_at.isoformat()}")
        lines.append("")
        
        lines.append("-" * 40)
        lines.append("CYCLE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Cycles: {report.total_cycles}")
        lines.append(f"Completed: {report.cycles_completed}")
        lines.append(f"Failed: {report.cycles_failed}")
        lines.append(f"Avg Duration: {report.avg_cycle_duration_ms:.2f}ms")
        lines.append("")
        
        lines.append("-" * 40)
        lines.append("ACTIVITY SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Signals Processed: {report.signals_processed}")
        lines.append(f"Recommendations: {report.recommendations_generated}")
        lines.append(f"Execution Intents: {report.execution_intents_generated}")
        lines.append("")
        
        lines.append("-" * 40)
        lines.append("ANOMALIES")
        lines.append("-" * 40)
        lines.append(f"Total Anomalies: {len(report.anomalies_detected)}")
        lines.append(f"Critical: {report.critical_anomalies}")
        lines.append(f"High Severity: {report.high_severity_anomalies}")
        lines.append("")
        
        lines.append("-" * 40)
        lines.append("HEALTH & READINESS")
        lines.append("-" * 40)
        lines.append(f"Health Score: {report.overall_health_score:.2f}")
        lines.append(f"Readiness Level: {report.readiness_level}")
        lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def create_monitoring_reporter() -> MonitoringReporter:
    """Factory function to create a monitoring reporter."""
    return MonitoringReporter()
