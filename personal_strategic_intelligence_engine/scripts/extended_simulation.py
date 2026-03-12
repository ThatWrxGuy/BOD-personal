#!/usr/bin/env python
"""Extended simulation script with detailed decision logging."""
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
    pass

class FinancialStateSim:
    pass

class StrategicGoalSim:
    pass

class HabitSim:
    pass

class DomainStateSim:
    pass


class MockDataGenerator:
    def __init__(self, seed_manager: SeedManager):
        self.seed = seed_manager
        self._rng = seed_manager.random
    
    def generate_personal_profile(self) -> PersonalProfileSim:
        rng = self._rng
        profile = PersonalProfileSim()
        age_ranges = ["20-25", "25-30", "30-35", "35-40", "40-45"]
        profile.age_range = rng.choice(age_ranges)
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
        domains = ["health", "wealth", "career", "learning", "relationships"]
        templates = {
            "health": ["Exercise regularly", "Improve sleep", "Reduce stress"],
            "wealth": ["Build emergency fund", "Pay off debt", "Invest more"],
            "career": ["Learn skills", "Network", "Get promotion"],
            "learning": ["Read books", "Take course", "Learn language"],
            "relationships": ["Family time", "Make friends", "Date nights"],
        }
        for i in range(8):
            domain = rng.choice(domains)
            goal = StrategicGoalSim()
            goal.id = f"goal-{i+1}"
            goal.title = rng.choice(templates.get(domain, ["Goal"]))
            goal.domain = domain
            goal.target_date = date.today() + timedelta(days=rng.randint(30, 180))
            goal.urgency_score = rng.random()
            goal.progress_percentage = rng.random() * 0.8
            goals.append(goal)
        return goals
    
    def generate_habits(self) -> List[HabitSim]:
        rng = self._rng
        habits = []
        templates = [
            ("Morning workout", "health", 0.7),
            ("Meditation", "health", 0.6),
            ("Track expenses", "wealth", 0.7),
            ("Clear inbox", "career", 0.7),
            ("Read 30 min", "learning", 0.6),
            ("Call family", "relationships", 0.5),
        ]
        for i, (name, domain, base_prob) in enumerate(templates):
            habit = HabitSim()
            habit.id = f"habit-{i+1}"
            habit.name = name
            habit.domain = domain
            habit.streak_count = rng.randint(0, 30)
            habit.completion_probability = base_prob + rng.uniform(-0.15, 0.15)
            habits.append(habit)
        return habits
    
    def generate_domain_states(self, scenario: str = "baseline") -> List[DomainStateSim]:
        rng = self._rng
        domains = ["health", "wealth", "career", "learning", "relationships", "personal_development", "operations", "strategic_projects"]
        states = []
        for domain in domains:
            state = DomainStateSim()
            state.domain = domain
            if scenario == "pressure":
                state.performance_score = rng.uniform(3.0, 6.0)
                state.risk_score = rng.uniform(4.0, 8.0)
            else:
                state.performance_score = rng.uniform(4.0, 7.0)
                state.risk_score = rng.uniform(2.0, 5.0)
            state.opportunity_score = rng.uniform(3.0, 7.0)
            state.momentum_score = rng.uniform(-2.0, 3.0)
            state.alignment_score = rng.uniform(5.0, 8.0)
            state.resource_allocation = 12.5 + rng.uniform(-3, 3)
            states.append(state)
        return states


# ============================================================
# SIMULATION ENGINE WITH DETAILED LOGGING
# ============================================================

class DecisionLog:
    def __init__(self):
        self.events: List[Dict] = []
        self.priority_decisions: List[Dict] = []
        self.resource_decisions: List[Dict] = []
        self.risk_alerts: List[Dict] = []
        self.opportunity_alerts: List[Dict] = []
        self.weekly_summaries: List[Dict] = []


class SimulationEngine:
    def __init__(self, seed_manager: SeedManager, mock_generator: MockDataGenerator, scenario: Dict):
        self.seed = seed_manager
        self.mock = mock_generator
        self.rng = seed_manager.random
        self.scenario = scenario
        self.disruption_chance = scenario.get("disruption_chance", 0.15)
        self.current_domains: List[DomainStateSim] = []
        self.scheduled_events = scenario.get("scheduled_events", [])
        self.decision_log = DecisionLog()
    
    async def run_simulation(self, initial_domains: List[DomainStateSim], days: int) -> Dict:
        self.current_domains = initial_domains
        
        for day in range(1, days + 1):
            self._simulate_day(day)
            
            # Weekly summary
            if day % 7 == 0:
                self._create_weekly_summary(day)
        
        return {
            "daily_summaries": [],  # Simplified for now
            "final_domains": self.current_domains,
            "decision_log": self.decision_log,
        }
    
    def _simulate_day(self, day: int):
        current_date = date.today() + timedelta(days=day)
        
        # Check for scheduled events
        events_today = [e for e in self.scheduled_events if e.get("day") == day]
        
        # Random disruptions
        if self.rng.random() < self.disruption_chance:
            event_types = [
                ("Unexpected expense", "wealth", 0.5, "Financial disruption"),
                ("Workload surge", "career", 0.6, "Productivity impact"),
                ("Health issue", "health", 0.4, "Energy reduction"),
                ("Schedule collapse", "operations", 0.7, "Chaos"),
                ("Motivation spike", "learning", -0.3, "Boost"),
                ("Side income", "wealth", -0.4, "Gain"),
                ("Relationship event", "relationships", 0.5, "Attention needed"),
            ]
            evt = self.rng.choice(event_types)
            events_today.append({
                "day": day,
                "description": evt[0],
                "domain": evt[1],
                "severity": evt[2],
                "type": evt[3]
            })
        
        # Process events
        for event in events_today:
            self._process_event(day, event)
        
        # Detect risks
        self._detect_risks(day)
        
        # Detect opportunities
        self._detect_opportunities(day)
        
        # Priority decisions
        self._make_priority_decisions(day)
        
        # Resource allocation decisions
        self._allocate_resources(day)
    
    def _process_event(self, day: int, event: Dict):
        desc = event.get("description", "Event")
        domain = event.get("domain", "operations")
        severity = event.get("severity", 0.5)
        
        # Log event
        self.decision_log.events.append({
            "day": day,
            "type": event.get("type", "disruption"),
            "description": desc,
            "domain": domain,
            "severity": severity,
            "action_taken": f"Adjust {domain} domain focus"
        })
        
        # Apply effects
        for d in self.current_domains:
            if d.domain == domain:
                effect = -severity if severity > 0 else abs(severity)
                d.performance_score = max(0, min(10, d.performance_score + effect))
                if severity > 0:
                    d.risk_score = min(10, d.risk_score + severity * 0.3)
    
    def _detect_risks(self, day: int):
        for d in self.current_domains:
            if d.risk_score > 7:
                self.decision_log.risk_alerts.append({
                    "day": day,
                    "domain": d.domain,
                    "risk_level": d.risk_score,
                    "recommendation": f"Immediate attention needed for {d.domain}",
                    "action": "Increase monitoring"
                })
            elif d.risk_score > 5:
                self.decision_log.risk_alerts.append({
                    "day": day,
                    "domain": d.domain,
                    "risk_level": d.risk_score,
                    "recommendation": f"Watch {d.domain} closely",
                    "action": "Schedule review"
                })
    
    def _detect_opportunities(self, day: int):
        for d in self.current_domains:
            if d.opportunity_score > 7:
                self.decision_log.opportunity_alerts.append({
                    "day": day,
                    "domain": d.domain,
                    "opportunity_level": d.opportunity_score,
                    "recommendation": f"Capitalize on {d.domain} opportunity",
                    "action": "Increase investment"
                })
    
    def _make_priority_decisions(self, day: int):
        # Sort domains by performance
        sorted_domains = sorted(self.current_domains, key=lambda d: d.performance_score)
        
        # Low performing domains need attention
        for d in sorted_domains[:2]:
            if d.performance_score < 4:
                self.decision_log.priority_decisions.append({
                    "day": day,
                    "domain": d.domain,
                    "current_score": round(d.performance_score, 2),
                    "decision": "INCREASE_PRIORITY",
                    "reason": f"Low performance ({d.performance_score:.1f}) below threshold",
                    "action": f"Shift resources to {d.domain}"
                })
    
    def _allocate_resources(self, day: int):
        # Calculate ideal allocation based on performance
        total_perf = sum(d.performance_score for d in self.current_domains)
        
        for d in self.current_domains:
            ideal_alloc = (d.performance_score / total_perf) * 100 if total_perf > 0 else 12.5
            diff = ideal_alloc - d.resource_allocation
            
            if abs(diff) > 5:  # Significant deviation
                self.decision_log.resource_decisions.append({
                    "day": day,
                    "domain": d.domain,
                    "current_allocation": round(d.resource_allocation, 1),
                    "ideal_allocation": round(ideal_alloc, 1),
                    "adjustment": "INCREASE" if diff > 0 else "DECREASE",
                    "amount": round(abs(diff), 1),
                    "reason": "Rebalance for optimal performance"
                })
                d.resource_allocation = d.resource_allocation + (diff * 0.2)  # Gradual adjustment
    
    def _create_weekly_summary(self, day: int):
        week = day // 7
        
        # Calculate weekly stats
        events_this_week = [e for e in self.decision_log.events if e["day"] > day - 7]
        risks_this_week = [r for r in self.decision_log.risk_alerts if r["day"] > day - 7]
        opps_this_week = [o for o in self.decision_log.opportunity_alerts if o["day"] > day - 7]
        
        self.decision_log.weekly_summaries.append({
            "week": week,
            "day_range": f"Day {day-6} to Day {day}",
            "events_count": len(events_this_week),
            "risks_count": len(risks_this_week),
            "opportunities_count": len(opps_this_week),
            "domains_requiring_attention": list(set([r["domain"] for r in risks_this_week])),
            "key_decision": self._summarize_weekly_decision(week)
        })
    
    def _summarize_weekly_decision(self, week: int):
        # Find most common priority decision this week
        week_decisions = [d for d in self.decision_log.priority_decisions 
                         if d["day"] > (week-1)*7 and d["day"] <= week*7]
        
        if week_decisions:
            most_urgent = week_decisions[0]
            return f"Prioritize {most_urgent['domain']} domain"
        
        return "Maintain current priorities"


async def run_simulation(seed: str, scenario: str, days: int, output_path: str = None) -> Dict:
    print(f"\n{'='*70}")
    print(f"EXTENDED SIMULATION WITH DETAILED DECISION LOGGING")
    print(f"{'='*70}")
    print(f"Seed: {seed}")
    print(f"Scenario: {scenario}")
    print(f"Duration: {days} days")
    print(f"{'='*70}\n")
    
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
    print(f"  Goals: {len(goals)}, Habits: {len(habits)}, Domains: {len(domains)}")
    
    # Build scenario
    scenario_data = {
        "name": f"{scenario.title()} Scenario",
        "disruption_chance": {"baseline": 0.15, "pressure": 0.3}.get(scenario, 0.2),
        "scheduled_events": [],
    }
    
    # Generate scheduled events
    event_templates = [
        ("Monthly review", "strategic_projects", 0.3),
        ("Quarterly planning", "operations", 0.4),
        ("Performance review", "career", 0.5),
    ]
    for i in range(min(10, days // 20)):
        day = (i + 1) * 20
        evt = event_templates[i % len(event_templates)]
        scenario_data["scheduled_events"].append({
            "day": day,
            "description": evt[0],
            "domain": evt[1],
            "severity": evt[2],
            "type": "scheduled"
        })
    
    # Run simulation
    print(f"\nRunning {days} day simulation...")
    engine = SimulationEngine(seed_manager, mock, scenario_data)
    results = await engine.run_simulation(domains, days)
    
    # Print detailed decision log
    log = results["decision_log"]
    
    print(f"\n{'='*70}")
    print("SIMULATION DECISIONS LOG")
    print(f"{'='*70}")
    
    # Total events
    print(f"\n📊 SUMMARY STATISTICS")
    print(f"   Total events: {len(log.events)}")
    print(f"   Priority decisions: {len(log.priority_decisions)}")
    print(f"   Resource reallocations: {len(log.resource_decisions)}")
    print(f"   Risk alerts: {len(log.risk_alerts)}")
    print(f"   Opportunity alerts: {len(log.opportunity_alerts)}")
    print(f"   Weekly summaries: {len(log.weekly_summaries)}")
    
    # Priority decisions
    print(f"\n🎯 PRIORITY DECISIONS (first 20)")
    print("-" * 70)
    for d in log.priority_decisions[:20]:
        print(f"   Day {d['day']:3d}: {d['decision']:20s} for {d['domain']:25s} - {d['reason'][:30]}")
    
    if len(log.priority_decisions) > 20:
        print(f"   ... and {len(log.priority_decisions) - 20} more")
    
    # Resource decisions
    print(f"\n💰 RESOURCE ALLOCATION DECISIONS (first 20)")
    print("-" * 70)
    for d in log.resource_decisions[:20]:
        print(f"   Day {d['day']:3d}: {d['adjustment']:8s} {d['amount']:5.1f}% for {d['domain']:20s}")
    
    if len(log.resource_decisions) > 20:
        print(f"   ... and {len(log.resource_decisions) - 20} more")
    
    # Risk alerts
    print(f"\n⚠️ RISK ALERTS (first 15)")
    print("-" * 70)
    for r in log.risk_alerts[:15]:
        print(f"   Day {r['day']:3d}: {r['domain']:25s} - Risk: {r['risk_level']:.1f} - {r['action']}")
    
    if len(log.risk_alerts) > 15:
        print(f"   ... and {len(log.risk_alerts) - 15} more")
    
    # Weekly summaries
    print(f"\n📅 WEEKLY SUMMARIES")
    print("-" * 70)
    for w in log.weekly_summaries:
        print(f"   Week {w['week']:2d}: {w['day_range']} | Events: {w['events_count']:2d} | Risks: {w['risks_count']} | Opps: {w['opportunities_count']:2d}")
        print(f"            Decision: {w['key_decision']}")
    
    # Final state
    print(f"\n{'='*70}")
    print("FINAL DOMAIN STATE")
    print(f"{'='*70}")
    print(f"{'Domain':<25} {'Perf':>8} {'Risk':>8} {'Opp':>8} {'Alloc':>8}")
    print("-" * 70)
    for d in results["final_domains"]:
        print(f"{d.domain:<25} {d.performance_score:>8.1f} {d.risk_score:>8.1f} {d.opportunity_score:>8.1f} {d.resource_allocation:>8.1f}")
    
    # Save detailed report
    if output_path:
        report = {
            "seed": seed,
            "scenario": scenario,
            "days": days,
            "summary": {
                "total_events": len(log.events),
                "priority_decisions": len(log.priority_decisions),
                "resource_decisions": len(log.resource_decisions),
                "risk_alerts": len(log.risk_alerts),
                "opportunity_alerts": len(log.opportunity_alerts),
            },
            "priority_decisions": log.priority_decisions,
            "resource_decisions": log.resource_decisions,
            "risk_alerts": log.risk_alerts,
            "opportunity_alerts": log.opportunity_alerts,
            "weekly_summaries": log.weekly_summaries,
            "events": log.events[:50],  # First 50 events
            "final_domains": [
                {"domain": d.domain, "performance": d.performance_score, "risk": d.risk_score}
                for d in results["final_domains"]
            ]
        }
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {output_path}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Run extended simulations with detailed logging")
    parser.add_argument("--seed", type=str, default="BOD-V4-SIM-BASELINE-001")
    parser.add_argument("--scenario", type=str, default="baseline")
    parser.add_argument("--days", type=int, default=256)
    parser.add_argument("--output", type=str)
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_simulation(args.seed, args.scenario, args.days, args.output))
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
