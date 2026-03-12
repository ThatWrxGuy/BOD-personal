"""Mock Data Generator - Generates synthetic personal, financial, behavioral, and strategic data."""
import logging
from datetime import datetime, date, timedelta
from typing import Optional

from app.simulation.seed_manager import SeedManager
from app.simulation.simulation_types import (
    PersonalProfileSim,
    FinancialStateSim,
    StrategicGoalSim,
    HabitSim,
    RiskSignalSim,
    OpportunitySignalSim,
    DomainStateSim,
    ScenarioType,
)

logger = logging.getLogger(__name__)


class MockDataGenerator:
    """Generates synthetic mock data from a seed."""
    
    def __init__(self, seed_manager: SeedManager):
        self.seed = seed_manager
        self._rng = seed_manager.random
    
    def generate_personal_profile(self) -> PersonalProfileSim:
        """Generate personal profile from seed."""
        rng = self._rng
        
        # Age ranges
        age_ranges = ["20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "50-55"]
        age_weights = [0.1, 0.15, 0.2, 0.2, 0.15, 0.12, 0.08]
        age_range = rng.choices(age_ranges, weights=age_weights)[0]
        
        # Work hours (30-60)
        work_hours = rng.randint(30, 60) + rng.random()
        
        # Available time (10-30)
        available_time = rng.randint(10, 30) + rng.random()
        
        # Energy baseline (0.3-0.9)
        energy_baseline = 0.3 + rng.random() * 0.6
        
        # Stress baseline (0.2-0.8)
        stress_baseline = 0.2 + rng.random() * 0.6
        
        # Focus stability (0.4-0.95)
        focus_stability = 0.4 + rng.random() * 0.55
        
        # Life complexity (0.2-0.9)
        life_complexity = 0.2 + rng.random() * 0.7
        
        logger.info(f"Generated personal profile: age={age_range}, work_hours={work_hours:.1f}")
        
        return PersonalProfileSim(
            age_range=age_range,
            work_hours=work_hours,
            available_time=available_time,
            energy_baseline=energy_baseline,
            stress_baseline=stress_baseline,
            focus_stability=focus_stability,
            life_complexity=life_complexity,
        )
    
    def generate_financial_state(self, scenario: ScenarioType = ScenarioType.BASELINE) -> FinancialStateSim:
        """Generate financial state from seed."""
        rng = self._rng
        
        # Base income (3000-15000)
        monthly_income = rng.randint(3000, 15000) + rng.random() * 1000
        
        # Fixed expenses (2000-6000)
        fixed_expenses = rng.randint(2000, 6000) + rng.random() * 500
        
        # Adjust for scenario
        if scenario == ScenarioType.PRESSURE:
            # Higher expenses, lower income
            fixed_expenses *= rng.uniform(1.1, 1.4)
            monthly_income *= rng.uniform(0.8, 1.0)
        
        # Debt balances (0-50000)
        if scenario == ScenarioType.PRESSURE:
            debt_balances = rng.randint(10000, 50000)
        else:
            debt_balances = rng.randint(0, 20000)
        
        # Investment balances (0-100000)
        investment_balances = rng.randint(0, 100000)
        
        # Liquidity (1000-20000)
        liquidity = rng.randint(1000, 20000)
        
        # Cash flow pressure
        cash_flow_pressure = (fixed_expenses / monthly_income) if monthly_income > 0 else 0.5
        if scenario == ScenarioType.PRESSURE:
            cash_flow_pressure = min(1.0, cash_flow_pressure * rng.uniform(1.2, 1.5))
        
        logger.info(f"Generated financial state: income={monthly_income:.0f}, debt={debt_balances:.0f}")
        
        return FinancialStateSim(
            monthly_income=monthly_income,
            fixed_expenses=fixed_expenses,
            debt_balances=debt_balances,
            investment_balances=investment_balances,
            liquidity=liquidity,
            cash_flow_pressure=cash_flow_pressure,
        )
    
    def generate_strategic_goals(self) -> list[StrategicGoalSim]:
        """Generate strategic goals from seed."""
        rng = self._rng
        
        goals = []
        domains = ["health", "wealth", "career", "learning", "relationships", "personal_development"]
        
        # Generate 5-10 goals
        num_goals = rng.randint(5, 10)
        
        goal_templates = {
            "health": [
                "Exercise regularly",
                "Improve sleep quality",
                "Reduce stress levels",
                "Maintain healthy weight",
                "Annual health checkup",
            ],
            "wealth": [
                "Build emergency fund",
                "Pay off debt",
                "Increase investments",
                "Retirement planning",
                "Reduce expenses",
            ],
            "career": [
                "Learn new skills",
                "Network expansion",
                "Performance improvement",
                "Career advancement",
                "Certification",
            ],
            "learning": [
                "Read 12 books",
                "Complete online course",
                "Learn new language",
                "Industry research",
                "Skill development",
            ],
            "relationships": [
                "Family time",
                "Social connections",
                "Friendship maintenance",
                "Date nights",
                "Community involvement",
            ],
            "personal_development": [
                "Meditation practice",
                "Journaling habit",
                "Time management",
                "Goal setting",
                "Personal projects",
            ],
        }
        
        for i in range(num_goals):
            domain = rng.choice(domains)
            titles = goal_templates.get(domain, ["Generic goal"])
            title = rng.choice(titles)
            
            # Remove used titles
            goal_templates[domain] = [t for t in goal_templates[domain] if t != title]
            
            # Generate dates
            days_until_due = rng.randint(7, 365)
            target_date = date.today() + timedelta(days=days_until_due)
            
            # Urgency and progress
            urgency = rng.random()
            progress = rng.random() * 0.8  # Max 80% at start
            
            goals.append(StrategicGoalSim(
                id=f"goal-{i+1}",
                title=title,
                description=f"Goal to {title.lower()}",
                domain=domain,
                target_date=target_date,
                urgency_score=urgency,
                progress_percentage=progress,
            ))
        
        logger.info(f"Generated {len(goals)} strategic goals")
        return goals
    
    def generate_habits(self) -> list[HabitSim]:
        """Generate habits from seed."""
        rng = self._rng
        
        habits = []
        domains = ["health", "wealth", "career", "learning", "relationships"]
        
        habit_templates = {
            "health": [
                ("Morning workout", 0.7),
                ("Meditation", 0.6),
                ("Sleep by 11pm", 0.5),
                ("Healthy meals", 0.7),
                ("Walk 10k steps", 0.6),
            ],
            "wealth": [
                ("Track expenses", 0.7),
                ("Investment review", 0.4),
                ("Budget check", 0.6),
                ("Save 20%", 0.5),
            ],
            "career": [
                ("Clear inbox", 0.7),
                ("Weekly review", 0.5),
                ("Skill practice", 0.5),
                ("Networking", 0.3),
            ],
            "learning": [
                ("Read 30 minutes", 0.6),
                ("Language practice", 0.5),
                ("Course work", 0.4),
                ("Podcast/listen", 0.6),
            ],
            "relationships": [
                ("Call family", 0.5),
                ("Social event", 0.4),
                ("Date night", 0.6),
                ("Reply messages", 0.7),
            ],
        }
        
        habit_id = 1
        for domain, templates in habit_templates.items():
            for name, base_prob in templates:
                # Streak count (0-30)
                streak_count = rng.randint(0, 30)
                
                # Completion probability with some variance
                completion_prob = base_prob + rng.uniform(-0.15, 0.15)
                completion_prob = max(0.1, min(0.95, completion_prob))
                
                # Focus adherence
                focus_adherence = base_prob + rng.uniform(-0.1, 0.1)
                focus_adherence = max(0.2, min(1.0, focus_adherence))
                
                habits.append(HabitSim(
                    id=f"habit-{habit_id}",
                    name=name,
                    domain=domain,
                    streak_count=streak_count,
                    completion_probability=completion_prob,
                    focus_adherence=focus_adherence,
                ))
                habit_id += 1
        
        logger.info(f"Generated {len(habits)} habits")
        return habits
    
    def generate_initial_risks(self, scenario: ScenarioType = ScenarioType.BASELINE) -> list[RiskSignalSim]:
        """Generate initial risk signals."""
        rng = self._rng
        
        risks = []
        
        # Always add some baseline risks
        base_risks = [
            ("income_instability", "career", 0.2, "Some income fluctuation risk"),
            ("debt_stress", "wealth", 0.3, "Debt management concern"),
            ("burnout_risk", "health", 0.25, "Workload stress potential"),
        ]
        
        if scenario == ScenarioType.PRESSURE:
            # More severe risks
            base_risks.extend([
                ("debt_stress", "wealth", 0.7, "High debt burden"),
                ("cash_flow_crisis", "wealth", 0.6, "Cash flow pressure"),
                ("schedule_overload", "career", 0.7, "Overwhelmed with work"),
            ])
        
        for risk_type, domain, severity, desc in base_risks:
            # Add some variance
            sev = severity + rng.uniform(-0.1, 0.1)
            sev = max(0.1, min(1.0, sev))
            
            risks.append(RiskSignalSim(
                type=risk_type,
                domain=domain,
                severity=sev,
                description=desc,
            ))
        
        logger.info(f"Generated {len(risks)} initial risks")
        return risks
    
    def generate_initial_opportunities(self, scenario: ScenarioType = ScenarioType.BASELINE) -> list[OpportunitySignalSim]:
        """Generate initial opportunity signals."""
        rng = self._rng
        
        opportunities = []
        
        base_opps = [
            ("side_income", "career", 0.4, "Potential for additional income"),
            ("skill_upgrade", "learning", 0.5, "Learning opportunity"),
            ("debt_payoff", "wealth", 0.3, "Debt reduction strategy"),
            ("health_improvement", "health", 0.4, "Health optimization"),
        ]
        
        if scenario == ScenarioType.OPPORTUNITY:
            # Stronger opportunities
            base_opps.extend([
                ("promotion", "career", 0.7, "Career advancement"),
                ("investment_return", "wealth", 0.6, "Investment gains"),
                ("new_connection", "relationships", 0.5, "Network expansion"),
            ])
        
        for opp_type, domain, impact, desc in base_opps:
            imp = impact + rng.uniform(-0.1, 0.15)
            imp = max(0.1, min(1.0, imp))
            
            opportunities.append(OpportunitySignalSim(
                type=opp_type,
                domain=domain,
                potential_impact=imp,
                description=desc,
            ))
        
        logger.info(f"Generated {len(opportunities)} initial opportunities")
        return opportunities
    
    def generate_domain_states(self, scenario: ScenarioType = ScenarioType.BASELINE) -> list[DomainStateSim]:
        """Generate initial domain states."""
        rng = self._rng
        
        domains = [
            "health", "wealth", "career", "learning", 
            "relationships", "personal_development", "operations", "strategic_projects"
        ]
        
        states = []
        
        for domain in domains:
            # Base scores with variance
            if scenario == ScenarioType.PRESSURE:
                # Lower overall scores
                base_perf = rng.uniform(3.0, 6.0)
                base_risk = rng.uniform(4.0, 8.0)
                base_alignment = rng.uniform(3.0, 7.0)
            elif scenario == ScenarioType.OPPORTUNITY:
                # Higher performance, good opportunities
                base_perf = rng.uniform(5.0, 8.0)
                base_risk = rng.uniform(2.0, 5.0)
                base_alignment = rng.uniform(6.0, 9.0)
            else:
                base_perf = rng.uniform(4.0, 7.0)
                base_risk = rng.uniform(2.0, 5.0)
                base_alignment = rng.uniform(5.0, 8.0)
            
            # Opportunity score
            base_opp = rng.uniform(3.0, 7.0)
            if scenario == ScenarioType.OPPORTUNITY:
                base_opp = rng.uniform(6.0, 9.0)
            
            # Momentum
            momentum = rng.uniform(-2.0, 3.0)
            
            # Resource allocation (roughly equal at start)
            resources = 100.0 / len(domains) + rng.uniform(-3.0, 3.0)
            
            states.append(DomainStateSim(
                domain=domain,
                performance_score=base_perf,
                risk_score=base_risk,
                opportunity_score=base_opp,
                momentum_score=momentum,
                alignment_score=base_alignment,
                resource_allocation=resources,
            ))
        
        logger.info(f"Generated {len(states)} domain states")
        return states
    
    def generate_full_initial_state(
        self, 
        scenario: ScenarioType = ScenarioType.BASELINE
    ) -> dict:
        """Generate complete initial state."""
        
        profile = self.generate_personal_profile()
        financial = self.generate_financial_state(scenario)
        goals = self.generate_strategic_goals()
        habits = self.generate_habits()
        risks = self.generate_initial_risks(scenario)
        opportunities = self.generate_initial_opportunities(scenario)
        domains = self.generate_domain_states(scenario)
        
        return {
            "personal_profile": profile,
            "financial_state": financial,
            "goals": goals,
            "habits": habits,
            "risks": risks,
            "opportunities": opportunities,
            "domain_states": domains,
        }


def create_mock_generator(seed: str) -> MockDataGenerator:
    """Create a mock data generator from a seed."""
    seed_manager = SeedManager(seed)
    return MockDataGenerator(seed_manager)
