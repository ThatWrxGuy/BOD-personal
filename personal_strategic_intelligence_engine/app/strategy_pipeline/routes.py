"""Strategy Pipeline API routes."""
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.strategy_pipeline.proposal_models import (
    DebateFeedback,
    DebateOutcome,
    GovernanceDecision,
    PipelineExecutionRequest,
    PipelineExecutionResult,
    ProposalCategory,
    ProposalStatus,
    ProposalSummary,
    RiskLevel,
    SimulationResult,
    StrategyPipelineRequest,
    StrategyProposal,
)
from app.strategy_pipeline.proposal_registry import get_registry
from app.strategy_pipeline.debate_engine import get_debate_engine
from app.strategy_pipeline.simulation_router import get_simulation_router
from app.strategy_pipeline.governance_router import get_governance_router
from app.strategy_pipeline.decision_logger import get_decision_journal
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/strategies", tags=["strategy-pipeline"])


# ============ Request/Response Models ============

class SubmitProposalResponse(BaseModel):
    """Response for proposal submission."""
    id: str
    title: str
    status: str
    created_at: str


class DebateResponse(BaseModel):
    """Response for debate results."""
    proposal_id: str
    completed: bool
    consensus: Optional[str] = None
    feedback: list
    average_confidence: float


class SimulationResponse(BaseModel):
    """Response for simulation results."""
    proposal_id: str
    completed: bool
    simulations: dict


class GovernanceSubmitResponse(BaseModel):
    """Response for governance submission."""
    proposal_id: str
    decision: GovernanceDecision


class HistoryResponse(BaseModel):
    """Response for decision history."""
    decisions: list
    total: int


# ============ Proposal Management Endpoints ============

@router.get("", response_model=list)
async def list_strategies(
    status_filter: Optional[str] = None,
    limit: int = 50,
):
    """
    List active proposals.
    
    Returns a list of all strategy proposals, optionally filtered by status.
    """
    registry = get_registry()
    
    if status_filter:
        try:
            status_enum = ProposalStatus(status_filter)
            proposals = registry.get_by_status(status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    else:
        proposals = registry.get_active()
    
    # Convert to response format
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "agent_id": p.agent_id,
            "category": p.category,
            "risk_level": p.risk_level,
            "confidence_score": p.confidence_score,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in proposals[:limit]
    ]


@router.get("/history", response_model=HistoryResponse)
async def get_decision_history(
    limit: int = 100,
    offset: int = 0,
):
    """
    Retrieve decision history.
    
    Returns a paginated list of all historical decisions.
    """
    journal = get_decision_journal()
    decisions = journal.get_history(limit=limit, offset=offset)
    
    return {
        "decisions": [d.to_dict() for d in decisions],
        "total": len(journal.decisions),
    }


@router.get("/{proposal_id}", response_model=dict)
async def get_strategy_details(
    proposal_id: str,
):
    """
    Retrieve proposal details.
    
    Returns detailed information about a specific proposal.
    """
    registry = get_registry()
    proposal = registry.get(proposal_id)
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal not found: {proposal_id}"
        )
    
    return {
        "id": proposal.id,
        "title": proposal.title,
        "description": proposal.description,
        "agent_id": proposal.agent_id,
        "category": proposal.category,
        "proposed_action": proposal.proposed_action,
        "expected_outcome": proposal.expected_outcome,
        "risk_level": proposal.risk_level,
        "confidence_score": proposal.confidence_score,
        "status": proposal.status,
        "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
        "updated_at": proposal.updated_at.isoformat() if proposal.updated_at else None,
        "submitted_at": proposal.submitted_at.isoformat() if proposal.submitted_at else None,
        "decided_at": proposal.decided_at.isoformat() if proposal.decided_at else None,
        "debate_id": proposal.debate_id,
        "simulation_results": proposal.simulation_results,
        "governance_decision": proposal.governance_decision,
        "tags": proposal.tags,
    }


@router.post("/propose", response_model=SubmitProposalResponse, status_code=status.HTTP_201_CREATED)
async def submit_proposal(
    request: StrategyPipelineRequest,
):
    """
    Submit strategy proposal.
    
    Creates a new strategy proposal and registers it in the system.
    """
    registry = get_registry()
    
    # Create proposal from request
    proposal = StrategyProposal(
        title=request.title,
        description=request.description,
        agent_id=request.agent_id,
        category=request.category,
        proposed_action=request.proposed_action,
        expected_outcome=request.expected_outcome,
        risk_level=request.risk_level,
        confidence_score=request.confidence_score,
        tags=request.tags,
    )
    
    # Register the proposal
    proposal = registry.register(proposal)
    
    logger.info(f"Created proposal: {proposal.id} - {proposal.title}")
    
    return {
        "id": proposal.id,
        "title": proposal.title,
        "status": proposal.status,
        "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
    }


# ============ Debate Endpoints ============

@router.post("/debate", response_model=DebateResponse)
async def trigger_debate(
    proposal_id: str,
):
    """
    Trigger debate process.
    
    Initiates multi-agent debate for the specified proposal.
    """
    registry = get_registry()
    debate_engine = get_debate_engine()
    
    # Get proposal
    proposal = registry.get(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal not found: {proposal_id}"
        )
    
    # Update status
    registry.update_status(proposal_id, ProposalStatus.IN_DEBATE)
    
    # Run debate
    feedback = await debate_engine.evaluate(proposal)
    
    # Get consensus
    consensus = debate_engine.get_consensus(feedback)
    avg_confidence = debate_engine.get_average_confidence(feedback)
    
    logger.info(f"Debate completed for proposal {proposal_id}: consensus={consensus}")
    
    return {
        "proposal_id": proposal_id,
        "completed": True,
        "consensus": consensus.value if hasattr(consensus, 'value') else str(consensus),
        "feedback": [
            {
                "agent_id": f.agent_id,
                "agent_name": f.agent_name,
                "role": f.role,
                "position": f.position,
                "argument_text": f.argument_text,
                "recommendation": f.recommendation.value if hasattr(f.recommendation, 'value') else str(f.recommendation),
                "confidence_score": f.confidence_score,
            }
            for f in feedback
        ],
        "average_confidence": avg_confidence,
    }


# ============ Simulation Endpoints ============

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulations(
    proposal_id: str,
    simulation_types: Optional[str] = None,
):
    """
    Run simulations.
    
    Executes simulation engines to evaluate proposal outcomes.
    """
    registry = get_registry()
    simulation_router = get_simulation_router()
    
    # Get proposal
    proposal = registry.get(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal not found: {proposal_id}"
        )
    
    # Update status
    registry.update_status(proposal_id, ProposalStatus.SIMULATING)
    
    # Parse simulation types
    sim_types = None
    if simulation_types:
        from app.strategy_pipeline.simulation_router import SimulationType
        sim_types = [SimulationType(t.strip()) for t in simulation_types.split(",")]
    
    # Run simulations
    results = await simulation_router.run_simulations(proposal, sim_types)
    
    # Update proposal with results
    proposal.simulation_results = {
        k: {
            "expected_return": v.expected_return,
            "max_drawdown": v.max_drawdown,
            "win_probability": v.win_probability,
            "risk_metrics": v.risk_metrics,
        }
        for k, v in results.items()
    }
    registry.update(proposal)
    
    logger.info(f"Simulations completed for proposal {proposal_id}")
    
    return {
        "proposal_id": proposal_id,
        "completed": True,
        "simulations": proposal.simulation_results,
    }


# ============ Governance Endpoints ============

@router.post("/submit", response_model=GovernanceSubmitResponse)
async def submit_to_governance(
    proposal_id: str,
):
    """
    Submit proposal to governance.
    
    Routes the proposal through the governance approval process.
    """
    registry = get_registry()
    simulation_router = get_simulation_router()
    governance_router = get_governance_router()
    
    # Get proposal
    proposal = registry.get(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal not found: {proposal_id}"
        )
    
    # Update status
    registry.update_status(proposal_id, ProposalStatus.PENDING_APPROVAL)
    
    # Get simulation results
    sim_results_dict = proposal.simulation_results or {}
    sim_results = {}
    from app.strategy_pipeline.simulation_router import SimulationType
    for k, v in sim_results_dict.items():
        sim_results[k] = SimulationResult(
            simulation_type=v.get("simulation_type", k),
            expected_return=v.get("expected_return"),
            max_drawdown=v.get("max_drawdown"),
            win_probability=v.get("win_probability"),
            risk_metrics=v.get("risk_metrics", {}),
        )
    
    # Submit to governance
    decision = await governance_router.submit(proposal, sim_results)
    
    # Update proposal status
    if decision.decision == "APPROVED":
        registry.update_status(proposal_id, ProposalStatus.APPROVED)
    else:
        registry.update_status(proposal_id, ProposalStatus.REJECTED)
    
    proposal.governance_decision = decision.decision
    registry.update(proposal)
    
    logger.info(f"Governance decision for proposal {proposal_id}: {decision.decision}")
    
    return {
        "proposal_id": proposal_id,
        "decision": {
            "decision_id": decision.decision_id,
            "proposal_id": decision.proposal_id,
            "approver_level": decision.approver_level,
            "decision": decision.decision,
            "rationale": decision.rationale,
            "conditions": decision.conditions,
            "risk_level": decision.risk_level,
            "decided_at": decision.decided_at.isoformat() if decision.decided_at else None,
        },
    }


# ============ Pipeline Execution ============

@router.post("/execute-pipeline", response_model=dict)
async def execute_pipeline(
    request: PipelineExecutionRequest,
):
    """
    Execute the complete strategy pipeline.
    
    Runs debate, simulation, and governance approval in sequence.
    """
    start_time = time.time()
    
    registry = get_registry()
    debate_engine = get_debate_engine()
    simulation_router = get_simulation_router()
    governance_router = get_governance_router()
    journal = get_decision_journal()
    
    # Get proposal
    proposal = registry.get(request.proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal not found: {request.proposal_id}"
        )
    
    # Submit proposal first
    registry.submit(request.proposal_id)
    
    debate_completed = False
    debate_outcome = None
    debate_feedback = []
    
    # Run debate if requested
    if request.run_debate:
        registry.update_status(request.proposal_id, ProposalStatus.IN_DEBATE)
        debate_feedback = await debate_engine.evaluate(proposal)
        debate_completed = True
        debate_outcome = debate_engine.get_consensus(debate_feedback)
    
    simulation_completed = False
    simulation_results = {}
    
    # Run simulation if requested
    if request.run_simulation:
        registry.update_status(request.proposal_id, ProposalStatus.SIMULATING)
        sim_results = await simulation_router.run_simulations(proposal)
        simulation_results = {
            k: {
                "expected_return": v.expected_return,
                "max_drawdown": v.max_drawdown,
                "win_probability": v.win_probability,
                "risk_metrics": v.risk_metrics,
            }
            for k, v in sim_results.items()
        }
        proposal.simulation_results = simulation_results
        registry.update(proposal)
        simulation_completed = True
    
    governance_completed = False
    governance_decision = None
    final_status = proposal.status
    
    # Submit to governance if requested
    if request.submit_to_governance:
        registry.update_status(request.proposal_id, ProposalStatus.PENDING_APPROVAL)
        
        # Convert sim results back to SimulationResult objects
        from app.strategy_pipeline.simulation_router import SimulationType
        sim_result_objs = {}
        for k, v in simulation_results.items():
            sim_result_objs[k] = SimulationResult(
                simulation_type=v.get("simulation_type", k),
                expected_return=v.get("expected_return"),
                max_drawdown=v.get("max_drawdown"),
                win_probability=v.get("win_probability"),
                risk_metrics=v.get("risk_metrics", {}),
            )
        
        governance_decision = await governance_router.submit(
            proposal,
            sim_result_objs,
            debate_feedback if debate_feedback else None,
        )
        
        governance_completed = True
        
        if governance_decision.decision == "APPROVED":
            final_status = ProposalStatus.APPROVED
            registry.update_status(request.proposal_id, ProposalStatus.APPROVED)
        else:
            final_status = ProposalStatus.REJECTED
            registry.update_status(request.proposal_id, ProposalStatus.REJECTED)
        
        proposal.governance_decision = governance_decision.decision
    
    # Log to decision journal
    journal.log_decision(
        proposal=proposal,
        simulation_results={
            k: SimulationResult(
                simulation_type=v.get("simulation_type", k),
                expected_return=v.get("expected_return"),
                max_drawdown=v.get("max_drawdown"),
                win_probability=v.get("win_probability"),
                risk_metrics=v.get("risk_metrics", {}),
            )
            for k, v in simulation_results.items()
        } if simulation_results else None,
        debate_feedback=debate_feedback if debate_feedback else None,
        governance_decision=governance_decision,
    )
    
    execution_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return {
        "proposal_id": request.proposal_id,
        "debate_completed": debate_completed,
        "debate_outcome": debate_outcome.value if debate_outcome and hasattr(debate_outcome, 'value') else str(debate_outcome) if debate_outcome else None,
        "debate_feedback": [
            {
                "agent_id": f.agent_id,
                "agent_name": f.agent_name,
                "recommendation": f.recommendation.value if hasattr(f.recommendation, 'value') else str(f.recommendation),
                "confidence_score": f.confidence_score,
            }
            for f in debate_feedback
        ],
        "simulation_completed": simulation_completed,
        "simulation_results": simulation_results,
        "governance_completed": governance_completed,
        "governance_decision": {
            "decision_id": governance_decision.decision_id,
            "decision": governance_decision.decision,
            "rationale": governance_decision.rationale,
            "approver_level": governance_decision.approver_level,
        } if governance_decision else None,
        "final_status": final_status.value if hasattr(final_status, 'value') else str(final_status),
        "execution_time_ms": execution_time,
    }


# ============ Statistics ============

@router.get("/statistics/summary")
async def get_statistics():
    """
    Get strategy pipeline statistics.
    
    Returns aggregate statistics about proposals and decisions.
    """
    registry = get_registry()
    journal = get_decision_journal()
    
    all_proposals = registry.list_all()
    decision_stats = journal.get_statistics()
    
    # Count proposals by status
    status_counts = {}
    for p in all_proposals:
        status = p.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Count by risk level
    risk_counts = {}
    for p in all_proposals:
        risk = p.risk_level
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    return {
        "total_proposals": len(all_proposals),
        "proposals_by_status": status_counts,
        "proposals_by_risk_level": risk_counts,
        "decision_statistics": decision_stats,
    }
