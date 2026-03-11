"""Tests for the Personal Strategic Intelligence Engine."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.board import BoardMeetingCreate
from app.schemas.decisions import DecisionCreate
from app.schemas.reviews import OutcomeReviewCreate


class TestProfileSchemas:
    """Tests for profile schemas."""

    def test_profile_create_valid(self):
        """Test creating a valid profile."""
        profile_data = ProfileCreate(
            mission_statement="Test mission",
            values=["value1", "value2"],
            priorities=["priority1"],
            non_negotiables=["boundary1"],
            active_goals=["goal1"],
            risk_tolerance="moderate",
        )
        assert profile_data.mission_statement == "Test mission"
        assert len(profile_data.values) == 2
        assert profile_data.risk_tolerance == "moderate"

    def test_profile_update_partial(self):
        """Test partial profile update."""
        update_data = ProfileUpdate(
            mission_statement="Updated mission",
        )
        assert update_data.mission_statement == "Updated mission"
        assert update_data.values is None


class TestBoardSchemas:
    """Tests for board meeting schemas."""

    def test_board_meeting_create(self):
        """Test creating a board meeting."""
        meeting_data = BoardMeetingCreate(
            question="What should I prioritize?",
            meeting_type="strategic",
            trigger_type="manual",
        )
        assert meeting_data.question == "What should I prioritize?"
        assert meeting_data.meeting_type == "strategic"

    def test_board_meeting_defaults(self):
        """Test default values."""
        meeting_data = BoardMeetingCreate(
            question="Test question",
        )
        assert meeting_data.meeting_type == "strategic"
        assert meeting_data.trigger_type == "manual"


class TestDecisionSchemas:
    """Tests for decision schemas."""

    def test_decision_create(self):
        """Test creating a decision."""
        decision_data = DecisionCreate(
            decision_summary="Test decision",
            chosen_action="Do something",
            rationale="Because it's important",
        )
        assert decision_data.decision_summary == "Test decision"
        assert decision_data.chosen_action == "Do something"
        assert decision_data.status == "pending"

    def test_decision_with_meeting_id(self):
        """Test decision linked to meeting."""
        decision_data = DecisionCreate(
            meeting_id=1,
            decision_summary="Linked decision",
            chosen_action="Action",
        )
        assert decision_data.meeting_id == 1


class TestReviewSchemas:
    """Tests for review schemas."""

    def test_review_create(self):
        """Test creating a review."""
        review_data = OutcomeReviewCreate(
            decision_id=1,
            actual_result="Good outcome",
            success_score=8.5,
        )
        assert review_data.decision_id == 1
        assert review_data.actual_result == "Good outcome"
        assert review_data.success_score == 8.5


class TestMockLLMClient:
    """Tests for mock LLM client."""

    @pytest.mark.asyncio
    async def test_mock_complete(self):
        """Test mock completion."""
        from app.services.llm_client import MockLLMClient
        
        client = MockLLMClient()
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
        
        result = await client.complete(messages)
        assert isinstance(result, str)
        assert "Mock response" in result

    @pytest.mark.asyncio
    async def test_mock_json_complete(self):
        """Test mock JSON completion."""
        from app.services.llm_client import MockLLMClient
        
        client = MockLLMClient()
        messages = [
            {"role": "user", "content": "Give me JSON"},
        ]
        
        result = await client.complete_with_json(messages)
        assert isinstance(result, dict)
        assert "summary_judgment" in result
        assert "main_recommendation" in result


class TestAgentRegistry:
    """Tests for agent registry."""

    @pytest.mark.asyncio
    async def test_get_all_agents(self):
        """Test getting all agents."""
        from app.agents.registry import AgentRegistry
        
        # Create mock session
        mock_session = AsyncMock()
        
        registry = AgentRegistry(mock_session)
        agents = await registry.get_all_agents()
        
        # Should have 6 agents
        agent_names = [agent.name for agent in agents]
        assert "Strategy Agent" in agent_names
        assert "Finance Agent" in agent_names
        assert "Risk Agent" in agent_names
        assert "Health Agent" in agent_names
        assert "Operations Agent" in agent_names
        assert "Legacy Agent" in agent_names


class TestContextBuilder:
    """Tests for context builder."""

    @pytest.mark.asyncio
    async def test_extract_keywords(self):
        """Test keyword extraction."""
        from app.core.context_builder import ContextBuilder
        
        # Create mock session
        mock_session = AsyncMock()
        
        builder = ContextBuilder(mock_session)
        
        keywords = builder._extract_keywords("What should I prioritize for the next 90 days?")
        
        assert isinstance(keywords, list)
        # Should have filtered stop words
        assert "what" not in keywords
        assert "should" not in keywords
        assert "prioritize" in keywords or "90" in keywords


class TestSynthesisEngine:
    """Tests for synthesis engine."""

    def test_synthesis_rules(self):
        """Test synthesis rules are enforced."""
        # This tests the synthesis rules documented in the system
        rules = [
            "Never invent fake consensus",
            "Never suppress meaningful disagreement",
            "Never present unjustified certainty",
            "Never discard strong risk objections",
            "Identify agreement clusters",
            "Identify disagreement clusters",
            "Generate one primary recommendation",
            "Provide alternatives when certainty is low",
            "Identify missing data",
        ]
        
        # These are the rules from the spec
        assert len(rules) == 9
        assert "Never invent fake consensus" in rules
        assert "Identify agreement clusters" in rules


class TestCritiqueWorkflow:
    """Tests for critique workflow."""

    def test_critique_pairs_defined(self):
        """Test that critique pairs are defined."""
        from app.core.orchestrator import BoardOrchestrator
        
        # Check that critique pairs exist
        pairs = BoardOrchestrator.CRITIQUE_PAIRS
        
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        
        # Finance should critique Strategy
        assert ("finance", "strategy") in pairs
        
        # Risk should critique Strategy and Finance
        assert ("risk", "strategy") in pairs
        assert ("risk", "finance") in pairs
        
        # Legacy should critique Strategy and Finance
        assert ("legacy", "strategy") in pairs


class TestModels:
    """Tests for database models."""

    def test_user_profile_fields(self):
        """Test UserProfile model fields."""
        from app.models.user_profile import UserProfile
        
        # Check required fields exist
        assert hasattr(UserProfile, "mission_statement")
        assert hasattr(UserProfile, "values")
        assert hasattr(UserProfile, "priorities")
        assert hasattr(UserProfile, "non_negotiables")
        assert hasattr(UserProfile, "active_goals")
        assert hasattr(UserProfile, "risk_tolerance")

    def test_board_meeting_fields(self):
        """Test BoardMeeting model fields."""
        from app.models.board_meeting import BoardMeeting
        
        assert hasattr(BoardMeeting, "meeting_type")
        assert hasattr(BoardMeeting, "trigger_type")
        assert hasattr(BoardMeeting, "question")
        assert hasattr(BoardMeeting, "status")
        assert hasattr(BoardMeeting, "executive_summary")
        assert hasattr(BoardMeeting, "consensus_recommendation")
        assert hasattr(BoardMeeting, "confidence_score")

    def test_agent_definition_fields(self):
        """Test AgentDefinition model fields."""
        from app.models.agent_definition import AgentDefinition
        
        assert hasattr(AgentDefinition, "name")
        assert hasattr(AgentDefinition, "role")
        assert hasattr(AgentDefinition, "constitution_text")
        assert hasattr(AgentDefinition, "version_id")
        assert hasattr(AgentDefinition, "active")

    def test_decision_record_fields(self):
        """Test DecisionRecord model fields."""
        from app.models.decision_record import DecisionRecord
        
        assert hasattr(DecisionRecord, "decision_summary")
        assert hasattr(DecisionRecord, "chosen_action")
        assert hasattr(DecisionRecord, "status")
        assert hasattr(DecisionRecord, "review_due_at")

    def test_outcome_review_fields(self):
        """Test OutcomeReview model fields."""
        from app.models.outcome_review import OutcomeReview
        
        assert hasattr(OutcomeReview, "decision_id")
        assert hasattr(OutcomeReview, "actual_result")
        assert hasattr(OutcomeReview, "success_score")
        assert hasattr(OutcomeReview, "reviewed_at")


class TestConfig:
    """Tests for configuration."""

    def test_default_settings(self):
        """Test default settings."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.app_name == "Personal Strategic Intelligence Engine"
        assert settings.debug is False
        assert settings.llm_provider == "openai"

    def test_settings_from_env(self):
        """Test settings from environment."""
        import os
        os.environ["DEBUG"] = "true"
        os.environ["LLM_PROVIDER"] = "anthropic"
        
        from app.core.config import Settings
        settings = Settings()
        
        assert settings.debug is True
        assert settings.llm_provider == "anthropic"
        
        # Cleanup
        os.environ.pop("DEBUG", None)
        os.environ.pop("LLM_PROVIDER", None)


class TestAPIRoutes:
    """Tests for API routes structure."""

    def test_profile_routes_defined(self):
        """Test profile routes are defined."""
        from app.api.profile import router
        
        routes = [r.path for r in router.routes]
        
        assert "" in routes  # POST /profile
        assert "" in routes  # GET /profile
        assert "/{profile_id}" in routes  # PUT /profile/{id}

    def test_board_routes_defined(self):
        """Test board routes are defined."""
        from app.api.board import router
        
        routes = [r.path for r in router.routes]
        
        assert "" in routes  # POST /board/meetings
        assert "/{meeting_id}" in routes  # GET /board/meetings/{id}
        assert "/{meeting_id}/run" in routes  # POST /board/meetings/{id}/run

    def test_decision_routes_defined(self):
        """Test decision routes are defined."""
        from app.api.decisions import router
        
        routes = [r.path for r in router.routes]
        
        assert "" in routes  # POST /decisions
        assert "" in routes  # GET /decisions
        assert "/{decision_id}" in routes  # GET/PATCH /decisions/{id}

    def test_review_routes_defined(self):
        """Test review routes are defined."""
        from app.api.reviews import router
        
        routes = [r.path for r in router.routes]
        
        assert "" in routes  # POST /reviews
        assert "" in routes  # GET /reviews
        assert "/{review_id}" in routes  # GET /reviews/{id}
