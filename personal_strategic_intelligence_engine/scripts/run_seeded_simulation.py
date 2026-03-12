#!/usr/bin/env python
"""CLI script for running seeded simulations."""
import argparse
import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.simulation.seed_manager import create_seed_manager
from app.simulation.mock_data_generator import MockDataGenerator
from app.simulation.scenario_builder import ScenarioBuilder
from app.simulation.simulation_engine_v2 import SimulationEngine
from app.simulation.results_analyzer import ResultsAnalyzer
from app.simulation.report_builder_v2 import ReportBuilder
from app.simulation.simulation_types_v2 import ScenarioType


async def run_simulation(
    seed: str,
    scenario: str,
    days: int,
    output_path: str = None,
) -> dict:
    """Run a seeded simulation."""
    
    print(f"\n{'='*60}")
    print(f"SEEDED SIMULATION")
    print(f"{'='*60}")
    print(f"Seed: {seed}")
    print(f"Scenario: {scenario}")
    print(f"Duration: {days} days")
    print(f"{'='*60}\n")
    
    # Map scenario string to ScenarioType
    scenario_type = ScenarioType(scenario.lower())
    
    # Create components
    print("Initializing simulation components...")
    seed_manager = create_seed_manager(seed)
    mock_generator = MockDataGenerator(seed_manager)
    scenario_builder = ScenarioBuilder(seed_manager, mock_generator)
    
    # Build scenario
    print("Building scenario...")
    scenario_data = scenario_builder.build_scenario(scenario_type)
    print(f"  Scenario: {scenario_data['name']}")
    print(f"  Disruption chance: {scenario_data['disruption_chance']:.0%}")
    
    # Create engine
    print("\nRunning simulation...")
    engine = SimulationEngine(seed_manager, mock_generator, scenario_data)
    
    # Create initial results
    from app.simulation.simulation_types_v2 import (
        SimulationMetadata,
        SimulationResults,
    )
    
    metadata = SimulationMetadata(
        simulation_id=seed_manager.generate_string(8),
        seed=seed,
        scenario_type=scenario_type,
        duration_days=days,
        start_time=datetime.now(),
    )
    
    results = SimulationResults(
        metadata=metadata,
        initial_profile=scenario_data["initial_state"]["personal_profile"],
        initial_financial=scenario_data["initial_state"]["financial_state"],
        initial_goals=scenario_data["initial_state"]["goals"],
        initial_habits=scenario_data["initial_state"]["habits"],
        initial_domains=scenario_data["initial_state"]["domain_states"],
    )
    
    # Run simulation
    results = await engine.run_simulation(results, days)
    
    # Analyze results
    print("\nAnalyzing results...")
    analyzer = ResultsAnalyzer()
    scores = analyzer.analyze(results)
    patterns = analyzer.detect_patterns(results)
    
    # Build report
    print("Building report...")
    builder = ReportBuilder()
    report = builder.build_report(results)
    
    # Print summary
    print(f"\n{'='*60}")
    print("SIMULATION COMPLETE")
    print(f"{'='*60}")
    print(f"Days simulated: {len(results.daily_summaries)}")
    print(f"Weeks: {len(results.weekly_summaries)}")
    print(f"\nSCORES:")
    for score_name, score_value in scores.items():
        print(f"  {score_name}: {score_value:.1f}/10")
    
    print(f"\nWEAKNESSES DETECTED:")
    if report.weaknesses:
        for weakness in report.weaknesses[:5]:
            print(f"  - {weakness}")
    else:
        print("  None")
    
    print(f"\nRECOMMENDATIONS:")
    for rec in report.recommendations[:3]:
        print(f"  - {rec}")
    
    # Save report
    if output_path:
        report_dict = builder.export_report_dict(report)
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        print(f"\nReport saved to: {output_path}")
    
    return report


from datetime import datetime


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Run seeded simulations of the Personal Strategic Intelligence Engine"
    )
    
    parser.add_argument(
        "--seed",
        type=str,
        default="BOD-V4-SIM-BASELINE-001",
        help="Seed for deterministic simulation (default: BOD-V4-SIM-BASELINE-001)"
    )
    
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["baseline", "pressure", "opportunity", "recovery", "conflict", "volatility"],
        default="baseline",
        help="Simulation scenario type (default: baseline)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to simulate (default: 30)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save JSON report"
    )
    
    args = parser.parse_args()
    
    # Run the simulation
    try:
        report = asyncio.run(run_simulation(
            seed=args.seed,
            scenario=args.scenario,
            days=args.days,
            output_path=args.output,
        ))
        
        print(f"\n{'='*60}")
        print("FINAL STATE:")
        print(f"{'='*60}")
        if report.final_state.get("domain_summary"):
            print(f"{'Domain':<25} {'Perf':>8} {'Risk':>8}")
            print("-" * 45)
            for d in report.final_state["domain_summary"]:
                print(f"{d['domain']:<25} {d['performance']:>8.1f} {d['risk']:>8.1f}")
        
        print(f"\nSimulation completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
