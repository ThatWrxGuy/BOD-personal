"""Context builder for assembling meeting context."""
import json
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.profile_memory import ProfileMemory
from app.memory.meeting_memory import MeetingMemory
from app.memory.decision_memory import DecisionMemory
from app.core.logging import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """Builds context for board meetings."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.profile_memory = ProfileMemory(session)
        self.meeting_memory = MeetingMemory(session)
        self.decision_memory = DecisionMemory(session)

    async def build_context(
        self,
        question: str,
        meeting_type: Optional[str] = None,
        include_recent: int = 5,
    ) -> dict[str, Any]:
        """Build complete context for a board meeting."""
        context = {}

        # Get user profile
        profile = await self.profile_memory.get()
        if profile:
            context["profile"] = self.profile_memory.to_dict(profile)
            context["profile_summary"] = self.profile_memory.to_summary(profile)

        # Get recent meetings
        recent_meetings = await self.meeting_memory.get_recent(
            limit=include_recent,
            meeting_type=meeting_type,
        )
        context["recent_meetings"] = recent_meetings

        # Get relevant decisions
        recent_decisions = await self.decision_memory.list(limit=include_recent)
        if recent_decisions[0]:
            context["recent_decisions"] = recent_decisions[0]

        # Try to find related meetings by keyword extraction
        keywords = self._extract_keywords(question)
        if keywords:
            related_meetings = []
            for keyword in keywords[:3]:
                matches = await self.meeting_memory.get_by_keyword(keyword, limit=3)
                related_meetings.extend(matches)
            
            # Deduplicate
            seen = set()
            unique_related = []
            for m in related_meetings:
                if m.id not in seen:
                    seen.add(m.id)
                    unique_related.append(m)
            
            context["related_meetings"] = unique_related[:5]

        return context

    def _extract_keywords(self, text: str) -> list[str]:
        """Simple keyword extraction from question."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "should", "what", "how", "why", "when",
            "is", "are", "was", "were", "be", "been", "being", "have",
            "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then",
            "once", "here", "there", "all", "each", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "i", "my", "me",
            "we", "our", "you", "your", "he", "she", "it", "they", "them",
            "their", "this", "that", "these", "those", "am", "about",
            "get", "go", "going", "want", "think", "know", "like", "make"
        }
        
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:5]

    async def get_context_snapshot(self, context: dict[str, Any]) -> str:
        """Create a text snapshot of context for storage."""
        snapshot_parts = []

        if "profile" in context:
            profile = context["profile"]
            snapshot_parts.append(
                f"Profile: Mission - {profile.get('mission_statement', 'N/A')[:100]}..."
            )

        if "recent_meetings" in context:
            meetings = context["recent_meetings"]
            if meetings:
                snapshot_parts.append(
                    f"Recent meetings: {len(meetings)} meetings in context"
                )

        return "\n".join(snapshot_parts) if snapshot_parts else "No context available"


async def get_context_builder(session: AsyncSession) -> ContextBuilder:
    """Get a context builder instance."""
    return ContextBuilder(session)
