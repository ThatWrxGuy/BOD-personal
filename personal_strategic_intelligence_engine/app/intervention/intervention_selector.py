"""Intervention Selector - Logic for selecting the most appropriate intervention."""
from typing import List, Optional, Tuple
from datetime import datetime, timedelta

from app.intervention.intervention_types import (
    Intervention,
    InterventionType,
    TriggerType,
    TriggerCondition,
    InterventionProtocol,
    InterventionPolicy,
    SystemStateSnapshot,
    DomainState,
)


class InterventionSelector:
    """Selects the most appropriate intervention based on system state."""
    
    def __init__(self, policy: InterventionPolicy):
        self.policy = policy
    
    def select_intervention(
        self,
        triggers: List[TriggerCondition],
        system_state: SystemStateSnapshot,
        recent_interventions: List[Intervention],
    ) -> Optional[Intervention]:
        """Select the best intervention based on triggers and system state."""
        
        if not triggers:
            return None
        
        # Sort triggers by severity
        sorted_triggers = sorted(triggers, key=lambda t: t.severity, reverse=True)
        
        # Find the most severe trigger
        primary_trigger = sorted_triggers[0]
        
        # Check cooldown - don't intervene too frequently
        if self._is_in_cooldown(primary_trigger, recent_interventions):
            return None
        
        # Check confidence threshold
        confidence = self._calculate_confidence(primary_trigger, system_state)
        if confidence < self.policy.confidence_threshold:
            return None
        
        # Select protocol based on trigger type
        from app.intervention.intervention_protocols import InterventionProtocols
        
        protocols = InterventionProtocols.get_protocols_for_trigger(primary_trigger.trigger_type)
        
        if not protocols:
            return None
        
        # Select best protocol
        selected_protocol = self._select_best_protocol(
            protocols, primary_trigger, system_state, recent_interventions
        )
        
        if not selected_protocol:
            return None
        
        # Create intervention
        intervention = self._create_intervention(
            selected_protocol, primary_trigger, confidence
        )
        
        return intervention
    
    def _is_in_cooldown(
        self,
        trigger: TriggerCondition,
        recent_interventions: List[Intervention],
    ) -> bool:
        """Check if domain is in cooldown period."""
        
        cooldown_end = datetime.utcnow() - timedelta(hours=self.policy.cooldown_hours)
        
        for inv in recent_interventions:
            if inv.target_domain == trigger.domain:
                if inv.timestamp > cooldown_end:
                    return True
        
        return False
    
    def _calculate_confidence(
        self,
        trigger: TriggerCondition,
        system_state: SystemStateSnapshot,
    ) -> float:
        """Calculate confidence that intervention will help."""
        
        confidence = 0.5  # Base confidence
        
        # Higher severity = higher confidence
        confidence += trigger.severity * 0.3
        
        # More occurrences = higher confidence
        if trigger.occurrence_count > 5:
            confidence += 0.1
        if trigger.occurrence_count > 10:
            confidence += 0.1
        
        # Sustained issues = higher confidence
        if trigger.duration_days > 7:
            confidence += 0.1
        
        # Check if domain has been declining
        domain = self._find_domain(system_state.domains, trigger.domain)
        if domain and domain.momentum_score < -3:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _select_best_protocol(
        self,
        protocols: List[InterventionProtocol],
        trigger: TriggerCondition,
        system_state: SystemStateSnapshot,
        recent_interventions: List[Intervention],
    ) -> Optional[InterventionProtocol]:
        """Select the best protocol from available options."""
        
        if not protocols:
            return None
        
        # Filter by cooldown
        available = []
        cooldown_end = datetime.utcnow() - timedelta(hours=24)
        
        for p in protocols:
            # Check if this protocol was recently used
            recently_used = any(
                inv.intervention_type == p.intervention_type and
                inv.timestamp > cooldown_end
                for inv in recent_interventions
            )
            if not recently_used:
                available.append(p)
        
        if not available:
            available = protocols
        
        # Score each protocol
        scored = []
        for p in available:
            score = self._score_protocol(p, trigger, system_state)
            scored.append((score, p))
        
        # Return highest scored
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return scored[0][1] if scored else None
    
    def _score_protocol(
        self,
        protocol: InterventionProtocol,
        trigger: TriggerCondition,
        system_state: SystemStateSnapshot,
    ) -> float:
        """Score a protocol based on fit."""
        
        score = 0.5  # Base score
        
        # Emergency protocols only for severe cases
        if protocol.is_emergency:
            if trigger.severity > 0.8:
                score += 0.3
            else:
                score -= 0.3
        
        # Match intervention type to domain needs
        domain = self._find_domain(system_state.domains, trigger.domain)
        if domain:
            if protocol.intervention_type == InterventionType.WORKLOAD_REDUCTION:
                if domain.risk_score > 6:
                    score += 0.2
            elif protocol.intervention_type == InterventionType.RISK_MITIGATION:
                if domain.risk_score > 5:
                    score += 0.2
            elif protocol.intervention_type == InterventionType.RESOURCE_REALLOCATION:
                if domain.resource_allocation < 10:
                    score += 0.2
        
        return score
    
    def _create_intervention(
        self,
        protocol: InterventionProtocol,
        trigger: TriggerCondition,
        confidence: float,
    ) -> Intervention:
        """Create an intervention from a protocol."""
        
        import uuid
        
        intervention = Intervention(
            intervention_id=str(uuid.uuid4())[:8],
            timestamp=datetime.utcnow(),
            trigger_reason=f"{trigger.trigger_type.value} detected",
            trigger_type=trigger.trigger_type,
            target_domain=trigger.domain,
            intervention_type=protocol.intervention_type,
            expected_effect=protocol.description,
            confidence_score=confidence,
            status="pending",
            actions=[],
        )
        
        # Add actions from protocol
        from app.intervention.intervention_types import InterventionAction
        
        for action_def in protocol.actions:
            action = InterventionAction(
                action_type=action_def.get("action_type", ""),
                target=action_def.get("target", ""),
                value=action_def.get("value"),
                reason=action_def.get("reason", ""),
            )
            intervention.actions.append(action)
        
        return intervention
    
    def _find_domain(self, domains: List[DomainState], name: str) -> Optional[DomainState]:
        """Find a domain by name."""
        for d in domains:
            if d.name == name:
                return d
        return None
    
    def can_intervene(
        self,
        recent_interventions: List[Intervention],
    ) -> bool:
        """Check if we can still intervene today."""
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        interventions_today = [
            inv for inv in recent_interventions
            if inv.timestamp > today_start
        ]
        
        return len(interventions_today) < self.policy.max_interventions_per_day
