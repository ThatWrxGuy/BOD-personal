"""End-to-end audit runner for comprehensive system validation.

Executes realistic scenarios and multi-cycle governance simulations.
"""
import asyncio
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import ApprovalTierLevel
from app.audit.audit_models import (
    ApprovalStatus,
    AuditCycleRecord,
    AuditMode,
    DecisionInventory,
    GateOutcome,
    GovernanceOutcomeReport,
    LearningReport,
    MasterAuditReport,
    ScenarioTypeAudit,
    VisionAlignment,
    AuditFindings,
)
from app.governance_simulation.scenario_generator import ScenarioGenerator
from app.governance_simulation.simulation_models import ScenarioType


class EndToEndAuditRunner:
    """Runner for end-to-end audit scenarios."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize audit runner."""
        self.seed = seed
        if seed:
            random.seed(seed)
        
        self.cycle_records: List[AuditCycleRecord] = []
        self.confidence_history: List[float] = []
        
        # Track repeated recommendations
        self.recommendation_tracker: Dict[str, int] = {}
    
    async def run_realistic_scenario_audit(
        self,
        scenario_type: ScenarioTypeAudit,
    ) -> List[AuditCycleRecord]:
        """Run realistic end-to-end scenario audit."""
        records = []
        
        # Generate scenario-specific signals
        signals = self._generate_scenario_signals(scenario_type)
        
        # Run multiple cycles for the scenario
        num_cycles = self._get_scenario_cycle_count(scenario_type)
        
        for cycle_num in range(1, num_cycles + 1):
            record = await self._run_audit_cycle(
                cycle_num=cycle_num,
                scenario_name=scenario_type.value,
                audit_mode=AuditMode.REALISTIC_SCENARIO,
                signals=signals,
                cycle_index=cycle_num,
            )
            records.append(record)
            self.cycle_records.append(record)
        
        return records
    
    async def run_multi_cycle_governance_audit(
        self,
        scenario_name: str = "governance_simulation",
        num_cycles: int = 50,
    ) -> List[AuditCycleRecord]:
        """Run multi-cycle governance simulation audit."""
        records = []
        
        # Generate varied signals
        generator = ScenarioGenerator(random_seed=self.seed)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        
        for cycle_num in range(1, num_cycles + 1):
            # Generate signals for this cycle
            signals = generator.generate_signals(scenario, cycle_num)
            
            record = await self._run_audit_cycle(
                cycle_num=cycle_num,
                scenario_name=scenario_name,
                audit_mode=AuditMode.MULTI_CYCLE_SIMULATION,
                signals=signals,
                cycle_index=cycle_num,
            )
            records.append(record)
            self.cycle_records.append(record)
        
        return records
    
    async def _run_audit_cycle(
        self,
        cycle_num: int,
        scenario_name: str,
        audit_mode: AuditMode,
        signals: List[Any],
        cycle_index: int,
    ) -> AuditCycleRecord:
        """Run a single audit cycle."""
        start_time = time.time()
        
        # Simulate state update
        state = self._simulate_state_update(signals, cycle_index)
        
        # Simulate forecasting
        forecasts = self._simulate_forecasting(state)
        
        # Simulate doctrine evaluation
        doctrine = self._simulate_doctrine_evaluation(state, cycle_index)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(state, doctrine, cycle_index)
        
        # Form execution intents
        execution_intents = self._form_execution_intents(recommendations, doctrine, cycle_index)
        
        # Evaluate governance gates
        gate_outcomes = self._evaluate_governance_gates(execution_intents, doctrine)
        
        # Determine approval status
        approval = self._determine_approval(execution_intents, gate_outcomes)
        
        # Simulate learning
        confidence_before = self.confidence_history[-1] if self.confidence_history else 0.5
        learning = self._simulate_learning(execution_intents, gate_outcomes, cycle_index)
        confidence_after = learning["confidence"]
        self.confidence_history.append(confidence_after)
        
        # Detect anomalies/conflicts
        conflicts, anomalies = self._detect_issues(doctrine, recommendations, cycle_index)
        
        # Track repeated recommendations
        self._track_recommendations(recommendations)
        
        # Build record
        record = AuditCycleRecord(
            cycle_id=f"audit_{scenario_name}_{cycle_num}",
            scenario_name=scenario_name,
            audit_mode=audit_mode,
            timestamp=datetime.utcnow(),
            cycle_duration_ms=(time.time() - start_time) * 1000,
            signals_received=[{"domain": s.domain, "magnitude": s.magnitude} for s in signals],
            signal_summary=self._summarize_signals(signals),
            state_summary=state,
            forecast_highlights=forecasts,
            doctrine_assessment=doctrine,
            alignment_score=doctrine.get("alignment_score", 0.0),
            alignment_level=doctrine.get("alignment_level", "neutral"),
            doctrine_flags=doctrine.get("risk_flags", []),
            doctrine_conflicts=doctrine.get("conflicts", []),
            recommendations=recommendations,
            recommendation_count=len(recommendations),
            execution_intents=execution_intents,
            execution_intent_count=len(execution_intents),
            policy_gate_outcome=gate_outcomes["policy"],
            doctrine_gate_outcome=gate_outcomes["doctrine"],
            risk_gate_outcome=gate_outcomes["risk"],
            approval_status=approval["status"],
            approval_tier=approval["tier"],
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            learning_updates=learning["updates"],
            conflicts_detected=conflicts,
            anomalies_detected=anomalies,
        )
        
        return record
    
    def _generate_scenario_signals(
        self,
        scenario_type: ScenarioTypeAudit,
    ) -> List[Dict[str, Any]]:
        """Generate scenario-specific signals."""
        scenarios = {
            ScenarioTypeAudit.PERSONAL_LIFE_OPTIMIZATION: [
                {"domain": "health", "magnitude": 0.7},
                {"domain": "operations", "magnitude": 0.5},
            ],
            ScenarioTypeAudit.FINANCIAL_STRESS_RECOVERY: [
                {"domain": "finance", "magnitude": -0.8},
                {"domain": "risk", "magnitude": 0.6},
            ],
            ScenarioTypeAudit.COMPETING_PRIORITIES: [
                {"domain": "strategy", "magnitude": 0.4},
                {"domain": "operations", "magnitude": 0.6},
                {"domain": "finance", "magnitude": 0.3},
            ],
            ScenarioTypeAudit.OPPORTUNITY_PRIORITIZATION: [
                {"domain": "strategy", "magnitude": 0.3},
                {"domain": "finance", "magnitude": 0.2},
                {"domain": "operations", "magnitude": 0.2},
            ],
            ScenarioTypeAudit.MIXED_DOMAIN_STRATEGIC: [
                {"domain": "health", "magnitude": 0.3},
                {"domain": "finance", "magnitude": 0.3},
                {"domain": "strategy", "magnitude": 0.3},
                {"domain": "operations", "magnitude": 0.3},
            ],
            ScenarioTypeAudit.GOVERNANCE_HEAVY: [
                {"domain": "risk", "magnitude": 0.4},
                {"domain": "strategy", "magnitude": 0.3},
                {"domain": "finance", "magnitude": 0.3},
            ],
        }
        
        return [
            type('Signal', (), s)() 
            for s in scenarios.get(scenario_type, [])
        ]
    
    def _get_scenario_cycle_count(self, scenario_type: ScenarioTypeAudit) -> int:
        """Get number of cycles for a scenario."""
        counts = {
            ScenarioTypeAudit.PERSONAL_LIFE_OPTIMIZATION: 5,
            ScenarioTypeAudit.FINANCIAL_STRESS_RECOVERY: 8,
            ScenarioTypeAudit.COMPETING_PRIORITIES: 6,
            ScenarioTypeAudit.OPPORTUNITY_PRIORITIZATION: 5,
            ScenarioTypeAudit.MIXED_DOMAIN_STRATEGIC: 7,
            ScenarioTypeAudit.GOVERNANCE_HEAVY: 10,
        }
        return counts.get(scenario_type, 5)
    
    def _simulate_state_update(
        self,
        signals: List[Any],
        cycle_index: int,
    ) -> Dict[str, Any]:
        """Simulate state update from signals."""
        state = {
            "domains": {},
        }
        
        # Track state across cycles for consistency
        if not hasattr(self, '_domain_state'):
            self._domain_state = {}
        
        for signal in signals:
            domain = signal.domain
            magnitude = signal.magnitude
            
            # Get previous state for smoothing
            prev_perf = self._domain_state.get(domain, {}).get("performance", 0.5)
            
            # Update domain performance based on signal with smoothing
            base_perf = 0.5 + (cycle_index * 0.02)  # Gradual improvement
            raw_perf = base_perf + (magnitude * 0.2)
            
            # Apply smoothing to reduce variance
            smoothed_perf = (prev_perf * 0.3) + (raw_perf * 0.7)
            smoothed_perf = max(0.0, min(1.0, smoothed_perf))
            
            state["domains"][domain] = {
                "performance": smoothed_perf,
                "risk": 1.0 - smoothed_perf,
                "reliability": 0.7 + random.uniform(-0.05, 0.05),
            }
            
            # Store for next cycle
            self._domain_state[domain] = {"performance": smoothed_perf}
        
        return state
    
    def _simulate_forecasting(self, state: Dict[str, Any]) -> List[str]:
        """Simulate forecasting/optimization output."""
        forecasts = []
        
        for domain, data in state.get("domains", {}).items():
            perf = data.get("performance", 0.5)
            if perf < 0.4:
                forecasts.append(f"{domain}: declining performance predicted")
            elif perf > 0.7:
                forecasts.append(f"{domain}: strong growth predicted")
            elif perf < 0.5:
                forecasts.append(f"{domain}: moderate improvement opportunity")
        
        return forecasts if forecasts else ["Stable performance across domains"]
    
    def _simulate_doctrine_evaluation(
        self,
        state: Dict[str, Any],
        cycle_index: int,
    ) -> Dict[str, Any]:
        """Simulate doctrine evaluation with improved consistency."""
        # Calculate alignment based on domain performance with normalization
        domains = state.get("domains", {})
        
        if not domains:
            alignment_score = 0.0
        else:
            perfs = [d.get("performance", 0.5) for d in domains.values()]
            avg_perf = sum(perfs) / len(perfs)
            
            # Use a more stable calculation with moderate binning
            # This reduces variance from small performance changes but keeps meaningful variation
            if avg_perf > 0.7:
                alignment_score = 0.8
            elif avg_perf > 0.55:
                alignment_score = 0.4
            elif avg_perf > 0.4:
                alignment_score = 0.1
            elif avg_perf > 0.25:
                alignment_score = -0.3
            else:
                alignment_score = -0.7
        
        # Determine alignment level with standard bands
        if alignment_score > 0.3:
            alignment_level = "aligned"
        elif alignment_score < -0.3:
            alignment_level = "misaligned"
        else:
            alignment_level = "neutral"
        
        # Generate risk flags with normalized thresholds
        risk_flags = []
        conflicts = []
        
        if any(d.get("risk", 0.5) > 0.65 for d in domains.values()):
            risk_flags.append("high_risk_domain_detected")
        
        if any(d.get("performance", 0.5) < 0.3 for d in domains.values()):
            risk_flags.append("low_performance_domain")
            conflicts.append({
                "type": "performance_conflict",
                "severity": "medium",
                "description": "Domain below critical threshold",
            })
        
        # Confidence based on alignment stability
        confidence = 0.5 + (alignment_score * 0.25)
        
        return {
            "alignment_score": alignment_score,
            "alignment_level": alignment_level,
            "confidence": confidence,
            "risk_flags": risk_flags,
            "conflicts": conflicts,
        }
    
    def _generate_recommendations(
        self,
        state: Dict[str, Any],
        doctrine: Dict[str, Any],
        cycle_index: int,
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on state and doctrine with improved coverage."""
        recommendations = []
        
        domains = state.get("domains", {})
        
        for domain, data in domains.items():
            perf = data.get("performance", 0.5)
            
            # Lower threshold to generate more recommendations
            if perf < 0.6:  # Changed from 0.5 to 0.6
                # Determine value based on severity
                if perf < 0.3:
                    value = "high"
                    priority = 0.9
                elif perf < 0.45:
                    value = "medium"
                    priority = 0.7
                else:
                    value = "low"
                    priority = 0.5
                
                # Action type based on performance level
                if perf < 0.3:
                    action = "critical_intervention"
                elif perf < 0.45:
                    action = "improve_performance"
                else:
                    action = "optimize_performance"
                
                recommendations.append({
                    "recommendation_id": f"rec_{domain}_{cycle_index}",
                    "domain": domain,
                    "action_type": action,
                    "priority": priority,
                    "confidence": doctrine.get("confidence", 0.5),
                    "value_assessment": value,
                })
        
        # Add strategic recommendations more reliably
        if len(domains) >= 2:
            # Check for cross-domain opportunities
            avg_perf = sum(d.get("performance", 0.5) for d in domains.values()) / len(domains)
            if avg_perf < 0.6:  # More sensitive threshold
                recommendations.append({
                    "recommendation_id": f"rec_strategy_{cycle_index}",
                    "domain": "strategy",
                    "action_type": "strategic_review",
                    "priority": 0.6,
                    "confidence": doctrine.get("confidence", 0.5),
                    "value_assessment": "medium",
                })
        
        return recommendations
    
    def _form_execution_intents(
        self,
        recommendations: List[Dict[str, Any]],
        doctrine: Dict[str, Any],
        cycle_index: int,
    ) -> List[Dict[str, Any]]:
        """Form execution intents from recommendations."""
        intents = []
        
        for rec in recommendations:
            # Only form intents for high-value recommendations
            if rec.get("value_assessment") in ["high", "medium"]:
                intent = {
                    "intent_id": f"intent_{rec['recommendation_id']}",
                    "recommendation_id": rec["recommendation_id"],
                    "domain": rec["domain"],
                    "action_type": rec["action_type"],
                    "confidence": rec["confidence"],
                    "requires_approval": True,
                }
                intents.append(intent)
        
        return intents
    
    def _evaluate_governance_gates(
        self,
        intents: List[Dict[str, Any]],
        doctrine: Dict[str, Any],
    ) -> Dict[str, GateOutcome]:
        """Evaluate governance gates."""
        # Policy gate
        policy = GateOutcome.PASSED
        if len(intents) > 5:
            policy = GateOutcome.BLOCKED
        
        # Doctrine gate
        doctrine_outcome = GateOutcome.PASSED
        if doctrine.get("alignment_level") == "misaligned":
            doctrine_outcome = GateOutcome.BLOCKED
        elif doctrine.get("risk_flags"):
            doctrine_outcome = GateOutcome.FLAGGED
        
        # Risk gate
        risk = GateOutcome.PASSED
        if doctrine.get("risk_flags"):
            # Check for critical flags
            if any("high_risk" in f for f in doctrine.get("risk_flags", [])):
                risk = GateOutcome.BLOCKED
            else:
                risk = GateOutcome.FLAGGED
        
        return {
            "policy": policy,
            "doctrine": doctrine_outcome,
            "risk": risk,
        }
    
    def _determine_approval(
        self,
        intents: List[Dict[str, Any]],
        gate_outcomes: Dict[str, GateOutcome],
    ) -> Dict[str, Any]:
        """Determine approval status."""
        if not intents:
            return {"status": ApprovalStatus.PENDING, "tier": "none"}
        
        # Check if blocked
        if any(g == GateOutcome.BLOCKED for g in gate_outcomes.values()):
            return {"status": ApprovalStatus.REJECTED, "tier": "tier_0_manual_only"}
        
        # Determine tier
        tier = ApprovalTierLevel.TIER_0_MANUAL_ONLY
        
        # Randomly assign tier for simulation
        tier_choice = random.random()
        if tier_choice < 0.5:
            tier = ApprovalTierLevel.TIER_0_MANUAL_ONLY
            status = ApprovalStatus.MANUAL_REQUIRED
        elif tier_choice < 0.8:
            tier = ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH
            status = ApprovalStatus.MANUAL_REQUIRED
        else:
            tier = ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO
            status = ApprovalStatus.APPROVED if random.random() < 0.3 else ApprovalStatus.MANUAL_REQUIRED
        
        return {"status": status, "tier": tier.value}
    
    def _simulate_learning(
        self,
        intents: List[Dict[str, Any]],
        gate_outcomes: Dict[str, GateOutcome],
        cycle_index: int,
    ) -> Dict[str, Any]:
        """Simulate learning and confidence updates."""
        updates = []
        
        # Calculate outcome
        passed = sum(1 for g in gate_outcomes.values() if g == GateOutcome.PASSED)
        total = len(gate_outcomes)
        
        if total > 0:
            success_rate = passed / total
            delta = (success_rate - 0.5) * 0.1
        else:
            delta = 0.0
        
        # Calculate new confidence
        prev_confidence = self.confidence_history[-1] if self.confidence_history else 0.5
        new_confidence = prev_confidence + delta
        new_confidence = max(0.1, min(0.9, new_confidence))
        
        if delta > 0.05:
            updates.append("confidence_increased")
        elif delta < -0.05:
            updates.append("confidence_decreased")
        
        if intents and passed == total:
            updates.append("positive_outcome_learned")
        
        return {
            "confidence": new_confidence,
            "updates": updates,
        }
    
    def _detect_issues(
        self,
        doctrine: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        cycle_index: int,
    ) -> tuple[List[str], List[str]]:
        """Detect conflicts and anomalies."""
        conflicts = []
        anomalies = []
        
        # Check for doctrine conflicts
        if doctrine.get("conflicts"):
            conflicts.extend([c.get("type", "unknown") for c in doctrine["conflicts"]])
        
        # Check for recommendation anomalies
        if len(recommendations) > 10:
            anomalies.append("recommendation_spike")
        
        if len(recommendations) == 0 and cycle_index > 3:
            anomalies.append("no_recommendations")
        
        return conflicts, anomalies
    
    def _track_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """Track repeated recommendations."""
        for rec in recommendations:
            rec_id = rec.get("recommendation_id", "")
            domain = rec.get("domain", "")
            
            # Track by domain + action type
            key = f"{domain}_{rec.get('action_type', '')}"
            self.recommendation_tracker[key] = self.recommendation_tracker.get(key, 0) + 1
    
    def _summarize_signals(self, signals: List[Any]) -> str:
        """Summarize signals as text."""
        if not signals:
            return "No signals"
        
        domains = [s.domain for s in signals]
        magnitudes = [s.magnitude for s in signals]
        
        return f"Signals: {', '.join(set(domains))}, avg magnitude: {sum(magnitudes)/len(magnitudes):.2f}"
    
    def build_decision_inventory(self) -> DecisionInventory:
        """Build decision inventory from cycle records."""
        inventory = DecisionInventory()
        
        for record in self.cycle_records:
            # Track total recommendations
            inventory.total_recommendations += record.recommendation_count
            
            # By domain
            for rec in record.recommendations:
                domain = rec.get("domain", "unknown")
                inventory.decisions_by_domain[domain] = inventory.decisions_by_domain.get(domain, 0) + 1
            
            # By urgency
            priority = rec.get("priority", 0.5)
            urgency = "high" if priority > 0.7 else "normal"
            inventory.decisions_by_urgency[urgency] = inventory.decisions_by_urgency.get(urgency, 0) + 1
            
            # By alignment
            if record.alignment_level == "aligned":
                inventory.aligned_decisions += 1
            elif record.alignment_level == "misaligned":
                inventory.misaligned_decisions += 1
            else:
                inventory.neutral_decisions += 1
            
            # By execution eligibility
            if record.execution_intent_count > 0:
                inventory.eligible_for_execution += 1
            
            if record.doctrine_gate_outcome == GateOutcome.BLOCKED:
                inventory.blocked_by_doctrine += 1
            if record.policy_gate_outcome == GateOutcome.BLOCKED:
                inventory.blocked_by_policy += 1
            if record.risk_gate_outcome == GateOutcome.BLOCKED:
                inventory.blocked_by_risk += 1
            
            if record.approval_status == ApprovalStatus.MANUAL_REQUIRED:
                inventory.requires_manual_approval += 1
            
            # Quality
            value = rec.get("value_assessment", "medium")
            if value == "high":
                inventory.high_value_decisions += 1
            elif value == "low":
                inventory.low_value_decisions += 1
        
        # Track repeated
        for key, count in self.recommendation_tracker.items():
            if count > 2:
                inventory.repeated_recommendations[key] = count
                inventory.noisy_decisions += count - 1
        
        return inventory
    
    def build_governance_outcomes(self) -> GovernanceOutcomeReport:
        """Build governance outcome report."""
        report = GovernanceOutcomeReport()
        
        for record in self.cycle_records:
            report.total_recommendations += record.recommendation_count
            report.total_execution_intents += record.execution_intent_count
            
            # Doctrine
            if record.doctrine_gate_outcome == GateOutcome.PASSED:
                report.doctrine_passes += 1
            else:
                report.doctrine_blocks += 1
            
            report.doctrine_flags_raised += len(record.doctrine_flags)
            
            # Policy
            if record.policy_gate_outcome == GateOutcome.PASSED:
                report.policy_passes += 1
            else:
                report.policy_blocks += 1
            
            # Risk
            if record.risk_gate_outcome == GateOutcome.PASSED:
                report.risk_passes += 1
            else:
                report.risk_rejections += 1
            
            # Approval
            if record.approval_status == ApprovalStatus.MANUAL_REQUIRED:
                report.approval_required_count += 1
                if record.approval_tier == "tier_0_manual_only":
                    report.manual_only_count += 1
                elif record.approval_tier == "tier_1_manual_fast_path":
                    report.fast_path_count += 1
            elif record.approval_status == ApprovalStatus.APPROVED:
                report.auto_approved_count += 1
        
        return report
    
    def build_learning_report(self) -> LearningReport:
        """Build learning report."""
        report = LearningReport()
        
        if not self.confidence_history:
            return report
        
        report.initial_confidence = self.confidence_history[0]
        report.final_confidence = self.confidence_history[-1]
        report.confidence_drift = report.final_confidence - report.initial_confidence
        report.confidence_min = min(self.confidence_history)
        report.confidence_max = max(self.confidence_history)
        
        # Detect drift events
        for i in range(1, len(self.confidence_history)):
            delta = self.confidence_history[i] - self.confidence_history[i-1]
            if delta < -0.2:
                report.confidence_collapse_events += 1
            elif delta > 0.2:
                report.confidence_inflation_events += 1
        
        # Detect oscillation
        changes = 0
        for i in range(2, len(self.confidence_history)):
            if (self.confidence_history[i] > self.confidence_history[i-1]) != \
               (self.confidence_history[i-1] > self.confidence_history[i-2]):
                changes += 1
        
        if changes > len(self.confidence_history) // 3:
            report.oscillating_confidence_events = 1
        
        return report


def create_audit_runner(seed: Optional[int] = None) -> EndToEndAuditRunner:
    """Factory function to create audit runner."""
    return EndToEndAuditRunner(seed=seed)
