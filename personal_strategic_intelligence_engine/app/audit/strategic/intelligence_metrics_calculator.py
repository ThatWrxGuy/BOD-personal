"""Intelligence Metrics Calculator.

Computes strategic intelligence metrics from audit data.
"""
from typing import Any, Dict, List

from app.audit.strategic.audit_models import (
    AuditSummary,
    CycleAuditRecord,
    DecisionRecord,
    GovernanceOutcome,
    LearningUpdate,
    PatternInsight,
    StrategicBehaviorScore,
    StrategicIntelligenceMetrics,
    TimeHorizon,
)


class IntelligenceMetricsCalculator:
    """Calculates strategic intelligence metrics."""
    
    def __init__(self):
        pass
    
    def calculate_metrics(
        self,
        cycles: List[CycleAuditRecord],
    ) -> StrategicIntelligenceMetrics:
        """Calculate all intelligence metrics."""
        
        # Calculate SSAR
        ssar = self._calculate_ssar(cycles)
        
        # Calculate SCS
        scs = self._calculate_scs(cycles)
        
        # Calculate SISR
        sisr = self._calculate_sisr(cycles)
        
        # Calculate decision quality scores
        coherence = self._calculate_coherence_score(cycles)
        justification = self._calculate_justification_score(cycles)
        proportional = self._calculate_proportional_response(cycles)
        domain_balance = self._calculate_domain_balance(cycles)
        execution_discipline = self._calculate_execution_discipline(cycles)
        
        # Calculate decision load
        avg_daily, weekly_load, saturation = self._calculate_decision_load(cycles)
        
        # Calculate drift
        drift_events, drift_severity = self._calculate_drift(cycles)
        
        return StrategicIntelligenceMetrics(
            ssar=ssar,
            ssar_rating=self._rate_ssar(ssar),
            scs=scs,
            scs_rating=self._rate_scs(scs),
            sisr=sisr,
            sisr_rating=self._rate_sisr(sisr),
            strategic_coherence_score=coherence,
            signal_justification_score=justification,
            proportional_response_score=proportional,
            domain_balance_score=domain_balance,
            execution_discipline_score=execution_discipline,
            avg_decisions_per_day=avg_daily,
            weekly_decision_load=weekly_load,
            recommendation_saturation_events=saturation,
            decision_load_classification=self._classify_load(avg_daily),
            drift_events=drift_events,
            drift_severity=drift_severity,
        )
    
    def _calculate_ssar(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Signal-to-Action Ratio."""
        
        total_signals = sum(len(c.signals_observed) for c in cycles)
        total_decisions = sum(len(c.decisions) for c in cycles)
        
        if total_signals == 0:
            return 0.0
        
        return total_decisions / total_signals
    
    def _rate_ssar(self, ssar: float) -> str:
        """Rate SSAR."""
        if ssar < 0.05:
            return "low"
        elif ssar <= 0.25:
            return "optimal"
        else:
            return "high"
    
    def _calculate_scs(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Strategic Consistency Score."""
        
        # Group decisions by time horizon
        horizon_decisions = {h: [] for h in TimeHorizon}
        
        for cycle in cycles:
            horizon_decisions[cycle.time_horizon].extend(cycle.decisions)
        
        # Simple consistency: check if higher horizon decisions align with lower
        # For now, use a heuristic based on domain consistency
        if not horizon_decisions[TimeHorizon.DAILY]:
            return 0.5
        
        # Check domain overlap between horizons
        daily_domains = set()
        for d in horizon_decisions[TimeHorizon.DAILY]:
            daily_domains.update(d.domains)
        
        yearly_domains = set()
        for d in horizon_decisions[TimeHorizon.YEARLY]:
            yearly_domains.update(d.domains)
        
        if not daily_domains:
            return 0.5
        
        # Calculate overlap
        overlap = len(daily_domains & yearly_domains) / len(daily_domains)
        
        return min(1.0, overlap + 0.5)  # Baseline 0.5
    
    def _rate_scs(self, scs: float) -> str:
        """Rate SCS."""
        if scs < 0.6:
            return "low"
        elif scs < 0.85:
            return "moderate"
        else:
            return "high"
    
    def _calculate_sisr(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Strategic Intervention Success Rate."""
        
        # Count successful outcomes
        successful = 0
        total = 0
        
        for cycle in cycles:
            for decision in cycle.decisions:
                if decision.outcome in ["improvement", "stabilization"]:
                    successful += 1
                if decision.outcome:
                    total += 1
        
        # If no outcomes recorded, estimate based on governance approval
        if total == 0:
            total_governance = sum(len(c.governance_outcomes) for c in cycles)
            approved = sum(
                sum(1 for g in c.governance_outcomes if g.approved)
                for c in cycles
            )
            return approved / total_governance if total_governance > 0 else 0.5
        
        return successful / total
    
    def _rate_sisr(self, sisr: float) -> str:
        """Rate SISR."""
        if sisr < 0.5:
            return "low"
        elif sisr < 0.7:
            return "moderate"
        else:
            return "high"
    
    def _calculate_coherence_score(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Strategic Coherence Score."""
        
        # Similar to SCS but for all horizons
        horizon_domains = {}
        
        for cycle in cycles:
            horizon = cycle.time_horizon
            if horizon not in horizon_domains:
                horizon_domains[horizon] = set()
            
            for decision in cycle.decisions:
                horizon_domains[horizon].update(decision.domains)
        
        if len(horizon_domains) < 2:
            return 0.8
        
        # Calculate average overlap between consecutive horizons
        overlaps = []
        horizons = sorted(horizon_domains.keys(), key=lambda h: h.value)
        
        for i in range(len(horizons) - 1):
            h1, h2 = horizons[i], horizons[i + 1]
            d1, d2 = horizon_domains[h1], horizon_domains[h2]
            
            if d1:
                overlap = len(d1 & d2) / len(d1)
                overlaps.append(overlap)
        
        return sum(overlaps) / len(overlaps) if overlaps else 0.5
    
    def _calculate_justification_score(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Signal Justification Score."""
        
        # Check if decisions have triggered_by signals
        total_decisions = 0
        justified = 0
        
        for cycle in cycles:
            for decision in cycle.decisions:
                total_decisions += 1
                if decision.triggered_by:
                    justified += 1
        
        return justified / total_decisions if total_decisions > 0 else 0.5
    
    def _calculate_proportional_response(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Proportional Response Score."""
        
        # Check if decision count matches signal severity
        # Simple heuristic: high severity signals -> more decisions
        
        total_responses = 0
        proportional = 0
        
        for cycle in cycles:
            signals = cycle.signals_observed
            decisions = len(cycle.decisions)
            
            if not signals:
                continue
            
            # Calculate average signal severity
            avg_severity = sum(abs(s.value) for s in signals) / len(signals)
            
            # Expected decisions based on severity
            expected = avg_severity * 5  # rough heuristic
            
            # Check proportionality
            if expected > 0:
                ratio = min(decisions, expected) / max(decisions, expected)
                proportional += ratio
                total_responses += 1
        
        return proportional / total_responses if total_responses > 0 else 0.5
    
    def _calculate_domain_balance(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Domain Balance Score."""
        
        # Count decisions per domain
        domain_counts = {}
        
        for cycle in cycles:
            for decision in cycle.decisions:
                for domain in decision.domains:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        if not domain_counts:
            return 0.5
        
        # Calculate balance (lower variance = higher balance)
        values = list(domain_counts.values())
        avg = sum(values) / len(values)
        
        if avg == 0:
            return 0.5
        
        # Coefficient of variation
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / avg
        
        # Convert to score (low CV = high balance)
        return max(0, 1 - cv)
    
    def _calculate_execution_discipline(
        self,
        cycles: List[CycleAuditRecord],
    ) -> float:
        """Calculate Execution Discipline Score."""
        
        # Check governance approval rates
        approved = 0
        total = 0
        
        for cycle in cycles:
            for outcome in cycle.governance_outcomes:
                total += 1
                if outcome.approved:
                    approved += 1
        
        # Also check policy compliance
        policy_passed = sum(
            sum(1 for o in c.governance_outcomes if o.policy_passed)
            for c in cycles
        )
        
        if total == 0:
            return 0.5
        
        approval_rate = approved / total
        
        # Higher approval = better discipline
        return approval_rate
    
    def _calculate_decision_load(
        self,
        cycles: List[CycleAuditRecord],
    ) -> tuple:
        """Calculate decision load metrics."""
        
        # Average decisions per day
        daily_cycles = [c for c in cycles if c.time_horizon == TimeHorizon.DAILY]
        
        if not daily_cycles:
            return 0.0, 0.0, 0
        
        total_decisions = sum(len(c.decisions) for c in daily_cycles)
        days = len(daily_cycles)
        
        avg_daily = total_decisions / days if days > 0 else 0
        
        # Weekly load (sum of weekly cycle decisions)
        weekly_cycles = [c for c in cycles if c.time_horizon == TimeHorizon.WEEKLY]
        weekly_load = sum(len(c.decisions) for c in weekly_cycles) / len(weekly_cycles) if weekly_cycles else 0
        
        # Saturation events (days with > 5 decisions)
        saturation = sum(1 for c in daily_cycles if len(c.decisions) > 5)
        
        return avg_daily, weekly_load, saturation
    
    def _classify_load(self, avg_daily: float) -> str:
        """Classify decision load."""
        if avg_daily < 2:
            return "low"
        elif avg_daily < 5:
            return "moderate"
        else:
            return "high"
    
    def _calculate_drift(
        self,
        cycles: List[CycleAuditRecord],
    ) -> tuple:
        """Calculate strategic drift."""
        
        # Detect when lower horizon decisions contradict higher
        drift_count = 0
        
        # Group by time horizon
        horizon_domains = {}
        
        for cycle in cycles:
            horizon = cycle.time_horizon
            if horizon not in horizon_domains:
                horizon_domains[horizon] = set()
            
            for decision in cycle.decisions:
                horizon_domains[horizon].update(decision.domains)
        
        # Check for drift
        daily = horizon_domains.get(TimeHorizon.DAILY, set())
        yearly = horizon_domains.get(TimeHorizon.YEARLY, set())
        
        if daily and yearly:
            # If daily domains are completely different from yearly
            if not daily & yearly:
                drift_count = 1
        
        severity = "none" if drift_count == 0 else "low"
        
        return drift_count, severity
    
    def calculate_behavior_score(
        self,
        metrics: StrategicIntelligenceMetrics,
    ) -> StrategicBehaviorScore:
        """Calculate overall strategic behavior score."""
        
        # Component scores
        signal_quality = metrics.ssar
        decision_coherence = metrics.strategic_coherence_score
        intervention_success = metrics.sisr
        governance = metrics.execution_discipline_score
        
        # Learning adaptation (estimated from metrics)
        learning_adaptation = 0.7  # Placeholder
        
        # Calculate overall
        overall = (
            signal_quality * 0.2 +
            decision_coherence * 0.25 +
            intervention_success * 0.25 +
            governance * 0.2 +
            learning_adaptation * 0.1
        ) * 100
        
        # Determine grade
        if overall >= 90:
            grade = "A"
        elif overall >= 80:
            grade = "B"
        elif overall >= 70:
            grade = "C"
        elif overall >= 60:
            grade = "D"
        else:
            grade = "F"
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if metrics.ssar_rating == "optimal":
            strengths.append("Optimal signal-to-action ratio")
        elif metrics.ssar_rating == "high":
            weaknesses.append("Too many decisions relative to signals")
        
        if metrics.scs_rating == "high":
            strengths.append("Strong strategic consistency")
        elif metrics.scs_rating == "low":
            weaknesses.append("Low strategic consistency across time horizons")
        
        if metrics.sisr_rating == "high":
            strengths.append("Effective intervention success rate")
        
        if metrics.decision_load_classification == "low":
            strengths.append("Manageable decision load")
        elif metrics.decision_load_classification == "high":
            weaknesses.append("High decision load may cause fatigue")
        
        return StrategicBehaviorScore(
            overall_score=overall,
            score_grade=grade,
            signal_interpretation_quality=signal_quality,
            decision_coherence=decision_coherence,
            intervention_success=intervention_success,
            governance_discipline=governance,
            learning_adaptation=learning_adaptation,
            assessment=self._generate_assessment(grade),
            strengths=strengths,
            weaknesses=weaknesses,
        )
    
    def _generate_assessment(self, grade: str) -> str:
        """Generate assessment text."""
        
        assessments = {
            "A": "Excellent strategic behavior. The system demonstrates sophisticated decision-making aligned with long-term goals.",
            "B": "Good strategic behavior. The system shows reasonable coherence with minor areas for improvement.",
            "C": "Adequate strategic behavior. The system makes reasonable decisions but could benefit from improved consistency.",
            "D": "Below average strategic behavior. Significant inconsistencies detected between time horizons.",
            "F": "Poor strategic behavior. The system demonstrates weak strategic reasoning and low coherence.",
        }
        
        return assessments.get(grade, "Unknown grade.")


def create_intelligence_metrics_calculator() -> IntelligenceMetricsCalculator:
    """Create an intelligence metrics calculator."""
    return IntelligenceMetricsCalculator()
