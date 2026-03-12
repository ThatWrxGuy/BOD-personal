#!/usr/bin/env python
"""Standalone CLI script for running seeded simulations."""
import argparse
import asyncio
import json
import sys
import os
import hashlib
import random
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any


# ============================================================
# SEED MANAGER
# ============================================================

class SeedManager:
    """Manages deterministic seed generation."""
    
    def __init__(self, seed: str):
        self.original_seed = seed.upper().strip().replace(" ", "-")
        self._random_generator = self._create_deterministic_generator(self.original_seed)
    
    def _create_deterministic_generator(self, seed: str) -> random.Random:
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        seed_int = int(seed_hash[:16], 16) % (2**31)
        return random.Random(seed_int)
    
    @property
    def random(self) -> random.Random:
        return self._random_generator
    
    def get_seed_hash(self) -> str:
        return hashlib.sha256(self.original_seed.encode()).hexdigest()
    
    def generate_string(self, length: int = 10) -> str:
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(self._random_generator.choice(chars) for _ in range(length))


# ============================================================
# MOCK DATA GENERATOR
# ============================================================

class PersonalProfileSim:
    age_range: str
    work_hours: float
    available_time: float
    energy_baseline: float
    stress_baseline: float
    focus_stability: float
    life_complexity: float


class FinancialStateSim:
    monthly_income: float
    fixed_expenses: float
    debt_balances: float
    investment_balances: float
    liquidity: float
    cash_flow_pressure: float


class StrategicGoalSim:
    id: str
    title: str
    description: str
    domain: str
    target_date: date
    urgency_score: float
    progress_percentage: float


class HabitSim:
    id: str
    name: str
    domain: str
    streak_count: int
    completion_probability: float
    focus_adherence: float


class DomainStateSim:
    domain: str
    performance_score: float
    risk_score: float
    opportunity_score: float
    momentum_score: float
    alignment_score: float
    resource_allocation: float


class MockDataGenerator:
    """Generates synthetic mock data from a seed."""
    
    def __init__(self, seed_manager: SeedManager):
        self.seed = seed_manager
        self._rng = seed_manager.random
    
    def generate_personal_profile(self) -> PersonalProfileSim:
        rng = self._rng
        
        age_ranges = ["20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "50-55"]
        age_weights = [0.1, 0.15, 0.2, 0.2, 0.15, 0.12, 0.08]
        age_range = rng.choices(age_ranges, weights=age_weights)[0]
        
        profile = PersonalProfileSim()
        profile.age_range = age_range
        profile.work_hours = rng.randint(30, 60) + rng.random()
        profile.available_time = rng.randint(10, 30) + rng.random()
        profile.energy_baseline = 0.3 + rng.random() * 0.6
        profile.stress_baseline = 0.2 + rng.random() * 0.6
        profile.focus_stability = 0.4 + rng.random() * 0.55
        profile.life_complexity = 0.2 + rng.random() * 0.7
        
        return profile
    
    def generate_financial_state(self, scenario: str = "baseline") -> FinancialStateSim:
        rng = self._rng
        
        fin = FinancialStateSim()
        fin.monthly_income = rng.randint(3000, 15000) + rng.random() * 1000
        fin.fixed_expenses = rng.randint(2000, 6000) + rng.random() * 500
        fin.debt_balances = rng.randint(0, 20000) if scenario != "pressure" else rng.randint(10000, 50000)
        fin.investment_balances = rng.randint(0, 100000)
        fin.liquidity = rng.randint(1000, 20000)
        fin.cash_flow_pressure = (fin.fixed_expenses / fin.monthly_income) if fin.monthly_income > 0 else 0.5
        
        return fin
    
    def generate_strategic_goals(self) -> List[StrategicGoalSim]:
        rng = self._rng
        
        goals = []
        domains = ["health", "wealth", "career", "learning", "relationships", "personal_development"]
        
        goal_templates = {
            "health": ["Exercise regularly", "Improve sleep", "Reduce stress"],
            "wealth": ["Build emergency fund", "Pay off debt", "Increase investments"],
            "career": ["Learn new skills", "Network expansion", "Performance improvement"],
            "learning": ["Read books", "Complete course", "Learn language"],
            "relationships": ["Family time", "Social connections", "Date nights"],
            "personal_development": ["Meditation", "Journaling", "Time management"],
        }
        
        for i in range(8):
            domain = rng.choice(domains)
            titles = goal_templates.get(domain, ["Goal"])
            title = rng.choice(titles)
            
            goal = StrategicGoalSim()
            goal.id = f"goal-{i+1}"
            goal.title = title
            goal.description = f"Goal to {title.lower()}"
            goal.domain = domain
            goal.target_date = date.today() + timedelta(days=rng.randint(30, 180))
            goal.urgency_score = rng.random()
            goal.progress_percentage = rng.random() * 0.8
            goals.append(goal)
        
        return goals
    
    def generate_habits(self) -> List[HabitSim]:
        rng = self._rng
        
        habits = []
        
        habit_templates = [
            ("Morning workout", "health", 0.7),
            ("Meditation", "health", 0.6),
            ("Track expenses", "wealth", 0.7),
            ("Clear inbox", "career", 0.7),
            ("Read 30 minutes", "learning", 0.6),
            ("Call family", "relationships", 0.5),
        ]
        
        for i, (name, domain, base_prob) in enumerate(habit_templates):
            habit = HabitSim()
            habit.id = f"habit-{i+1}"
            habit.name = name
            habit.domain = domain
            habit.streak_count = rng.randint(0, 30)
            habit.completion_probability = base_prob + rng.uniform(-0.15, 0.15)
            habit.focus_adherence = base_prob + rng.uniform(-0.1, 0.1)
            habits.append(habit)
        
        return habits
    
    def generate_domain_states(self, scenario: str = "baseline") -> List[DomainStateSim]:
        rng = self._rng
        
        domains = [
            "health", "wealth", "career", "learning", 
            "relationships", "personal_development", "operations", "strategic_projects"
        ]
        
        states = []
        
        for domain in domains:
            if scenario == "pressure":
                base_perf = rng.uniform(3.0, 6.0)
                base_risk = rng.uniform(4.0, 8.0)
            else:
                base_perf = rng.uniform(4.0, 7.0)
                base_risk = rng.uniform(2.0, 5.0)
            
            state = DomainStateSim()
            state.domain = domain
            state.performance_score = base_perf
            state.risk_score = base_risk
            state.opportunity_score = rng.uniform(3.0, 7.0)
            state.momentum_score = rng.uniform(-2.0, 3.0)
            state.alignment_score = rng.uniform(5.0, 8.0)
            state.resource_allocation = 12.5 + rng.uniform(-3, 3)
            states.append(state)
        
        return states


# ============================================================
# SIMULATION ENGINE
# ============================================================

class SimulatedEvent:
    def __init__(self, description: str, affected_domain: str, severity: float):
        self.description = description
        self.affected_domain = affected_domain
        self.severity = severity


class DailySummary:
    def __init__(self, day: int, date_: date):
        self.day = day
        self.date = date_
        self.events_triggered: List[str] = []
        self.risks_detected: List[str] = []
        self.opportunities_detected: List[str] = []
        self.priority_shifts: List[Dict] = []
        self.summary = ""


class SimulationEngine:
    """Runs the simulation timeline."""
    
    def __init__(self, seed_manager: SeedManager, mock_generator: MockDataGenerator, scenario: Dict):
        self.seed = seed_manager
        self.mock = mock_generator
        self.rng = seed_manager.random
        self.scenario = scenario
        self.disruption_chance = scenario.get("disruption_chance", 0.15)
        self.current_domains: List[DomainStateSim] = []
        self.scheduled_events = scenario.get("scheduled_events", [])
    
    async def run_simulation(self, initial_domains: List[DomainStateSim], days: int) -> Dict:
        """Run simulation for specified days."""
        
        self.current_domains = initial_domains
        daily_summaries = []
        
        for day in range(1, days + 1):
            summary = self._simulate_day(day)
            daily_summaries.append(summary)
        
        return {
            "daily_summaries": daily_summaries,
            "final_domains": self.current_domains,
        }
    
    def _simulate_day(self, day: int) -> DailySummary:
        current_date = date.today() + timedelta(days=day)
        summary = DailySummary(day, current_date)
        
        # Check for scheduled events
        events_today = [e for e in self.scheduled_events if e.get("day") == day]
        
        # Random disruptions
        if self.rng.random() < self.disruption_chance:
            event_types = [
                ("Unexpected expense", "wealth", 0.5),
                ("Workload surge", "career", 0.6),
                ("Health setback", "health", 0.4),
                ("Schedule collapse", "operations", 0.7),
            ]
            evt = self.rng.choice(event_types)
            events_today.append({"description": evt[0], "domain": evt[1], "severity": evt[2]})
        
        # Process events
        for event in events_today:
            summary.events_triggered.append(event.get("description", "Event"))
            # Apply effects
            for d in self.current_domains:
                if d.domain == event.get("domain"):
                    d.performance_score = max(0, min(10, d.performance_score + self.rng.uniform(-0.5, 0.5)))
        
        # Detect risks and opportunities
        for d in self.current_domains:
            if d.risk_score > 7:
                summary.risks_detected.append(f"High risk in {d.domain}")
            if d.opportunity_score > 7:
                summary.opportunities_detected.append(f"Opportunity in {d.domain}")
        
        # Priority shifts for low-performing domains
        low_domains = sorted(self.current_domains, key=lambda d: d.performance_score)[:2]
        for d in low_domains:
            if d.performance_score < 4:
                summary.priority_shifts.append({"domain": d.domain, "action": "increase_priority"})
        
        summary.summary = f"Day {day}: {len(summary.events_triggered)} events, {len(summary.risks_detected)} risks"
        
        return summary


# ============================================================
# RESULTS ANALYZER
# ============================================================

class ResultsAnalyzer:
    """Analyzes simulation results."""
    
    def analyze(self, results: Dict) -> Dict[str, float]:
        scores = {}
        
        daily_summaries = results.get("daily_summaries", [])
        
        if not daily_summaries:
            return {"stability": 5.0, "responsiveness": 5.0, "balance": 5.0}
        
        # Stability: variance in performance
        if daily_summaries:
            avg_perfs = []
            for d in daily_summaries:
                # Simple calculation
                avg_perfs.append(len(d.events_triggered) * 0.1)
            
            variance = (sum(avg_perfs) / len(avg_perfs)) if avg_perfs else 0
            scores["stability"] = max(0, min(10, 10 - variance))
        
        # Responsiveness
        total_shifts = sum(len(d.priority_shifts) for d in daily_summaries)
        scores["responsiveness"] = min(10, total_shifts / 2)
        
        # Balance
        final_domains = results.get("final_domains", [])
        if final_domains:
            perfs = [d.performance_score for d in final_domains]
            avg = sum(perfs) / len(perfs)
            variance = sum((p - avg) ** 2 for p in perfs) / len(perfs)
            scores["balance"] = max(0, min(10, 10 - variance ** 0.5))
        else:
            scores["balance"] = 5.0
        
        return scores


# ============================================================
# MAIN RUNNER
# ============================================================

async def run_simulation(seed: str, scenario: str, days: int, output_path: str = None) -> Dict:
    """Run a seeded simulation."""
    
    print(f"\n{'='*60}")
    print(f"SEEDED SIMULATION")
    print(f"{'='*60}")
    print(f"Seed: {seed}")
    print(f"Scenario: {scenario}")
    print(f"Duration: {days} days")
    print(f"{'='*60}\n")
    
    # Initialize
    seed_manager = SeedManager(seed)
    print(f"Seed hash: {seed_manager.get_seed_hash()[:16]}...")
    
    mock = MockDataGenerator(seed_manager)
    
    # Generate initial state
    print("\nGenerating initial state...")
    profile = mock.generate_personal_profile()
    financial = mock.generate_financial_state(scenario)
    goals = mock.generate_strategic_goals()
    habits = mock.generate_habits()
    domains = mock.generate_domain_states(scenario)
    
    print(f"  Profile: {profile.age_range}, work {profile.work_hours:.0f}h/week")
    print(f"  Financial: ${financial.monthly_income:.0f}/month, ${financial.debt_balances:.0f} debt")
    print(f"  Goals: {len(goals)}")
    print(f"  Habits: {len(habits)}")
    print(f"  Domains: {len(domains)}")
    
    # Build scenario
    scenario_data = {
        "name": f"{scenario.title()} Scenario",
        "disruption_chance": {"baseline": 0.15, "pressure": 0.3, "opportunity": 0.15}.get(scenario, 0.2),
        "scheduled_events": [],
    }
    
    # Generate some scheduled events
    for i in range(min(5, days // 5)):
        day = (i + 1) * 5
        scenario_data["scheduled_events"].append({
            "day": day,
            "description": f"Planned event {i+1}",
            "domain": "operations",
            "severity": 0.4,
        })
    
    # Run simulation
    print(f"\nRunning {days} day simulation...")
    engine = SimulationEngine(seed_manager, mock, scenario_data)
    results = await engine.run_simulation(domains, days)
    
    # Analyze
    print("Analyzing results...")
    analyzer = ResultsAnalyzer()
    scores = analyzer.analyze(results)
    
    # Print summary
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"\nSCORES:")
    for name, value in scores.items():
        print(f"  {name}: {value:.1f}/10")
    
    # Save report
    report = {
        "seed": seed,
        "scenario": scenario,
        "days": days,
        "scores": scores,
        "final_domains": [
            {"domain": d.domain, "performance": d.performance_score, "risk": d.risk_score}
            for d in results["final_domains"]
        ],
    }
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {output_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Run seeded simulations")
    parser.add_argument("--seed", type=str, default="BOD-V4-SIM-BASELINE-001")
    parser.add_argument("--scenario", type=str, choices=["baseline", "pressure", "opportunity", "recovery", "conflict", "volatility"], default="baseline")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", type=str)
    
    args = parser.parse_args()
    
    try:
        report = asyncio.run(run_simulation(args.seed, args.scenario, args.days, args.output))
        
        print(f"\n{'='*60}")
        print("FINAL DOMAIN STATE:")
        print(f"{'='*60}")
        print(f"{'Domain':<25} {'Perf':>8} {'Risk':>8}")
        print("-" * 45)
        for d in report["final_domains"]:
            print(f"{d['domain']:<25} {d['performance']:>8.1f} {d['risk']:>8.1f}")
        
        print("\nSimulation completed successfully!")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
