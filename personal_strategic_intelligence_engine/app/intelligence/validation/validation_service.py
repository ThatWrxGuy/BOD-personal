"""Validation Service - Central orchestration for system validation."""
import uuid
from typing import List

from app.intelligence.validation.simulation_models import (
    ValidationReport,
    SimulationScenario,
    SimulationResult,
    PerformanceComparison,
    SystemAuditReport,
)
from app.intelligence.validation.scenario_generator import get_scenario_generator
from app.intelligence.validation.baseline_simulator import get_baseline_simulator
from app.intelligence.validation.system_simulator import get_system_simulator
from app.intelligence.validation.performance_comparator import get_performance_comparator
from app.intelligence.validation.audit_engine import get_audit_engine


class ValidationService:
    """Central orchestration for system validation."""
    
    def __init__(self):
        self.scenario_generator = get_scenario_generator()
        self.baseline_simulator = get_baseline_simulator()
        self.system_simulator = get_system_simulator()
        self.comparator = get_performance_comparator()
        self.audit_engine = get_audit_engine()
        
        # History
        self.results: List[ValidationReport] = []
    
    def run_validation(
        self,
        num_scenarios: int = 5,
    ) -> ValidationReport:
        """Run complete validation."""
        
        # Generate scenarios
        scenarios = self.scenario_generator.generate_batch(num_scenarios)
        
        # Run baseline simulations
        baseline_results = []
        for scenario in scenarios:
            result = self.baseline_simulator.simulate(scenario)
            baseline_results.append(result)
        
        # Run system simulations
        system_results = []
        for scenario in scenarios:
            result = self.system_simulator.simulate(scenario)
            system_results.append(result)
        
        # Compare results
        comparisons = self.comparator.compare_batch(baseline_results, system_results)
        
        # Run audit
        audit_report = self.audit_engine.audit_system()
        
        # Calculate summary
        summary = self.comparator.get_summary()
        
        # Build report
        report = ValidationReport(
            id=str(uuid.uuid4())[:8],
            scenarios_run=len(scenarios),
            scenarios_succeeded=sum(1 for c in comparisons if c.system_wins),
            average_improvement=summary.get("average_improvement", 0),
            average_risk_reduction=summary.get("average_risk_reduction", 0),
            system_wins=summary.get("system_wins", 0),
            baseline_wins=summary.get("baseline_wins", 0),
            performance_comparisons=comparisons,
            audit_report=audit_report,
        )
        
        self.results.append(report)
        
        return report
    
    def run_scenario(
        self,
        scenario: SimulationScenario,
    ) -> tuple[SimulationResult, SimulationResult, PerformanceComparison]:
        """Run a single scenario through both simulators."""
        
        # Baseline
        baseline = self.baseline_simulator.simulate(scenario)
        
        # System
        system = self.system_simulator.simulate(scenario)
        
        # Compare
        comparison = self.comparator.compare(baseline, system)
        
        return baseline, system, comparison
    
    def get_audit_report(self) -> SystemAuditReport:
        """Get system audit report."""
        
        return self.audit_engine.audit_system()
    
    def get_results(self) -> List[ValidationReport]:
        """Get validation history."""
        
        return self.results


_service: ValidationService = None


def get_validation_service() -> ValidationService:
    """Get the global validation service."""
    global _service
    if _service is None:
        _service = ValidationService()
    return _service
