"""Tests for Debate Engine."""
import pytest
from app.executive_agents import (
    DebateEngine,
    AgentProposal,
    ExecutiveRole,
    DebatePosition,
    ProposalStatus,
    ProposalPriority,
)


class TestDebateEngine:
    """Tests for DebateEngine."""

    def setup_method(self):
        self.engine = DebateEngine()

    def test_create_debate(self):
        """Test creating a debate."""
        proposal = AgentProposal(
            proposal_id="test_prop",
            origin_agent=ExecutiveRole.CFO,
            strategy_summary="Test proposal",
        )
        
        debate = self.engine.create_debate(proposal)
        
        assert debate is not None
        assert debate.proposal_id == "test_prop"
        assert len(debate.arguments) == 0

    def test_submit_argument(self):
        """Test submitting an argument."""
        proposal = AgentProposal(
            proposal_id="test_prop",
            origin_agent=ExecutiveRole.CFO,
            strategy_summary="Test proposal",
        )
        
        debate = self.engine.create_debate(proposal)
        
        argument = self.engine.submit_argument(
            debate.round_id,
            "cfo",
            DebatePosition.SUPPORT,
            "I support this proposal",
            [{"evidence": "test"}],
        )
        
        assert argument is not None
        assert argument.position == DebatePosition.SUPPORT
        assert len(debate.arguments) == 1

    def test_generate_debate_summary(self):
        """Test generating debate summary."""
        proposal = AgentProposal(
            proposal_id="test_prop",
            origin_agent=ExecutiveRole.CFO,
            strategy_summary="Test proposal",
        )
        
        debate = self.engine.create_debate(proposal)
        
        # Add arguments
        self.engine.submit_argument(
            debate.round_id,
            "cfo",
            DebatePosition.SUPPORT,
            "Support argument",
            [],
        )
        
        self.engine.submit_argument(
            debate.round_id,
            "cro",
            DebatePosition.OPPOSE,
            "Oppose argument",
            [],
        )
        
        summary = self.engine.generate_debate_summary(debate.round_id)
        
        assert summary is not None
        assert len(summary.arguments_for) >= 1
        assert len(summary.arguments_against) >= 1

    def test_conduct_debate(self):
        """Test conducting full debate."""
        proposals = [
            AgentProposal(
                proposal_id="prop1",
                origin_agent=ExecutiveRole.CFO,
                strategy_summary="Proposal 1",
                financial_impact={"expected_return": 0.1},
            ),
            AgentProposal(
                proposal_id="prop2",
                origin_agent=ExecutiveRole.CRO,
                strategy_summary="Proposal 2",
                risk_assessment={"current_exposure": 0.8},
            ),
        ]
        
        agents = [
            {"role": "cfo"},
            {"role": "cro"},
            {"role": "cko"},
        ]
        
        summaries = self.engine.conduct_debate(proposals, agents)
        
        assert len(summaries) == 2
        assert all(s is not None for s in summaries)
