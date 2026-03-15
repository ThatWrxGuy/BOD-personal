"""Strategy Pipeline - PSIE Decision Making Subsystem.

This subsystem provides the formal process through which agent-generated insights
become structured strategic decisions through validation, simulation, governance
review, and approval.

The Strategy Pipeline introduces:
- Structured strategy proposal generation
- Multi-agent review and debate
- Simulation-based outcome evaluation
- Governance-controlled approval
- Permanent decision logging and auditability

System flow:
    Signals → Agents → Strategy Proposal → Debate → Simulation → Governance → Execution

Components:
- proposal_models: Canonical schema for strategy proposals
- proposal_registry: Manages proposal lifecycle
- debate_engine: Multi-agent evaluation
- simulation_router: Outcome evaluation
- governance_router: Risk and approval rules
- decision_logger: Permanent audit log

API Endpoints:
- GET /strategies - List active proposals
- GET /strategies/{id} - Retrieve proposal details
- POST /strategies/propose - Submit strategy proposal
- POST /strategies/debate - Trigger debate process
- POST /strategies/simulate - Run simulations
- POST /strategies/submit - Submit proposal to governance
- GET /strategies/history - Retrieve decision history
"""

from app.strategy_pipeline.proposal_models import (
    DebateOutcome,
    DebateFeedback,
    GovernanceDecision,
    ProposalCategory,
    ProposalStatus,
    ProposalSummary,
    RiskLevel,
    SimulationResult,
    StrategyPipelineRequest,
    StrategyProposal,
    PipelineExecutionRequest,
    PipelineExecutionResult,
)

from app.strategy_pipeline.proposal_registry import (
    ProposalRegistry,
    get_registry,
)

from app.strategy_pipeline.debate_engine import (
    DebateAgent,
    DebateAgentRole,
    DebateEngine,
    get_debate_engine,
)

from app.strategy_pipeline.simulation_router import (
    SimulationRouter,
    SimulationType,
    get_simulation_router,
)

from app.strategy_pipeline.governance_router import (
    ApprovalLevel,
    GovernanceRouter,
    get_governance_router,
)

from app.strategy_pipeline.decision_logger import (
    DecisionJournal,
    DecisionRecord,
    get_decision_journal,
)

from app.strategy_pipeline.routes import router

__all__ = [
    # Models
    "DebateOutcome",
    "DebateFeedback",
    "GovernanceDecision",
    "ProposalCategory",
    "ProposalStatus",
    "ProposalSummary",
    "RiskLevel",
    "SimulationResult",
    "StrategyPipelineRequest",
    "StrategyProposal",
    "PipelineExecutionRequest",
    "PipelineExecutionResult",
    # Registry
    "ProposalRegistry",
    "get_registry",
    # Debate
    "DebateAgent",
    "DebateAgentRole",
    "DebateEngine",
    "get_debate_engine",
    # Simulation
    "SimulationRouter",
    "SimulationType",
    "get_simulation_router",
    # Governance
    "ApprovalLevel",
    "GovernanceRouter",
    "get_governance_router",
    # Decision Logger
    "DecisionJournal",
    "DecisionRecord",
    "get_decision_journal",
    # Routes
    "router",
]
