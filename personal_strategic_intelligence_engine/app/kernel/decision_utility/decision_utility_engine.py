"""Decision Utility Engine - Scores candidate decisions."""
import uuid
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kernel import DecisionUtilityScore
from app.kernel.priorities.priority_engine import PriorityEngine
from app.core.logging import get_logger

logger = get_logger(__name__)


class DecisionUtilityEngine:
    """Evaluates candidate decisions using structured scoring."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.priority_engine: Optional[PriorityEngine] = None
    
    async def score_decision(
        self,
        decision_type: str,
        decision_description: str,
        expected_value: float = 0.0,
        risk_assessment: float = 0.5,
        confidence: float = 0.5,
        reversibility: float = 0.5,
        resource_cost: float = 0.0,
        strategic_alignment: float = 0.5,
        market_regime: str = "NEUTRAL",
        decision_id: Optional[uuid.UUID] = None,
    ) -> DecisionUtilityScore:
        """Score a candidate decision."""
        
        # Get active priorities
        priorities = await self._get_priorities()
        
        # Calculate score components
        risk_penalty = self._calculate_risk_penalty(risk_assessment, market_regime)
        
        alignment_score = strategic_alignment * self._calculate_priority_alignment(priorities)
        
        # Calculate final utility
        utility_score = self._calculate_utility(
            expected_value=expected_value,
            risk_penalty=risk_penalty,
            confidence=confidence,
            alignment_score=alignment_score,
            reversibility=reversibility,
            resource_cost=resource_cost,
        )
        
        # Create score record
        score = DecisionUtilityScore(
            decision_id=decision_id,
            decision_type=decision_type,
            decision_description=decision_description,
            expected_value=expected_value,
            risk_penalty=risk_penalty,
            confidence_score=confidence,
            alignment_score=alignment_score,
            reversibility_score=reversibility,
            resource_cost=resource_cost,
            utility_score=utility_score,
            market_regime=market_regime,
            active_priorities=[p["name"] for p in priorities[:3]],
        )
        
        self.session.add(score)
        await self.session.commit()
        await self.session.refresh(score)
        
        logger.info(f"Scored decision: {decision_type} with utility {utility_score:.2f}")
        
        return score
    
    def _calculate_risk_penalty(self, risk_assessment: float, market_regime: str) -> float:
        """Calculate risk penalty based on risk and market conditions."""
        
        base_penalty = risk_assessment
        
        # Adjust for market regime
        regime_multipliers = {
            "BULL": 0.8,
            "NEUTRAL": 1.0,
            "VOLATILE": 1.3,
            "BEAR": 1.5,
        }
        
        multiplier = regime_multipliers.get(market_regime, 1.0)
        
        return min(1.0, base_penalty * multiplier)
    
    def _calculate_priority_alignment(self, priorities: list) -> float:
        """Calculate alignment with current priorities."""
        
        if not priorities:
            return 0.5
        
        # Average weight of top priorities
        top_weights = [p.get("weight", 0) for p in priorities[:3]]
        
        return sum(top_weights) / len(top_weights) if top_weights else 0.5
    
    def _calculate_utility(
        self,
        expected_value: float,
        risk_penalty: float,
        confidence: float,
        alignment_score: float,
        reversibility: float,
        resource_cost: float,
    ) -> float:
        """Calculate final utility score."""
        
        # Weighted formula
        utility = (
            expected_value * 0.25 +
            (1 - risk_penalty) * 0.25 +
            confidence * 0.15 +
            alignment_score * 0.15 +
            reversibility * 0.1 -
            resource_cost * 0.1
        )
        
        return max(0.0, min(1.0, utility))
    
    async def _get_priorities(self) -> list:
        """Get active priorities."""
        
        if self.priority_engine is None:
            from app.kernel.priorities.priority_engine import get_priority_engine
            self.priority_engine = await get_priority_engine(self.session)
        
        return await self.priority_engine.get_active_priorities()
    
    async def compare_decisions(self, decisions: list) -> list:
        """Compare multiple decisions and rank by utility."""
        
        scored = []
        
        for decision in decisions:
            score = await self.score_decision(
                decision_type=decision.get("type", "UNKNOWN"),
                decision_description=decision.get("description", ""),
                expected_value=decision.get("expected_value", 0.0),
                risk_assessment=decision.get("risk", 0.5),
                confidence=decision.get("confidence", 0.5),
                reversibility=decision.get("reversibility", 0.5),
                resource_cost=decision.get("resource_cost", 0.0),
                strategic_alignment=decision.get("alignment", 0.5),
                market_regime=decision.get("market_regime", "NEUTRAL"),
            )
            
            scored.append({
                "decision": decision,
                "score": score,
                "utility": score.utility_score,
            })
        
        # Sort by utility descending
        scored.sort(key=lambda x: x["utility"], reverse=True)
        
        return scored


async def get_decision_utility_engine(session: AsyncSession) -> DecisionUtilityEngine:
    """Get decision utility engine instance."""
    return DecisionUtilityEngine(session)
