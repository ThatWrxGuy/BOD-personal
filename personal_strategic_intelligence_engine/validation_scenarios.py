"""
End-to-End Validation Scenarios for Strategic Intelligence Engine.

Validates core optimization and scoring components with realistic scenarios.
"""
from app.optimization.domain_optimizer import DomainOptimizer
from app.optimization.domain_scorer import DomainScorer
from app.optimization.tradeoff_engine import TradeoffEngine
from app.optimization.optimization_types import (
    LifeDomain, DomainMetrics
)


class ValidationResult:
    def __init__(self, name: str, status: str, details: dict):
        self.name = name
        self.status = status  # PASS, CONCERN, FAIL
        self.details = details


def scenario_1_financial_stress():
    """Financial Stress - wealth domain at critical level."""
    print("\n" + "="*50)
    print("SCENARIO 1: FINANCIAL STRESS")
    print("="*50)
    
    # Critical: low performance, high risk in wealth
    metrics = [
        DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=7.0, risk_score=2.0, opportunity_score=6.0,
            momentum_score=5.0, alignment_score=7.0,
            resource_allocation=20.0, strategic_priority=3,
        ),
        DomainMetrics(
            domain=LifeDomain.WEALTH,
            performance_score=3.0, risk_score=8.0, opportunity_score=4.0,
            momentum_score=2.0, alignment_score=3.0,
            resource_allocation=60.0, strategic_priority=1,
        ),
    ]
    
    optimizer = DomainOptimizer()
    cycle = optimizer.run_optimization_cycle(metrics)
    recommendations = cycle.recommendations
    
    scorer = DomainScorer()
    health_scores = scorer.score_all_domains(metrics)
    
    print(f"Recommendations: {len(recommendations)}")
    wealth_recs = [r for r in recommendations if r.target_domain == LifeDomain.WEALTH]
    print(f"Wealth recommendations: {len(wealth_recs)}")
    print(f"Wealth health score: {health_scores.get(LifeDomain.WEALTH, 0):.2f}")
    
    status = "PASS" if len(wealth_recs) > 0 else "FAIL"
    print(f"Status: {status}")
    
    return ValidationResult("Financial Stress", status, {
        "wealth_recs": len(wealth_recs),
        "wealth_score": health_scores.get(LifeDomain.WEALTH, 0),
    })


def scenario_2_opportunity_prioritization():
    """Opportunity Prioritization - rank by expected value."""
    print("\n" + "="*50)
    print("SCENARIO 2: OPPORTUNITY PRIORITIZATION")
    print("="*50)
    
    # High opportunity in career
    metrics = [
        DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=7.0, risk_score=2.0, opportunity_score=8.0,
            momentum_score=6.0, alignment_score=7.0,
            resource_allocation=20.0, strategic_priority=1,
        ),
        DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=7.0, risk_score=3.0, opportunity_score=9.0,
            momentum_score=7.0, alignment_score=8.0,
            resource_allocation=40.0, strategic_priority=1,
        ),
    ]
    
    optimizer = DomainOptimizer()
    cycle = optimizer.run_optimization_cycle(metrics)
    recommendations = cycle.recommendations
    
    print(f"Recommendations: {len(recommendations)}")
    high_priority = [r for r in recommendations if r.priority > 0.5]
    print(f"High priority: {len(high_priority)}")
    
    status = "PASS" if len(high_priority) > 0 else "CONCERN"
    print(f"Status: {status}")
    
    return ValidationResult("Opportunity", status, {"high_priority": len(high_priority)})


def scenario_3_conflicting_goals():
    """Conflicting Goals - tradeoff detection."""
    print("\n" + "="*50)
    print("SCENARIO 3: CONFLICTING GOALS")
    print("="*50)
    
    # Competing resource allocations
    metrics = [
        DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=5.0, risk_score=6.0, opportunity_score=7.0,
            momentum_score=3.0, alignment_score=8.0,
            resource_allocation=30.0, strategic_priority=1,
        ),
        DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=8.0, risk_score=4.0, opportunity_score=9.0,
            momentum_score=8.0, alignment_score=9.0,
            resource_allocation=70.0, strategic_priority=2,
        ),
    ]
    
    engine = TradeoffEngine()
    conflicts = engine.detect_conflicts(metrics)
    
    print(f"Conflicts detected: {len(conflicts)}")
    for c in conflicts[:3]:
        print(f"  - {c.get('type', 'unknown')}")
    
    status = "PASS" if len(conflicts) > 0 else "CONCERN"
    print(f"Status: {status}")
    
    return ValidationResult("Conflicting Goals", status, {"conflicts": len(conflicts)})


def scenario_4_risk_escalation():
    """Risk Escalation - multiple risks in one domain."""
    print("\n" + "="*50)
    print("SCENARIO 4: RISK ESCALATION")
    print("="*50)
    
    # Health at high risk
    metrics = [
        DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=3.0, risk_score=9.0, opportunity_score=4.0,
            momentum_score=2.0, alignment_score=5.0,
            resource_allocation=50.0, strategic_priority=1,
        ),
        DomainMetrics(
            domain=LifeDomain.WEALTH,
            performance_score=6.0, risk_score=4.0, opportunity_score=5.0,
            momentum_score=5.0, alignment_score=6.0,
            resource_allocation=25.0, strategic_priority=2,
        ),
    ]
    
    optimizer = DomainOptimizer()
    cycle = optimizer.run_optimization_cycle(metrics)
    recommendations = cycle.recommendations
    
    scorer = DomainScorer()
    health_scores = scorer.score_all_domains(metrics)
    
    health_recs = [r for r in recommendations if r.target_domain == LifeDomain.HEALTH]
    print(f"Health recommendations: {len(health_recs)}")
    print(f"Health score: {health_scores.get(LifeDomain.HEALTH, 0):.2f}")
    
    status = "PASS" if len(health_recs) >= 1 else "FAIL"
    print(f"Status: {status}")
    
    return ValidationResult("Risk Escalation", status, {
        "health_recs": len(health_recs),
        "health_score": health_scores.get(LifeDomain.HEALTH, 0),
    })


def scenario_5_multi_domain_mixed():
    """Multi-Domain Mixed - some thriving, some struggling."""
    print("\n" + "="*50)
    print("SCENARIO 5: MULTI-DOMAIN MIXED")
    print("="*50)
    
    # Mixed state
    metrics = [
        DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=8.0, risk_score=2.0, opportunity_score=7.0,
            momentum_score=7.0, alignment_score=8.0,
            resource_allocation=15.0, strategic_priority=3,
        ),
        DomainMetrics(
            domain=LifeDomain.WEALTH,
            performance_score=4.0, risk_score=7.0, opportunity_score=6.0,
            momentum_score=2.0, alignment_score=5.0,
            resource_allocation=50.0, strategic_priority=1,
        ),
        DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=6.0, risk_score=4.0, opportunity_score=7.0,
            momentum_score=5.0, alignment_score=6.0,
            resource_allocation=20.0, strategic_priority=2,
        ),
        DomainMetrics(
            domain=LifeDomain.RELATIONSHIPS,
            performance_score=9.0, risk_score=1.0, opportunity_score=5.0,
            momentum_score=8.0, alignment_score=9.0,
            resource_allocation=5.0, strategic_priority=4,
        ),
        DomainMetrics(
            domain=LifeDomain.LEARNING,
            performance_score=5.0, risk_score=3.0, opportunity_score=8.0,
            momentum_score=3.0, alignment_score=6.0,
            resource_allocation=10.0, strategic_priority=5,
        ),
    ]
    
    optimizer = DomainOptimizer()
    cycle = optimizer.run_optimization_cycle(metrics)
    recommendations = cycle.recommendations
    
    scorer = DomainScorer()
    health_scores = scorer.score_all_domains(metrics)
    
    print(f"Recommendations: {len(recommendations)}")
    print("Domain scores:")
    for d, s in sorted(health_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {d.value}: {s:.2f}")
    
    wealth_recs = [r for r in recommendations if r.target_domain == LifeDomain.WEALTH]
    learning_recs = [r for r in recommendations if r.target_domain == LifeDomain.LEARNING]
    
    status = "PASS" if len(wealth_recs) > 0 and len(learning_recs) > 0 else "CONCERN"
    print(f"Status: {status}")
    
    return ValidationResult("Multi-Domain Mixed", status, {
        "wealth_recs": len(wealth_recs),
        "learning_recs": len(learning_recs),
    })


def scenario_6_recovery():
    """Recovery/Stabilization - post-crisis."""
    print("\n" + "="*50)
    print("SCENARIO 6: RECOVERY/STABILIZATION")
    print("="*50)
    
    # All low but stable
    metrics = [
        DomainMetrics(
            domain=LifeDomain.HEALTH,
            performance_score=4.0, risk_score=5.0, opportunity_score=5.0,
            momentum_score=4.0, alignment_score=5.0,
            resource_allocation=33.0, strategic_priority=1,
        ),
        DomainMetrics(
            domain=LifeDomain.WEALTH,
            performance_score=4.0, risk_score=5.0, opportunity_score=4.0,
            momentum_score=4.0, alignment_score=5.0,
            resource_allocation=33.0, strategic_priority=1,
        ),
        DomainMetrics(
            domain=LifeDomain.CAREER,
            performance_score=4.0, risk_score=4.0, opportunity_score=6.0,
            momentum_score=4.0, alignment_score=5.0,
            resource_allocation=34.0, strategic_priority=2,
        ),
    ]
    
    optimizer = DomainOptimizer()
    cycle = optimizer.run_optimization_cycle(metrics)
    recommendations = cycle.recommendations
    
    print(f"Recommendations: {len(recommendations)}")
    
    aggressive = [r for r in recommendations if "increase" in str(r.action_type).lower() and r.priority > 0.8]
    recovery = [r for r in recommendations if "recovery" in str(r.action_type).lower() or "maintain" in str(r.action_type).lower()]
    
    print(f"Aggressive: {len(aggressive)}, Recovery: {len(recovery)}")
    
    status = "PASS" if len(aggressive) == 0 or len(recovery) > 0 else "CONCERN"
    print(f"Status: {status}")
    
    return ValidationResult("Recovery", status, {
        "aggressive": len(aggressive),
        "recovery": len(recovery),
    })


def run_all():
    """Run all validation scenarios."""
    print("\n" + "="*60)
    print("STRATEGIC INTELLIGENCE ENGINE - END-TO-END VALIDATION")
    print("="*60)
    
    results = [
        scenario_1_financial_stress(),
        scenario_2_opportunity_prioritization(),
        scenario_3_conflicting_goals(),
        scenario_4_risk_escalation(),
        scenario_5_multi_domain_mixed(),
        scenario_6_recovery(),
    ]
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    pass_count = sum(1 for r in results if r.status == "PASS")
    concern_count = sum(1 for r in results if r.status == "CONCERN")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    
    for r in results:
        print(f"{r.name}: {r.status}")
    
    print(f"\nPASS: {pass_count} | CONCERN: {concern_count} | FAIL: {fail_count}")
    
    return results


if __name__ == "__main__":
    run_all()
