"""Tests for Executive Agents."""
import pytest
from app.executive_agents import (
    CEOAgent,
    CFOAgent,
    COOAgent,
    CSOAgent,
    CROAgent,
    CKOAgent,
    CPOAgent,
    ExecutiveRole,
    AgentProposal,
    ProposalPriority,
)


class TestCEOAgent:
    """Tests for CEO Agent."""

    def setup_method(self):
        self.agent = CEOAgent()

    def test_initialization(self):
        """Test CEO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.CEO
        assert self.agent.name == "Chief Executive Officer"

    def test_analyze_state(self):
        """Test state analysis."""
        state = {
            "operational_state": {"current_tasks": []},
            "strategic_state": {"confidence_score": 0.8},
            "risk_state": {"identified_risks": []},
        }
        
        analysis = self.agent.analyze_state(state)
        
        assert analysis["role"] == "ceo"
        assert "system_health" in analysis

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {"system_health": {"risk_count": 2}}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CEO
        assert proposal.priority == ProposalPriority.MEDIUM


class TestCFOAgent:
    """Tests for CFO Agent."""

    def setup_method(self):
        self.agent = CFOAgent()

    def test_initialization(self):
        """Test CFO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.CFO

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {"financial_position": {}}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CFO
        assert proposal.financial_impact is not None
        assert proposal.priority == ProposalPriority.HIGH


class TestCOOAgent:
    """Tests for COO Agent."""

    def setup_method(self):
        self.agent = COOAgent()

    def test_initialization(self):
        """Test COO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.COO

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {"execution_capacity": 0.9}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.COO
        assert proposal.operational_feasibility is not None


class TestCSOAgent:
    """Tests for CSO Agent."""

    def setup_method(self):
        self.agent = CSOAgent()

    def test_initialization(self):
        """Test CSO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.CSO

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {"confidence": 0.7}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CSO
        assert proposal.alignment_score is not None


class TestCROAgent:
    """Tests for CRO Agent."""

    def setup_method(self):
        self.agent = CROAgent()

    def test_initialization(self):
        """Test CRO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.CRO

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {"risk_severity_index": 0.6}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CRO
        assert proposal.risk_assessment is not None
        assert proposal.confidence_score == 0.85


class TestCKOAgent:
    """Tests for CKO Agent."""

    def setup_method(self):
        self.agent = CKOAgent()

    def test_initialization(self):
        """Test CKO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.CKO

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {"doctrine_alignment": 0.7}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CKO


class TestCPOAgent:
    """Tests for CPO Agent."""

    def setup_method(self):
        self.agent = CPOAgent()

    def test_initialization(self):
        """Test CPO agent initializes correctly."""
        assert self.agent.role == ExecutiveRole.CPO

    def test_generate_proposal(self):
        """Test proposal generation."""
        analysis = {}
        
        proposal = self.agent.generate_proposal(analysis)
        
        assert proposal.origin_agent == ExecutiveRole.CPO
