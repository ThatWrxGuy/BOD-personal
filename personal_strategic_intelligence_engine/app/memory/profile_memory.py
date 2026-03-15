"""Memory layer for profile storage and retrieval."""
import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileSummary
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProfileMemory:
    """Persistent storage for user profile."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile_data: ProfileCreate) -> UserProfile:
        """Create a new user profile."""
        # Check if profile already exists
        result = await self.session.execute(select(UserProfile))
        existing_profile = result.scalars().first()
        
        if existing_profile:
            raise ValueError("Profile already exists. Use update instead.")

        profile = UserProfile(
            mission_statement=profile_data.mission_statement,
            values=json.dumps(profile_data.values),
            priorities=json.dumps(profile_data.priorities),
            non_negotiables=json.dumps(profile_data.non_negotiables),
            active_goals=json.dumps(profile_data.active_goals),
            constraints=json.dumps(profile_data.constraints) if profile_data.constraints else None,
            risk_tolerance=profile_data.risk_tolerance,
            name=profile_data.name,
            email=profile_data.email,
        )
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        return profile

    async def get(self, profile_id: Optional[int] = None) -> Optional[UserProfile]:
        """Get user profile by ID or return the first one."""
        if profile_id:
            result = await self.session.execute(
                select(UserProfile).where(UserProfile.id == profile_id)
            )
            return result.scalars().first()
        
        # Return the first profile
        result = await self.session.execute(select(UserProfile))
        return result.scalars().first()

    async def update(self, profile_id: int, profile_data: ProfileUpdate) -> Optional[UserProfile]:
        """Update an existing profile."""
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.id == profile_id)
        )
        profile = result.scalars().first()
        
        if not profile:
            return None

        # Update fields if provided
        if profile_data.mission_statement is not None:
            profile.mission_statement = profile_data.mission_statement
        if profile_data.values is not None:
            profile.values = json.dumps(profile_data.values)
        if profile_data.priorities is not None:
            profile.priorities = json.dumps(profile_data.priorities)
        if profile_data.non_negotiables is not None:
            profile.non_negotiables = json.dumps(profile_data.non_negotiables)
        if profile_data.active_goals is not None:
            profile.active_goals = json.dumps(profile_data.active_goals)
        if profile_data.constraints is not None:
            profile.constraints = json.dumps(profile_data.constraints)
        if profile_data.risk_tolerance is not None:
            profile.risk_tolerance = profile_data.risk_tolerance
        if profile_data.name is not None:
            profile.name = profile_data.name
        if profile_data.email is not None:
            profile.email = profile_data.email

        await self.session.commit()
        await self.session.refresh(profile)
        
        return profile

    def to_summary(self, profile: UserProfile) -> ProfileSummary:
        """Convert profile to summary format for context."""
        return ProfileSummary(
            mission_statement=profile.mission_statement,
            values=json.loads(profile.values),
            priorities=json.loads(profile.priorities),
            non_negotiables=json.loads(profile.non_negotiables),
            active_goals=json.loads(profile.active_goals),
            risk_tolerance=profile.risk_tolerance,
        )

    def to_dict(self, profile: UserProfile) -> dict:
        """Convert profile to dict for context."""
        return {
            "mission_statement": profile.mission_statement,
            "values": json.loads(profile.values),
            "priorities": json.loads(profile.priorities),
            "non_negotiables": json.loads(profile.non_negotiables),
            "active_goals": json.loads(profile.active_goals),
            "constraints": json.loads(profile.constraints) if profile.constraints else [],
            "risk_tolerance": profile.risk_tolerance,
            "name": profile.name,
            "email": profile.email,
        }


async def get_profile_memory(session: AsyncSession) -> ProfileMemory:
    """Get a profile memory instance."""
    return ProfileMemory(session)
