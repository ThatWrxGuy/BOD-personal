"""Recommendation Classifier - classifies recommendations based on governance requirements."""
from typing import List, Any, Dict

from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation, Priority
from app.finance.governance.models.financial_decision_request import DecisionClass


class RecommendationClassifier:
    """
    Classifies recommendations based on governance requirements.
    
    Classification rules:
    - Low-impact insights → informational
    - Financial behavior changes → user_approval
    - Strategic financial decisions → board_review
    """

    # Keywords that indicate different decision classes
    BOARD_REVIEW_KEYWORDS = [
        "major", "significant", "strategic", "allocation", "rebalance",
        "retirement", "estate", "trust", "tax", "optimization",
        "large", "substantial", "portfolio", "diversification",
    ]
    
    USER_APPROVAL_KEYWORDS = [
        "debt", "payoff", "increase", "decrease", "adjust",
        "change", "modify", "shift", "transfer", "consolidate",
    ]
    
    # Priority threshold for board review
    BOARD_REVIEW_PRIORITY_THRESHOLD = Priority.HIGH

    @staticmethod
    def classify(recommendation: FinancialRecommendation) -> DecisionClass:
        """
        Classify a recommendation based on governance requirements.

        Args:
            recommendation: The financial recommendation to classify

        Returns:
            DecisionClass indicating the required approval level
        """
        title_lower = recommendation.title.lower()
        summary_lower = recommendation.summary.lower()
        
        # Check for board review criteria
        if RecommendationClassifier._requires_board_review(recommendation, title_lower, summary_lower):
            return DecisionClass.BOARD_REVIEW
        
        # Check for user approval criteria
        if RecommendationClassifier._requires_user_approval(title_lower, summary_lower):
            return DecisionClass.USER_APPROVAL
        
        # Default to informational
        return DecisionClass.INFORMATIONAL

    @staticmethod
    def _requires_board_review(
        recommendation: FinancialRecommendation,
        title_lower: str,
        summary_lower: str,
    ) -> bool:
        """Check if recommendation requires board review."""
        # High priority items require board review
        if recommendation.priority == Priority.CRITICAL:
            return True
        
        # Check keywords
        for keyword in RecommendationClassifier.BOARD_REVIEW_KEYWORDS:
            if keyword in title_lower or keyword in summary_lower:
                return True
        
        # Large expected benefits may require board review
        if "significant" in summary_lower or "substantial" in summary_lower:
            return True
        
        return False

    @staticmethod
    def _requires_user_approval(title_lower: str, summary_lower: str) -> bool:
        """Check if recommendation requires user approval."""
        for keyword in RecommendationClassifier.USER_APPROVAL_KEYWORDS:
            if keyword in title_lower or keyword in summary_lower:
                return True
        
        return False

    @staticmethod
    def classify_batch(recommendations: List[FinancialRecommendation]) -> Dict[DecisionClass, List[FinancialRecommendation]]:
        """
        Classify multiple recommendations.

        Args:
            recommendations: List of financial recommendations

        Returns:
            Dictionary mapping DecisionClass to list of recommendations
        """
        classified = {
            DecisionClass.INFORMATIONAL: [],
            DecisionClass.USER_APPROVAL: [],
            DecisionClass.BOARD_REVIEW: [],
        }
        
        for recommendation in recommendations:
            decision_class = RecommendationClassifier.classify(recommendation)
            classified[decision_class].append(recommendation)
        
        return classified

    @staticmethod
    def get_approval_summary(recommendations: List[FinancialRecommendation]) -> Dict[str, int]:
        """
        Get summary of approval requirements.

        Args:
            recommendations: List of financial recommendations

        Returns:
            Dictionary with counts per decision class
        """
        classified = RecommendationClassifier.classify_batch(recommendations)
        
        return {
            "informational": len(classified[DecisionClass.INFORMATIONAL]),
            "user_approval_required": len(classified[DecisionClass.USER_APPROVAL]),
            "board_review_required": len(classified[DecisionClass.BOARD_REVIEW]),
        }
