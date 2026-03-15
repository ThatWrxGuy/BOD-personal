"""Finance Intelligence Service - coordinates the intelligence pipeline."""
from typing import Any, Dict, List, Optional

from app.finance.services.finance_state_service import FinanceStateService
from app.finance.intelligence.detectors.risk_detector import RiskDetector
from app.finance.intelligence.detectors.opportunity_detector import OpportunityDetector
from app.finance.intelligence.detectors.signal_extractor import SignalExtractor
from app.finance.intelligence.engines.recommendation_engine import RecommendationEngine
from app.finance.intelligence.engines.confidence_engine import ConfidenceEngine
from app.finance.intelligence.models.financial_signal import FinancialSignal
from app.finance.intelligence.models.financial_risk import FinancialRisk
from app.finance.intelligence.models.financial_opportunity import FinancialOpportunity
from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation


class FinanceIntelligenceService:
    """
    Coordinates the finance intelligence pipeline.
    
    Workflow:
    1. Retrieve financial state
    2. Run risk detection
    3. Run opportunity detection
    4. Extract financial signals
    5. Generate recommendations
    6. Score recommendation confidence
    """

    def __init__(self, finance_state_service: FinanceStateService):
        self.finance_state_service = finance_state_service

    async def generate_financial_signals(self, profile_id: int) -> List[FinancialSignal]:
        """
        Generate financial signals for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of FinancialSignal objects
        """
        # Get financial state
        financial_state = await self.finance_state_service.get_financial_state(profile_id)
        if not financial_state:
            return []

        # Run risk detection
        risks = self._detect_risks(financial_state)

        # Run opportunity detection
        opportunities = self._detect_opportunities(financial_state)

        # Extract signals
        signals = SignalExtractor.extract(risks, opportunities)

        return signals

    async def generate_financial_recommendations(
        self, profile_id: int
    ) -> List[FinancialRecommendation]:
        """
        Generate financial recommendations for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of FinancialRecommendation objects
        """
        # Get financial state
        financial_state = await self.finance_state_service.get_financial_state(profile_id)
        if not financial_state:
            return []

        # Get financial metrics
        financial_metrics = await self.finance_state_service.get_financial_metrics(profile_id)

        # Run risk detection
        risks = self._detect_risks(financial_state)

        # Run opportunity detection
        opportunities = self._detect_opportunities(financial_state)

        # Extract signals
        signals = SignalExtractor.extract(risks, opportunities)

        # Generate recommendations
        recommendations = RecommendationEngine.generate(financial_state, signals)

        # Score confidence
        recommendations = ConfidenceEngine.score(recommendations, financial_state)

        return recommendations

    async def get_financial_risks(self, profile_id: int) -> List[FinancialRisk]:
        """
        Get detected financial risks for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of FinancialRisk objects
        """
        financial_state = await self.finance_state_service.get_financial_state(profile_id)
        if not financial_state:
            return []

        return self._detect_risks(financial_state)

    async def get_financial_opportunities(
        self, profile_id: int
    ) -> List[FinancialOpportunity]:
        """
        Get detected financial opportunities for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            List of FinancialOpportunity objects
        """
        financial_state = await self.finance_state_service.get_financial_state(profile_id)
        if not financial_state:
            return []

        return self._detect_opportunities(financial_state)

    def _detect_risks(self, financial_state: Dict[str, Any]) -> List[FinancialRisk]:
        """Detect risks from financial state."""
        empty_metrics = {}
        return RiskDetector.detect(financial_state, empty_metrics)

    def _detect_opportunities(
        self, financial_state: Dict[str, Any]
    ) -> List[FinancialOpportunity]:
        """Detect opportunities from financial state."""
        empty_metrics = {}
        return OpportunityDetector.detect(financial_state, empty_metrics)
