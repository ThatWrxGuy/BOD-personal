"""
BB-APP-002: Reviews Service

Per BB-APP-002 Section 8.7 - Reviews Integration.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.read_models import (
    ReviewDetailReadModel,
    ReviewSummaryReadModel,
    ReviewActionSummary,
    ReviewRecommendationSummary,
)


class ReviewsService:
    """Service for review cycles."""
    
    # Mock review store
    _reviews = {
        "review-1": {
            "id": "review-1",
            "review_type": "weekly",
            "status": "completed",
            "period_start": datetime.now() - timedelta(days=7),
            "period_end": datetime.now() - timedelta(days=1),
            "overall_score": 78,
            "actions": {
                "completed": 5,
                "missed": 2,
                "total": 7
            },
            "recommendations": {
                "accepted": 3,
                "rejected": 1,
                "deferred": 1
            },
            "progress_highlights": [
                "Career goals progressed well",
                "Financial discipline maintained",
                "Completed all health checkups"
            ],
            "missed_priorities": [
                "Sleep consistency slipped mid-week",
                "Social connections below target"
            ],
            "lessons_learned": [
                "Morning routines more effective than evening",
                "Buffer time between meetings improves focus"
            ],
            "next_period_focus": [
                "Improve sleep consistency",
                "Increase social engagement",
                "Complete skill certification"
            ],
            "started_at": datetime.now() - timedelta(days=7),
            "completed_at": datetime.now() - timedelta(days=1),
        },
        "review-2": {
            "id": "review-2",
            "review_type": "weekly",
            "status": "completed",
            "period_start": datetime.now() - timedelta(days=14),
            "period_end": datetime.now() - timedelta(days=8),
            "overall_score": 72,
            "actions": {
                "completed": 4,
                "missed": 3,
                "total": 7
            },
            "recommendations": {
                "accepted": 2,
                "rejected": 2,
                "deferred": 0
            },
            "progress_highlights": [
                "Started new exercise routine",
                "Network expansion on track"
            ],
            "missed_priorities": [
                "Budget review delayed",
                "Reading goals behind"
            ],
            "lessons_learned": [
                "Need more realistic weekly targets"
            ],
            "next_period_focus": [
                "Complete budget review",
                "Stick to reading schedule"
            ],
            "started_at": datetime.now() - timedelta(days=14),
            "completed_at": datetime.now() - timedelta(days=8),
        },
        "review-3": {
            "id": "review-3",
            "review_type": "weekly",
            "status": "in_progress",
            "period_start": datetime.now() - timedelta(days=7),
            "period_end": datetime.now(),
            "overall_score": 0,
            "actions": {
                "completed": 0,
                "missed": 0,
                "total": 0
            },
            "recommendations": {
                "accepted": 0,
                "rejected": 0,
                "deferred": 0
            },
            "progress_highlights": [],
            "missed_priorities": [],
            "lessons_learned": [],
            "next_period_focus": [],
            "started_at": datetime.now() - timedelta(hours=1),
            "completed_at": None,
        },
    }
    
    async def list_reviews(
        self,
        user_id: str,
        review_type: Optional[str] = None,
        limit: int = 50
    ) -> List[ReviewSummaryReadModel]:
        """List reviews."""
        results = []
        
        for review in self._reviews.values():
            if review_type and review["review_type"] != review_type:
                continue
            
            results.append(ReviewSummaryReadModel(
                id=review["id"],
                review_type=review["review_type"],
                status=review["status"],
                period_start=review["period_start"],
                period_end=review["period_end"],
                overall_score=review["overall_score"],
            ))
        
        # Sort by most recent
        results.sort(key=lambda x: x.period_end or x.period_start, reverse=True)
        return results[:limit]
    
    async def get_review(
        self,
        review_id: str,
        user_id: str
    ) -> Optional[ReviewDetailReadModel]:
        """Get detailed review."""
        review = self._reviews.get(review_id)
        if not review:
            return None
        
        return ReviewDetailReadModel(
            id=review["id"],
            review_type=review["review_type"],
            status=review["status"],
            period_start=review["period_start"],
            period_end=review["period_end"],
            overall_score=review["overall_score"],
            actions=ReviewActionSummary(**review["actions"]),
            recommendations=ReviewRecommendationSummary(**review["recommendations"]),
            progress_highlights=review["progress_highlights"],
            missed_priorities=review["missed_priorities"],
            lessons_learned=review["lessons_learned"],
            next_period_focus=review["next_period_focus"],
            started_at=review["started_at"],
            completed_at=review.get("completed_at"),
        )
    
    async def get_current_review(
        self,
        user_id: str,
        review_type: str = "weekly"
    ) -> Optional[ReviewDetailReadModel]:
        """Get current in-progress review."""
        for review in self._reviews.values():
            if review["review_type"] == review_type and review["status"] == "in_progress":
                return await self.get_review(review["id"], user_id)
        return None


# Singleton instance
reviews_service = ReviewsService()
