#!/usr/bin/env python
"""Simulation with Intervention Engine - Before/After Comparison."""
import random
import hashlib
import json
from datetime import date, timedelta
from typing import Dict, List


class SeedManager:
    def __init__(self, seed: str):
        self.original_seed = seed.upper().strip().replace(" ", "-")
        self._rng = self._create_generator(self.original_seed)
    
    def _create_generator(self, seed: str) -> random.Random:
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        seed_int = int(seed_hash[:16], 16) % (2**31)
        return random.Random(seed_int)
    
    @property
    def random(self):
        return self._rng


class DomainState:
    def __init__(self, name: str, perf: float, risk: float, opp: float, momentum: float, align: float, alloc: float):
        self.name = name
        self.performance_score = perf
        self.risk_score = risk
        self.opportunity_score = opp
        self.momentum_score = momentum
        self.alignment_score = align
        self.resource_allocation = alloc


# Simplified Intervention Engine
class InterventionEngine:
    def __init__(self):
        self.max_per_day = 5
        self.cooldown_hours = 1
        self.intervention_count = 0
        self.history = []
    
    def should_intervene(self, domains: List[DomainState], risk_alerts: List) -> bool:
        # Check if intervention needed
        for d in domains:
            if d.performance_score < 3 or d.risk_score > 7:
                if self.intervention_count < self.max_per_day:
                    return True
        return False
    
    def run_intervention(self, domains: List[DomainState], risk_alerts: List) -> Dict:
        actions = []
        
        # Find worst domain
        worst = min(domains, key=lambda d: d.performance_score)
        
        # Execute intervention
        if worst.performance_score < 3:
            # Recovery action
            worst.performance_score += 1.5
            worst.risk_score = max(0, worst.risk_score - 0.5)
            actions.append(f"Recovery protocol on {worst.name}")
        
        if worst.risk_score > 7:
            # Risk mitigation
            worst.risk_score -= 1.0
            actions.append(f"Risk mitigation on {worst.name}")
        
        self.intervention_count += 1
        self.history.append({"domain": worst.name, "actions": actions})
        
        return {"intervened": worst.name, "actions": actions}


def run_simulation(seed: str, use_intervention: bool, days: int):
    """Run simulation with or without intervention engine."""
    
    seed_mgr = SeedManager(seed)
    rng = seed_mgr.random
    
    # Initialize domains
    domains = [
        DomainState("health", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("wealth", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("career", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("learning", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("relationships", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("personal_development", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("operations", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
        DomainState("strategic_projects", 5.0, 4.0, 5.0, 0.0, 6.0, 12.5),
    ]
    
    # Tracking
    priority_decisions = []
    resource_decisions = []
    risk_alerts_list = []
    interventions = []
    events = []
    oscillation_count = 0
    
    intervention_engine = InterventionEngine() if use_intervention else None
    
    # Simulation
    for day in range(1, days + 1):
        # Random events
        if rng.random() < 0.15:
            event_types = [
                ("expense", "wealth", 0.5),
                ("workload", "career", 0.6),
                ("health", "health", 0.4),
                ("schedule", "operations", 0.7),
            ]
            evt = rng.choice(event_types)
            events.append({"day": day, "type": evt[0], "domain": evt[1], "severity": evt[2]})
            
            # Apply event effects
            for d in domains:
                if d.name == evt[1]:
                    d.performance_score = max(0, min(10, d.performance_score - evt[2]))
                    d.risk_score = min(10, d.risk_score + evt[2] * 0.5)
        
        # Priority decisions (the OLD way - just flagging problems)
        sorted_domains = sorted(domains, key=lambda d: d.performance_score)
        for d in sorted_domains[:2]:
            if d.performance_score < 4:
                priority_decisions.append({
                    "day": day,
                    "domain": d.name,
                    "action": "INCREASE_PRIORITY",
                    "score": d.performance_score
                })
        
        # Detect oscillation (same domains repeatedly flagged)
        low_domains = [d.name for d in domains if d.performance_score < 4]
        if len(low_domains) > 0 and len(priority_decisions) > 10:
            # Check if same domains keep appearing
            recent = [p for p in priority_decisions[-20:] if p["domain"] in low_domains]
            if len(recent) > 15:
                oscillation_count += 1
        
        # Risk alerts
        for d in domains:
            if d.risk_score > 5:
                risk_alerts_list.append({"day": day, "domain": d.name, "risk": d.risk_score})
        
        # Resource reallocation (OLD way - just shifting, not fixing)
        if day % 30 == 0:
            # Just shuffle resources without fixing root causes
            for d in domains:
                d.resource_allocation = 12.5 + rng.uniform(-3, 3)
            resource_decisions.append({"day": day, "type": "rebalance"})
        
        # NEW: Intervention Engine (if enabled)
        if use_intervention and intervention_engine:
            if intervention_engine.should_intervene(domains, risk_alerts_list):
                result = intervention_engine.run_intervention(domains, risk_alerts_list)
                interventions.append({"day": day, **result})
    
    # Calculate results
    final_domains = {d.name: {"perf": d.performance_score, "risk": d.risk_score} for d in domains}
    
    # Count unique domains that had priority escalation without improvement
    domain_escalation = {}
    for p in priority_decisions:
        dom = p["domain"]
        if dom not in domain_escalation:
            domain_escalation[dom] = 0
        domain_escalation[dom] += 1
    
    # Find domains that stayed collapsed
    collapsed_domains = [d.name for d in domains if d.performance_score < 3]
    
    return {
        "priority_decisions": len(priority_decisions),
        "resource_reallocations": len(resource_decisions),
        "risk_alerts": len(risk_alerts_list),
        "oscillation_events": oscillation_count,
        "interventions_executed": len(interventions),
        "final_domains": final_domains,
        "domain_escalations": domain_escalation,
        "collapsed_domains": collapsed_domains,
        "intervention_history": interventions,
    }


def main():
    print("=" * 80)
    print("SIMULATION COMPARISON: BEFORE vs AFTER INTERVENTION ENGINE")
    print("=" * 80)
    
    # Run WITHOUT intervention (baseline/pressure scenario)
    print("\n" + "="*40)
    print("RUNNING BASELINE SIMULATION (WITHOUT INTERVENTION)")
    print("="*40)
    
    baseline = run_simulation("BOD-V4-SIM-BASELINE-001", use_intervention=False, days=256)
    
    print(f"\nResults (No Intervention):")
    print(f"  Priority Decisions: {baseline['priority_decisions']}")
    print(f"  Risk Alerts: {baseline['risk_alerts']}")
    print(f"  Resource Reallocations: {baseline['resource_reallocations']}")
    print(f"  Oscillation Events: {baseline['oscillation_events']}")
    print(f"  Collapsed Domains: {baseline['collapsed_domains']}")
    
    # Run WITH intervention
    print("\n" + "="*40)
    print("RUNNING SIMULATION WITH INTERVENTION ENGINE")
    print("="*40)
    
    with_intervention = run_simulation("BOD-V4-SIM-BASELINE-001", use_intervention=True, days=256)
    
    print(f"\nResults (With Intervention):")
    print(f"  Priority Decisions: {with_intervention['priority_decisions']}")
    print(f"  Risk Alerts: {with_intervention['risk_alerts']}")
    print(f"  Resource Reallocations: {with_intervention['resource_reallocations']}")
    print(f"  Oscillation Events: {with_intervention['oscillation_events']}")
    print(f"  Interventions Executed: {with_intervention['interventions_executed']}")
    print(f"  Collapsed Domains: {with_intervention['collapsed_domains']}")
    
    # Comparison
    print("\n" + "="*80)
    print("BEFORE vs AFTER COMPARISON")
    print("="*80)
    
    print(f"\n{'Metric':<30} {'Before':>15} {'After':>15} {'Change':>15}")
    print("-" * 80)
    
    print(f"{'Priority Decisions':<30} {baseline['priority_decisions']:>15} {with_intervention['priority_decisions']:>15} {with_intervention['priority_decisions'] - baseline['priority_decisions']:>+15}")
    print(f"{'Risk Alerts':<30} {baseline['risk_alerts']:>15} {with_intervention['risk_alerts']:>15} {with_intervention['risk_alerts'] - baseline['risk_alerts']:>+15}")
    print(f"{'Oscillation Events':<30} {baseline['oscillation_events']:>15} {with_intervention['oscillation_events']:>15} {with_intervention['oscillation_events'] - baseline['oscillation_events']:>+15}")
    print(f"{'Collapsed Domains':<30} {len(baseline['collapsed_domains']):>15} {len(with_intervention['collapsed_domains']):>15} {len(with_intervention['collapsed_domains']) - len(baseline['collapsed_domains']):>+15}")
    print(f"{'Interventions':<30} {'0':>15} {with_intervention['interventions_executed']:>15} {with_intervention['interventions_executed']:>+15}")
    
    print("\n" + "="*80)
    print("FINAL DOMAIN STATES")
    print("="*80)
    
    print(f"\n{'Domain':<25} {'Before Perf':>12} {'After Perf':>12} {'Before Risk':>12} {'After Risk':>12}")
    print("-" * 80)
    
    for dom in baseline['final_domains']:
        before = baseline['final_domains'][dom]
        after = with_intervention['final_domains'].get(dom, before)
        print(f"{dom:<25} {before['perf']:>12.1f} {after['perf']:>12.1f} {before['risk']:>12.1f} {after['risk']:>12.1f}")
    
    # Analysis
    print("\n" + "="*80)
    print("INTERVENTION EFFECTIVENESS ANALYSIS")
    print("="*80)
    
    # 1. Priority escalation without improvement
    before_escalation = sum(baseline['domain_escalations'].values())
    after_escalation = sum(with_intervention['domain_escalations'].values())
    
    print(f"\n1. PRIORITY ESCALATION REDUCTION:")
    print(f"   Before: {before_escalation} priority decisions")
    print(f"   After:  {after_escalation} priority decisions")
    print(f"   Change: {after_escalation - before_escalation:+d} ({((after_escalation - before_escalation) / max(before_escalation, 1)) * 100:+.1f}%)")
    
    # 2. Unresolved domain collapse
    before_collapsed = len(baseline['collapsed_domains'])
    after_collapsed = len(with_intervention['collapsed_domains'])
    
    print(f"\n2. UNRESOLVED DOMAIN COLLAPSE:")
    print(f"   Before: {before_collapsed} domains collapsed")
    print(f"   After:  {after_collapsed} domains collapsed")
    print(f"   Change: {after_collapsed - before_collapsed:+d}")
    
    # 3. Operations and Wealth outcomes
    ops_before = baseline['final_domains'].get('operations', {'perf': 0, 'risk': 0})
    ops_after = with_intervention['final_domains'].get('operations', {'perf': 0, 'risk': 0})
    wealth_before = baseline['final_domains'].get('wealth', {'perf': 0, 'risk': 0})
    wealth_after = with_intervention['final_domains'].get('wealth', {'perf': 0, 'risk': 0})
    
    print(f"\n3. OPERATIONS & WEALTH OUTCOMES:")
    print(f"   Operations: {ops_before['perf']:.1f} -> {ops_after['perf']:.1f} (perf), {ops_before['risk']:.1f} -> {ops_after['risk']:.1f} (risk)")
    print(f"   Wealth:    {wealth_before['perf']:.1f} -> {wealth_after['perf']:.1f} (perf), {wealth_before['risk']:.1f} -> {wealth_after['risk']:.1f} (risk)")
    
    # 4. Risk reduction
    before_risk = sum(d['risk'] for d in baseline['final_domains'].values())
    after_risk = sum(d['risk'] for d in with_intervention['final_domains'].values())
    
    print(f"\n4. TOTAL RISK EXPOSURE:")
    print(f"   Before: {before_risk:.1f}")
    print(f"   After:  {after_risk:.1f}")
    print(f"   Change: {after_risk - before_risk:+.1f}")
    
    # 5. Performance improvement
    before_perf = sum(d['perf'] for d in baseline['final_domains'].values())
    after_perf = sum(d['perf'] for d in with_intervention['final_domains'].values())
    
    print(f"\n5. TOTAL PERFORMANCE:")
    print(f"   Before: {before_perf:.1f}")
    print(f"   After:  {after_perf:.1f}")
    print(f"   Change: {after_perf - before_perf:+.1f}")
    
    print("\n" + "="*80)
    print("KEY OBSERVATIONS")
    print("="*80)
    
    observations = []
    
    if after_escalation < before_escalation:
        observations.append("✓ Reduced repeated priority escalation without improvement")
    else:
        observations.append("✗ Priority escalation not reduced")
    
    if after_collapsed < before_collapsed:
        observations.append("✓ Reduced unresolved domain collapse")
    else:
        observations.append("✗ Domain collapse not addressed")
    
    if ops_after['perf'] > ops_before['perf']:
        observations.append(f"✓ Improved operations performance ({ops_before['perf']:.1f} -> {ops_after['perf']:.1f})")
    
    if wealth_after['perf'] > wealth_before['perf']:
        observations.append(f"✓ Improved wealth performance ({wealth_before['perf']:.1f} -> {wealth_after['perf']:.1f})")
    
    if after_risk < before_risk:
        observations.append(f"✓ Reduced overall risk exposure ({before_risk:.1f} -> {after_risk:.1f})")
    
    for obs in observations:
        print(f"  {obs}")
    
    return baseline, with_intervention


if __name__ == "__main__":
    main()
