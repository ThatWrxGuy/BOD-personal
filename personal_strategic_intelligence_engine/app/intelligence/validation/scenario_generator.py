"""Scenario Generator - Generates test scenarios for validation."""
import uuid
from typing import List, Dict, Any

from app.intelligence.validation.simulation_models import (
    SimulationScenario,
    ScenarioDomain,
)


class ScenarioGenerator:
    """Generates test scenarios for system validation."""
    
    def __init__(self):
        self.generated_scenarios: List[SimulationScenario] = []
    
    def generate_scenario(
        self,
        domain: str = "mixed",
    ) -> SimulationScenario:
        """Generate a scenario based on domain."""
        
        domain = ScenarioDomain(domain)
        
        if domain == ScenarioDomain.FINANCIAL:
            return self._generate_financial_scenario()
        elif domain == ScenarioDomain.CAREER:
            return self._generate_career_scenario()
        elif domain == ScenarioDomain.HEALTH:
            return self._generate_health_scenario()
        elif domain == ScenarioDomain.OPERATIONS:
            return self._generate_operations_scenario()
        else:
            return self._generate_mixed_scenario()
    
    def generate_batch(
        self,
        count: int = 5,
        domains: List[str] = None,
    ) -> List[SimulationScenario]:
        """Generate multiple scenarios."""
        
        scenarios = []
        
        if domains is None:
            domains = [d.value for d in ScenarioDomain]
        
        for i in range(count):
            domain = domains[i % len(domains)]
            scenario = self.generate_scenario(domain)
            scenarios.append(scenario)
            self.generated_scenarios.append(scenario)
        
        return scenarios
    
    def _generate_financial_scenario(self) -> SimulationScenario:
        """Generate a financial domain scenario."""
        
        import random
        
        scenarios = [
            {
                "name": "Debt Pressure",
                "description": "High-interest debt accumulation requiring strategic response",
                "goal": "Reduce debt by 30% while maintaining financial stability",
                "challenges": ["High interest rates", "Limited cash flow"],
            },
            {
                "name": "Investment Opportunity",
                "description": "Unexpected investment opportunity with time pressure",
                "goal": "Allocate resources optimally to capture opportunity",
                "challenges": ["Competing priorities", "Risk assessment needed"],
            },
            {
                "name": "Income Disruption",
                "description": "Unexpected income reduction requiring adaptation",
                "goal": "Maintain financial health with reduced income",
                "challenges": ["Budget constraints", "Priority adjustments"],
            },
        ]
        
        base = random.choice(scenarios)
        
        scenario = SimulationScenario(
            id=str(uuid.uuid4())[:8],
            name=base["name"],
            description=base["description"],
            domain=ScenarioDomain.FINANCIAL,
            initial_state={
                "wealth": random.randint(3, 6),
                "income_stability": random.randint(4, 7),
                "debt_level": random.randint(4, 8),
                "savings": random.randint(2, 5),
            },
            goal=base["goal"],
            goal_metrics={"target_debt_reduction": 30.0},
            constraints={"max_monthly_payment": 500},
            expected_challenges=base["challenges"],
        )
        
        return scenario
    
    def _generate_career_scenario(self) -> SimulationScenario:
        """Generate a career domain scenario."""
        
        import random
        
        scenarios = [
            {
                "name": "Promotion Opportunity",
                "description": "Available promotion requiring skill development",
                "goal": "Secure promotion within 6 months",
                "challenges": ["Skill gaps", "Time constraints"],
            },
            {
                "name": "Job Security Concern",
                "description": "Workforce changes threatening job stability",
                "goal": "Maintain employment and grow skills",
                "challenges": ["External factors", "Competition"],
            },
        ]
        
        base = random.choice(scenarios)
        
        scenario = SimulationScenario(
            id=str(uuid.uuid4())[:8],
            name=base["name"],
            description=base["description"],
            domain=ScenarioDomain.CAREER,
            initial_state={
                "skill_level": random.randint(4, 7),
                "network_strength": random.randint(3, 6),
                "job_security": random.randint(4, 7),
                "market_value": random.randint(4, 7),
            },
            goal=base["goal"],
            goal_metrics={"timeline_months": 6},
            expected_challenges=base["challenges"],
        )
        
        return scenario
    
    def _generate_health_scenario(self) -> SimulationScenario:
        """Generate a health domain scenario."""
        
        import random
        
        scenarios = [
            {
                "name": "Health Decline",
                "description": "Declining health metrics requiring intervention",
                "goal": "Improve health score by 2 points",
                "challenges": ["Time constraints", "Habit formation"],
            },
            {
                "name": "Preventive Focus",
                "description": "Proactive health management opportunity",
                "goal": "Establish sustainable health practices",
                "challenges": ["Consistency", "Resource allocation"],
            },
        ]
        
        base = random.choice(scenarios)
        
        scenario = SimulationScenario(
            id=str(uuid.uuid4())[:8],
            name=base["name"],
            description=base["description"],
            domain=ScenarioDomain.HEALTH,
            initial_state={
                "health_score": random.randint(3, 6),
                "exercise_frequency": random.randint(2, 5),
                "sleep_quality": random.randint(3, 6),
                "stress_level": random.randint(4, 8),
            },
            goal=base["goal"],
            goal_metrics={"target_improvement": 2.0},
            expected_challenges=base["challenges"],
        )
        
        return scenario
    
    def _generate_operations_scenario(self) -> SimulationScenario:
        """Generate an operations domain scenario."""
        
        import random
        
        scenarios = [
            {
                "name": "Efficiency Improvement",
                "description": "Operational inefficiencies reducing productivity",
                "goal": "Improve operational efficiency by 25%",
                "challenges": ["Change resistance", "Resource limits"],
            },
            {
                "name": "Process Optimization",
                "description": "Streamline daily operations",
                "goal": "Reduce time waste by 30%",
                "challenges": ["Habit changes", "Priority shifts"],
            },
        ]
        
        base = random.choice(scenarios)
        
        scenario = SimulationScenario(
            id=str(uuid.uuid4())[:8],
            name=base["name"],
            description=base["description"],
            domain=ScenarioDomain.OPERATIONS,
            initial_state={
                "efficiency_score": random.randint(3, 6),
                "time_management": random.randint(3, 6),
                "automation_level": random.randint(2, 5),
                "task_completion_rate": random.randint(4, 7),
            },
            goal=base["goal"],
            goal_metrics={"target_improvement": 25.0},
            expected_challenges=base["challenges"],
        )
        
        return scenario
    
    def _generate_mixed_scenario(self) -> SimulationScenario:
        """Generate a mixed domain scenario."""
        
        import random
        
        # Combine elements from multiple domains
        scenario = SimulationScenario(
            id=str(uuid.uuid4())[:8],
            name="Multi-Domain Challenge",
            description="Complex scenario affecting multiple life domains",
            domain=ScenarioDomain.MIXED,
            initial_state={
                "health": random.randint(3, 6),
                "wealth": random.randint(3, 6),
                "career": random.randint(3, 6),
                "operations": random.randint(3, 6),
                "relationships": random.randint(3, 6),
            },
            goal="Balance and improve across all domains",
            goal_metrics={"overall_improvement": 15.0},
            constraints={"resource_limit": 100},
            expected_challenges=["Competing priorities", "Time allocation"],
        )
        
        return scenario
    
    def get_scenarios(self) -> List[SimulationScenario]:
        """Get all generated scenarios."""
        
        return self.generated_scenarios


_generator: ScenarioGenerator = None


def get_scenario_generator() -> ScenarioGenerator:
    """Get the global scenario generator."""
    global _generator
    if _generator is None:
        _generator = ScenarioGenerator()
    return _generator
