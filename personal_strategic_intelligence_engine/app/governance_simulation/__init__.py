"""Governance Simulation & Stress Testing Framework.

This module provides comprehensive governance simulation capabilities to validate
the stability of the strategic operating system under various stress conditions.

Key Components:
- simulation_models: Data models for simulation scenarios and results
- scenario_generator: Generates different types of stress scenarios
- governance_simulator: Core orchestration engine for running simulations
- stability_metrics: Computes governance stability metrics
- oscillation_detector: Detects recommendation and policy oscillations
- doctrine_conflict_detector: Analyzes doctrine behavior inconsistencies
- policy_stress_tester: Tests approval tier and threshold behavior
- execution_feedback_analyzer: Analyzes execution-intent and feedback
- saturation_analyzer: Measures governance overload conditions
- simulation_reporter: Produces structured simulation reports

Safety:
All simulations run in REPLAY_MODE with LIVE_EXECUTION_ENABLED = False.
No real-world actions can be triggered during simulation.

Usage:
    from app.governance_simulation import run_governance_simulation, generate_simulation_report
    
    # Run a simulation
    result = run_governance_simulation(ScenarioType.STEADY_STATE, cycle_count=100)
    
    # Generate report
    report = generate_simulation_report([result])
"""
from app.governance_simulation.simulation_models import (
    ConflictSeverity,
    GovernanceSimulationCycle,
    GovernanceSimulationResult,
    GovernanceSimulationScenario,
    GovernanceStressReport,
    OscillationEvent,
    OscillationType,
    SaturationEvent,
    ScenarioType,
    SimulationCyclePhase,
    StabilityMetric,
    TierTransitionEvent,
    # Constants
    REPLAY_MODE,
    LIVE_EXECUTION_ENABLED,
    AUTO_EXECUTION_ENABLED,
    EXECUTION_MODE,
)
from app.governance_simulation.scenario_generator import (
    ScenarioGenerator,
    create_scenario_generator,
)
from app.governance_simulation.governance_simulator import (
    GovernanceSimulator,
    create_governance_simulator,
    run_governance_simulation,
)
from app.governance_simulation.stability_metrics import (
    compute_all_stability_metrics,
    compute_confidence_stability,
    compute_doctrine_consistency,
    compute_execution_pressure,
    compute_governance_load,
    compute_overall_stability,
    compute_recommendation_stability,
    compute_tier_stability,
)
from app.governance_simulation.oscillation_detector import (
    OscillationDetector,
    detect_oscillations,
)
from app.governance_simulation.doctrine_conflict_detector import (
    DoctrineConflictDetector,
    detect_doctrine_conflicts,
)
from app.governance_simulation.policy_stress_tester import (
    PolicyStressTester,
    run_policy_stress_test,
)
from app.governance_simulation.execution_feedback_analyzer import (
    ExecutionFeedbackAnalyzer,
    analyze_execution_feedback,
)
from app.governance_simulation.saturation_analyzer import (
    SaturationAnalyzer,
    analyze_saturation,
)
from app.governance_simulation.simulation_reporter import (
    SimulationReporter,
    generate_simulation_report,
    generate_text_report,
)

__all__ = [
    # Models
    "ConflictSeverity",
    "GovernanceSimulationCycle",
    "GovernanceSimulationResult",
    "GovernanceSimulationScenario",
    "GovernanceStressReport",
    "OscillationEvent",
    "OscillationType",
    "SaturationEvent",
    "ScenarioType",
    "SimulationCyclePhase",
    "StabilityMetric",
    "TierTransitionEvent",
    # Constants
    "REPLAY_MODE",
    "LIVE_EXECUTION_ENABLED",
    "AUTO_EXECUTION_ENABLED",
    "EXECUTION_MODE",
    # Generators
    "ScenarioGenerator",
    "create_scenario_generator",
    # Simulator
    "GovernanceSimulator",
    "create_governance_simulator",
    "run_governance_simulation",
    # Metrics
    "compute_all_stability_metrics",
    "compute_confidence_stability",
    "compute_doctrine_consistency",
    "compute_execution_pressure",
    "compute_governance_load",
    "compute_overall_stability",
    "compute_recommendation_stability",
    "compute_tier_stability",
    # Detectors
    "OscillationDetector",
    "detect_oscillations",
    "DoctrineConflictDetector",
    "detect_doctrine_conflicts",
    # Testers
    "PolicyStressTester",
    "run_policy_stress_test",
    # Analyzers
    "ExecutionFeedbackAnalyzer",
    "analyze_execution_feedback",
    "SaturationAnalyzer",
    "analyze_saturation",
    # Reporters
    "SimulationReporter",
    "generate_simulation_report",
    "generate_text_report",
]
