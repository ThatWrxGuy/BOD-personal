"""Tests for Agent Council."""
import pytest
from app.executive_agents import (
    AgentCouncil,
    ExecutiveRole,
    get_agent_council,
    reset_agent_council,
    CEOAgent,
    CFOAgent,
    COOAgent,
)


class TestAgentCouncil:
    """Tests for AgentCouncil."""

    def setup_method(self):
        reset_agent_council()

    def test_council_initialization(self):
        """Test council initializes correctly."""
        council = AgentCouncil()
        
        assert council.ceo is not None
        assert len(council.agents) == 7  # All 7 executive roles

    def test_get_agent(self):
        """Test getting specific agent."""
        council = AgentCouncil()
        
        ceo = council.get_agent(ExecutiveRole.CEO)
        assert ceo is not None
        assert ceo.role == ExecutiveRole.CEO

    def test_get_council_status(self):
        """Test getting council status."""
        council = AgentCouncil()
        
        status = council.get_council_status()
        
        assert status["agents_active"] == 7
        assert "ceo" in status["agent_roles"]

    def test_conduct_council_cycle(self):
        """Test conducting a council cycle."""
        council = AgentCouncil()
        
        decision = council.conduct_council_cycle()
        
        assert decision is not None
        assert decision.decision_id is not None
        assert decision.selected_proposal is not None
        assert len(decision.participating_agents) > 0

    def test_singleton(self):
        """Test singleton access."""
        council1 = get_agent_council()
        council2 = get_agent_council()
        
        assert council1 is council2


class TestIndividualAgents:
    """Tests for individual agents."""

    def test_ceo_agent(self):
        """Test CEO agent."""
        ceo = CEOAgent()
        
        assert ceo.role == ExecutiveRole.CEO
        assert ceo.name == "Chief Executive Officer"
        
        # Test analysis
        analysis = ceo.analyze_state({"operational_state": {}, "strategic_state": {}})
        assert analysis["role"] == "ceo"

    def test_cfo_agent(self):
        """Test CFO agent."""
        cfo = CFOAgent()
        
        assert cfo.role == ExecutiveRole.CFO
        
        # Test proposal generation
        analysis = {"financial_position": {}}
        proposal = cfo.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CFO
        assert proposal.financial_impact is not None

    def test_coo_agent(self):
        """Test COO agent."""
        coo = COOAgent()
        
        assert coo.role == ExecutiveRole.COO
        
        # Test proposal generation
        analysis = {"current_tasks": [], "execution_capacity": 0.9}
        proposal = coo.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.COO
        assert proposal.operational_feasibility is not None
