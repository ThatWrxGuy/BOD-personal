"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import (
    UserProfile,
    AgentDefinition,
    BoardMeeting,
    AgentResponse,
    CritiqueResponse,
    DecisionRecord,
    OutcomeReview,
    StrategicInsight,
    AgentPerformance,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create an async test session with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def sample_profile(async_session: AsyncSession) -> UserProfile:
    """Create a sample user profile."""
    import json
    
    profile = UserProfile(
        mission_statement="To live a meaningful and impactful life",
        values=json.dumps(["integrity", "growth", "family"]),
        priorities=json.dumps(["career", "health", "relationships"]),
        non_negotiables=json.dumps(["never compromise ethics", "always be there for family"]),
        active_goals=json.dumps(["build successful career", "run a marathon"]),
        risk_tolerance="moderate",
        name="Test User",
        email="test@example.com",
    )
    async_session.add(profile)
    await async_session.commit()
    await async_session.refresh(profile)
    return profile


@pytest.fixture
async def sample_agents(async_session: AsyncSession) -> list[AgentDefinition]:
    """Create sample agent definitions."""
    agents = [
        AgentDefinition(
            name="Strategy Agent",
            role="Chief Strategy Officer",
            constitution_text="Strategy constitution",
            version_id="1.0.0",
        ),
        AgentDefinition(
            name="Finance Agent",
            role="Chief Financial Officer",
            constitution_text="Finance constitution",
            version_id="1.0.0",
        ),
        AgentDefinition(
            name="Risk Agent",
            role="Chief Risk Officer",
            constitution_text="Risk constitution",
            version_id="1.0.0",
        ),
        AgentDefinition(
            name="Health Agent",
            role="Chief Health Officer",
            constitution_text="Health constitution",
            version_id="1.0.0",
        ),
        AgentDefinition(
            name="Operations Agent",
            role="Chief Operating Officer",
            constitution_text="Operations constitution",
            version_id="1.0.0",
        ),
        AgentDefinition(
            name="Legacy Agent",
            role="Chief Alignment Officer",
            constitution_text="Legacy constitution",
            version_id="1.0.0",
        ),
    ]
    async_session.add_all(agents)
    await async_session.commit()
    for agent in agents:
        await async_session.refresh(agent)
    return agents


@pytest.fixture
async def sample_meeting(
    async_session: AsyncSession,
    sample_profile: UserProfile,
) -> BoardMeeting:
    """Create a sample board meeting."""
    meeting = BoardMeeting(
        meeting_type="strategic",
        trigger_type="manual",
        question="What should I prioritize for the next 90 days?",
        status="pending",
    )
    async_session.add(meeting)
    await async_session.commit()
    await async_session.refresh(meeting)
    return meeting


@pytest.fixture
async def sample_decision(
    async_session: AsyncSession,
    sample_meeting: BoardMeeting,
) -> DecisionRecord:
    """Create a sample decision."""
    decision = DecisionRecord(
        meeting_id=sample_meeting.id,
        decision_summary="Focus on career growth",
        chosen_action="Take on leadership role",
        rationale="It's aligned with my long-term goals",
        status="pending",
    )
    async_session.add(decision)
    await async_session.commit()
    await async_session.refresh(decision)
    return decision
