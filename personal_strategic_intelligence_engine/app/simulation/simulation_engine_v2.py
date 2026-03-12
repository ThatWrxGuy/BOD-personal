"""Simulation Engine - Runs the simulation timeline and invokes platform subsystems."""
import logging
from datetime import datetime, date, timedelta
from typing import Any, Optional

from app.simulation.seed_manager import SeedManager
from app.simulation.mock_data_generator import MockDataGenerator
from app.simulation.simulation_types_v2 import (
    SimulationResults,
    SimulationMetadata,
    SimulationStatus,
    DailySummary,
    WeeklySummary,
    SimulatedEvent,
    EventType,
    ScenarioType,
    DomainStateSim,
    SubsystemStatus,
)

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Runs the simulation timeline."""
    
    def __init__(
        self, 
        seed_manager: SeedManager, 
        mock_generator: MockDataGenerator,
        scenario: dict
    ):
        self.seed = seed_manager
        self.mock = mock_generator
        self.rng = seed_manager.random
        self.scenario = scenario
        self.scheduled_events = scenario.get("scheduled_events", [])
        self.disruption_chance = scenario.get("disruption_chance", 0.15)
        
        # Current state
        self.current_domains: list[DomainStateSim] = []
        self.current_day = 0
        self.subsystems_invoked: list[SubsystemStatus] = []
    
    async def run_simulation(
        self, 
        results: SimulationResults, 
        duration_days: int
    ) -> SimulationResults:
        """Run the simulation for specified days."""
        
        logger.info(f"Running simulation for {duration_days} days")
        
        # Initialize current state
        self.current_domains = [d.copy() for d in results.initial_domains]
        
        # Run daily simulation
        for day in range(1, duration_days + 1):
            self.current_day = day
            daily_summary = await self._simulate_day(day)
            results.daily_summaries.append(daily_summary)
            
            # Weekly summary
            if day % 7 == 0:
                week = day // 7
                week_summary = await self._create_weekly_summary(week, results.daily_summaries[-7:])
                results.weekly_summaries.append(week_summary)
        
        # Final state
        results.final_domains = self.current_domains
        
        # Run analysis
        results = self._analyze_results(results)
        
        # Update metadata
        results.metadata.subsystems_used = self.subsystems_invoked
        
        logger.info(f"Simulation completed: {len(results.daily_summaries)} days")
        
        return results
    
    async def _simulate_day(self, day: int) -> DailySummary:
        """Simulate a single day."""
        
        current_date = date.today() + timedelta(days=day)
        
        # Morning state (domain scores at start of day)
        morning_state = {
            d.domain: {
                "performance": d.performance_score,
                "risk": d.risk_score,
                "opportunity": d.opportunity_score,
                "momentum": d.momentum_score,
            }
            for d in self.current_domains
        }
        
        # Check for scheduled event
        events_today = [e for e in self.scheduled_events if e.get("day") == day]
        
        # Maybe trigger random disruption
        if self.rng.random() < self.disruption_chance:
            disruption = self._generate_random_disruption(day)
            events_today.append(disruption)
        
        # Process events
        events_triggered = []
        for event in events_today:
            processed = self._process_event(event, day)
            events_triggered.append(processed.description)
            self._apply_event_effects(processed)
        
        # Update daily state
        risks_detected = self._detect_risks()
        opportunities_detected = self._detect_opportunities()
        priority_shifts = self._calculate_priority_shifts()
        
        # Simulate habit performance
        habit_performance = self._simulate_habits()
        
        # Domain changes from yesterday
        domain_changes = self._calculate_domain_changes()
        
        # End of day summary
        summary_text = f"Day {day}: {len(events_triggered)} events, {len(risks_detected)} risks, {len(opportunities_detected)} opportunities"
        
        return DailySummary(
            day=day,
            date=current_date,
            morning_state=morning_state,
            events_triggered=events_triggered,
            risks_detected=risks_detected,
            opportunities_detected=opportunities_detected,
            priority_shifts=priority_shifts,
            domain_changes=domain_changes,
            habit_performance=habit_performance,
            summary=summary_text,
        )
    
    def _generate_random_disruption(self, day: int) -> dict:
        """Generate a random disruption event."""
        
        event_types = [
            EventType.UNEXPECTED_EXPENSE,
            EventType.WORKLOAD_SURGE,
            EventType.MISSED_HABIT_STREAK,
            EventType.HEALTH_SETBACK,
            EventType.SCHEDULE_COLLAPSE,
        ]
        
        event_type = self.rng.choice(event_types)
        severity = self.rng.uniform(0.3, 0.7)
        
        domain_map = {
            EventType.UNEXPECTED_EXPENSE: "wealth",
            EventType.WORKLOAD_SURGE: "career",
            EventType.MISSED_HABIT_STREAK: "health",
            EventType.HEALTH_SETBACK: "health",
            EventType.SCHEDULE_COLLAPSE: "operations",
        }
        
        return {
            "id": f"disruption-{day}",
            "day": day,
            "event_type": event_type,
            "affected_domain": domain_map.get(event_type, "operations"),
            "severity": severity,
            "description": f"Random disruption: {event_type.value}",
            "expected_effect": "Various impacts",
            "is_disruption": True,
        }
    
    def _process_event(self, event: dict, day: int) -> SimulatedEvent:
        """Process an event and return simulated event."""
        
        return SimulatedEvent(
            id=event.get("id", f"event-{day}"),
            timestamp=datetime.now(),
            event_type=event.get("event_type", EventType.UNEXPECTED_EXPENSE),
            affected_domain=event.get("affected_domain", "operations"),
            severity=event.get("severity", 0.5),
            description=event.get("description", "Event occurred"),
            expected_effect=event.get("expected_effect", ""),
        )
    
    def _apply_event_effects(self, event: SimulatedEvent) -> None:
        """Apply event effects to domains."""
        
        domain = event.affected_domain
        severity = event.severity
        
        # Find affected domain
        for d in self.current_domains:
            if d.domain == domain:
                # Apply effects based on event type
                if event.event_type == EventType.UNEXPECTED_EXPENSE:
                    d.performance_score = max(0, d.performance_score - severity * 0.5)
                    d.risk_score = min(10, d.risk_score + severity * 0.5)
                elif event.event_type == EventType.WORKLOAD_SURGE:
                    d.performance_score = min(10, d.performance_score + severity * 0.3)
                    d.risk_score = min(10, d.risk_score + severity * 0.4)
                elif event.event_type == EventType.MISSED_HABIT_STREAK:
                    d.momentum_score = max(-10, d.momentum_score - severity * 2)
                elif event.event_type == EventType.MOTIVATION_SURGE:
                    d.momentum_score = min(10, d.momentum_score + severity * 2)
                    d.performance_score = min(10, d.performance_score + severity * 0.3)
                elif event.event_type == EventType.LEARNING_BREAKTHROUGH:
                    d.performance_score = min(10, d.performance_score + severity * 0.5)
                    d.opportunity_score = min(10, d.opportunity_score + severity * 0.3)
                elif event.event_type == EventType.SIDE_INCOME_OPPORTUNITY:
                    d.opportunity_score = min(10, d.opportunity_score + severity * 0.6)
                elif event.event_type == EventType.DEBT_STRESS_SPIKE:
                    d.risk_score = min(10, d.risk_score + severity * 0.7)
                    d.momentum_score = max(-10, d.momentum_score - severity * 0.5)
                elif event.event_type == EventType.HEALTH_SETBACK:
                    d.performance_score = max(0, d.performance_score - severity * 0.6)
                    d.risk_score = min(10, d.risk_score + severity * 0.4)
                elif event.event_type == EventType.GOAL_PROGRESS_SURGE:
                    d.performance_score = min(10, d.performance_score + severity * 0.5)
                    d.momentum_score = min(10, d.momentum_score + severity * 0.4)
                break
    
    def _detect_risks(self) -> list[str]:
        """Detect current risks."""
        
        risks = []
        
        for d in self.current_domains:
            if d.risk_score > 7:
                risks.append(f"High risk in {d.domain}: {d.risk_score:.1f}")
            if d.momentum_score < -5:
                risks.append(f"Negative momentum in {d.domain}: {d.momentum_score:.1f}")
            if d.performance_score < 3:
                risks.append(f"Low performance in {d.domain}: {d.performance_score:.1f}")
        
        return risks
    
    def _detect_opportunities(self) -> list[str]:
        """Detect current opportunities."""
        
        opportunities = []
        
        for d in self.current_domains:
            if d.opportunity_score > 7:
                opportunities.append(f"Opportunity in {d.domain}: {d.opportunity_score:.1f}")
            if d.momentum_score > 5:
                opportunities.append(f"Positive momentum in {d.domain}: {d.momentum_score:.1f}")
        
        return opportunities
    
    def _calculate_priority_shifts(self) -> list[dict]:
        """Calculate priority shifts."""
        
        shifts = []
        
        # Sort domains by performance score
        sorted_domains = sorted(
            self.current_domains, 
            key=lambda d: d.performance_score
        )
        
        # Identify lowest performing domains that might need priority
        for d in sorted_domains[:2]:
            if d.performance_score < 4:
                shifts.append({
                    "domain": d.domain,
                    "action": "increase_priority",
                    "reason": f"Low performance: {d.performance_score:.1f}",
                })
        
        return shifts
    
    def _simulate_habits(self) -> dict[str, float]:
        """Simulate habit completion."""
        
        performance = {}
        
        # Simulate based on domain performance
        for d in self.current_domains:
            base_prob = 0.5 + (d.performance_score / 20) + (d.momentum_score / 40)
            completion_rate = max(0.1, min(1.0, base_prob + self.rng.uniform(-0.1, 0.1)))
            performance[d.domain] = completion_rate
        
        return performance
    
    def _calculate_domain_changes(self) -> dict[str, float]:
        """Calculate domain score changes from previous day."""
        
        changes = {}
        
        for d in self.current_domains:
            # Simple change tracking
            changes[d.domain] = d.performance_score
        
        return changes
    
    async def _create_weekly_summary(
        self, 
        week: int, 
        daily_summaries: list[DailySummary]
    ) -> WeeklySummary:
        """Create weekly summary."""
        
        start_date = daily_summaries[0].date
        end_date = daily_summaries[-1].date
        
        # Calculate average performance
        all_perf = []
        for d in daily_summaries:
            for domain, scores in d.morning_state.items():
                all_perf.append(scores.get("performance", 5))
        
        avg_perf = sum(all_perf) / len(all_perf) if all_perf else 5.0
        
        # Collect risks and opportunities
        risks = set()
        opportunities = set()
        adjustments = set()
        
        for d in daily_summaries:
            risks.update(d.risks_detected)
            opportunities.update(d.opportunities_detected)
            for shift in d.priority_shifts:
                adjustments.add(f"{shift['domain']}: {shift['action']}")
        
        summary_text = (
            f"Week {week}: avg_performance={avg_perf:.1f}, "
            f"risks={len(risks)}, opportunities={len(opportunities)}"
        )
        
        return WeeklySummary(
            week=week,
            start_date=start_date,
            end_date=end_date,
            daily_summaries=daily_summaries,
            average_performance=avg_perf,
            risks_emerged=list(risks)[:5],
            opportunities_captured=list(opportunities)[:5],
            strategic_adjustments=list(adjustments)[:5],
            summary=summary_text,
        )
    
    def _analyze_results(self, results: SimulationResults) -> SimulationResults:
        """Analyze simulation results."""
        
        scores = {}
        
        # Strategic Stability Score
        if results.daily_summaries:
            momentum_changes = []
            for d in results.daily_summaries:
                domain_perfs = list(d.morning_state.values())
                if domain_perfs:
                    perfs = [s.get("performance", 5) for s in domain_perfs]
                    momentum_changes.append(max(perfs) - min(perfs))
            
            avg_spread = sum(momentum_changes) / len(momentum_changes) if momentum_changes else 0
            scores["strategic_stability"] = max(0, 10 - avg_spread)
        else:
            scores["strategic_stability"] = 5.0
        
        # Responsiveness Score
        total_shifts = sum(
            len(d.priority_shifts) 
            for d in results.daily_summaries
        )
        days = len(results.daily_summaries) or 1
        scores["responsiveness"] = min(10, (total_shifts / days) * 2)
        
        # Domain Balance Score
        if results.final_domains:
            perfs = [d.performance_score for d in results.final_domains]
            avg = sum(perfs) / len(perfs)
            variance = sum((p - avg) ** 2 for p in perfs) / len(perfs)
            balance = max(0, 10 - (variance ** 0.5))
            scores["domain_balance"] = balance
        else:
            scores["domain_balance"] = 5.0
        
        # Recovery Score (how much domains improved from low)
        if results.final_domains and results.initial_domains:
            recovery_points = 0
            for final, initial in zip(results.final_domains, results.initial_domains):
                if initial.performance_score < 4 and final.performance_score > initial.performance_score:
                    recovery_points += 1
            scores["recovery"] = min(10, recovery_points * 2)
        else:
            scores["recovery"] = 5.0
        
        # Execution Quality
        total_events = len(results.daily_summaries) * 2
        handled = total_events
        scores["execution_quality"] = min(10, (handled / max(total_events, 1)) * 10)
        
        results.analysis_scores = scores
        
        # Generate recommendations
        results.recommendations = self._generate_recommendations(scores)
        
        # Detect issues
        results.detected_issues = self._detect_issues(results)
        
        return results
    
    def _generate_recommendations(self, scores: dict) -> list[str]:
        """Generate recommendations based on scores."""
        
        recs = []
        
        if scores.get("strategic_stability", 5) < 5:
            recs.append("Consider stabilizing domain priorities - high volatility detected")
        
        if scores.get("responsiveness", 5) < 3:
            recs.append("System may not be responding adequately to changes")
        
        if scores.get("domain_balance", 5) < 4:
            recs.append("Domain imbalance detected - consider rebalancing resources")
        
        if scores.get("recovery", 5) < 3:
            recs.append("Recovery mechanisms may need improvement")
        
        if not recs:
            recs.append("System performed within acceptable parameters")
        
        return recs
    
    def _detect_issues(self, results: SimulationResults) -> list[str]:
        """Detect issues in simulation results."""
        
        issues = []
        
        # Check for domain neglect
        if results.final_domains:
            for d in results.final_domains:
                if d.performance_score < 3:
                    issues.append(f"Domain {d.domain} critical: {d.performance_score:.1f}")
        
        # Check for oscillating priorities
        if len(results.daily_summaries) > 7:
            shift_counts = [len(d.priority_shifts) for d in results.daily_summaries[-7:]]
            if sum(shift_counts) > 10:
                issues.append("Oscillating priorities detected")
        
        # Check for strategic drift
        if results.final_domains and results.initial_domains:
            drift = sum(
                abs(f.performance_score - i.performance_score)
                for f, i in zip(results.final_domains, results.initial_domains)
            )
            if drift > 15:
                issues.append(f"Strategic drift detected: {drift:.1f}")
        
        return issues


def create_simulation_engine(
    seed: str, 
    scenario_type: ScenarioType,
) -> SimulationEngine:
    """Create a simulation engine."""
    from app.simulation.seed_manager import SeedManager
    from app.simulation.mock_data_generator import MockDataGenerator
    from app.simulation.scenario_builder import ScenarioBuilder
    
    seed_manager = SeedManager(seed)
    mock_generator = MockDataGenerator(seed_manager)
    scenario_builder = ScenarioBuilder(seed_manager, mock_generator)
    scenario = scenario_builder.build_scenario(scenario_type)
    
    return SimulationEngine(seed_manager, mock_generator, scenario)
