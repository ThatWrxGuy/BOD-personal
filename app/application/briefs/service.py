"""
BB-APP-002: Briefs Service

Per BB-APP-002 Section 8.2 - Briefs Integration.
"""

from datetime import datetime, timedelta
from typing import List

from app.read_models import (
    BriefDetailReadModel,
    BriefSummary,
    BriefDomainSection,
    BriefRecommendation,
    BriefRiskAlert,
    StrategicPosture,
    DomainStatus,
)


class BriefsService:
    """Service for executive briefs."""
    
    async def list_briefs(self, user_id: str) -> List[BriefSummary]:
        """List all briefs for user."""
        # Mock data - in production, this would query the database
        now = datetime.now()
        return [
            BriefSummary(
                id="brief-001",
                title=f"Executive Brief - Week {((now.day - 1) // 7) + 1}, {now.strftime('%Y')}",
                generated_at=now - timedelta(hours=2),
                posture=StrategicPosture.NEUTRAL,
                readiness_score=85
            ),
            BriefSummary(
                id="brief-002",
                title=f"Executive Brief - Week {((now.day - 8) // 7) + 1}, {now.strftime('%Y')}",
                generated_at=now - timedelta(days=7),
                posture=StrategicPosture.OFFENSIVE,
                readiness_score=82
            ),
            BriefSummary(
                id="brief-003",
                title=f"Executive Brief - Week {((now.day - 15) // 7) + 1}, {now.strftime('%Y')}",
                generated_at=now - timedelta(days=14),
                posture=StrategicPosture.DEFENSIVE,
                readiness_score=68
            ),
        ]
    
    async def get_brief(self, brief_id: str, user_id: str) -> BriefDetailReadModel | None:
        """Get detailed brief by ID."""
        # Mock data - in production, this would query the database
        if brief_id == "brief-001":
            return BriefDetailReadModel(
                id="brief-001",
                title="Executive Brief - Week 12, 2024",
                generated_at=datetime.now() - timedelta(hours=2),
                cycle_type="weekly",
                status="current",
                posture=StrategicPosture.NEUTRAL,
                readiness_score=85,
                risk_alerts=[
                    BriefRiskAlert(
                        id="alert-1",
                        severity="medium",
                        message="Health domain showing declining trend",
                        domain="Health"
                    ),
                    BriefRiskAlert(
                        id="alert-2",
                        severity="low",
                        message="Intelligence domain needs attention",
                        domain="Intelligence"
                    ),
                ],
                domain_sections=[
                    BriefDomainSection(
                        domain_id="finance",
                        domain_name="Finance",
                        summary="Strong performance with increased savings rate",
                        status=DomainStatus.HEALTHY,
                        key_insight="Retirement contributions above target",
                        recommendations_count=3
                    ),
                    BriefDomainSection(
                        domain_id="health",
                        domain_name="Health",
                        summary="Sleep patterns irregular, energy levels fluctuating",
                        status=DomainStatus.CAUTION,
                        key_insight="Recovery metrics below baseline",
                        recommendations_count=2
                    ),
                ],
                recommendations=[
                    BriefRecommendation(
                        id="rec-1",
                        title="Increase retirement savings by 5%",
                        domain="Finance",
                        priority=1,
                        confidence=0.85,
                        rationale="Based on current savings rate and retirement goals"
                    ),
                    BriefRecommendation(
                        id="rec-2",
                        title="Schedule weekly social connection time",
                        domain="Relationships",
                        priority=2,
                        confidence=0.72,
                        rationale="Relationship domain showing declining engagement"
                    ),
                ],
                executive_summary="Overall system health is stable with minor alerts in Health and Intelligence domains. Financial discipline remains strong.",
                confidence_indicators={
                    "data_quality": 0.9,
                    "signal_strength": 0.85,
                    "analysis_completeness": 0.88
                }
            )
        return None
    
    async def compare_briefs(self, brief_id_1: str, brief_id_2: str) -> dict:
        """Compare two briefs."""
        # Mock comparison
        return {
            "brief_1": brief_id_1,
            "brief_2": brief_id_2,
            "changes": {
                "readiness_score": {"from": 82, "to": 85, "change": "+3"},
                "posture": {"from": "offensive", "to": "neutral"},
                "risk_alerts": {"from": 1, "to": 2, "change": "+1"},
            }
        }


# Singleton instance
briefs_service = BriefsService()
