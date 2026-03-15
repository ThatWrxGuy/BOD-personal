"""Stability metrics computation for governance simulations.

Computes various stability metrics to assess governance behavior.
"""
import math
from datetime import datetime
from typing import Any, Dict, List

from app.governance_simulation.simulation_models import (
    GovernanceSimulationCycle,
    GovernanceSimulationResult,
    StabilityMetric,
)


def compute_recommendation_stability(
    cycles: List[GovernanceSimulationCycle],
) -> float:
    """Compute stability of recommendations across cycles.
    
    Returns a score from 0.0 (unstable) to 1.0 (stable).
    """
    if len(cycles) < 2:
        return 1.0
    
    # Track recommendation patterns
    recommendation_domains = []
    
    for cycle in cycles:
        domains = set()
        for rec in cycle.recommendations:
            domains.add(rec.get("domain", "unknown"))
        recommendation_domains.append(domains)
    
    # Calculate stability as consistency of domain coverage
    if not recommendation_domains:
        return 1.0
    
    # Count how often each domain appears
    domain_counts: Dict[str, int] = {}
    for domains in recommendation_domains:
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Calculate coefficient of variation for domain counts
    if not domain_counts:
        return 1.0
    
    counts = list(domain_counts.values())
    mean_count = sum(counts) / len(counts)
    
    if mean_count == 0:
        return 1.0
    
    # Standard deviation
    variance = sum((c - mean_count) ** 2 for c in counts) / len(counts)
    std_dev = math.sqrt(variance)
    
    # Coefficient of variation (lower = more stable)
    cv = std_dev / mean_count
    
    # Convert to stability score (1 - normalized cv)
    stability = 1.0 / (1.0 + cv)
    
    return max(0.0, min(1.0, stability))


def compute_doctrine_consistency(
    cycles: List[GovernanceSimulationCycle],
) -> float:
    """Compute consistency of doctrine evaluations.
    
    Returns a score from 0.0 (inconsistent) to 1.0 (consistent).
    """
    if len(cycles) < 2:
        return 1.0
    
    alignment_scores = []
    
    for cycle in cycles:
        if cycle.doctrine_assessment:
            score = cycle.doctrine_assessment.get("alignment_score", 0.0)
            alignment_scores.append(score)
    
    if len(alignment_scores) < 2:
        return 1.0
    
    # Calculate variance in alignment scores
    mean = sum(alignment_scores) / len(alignment_scores)
    variance = sum((s - mean) ** 2 for s in alignment_scores) / len(alignment_scores)
    std_dev = math.sqrt(variance)
    
    # Convert to consistency score (lower variance = higher consistency)
    # Max expected std_dev is 1.0 (range -1 to 1)
    consistency = 1.0 - std_dev
    
    return max(0.0, min(1.0, consistency))


def compute_tier_stability(
    cycles: List[GovernanceSimulationCycle],
) -> float:
    """Compute stability of approval tier transitions.
    
    Returns a score from 0.0 (unstable) to 1.0 (stable).
    """
    if len(cycles) < 2:
        return 1.0
    
    tiers = [cycle.current_tier for cycle in cycles if cycle.current_tier]
    
    if len(tiers) < 2:
        return 1.0
    
    # Count transitions
    transitions = 0
    for i in range(1, len(tiers)):
        if tiers[i] != tiers[i - 1]:
            transitions += 1
    
    # Calculate transition rate
    transition_rate = transitions / (len(tiers) - 1)
    
    # Convert to stability score (lower transitions = higher stability)
    stability = 1.0 - transition_rate
    
    return max(0.0, min(1.0, stability))


def compute_confidence_stability(
    cycles: List[GovernanceSimulationCycle],
) -> float:
    """Compute stability of confidence levels.
    
    Returns a score from 0.0 (unstable) to 1.0 (stable).
    """
    if len(cycles) < 2:
        return 1.0
    
    confidence_values = []
    
    for cycle in cycles:
        if cycle.doctrine_assessment:
            conf = cycle.doctrine_assessment.get("confidence", 0.5)
            confidence_values.append(conf)
    
    if len(confidence_values) < 2:
        return 1.0
    
    # Calculate variance in confidence
    mean = sum(confidence_values) / len(confidence_values)
    variance = sum((c - mean) ** 2 for c in confidence_values) / len(confidence_values)
    std_dev = math.sqrt(variance)
    
    # Convert to stability score
    stability = 1.0 - (std_dev * 2)  # Scale to 0-1
    
    return max(0.0, min(1.0, stability))


def compute_execution_pressure(
    cycles: List[GovernanceSimulationCycle],
) -> float:
    """Compute execution pressure (proportion of cycles with execution intents).
    
    Returns a score from 0.0 (low pressure) to 1.0 (high pressure).
    """
    if not cycles:
        return 0.0
    
    cycles_with_intents = sum(
        1 for cycle in cycles 
        if cycle.execution_intents and len(cycle.execution_intents) > 0
    )
    
    pressure = cycles_with_intents / len(cycles)
    
    return max(0.0, min(1.0, pressure))


def compute_governance_load(
    cycles: List[GovernanceSimulationCycle],
) -> float:
    """Compute governance load (recommendations and risk flags per cycle).
    
    Returns a score from 0.0 (low load) to 1.0 (high load).
    """
    if not cycles:
        return 0.0
    
    total_recommendations = sum(len(cycle.recommendations) for cycle in cycles)
    total_risk_flags = sum(
        len(cycle.doctrine_assessment.get("risk_flags", [])) 
        if cycle.doctrine_assessment else 0 
        for cycle in cycles
    )
    
    # Calculate average per cycle
    avg_recommendations = total_recommendations / len(cycles)
    avg_risk_flags = total_risk_flags / len(cycles)
    
    # Normalize (assuming max reasonable load is 10 recommendations or 5 risk flags per cycle)
    rec_score = min(avg_recommendations / 10.0, 1.0)
    flag_score = min(avg_risk_flags / 5.0, 1.0)
    
    # Combined load score
    load = (rec_score * 0.7) + (flag_score * 0.3)
    
    return max(0.0, min(1.0, load))


def compute_overall_stability(
    recommendation_stability: float,
    doctrine_consistency: float,
    tier_stability: float,
    confidence_stability: float,
    governance_load: float,
) -> float:
    """Compute overall governance stability score.
    
    Weighted average of component scores.
    """
    # Invert governance load (high load = lower stability)
    load_stability = 1.0 - governance_load
    
    # Weighted combination
    weights = {
        "recommendation": 0.25,
        "doctrine": 0.25,
        "tier": 0.20,
        "confidence": 0.15,
        "load": 0.15,
    }
    
    overall = (
        recommendation_stability * weights["recommendation"] +
        doctrine_consistency * weights["doctrine"] +
        tier_stability * weights["tier"] +
        confidence_stability * weights["confidence"] +
        load_stability * weights["load"]
    )
    
    return max(0.0, min(1.0, overall))


def compute_all_stability_metrics(
    result: GovernanceSimulationResult,
) -> List[StabilityMetric]:
    """Compute all stability metrics for a simulation result."""
    cycles = result.cycles
    
    # Compute individual metrics
    recommendation_stability = compute_recommendation_stability(cycles)
    doctrine_consistency = compute_doctrine_consistency(cycles)
    tier_stability = compute_tier_stability(cycles)
    confidence_stability = compute_confidence_stability(cycles)
    execution_pressure = compute_execution_pressure(cycles)
    governance_load = compute_governance_load(cycles)
    overall_stability = compute_overall_stability(
        recommendation_stability,
        doctrine_consistency,
        tier_stability,
        confidence_stability,
        governance_load,
    )
    
    # Update result
    result.recommendation_stability_score = recommendation_stability
    result.doctrine_consistency_score = doctrine_consistency
    result.tier_stability_score = tier_stability
    result.confidence_stability_score = confidence_stability
    result.execution_pressure_score = execution_pressure
    result.governance_load_score = governance_load
    result.overall_stability_score = overall_stability
    
    # Create metric objects
    metrics = [
        StabilityMetric(
            metric_name="recommendation_stability",
            value=recommendation_stability,
            details={"cycles_analyzed": len(cycles)},
        ),
        StabilityMetric(
            metric_name="doctrine_consistency",
            value=doctrine_consistency,
            details={"cycles_analyzed": len(cycles)},
        ),
        StabilityMetric(
            metric_name="tier_stability",
            value=tier_stability,
            details={"cycles_analyzed": len(cycles)},
        ),
        StabilityMetric(
            metric_name="confidence_stability",
            value=confidence_stability,
            details={"cycles_analyzed": len(cycles)},
        ),
        StabilityMetric(
            metric_name="execution_pressure",
            value=execution_pressure,
            details={"cycles_analyzed": len(cycles)},
        ),
        StabilityMetric(
            metric_name="governance_load",
            value=governance_load,
            details={"cycles_analyzed": len(cycles)},
        ),
        StabilityMetric(
            metric_name="overall_stability",
            value=overall_stability,
            details={
                "recommendation_weight": 0.25,
                "doctrine_weight": 0.25,
                "tier_weight": 0.20,
                "confidence_weight": 0.15,
                "load_weight": 0.15,
            },
        ),
    ]
    
    result.stability_metrics = metrics
    
    return metrics
