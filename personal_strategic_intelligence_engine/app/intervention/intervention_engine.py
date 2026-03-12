"""Intervention Engine - Main engine for strategic interventions."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.intervention.intervention_types import (
    Intervention,
    InterventionPolicy,
    InterventionStatus,
    TriggerCondition,
    TriggerType,
    SystemStateSnapshot,
    DomainState,
    InterventionStatistics,
)
from app.intervention.intervention_protocols import InterventionProtocols
from app.intervention.intervention_selector import InterventionSelector
from app.intervention.intervention_executor import InterventionExecutor

logger = logging.getLogger(__name__)


class InterventionEngine:
    """Main intervention engine that detects problems and executes fixes."""
    
    def __init__(self, policy: Optional[InterventionPolicy] = None):
        self.policy = policy or InterventionPolicy()
        self.selector = InterventionSelector(self.policy)
        self.executor = InterventionExecutor()
        self.history: List[Intervention] = []
        self.trigger_conditions: Dict[str, List[TriggerCondition]] = {}
    
    def detect_triggers(
        self,
        domains: List[DomainState],
        risk_alerts: List[str],
        recent_events: List[str],
    ) -> List[TriggerCondition]:
        """Detect conditions that should trigger interventions."""
        
        triggers = []
        
        # Check for domain performance collapse
        for domain in domains:
            if domain.performance_score < 3:
                trigger = self._create_trigger(
                    TriggerType.DOMAIN_PERFORMANCE_COLLAPSE,
                    domain.name,
                    1.0 - (domain.performance_score / 3),
                )
                triggers.append(trigger)
        
        # Check for risk escalation
        for domain in domains:
            if domain.risk_score > 7:
                trigger = self._create_trigger(
                    TriggerType.RISK_ESCALATION,
                    domain.name,
                    (domain.risk_score - 7) / 3,
                )
                triggers.append(trigger)
        
        # Check for priority oscillation
        oscillation_count = self._detect_oscillation(domains)
        if oscillation_count > 10:
            for domain in domains:
                if domain.momentum_score < -2:
                    trigger = self._create_trigger(
                        TriggerType.PRIORITY_OSCILLATION,
                        domain.name,
                        0.7,
                    )
                    triggers.append(trigger)
        
        # Check for sustained imbalance
        imbalanced = self._detect_imbalance(domains)
        if imbalanced:
            for domain_name in imbalanced:
                trigger = self._create_trigger(
                    TriggerType.SUSTAINED_IMBALANCE,
                    domain_name,
                    0.6,
                )
                triggers.append(trigger)
        
        # Check for excessive alerts
        if len(risk_alerts) > 20:
            for domain in domains:
                if domain.risk_score > 5:
                    trigger = self._create_trigger(
                        TriggerType.EXCESSIVE_ALERTS,
                        domain.name,
                        min(1.0, len(risk_alerts) / 50),
                    )
                    triggers.append(trigger)
        
        # Check for execution overload
        if len(recent_events) > 10:
            for domain in domains:
                if domain.performance_score < 5:
                    trigger = self._create_trigger(
                        TriggerType.EXECUTION_OVERLOAD,
                        domain.name,
                        0.6,
                    )
                    triggers.append(trigger)
        
        # Check for resource starvation
        for domain in domains:
            if domain.resource_allocation < 8:
                trigger = self._create_trigger(
                    TriggerType.RESOURCE_STARVATION,
                    domain.name,
                    (10 - domain.resource_allocation) / 20,
                )
                triggers.append(trigger)
        
        # Check for strategic drift
        drift_score = self._detect_strategic_drift(domains)
        if drift_score > 5:
            trigger = self._create_trigger(
                TriggerType.STRATEGIC_DRIFT,
                "all",
                drift_score / 10,
            )
            triggers.append(trigger)
        
        logger.info(f"Detected {len(triggers)} intervention triggers")
        
        return triggers
    
    def _create_trigger(
        self,
        trigger_type: TriggerType,
        domain: str,
        severity: float,
    ) -> TriggerCondition:
        """Create or update a trigger condition."""
        
        key = f"{domain}_{trigger_type.value}"
        
        if key not in self.trigger_conditions:
            self.trigger_conditions[key] = []
        
        # Update existing or create new
        existing = [t for t in self.trigger_conditions[key] if t.trigger_type == trigger_type]
        
        if existing:
            trigger = existing[0]
            trigger.occurrence_count += 1
            trigger.last_detected = datetime.utcnow()
            trigger.severity = max(trigger.severity, severity)
            trigger.duration_days += 1
        else:
            trigger = TriggerCondition(
                trigger_type=trigger_type,
                domain=domain,
                severity=severity,
                duration_days=1,
                occurrence_count=1,
                first_detected=datetime.utcnow(),
                last_detected=datetime.utcnow(),
            )
            self.trigger_conditions[key].append(trigger)
        
        return trigger
    
    def _detect_oscillation(self, domains: List[DomainState]) -> int:
        """Detect priority oscillation."""
        oscillating = 0
        for domain in domains:
            if -5 < domain.momentum_score < -2:
                oscillating += 1
        return oscillating
    
    def _detect_imbalance(self, domains: List[DomainState]) -> List[str]:
        """Detect sustained domain imbalance."""
        if not domains:
            return []
        
        avg_perf = sum(d.performance_score for d in domains) / len(domains)
        imbalanced = []
        
        for domain in domains:
            if abs(domain.performance_score - avg_perf) > 3:
                imbalanced.append(domain.name)
        
        return imbalanced
    
    def _detect_strategic_drift(self, domains: List[DomainState]) -> float:
        """Detect strategic drift."""
        if not domains:
            return 0
        
        # Compare current alignment with ideal
        drift = 0
        for domain in domains:
            # Low alignment means drift from strategic goals
            drift += (10 - domain.alignment_score)
        
        return drift / len(domains)
    
    def run_intervention_cycle(
        self,
        domains: List[DomainState],
        risk_alerts: List[str],
        recent_events: List[str],
    ) -> List[Intervention]:
        """Run a full intervention cycle."""
        
        logger.info("Running intervention cycle")
        
        # Detect triggers
        triggers = self.detect_triggers(domains, risk_alerts, recent_events)
        
        if not triggers:
            logger.info("No intervention triggers detected")
            return []
        
        # Check if we can intervene
        if not self.selector.can_intervene(self.history):
            logger.info("Intervention cooldown active")
            return []
        
        # Build system state
        system_state = SystemStateSnapshot(
            domains=domains,
            active_risks=risk_alerts,
            recent_events=recent_events,
            oscillation_count=sum(1 for d in domains if d.momentum_score < -2),
            alert_count_24h=len(risk_alerts),
        )
        
        # Select intervention
        intervention = self.selector.select_intervention(
            triggers, system_state, self.history
        )
        
        if not intervention:
            logger.info("No suitable intervention selected")
            return []
        
        # Execute intervention
        results = self.executor.execute_intervention(intervention, domains)
        
        # Record intervention
        self.history.append(intervention)
        
        logger.info(f"Intervention {intervention.intervention_id} completed")
        
        return [intervention]
    
    def get_statistics(self) -> InterventionStatistics:
        """Get intervention statistics."""
        
        stats = InterventionStatistics()
        
        stats.total_interventions = len(self.history)
        
        # Count by type
        by_type: Dict[str, int] = {}
        by_domain: Dict[str, int] = {}
        
        successful = 0
        total_confidence = 0
        
        for inv in self.history:
            by_type[inv.intervention_type.value] = by_type.get(inv.intervention_type.value, 0) + 1
            by_domain[inv.target_domain] = by_domain.get(inv.target_domain, 0) + 1
            
            if inv.status == InterventionStatus.COMPLETED:
                successful += 1
            
            total_confidence += inv.confidence_score
        
        stats.by_type = by_type
        stats.by_domain = by_domain
        
        if len(self.history) > 0:
            stats.success_rate = successful / len(self.history)
            stats.average_confidence = total_confidence / len(self.history)
        
        return stats
    
    def get_active_interventions(self) -> List[Intervention]:
        """Get currently active interventions."""
        return [
            inv for inv in self.history
            if inv.status in [InterventionStatus.PENDING, InterventionStatus.EXECUTING]
        ]
    
    def get_recent_interventions(self, hours: int = 24) -> List[Intervention]:
        """Get recent interventions."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [inv for inv in self.history if inv.timestamp > cutoff]


# Global engine instance
_intervention_engine: Optional[InterventionEngine] = None


def get_intervention_engine() -> InterventionEngine:
    """Get the global intervention engine."""
    global _intervention_engine
    if _intervention_engine is None:
        _intervention_engine = InterventionEngine()
    return _intervention_engine
