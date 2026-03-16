"""
PSIP - Personal Strategic Intelligence Platform

A comprehensive system implementing the PSIP-001 directive.

Architecture:
- Layer 1: Strategic Intelligence Core (Strategy Lab, Simulation Engine, etc.)
- Layer 2: Governance Layer (Executive Council, Risk Governor, etc.)
- Layer 3: Domain Intelligence Systems (Finance, Health, Career, etc.)
- Infrastructure: Memory Engine, Signal System
- Outputs: Executive Briefs, Domain Reports

This is the main entry point for the PSIP system.
"""

from layer1_strategic_intelligence_core import (
    StrategyLab, StrategicHypothesis,
    SimulationEngine, SimulationResult,
    EdgeDiscoveryEngine, Edge,
    KnowledgeGraph, Node, Relationship,
    LearningEngine, Lesson, DecisionRecord,
    ScenarioPlanner, Scenario, ScenarioType, Timeframe,
    SignalFusionEngine, Signal, FusedSignal
)

from layer2_governance_layer import (
    ExecutiveCouncil, CouncilMember, CouncilDecision, DecisionPriority, DecisionStatus,
    RiskGovernor, Risk, RiskThreshold, RiskLevel, RiskStatus,
    ExecutionGateManager, ExecutionGate, GatePolicy, GateStatus, GateStep,
    CapitalDeploymentCoordinator, CapitalAllocation, CapitalBudget, AllocationStatus,
    PriorityRouter, Task, Priority, TaskStatus
)

from layer3_domain_intelligence import (
    ChiefOfficer, DomainSignal, DomainStrategy, DomainReport,
    ChiefFinancialOfficer,
    ChiefHealthOfficer,
    ChiefCareerOfficer,
    ChiefRelationshipOfficer,
    ChiefIntelligenceOfficer,
    ChiefLifeArchitect
)

from infrastructure import (
    MemoryEngine, MemoryEntry,
    SignalSystem, Signal, SignalRoute, SignalPriority, SignalStatus
)

from outputs import (
    ExecutiveBriefGenerator, ExecutiveBrief
)


class PSIP:
    """
    Personal Strategic Intelligence Platform
    
    Main class that orchestrates all PSIP components.
    """
    
    def __init__(self, total_capital: float = 100000):
        # Layer 1: Strategic Intelligence Core
        self.strategy_lab = StrategyLab()
        self.simulation_engine = SimulationEngine()
        self.edge_discovery = EdgeDiscoveryEngine()
        self.knowledge_graph = KnowledgeGraph()
        self.learning_engine = LearningEngine()
        self.scenario_planner = ScenarioPlanner()
        self.signal_fusion = SignalFusionEngine()
        
        # Layer 2: Governance Layer
        self.executive_council = ExecutiveCouncil()
        self.risk_governor = RiskGovernor()
        self.execution_gate = ExecutionGateManager()
        self.capital_coordinator = CapitalDeploymentCoordinator(total_capital)
        self.priority_router = PriorityRouter()
        
        # Layer 3: Domain Intelligence
        self.domains = {
            "finance": ChiefFinancialOfficer(),
            "health": ChiefHealthOfficer(),
            "career": ChiefCareerOfficer(),
            "relationships": ChiefRelationshipOfficer(),
            "intelligence": ChiefIntelligenceOfficer(),
            "life_architecture": ChiefLifeArchitect()
        }
        
        # Infrastructure
        self.memory = MemoryEngine()
        self.signal_system = SignalSystem()
        
        # Outputs
        self.brief_generator = ExecutiveBriefGenerator()
        
        # Initialize governance
        self._initialize_governance()
    
    def _initialize_governance(self):
        """Initialize governance layer"""
        # Add council members
        self.executive_council.add_member("cfo", "CFO", "Chief Financial Officer", "finance", 1.0)
        self.executive_council.add_member("cho", "CHO", "Chief Health Officer", "health", 1.0)
        self.executive_council.add_member("cco", "CCO", "Chief Career Officer", "career", 1.0)
        self.executive_council.add_member("cro", "CRO", "Chief Relationship Officer", "relationships", 1.0)
        self.executive_council.add_member("cio", "CIO", "Chief Intelligence Officer", "intelligence", 1.0)
        self.executive_council.add_member("cla", "CLA", "Chief Life Architect", "life_architecture", 1.0)
        
        # Add risk thresholds
        for domain in self.domains.keys():
            self.risk_governor.add_threshold(domain, 0.7, 0.5, 0.6)
        
        # Add domain priorities
        for domain in self.domains.keys():
            self.priority_router.add_domain_priority(domain, 5)
    
    def process_signal(self, signal_data: dict):
        """Process an incoming signal through the full pipeline"""
        # 1. Emit signal
        signal = self.signal_system.emit(
            source=signal_data.get("source", "unknown"),
            signal_type=signal_data.get("type", "general"),
            domain=signal_data.get("domain", "general"),
            payload=signal_data.get("payload", {}),
            priority=SignalPriority.NORMAL
        )
        
        # 2. Store in memory
        self.memory.store(
            memory_type="signal",
            content=signal_data,
            domain=signal_data.get("domain"),
            importance=signal_data.get("importance", 0.5)
        )
        
        return signal
    
    def analyze_domain(self, domain: str) -> dict:
        """Analyze a specific domain"""
        if domain not in self.domains:
            return {"error": "Domain not found"}
        
        chief = self.domains[domain]
        
        # Get signals for domain
        signals = self.signal_system.get_signals_by_domain(domain)
        
        # Convert to DomainSignal format
        domain_signals = [
            DomainSignal(
                id=s.id,
                domain=s.domain,
                signal_type=s.signal_type,
                title=s.payload.get("title", ""),
                description=s.payload.get("description", ""),
                data=s.payload,
                strength=s.payload.get("strength", 0.5),
                confidence=s.payload.get("confidence", 0.5)
            )
            for s in signals
        ]
        
        # Analyze
        analysis = chief.analyze_signals(domain_signals)
        
        # Generate strategy
        strategy = chief.generate_strategy(analysis)
        
        return {
            "domain": domain,
            "analysis": analysis,
            "strategy": {
                "id": strategy.id,
                "title": strategy.title,
                "priority": strategy.priority,
                "action_items": strategy.action_items
            },
            "status": chief.get_domain_status()
        }
    
    def generate_executive_brief(self) -> ExecutiveBrief:
        """Generate an executive brief"""
        # First, analyze all domains to process signals into strategies
        for domain in self.domains.keys():
            self.analyze_domain(domain)
        
        # Get domain reports
        domain_reports = {}
        
        for domain, chief in self.domains.items():
            report = chief.create_report()
            domain_reports[domain] = {
                "summary": f"{domain.capitalize()}: {chief.get_domain_status()}",
                "recommendations": [r for r in report.recommendations],
                "opportunities": chief.get_active_strategies(),
                "risks": []
            }
        
        # Get strategy status
        active_strategies = []
        for chief in self.domains.values():
            active_strategies.extend(chief.get_active_strategies())
        
        strategy_status = {
            "active_strategies": [{"id": s.id, "title": s.title} for s in active_strategies]
        }
        
        # Get risk summary
        risk_summary = self.risk_governor.get_risk_summary()
        
        # Generate brief
        brief = self.brief_generator.generate(domain_reports, strategy_status, risk_summary)
        
        return brief
    
    def get_system_status(self) -> dict:
        """Get overall system status"""
        return {
            "layer1_strategic": {
                "hypotheses": len(self.strategy_lab.hypotheses),
                "simulations": len(self.simulation_engine.simulation_history),
                "edges": len(self.edge_discovery.edges),
                "knowledge_nodes": len(self.knowledge_graph.nodes),
                "lessons": len(self.learning_engine.lessons),
                "scenarios": len(self.scenario_planner.scenarios),
                "signals": len(self.signal_fusion.raw_signals)
            },
            "layer2_governance": {
                "council_members": len(self.executive_council.members),
                "pending_decisions": len(self.executive_council.get_pending_decisions()),
                "risks": self.risk_governor.get_risk_summary(),
                "gates": self.execution_gate.get_gate_summary(),
                "capital": self.capital_coordinator.get_portfolio_summary(),
                "tasks": self.priority_router.get_priority_summary()
            },
            "layer3_domains": {
                domain: chief.get_domain_status()
                for domain, chief in self.domains.items()
            },
            "infrastructure": {
                "memory": self.memory.get_stats(),
                "signals": self.signal_system.get_signal_summary()
            }
        }


__all__ = [
    "PSIP",
    
    # Layer 1 exports
    "StrategyLab", "StrategicHypothesis",
    "SimulationEngine", "SimulationResult",
    "EdgeDiscoveryEngine", "Edge",
    "KnowledgeGraph", "Node", "Relationship",
    "LearningEngine", "Lesson", "DecisionRecord",
    "ScenarioPlanner", "Scenario", "ScenarioType", "Timeframe",
    "SignalFusionEngine", "Signal", "FusedSignal",
    
    # Layer 2 exports
    "ExecutiveCouncil", "CouncilMember", "CouncilDecision", "DecisionPriority", "DecisionStatus",
    "RiskGovernor", "Risk", "RiskThreshold", "RiskLevel", "RiskStatus",
    "ExecutionGateManager", "ExecutionGate", "GatePolicy", "GateStatus", "GateStep",
    "CapitalDeploymentCoordinator", "CapitalAllocation", "CapitalBudget", "AllocationStatus",
    "PriorityRouter", "Task", "Priority", "TaskStatus",
    
    # Layer 3 exports
    "ChiefOfficer", "DomainSignal", "DomainStrategy", "DomainReport",
    "ChiefFinancialOfficer",
    "ChiefHealthOfficer",
    "ChiefCareerOfficer",
    "ChiefRelationshipOfficer",
    "ChiefIntelligenceOfficer",
    "ChiefLifeArchitect",
    
    # Infrastructure exports
    "MemoryEngine", "MemoryEntry",
    "SignalSystem", "Signal", "SignalRoute", "SignalPriority", "SignalStatus",
    
    # Outputs exports
    "ExecutiveBriefGenerator", "ExecutiveBrief",
]
