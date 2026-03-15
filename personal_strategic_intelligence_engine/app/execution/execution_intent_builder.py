"""Execution intent builder - transforms recommendations into executable intents."""
import logging
from typing import Any, Dict, Optional

from app.execution.execution_models import ExecutionIntent

logger = logging.getLogger(__name__)


class ExecutionIntentBuilder:
    """Builds execution intents from recommendations."""

    def __init__(self):
        self._valid_action_types = {
            "adjust_priority",
            "allocate_resource",
            "generate_insight",
            "create_reminder",
            "adjust_threshold",
            "update_parameter",
        }

    def build_intent(
        self,
        recommendation_id: str,
        recommendation: Dict[str, Any],
        confidence: float = 0.5,
    ) -> ExecutionIntent:
        """
        Build an execution intent from a recommendation.
        
        Args:
            recommendation_id: ID of the source recommendation
            recommendation: Recommendation dictionary with action details
            confidence: Confidence score from learning/optimization
            
        Returns:
            ExecutionIntent ready for validation
        """
        # Extract domain
        domain = recommendation.get("target_domain", recommendation.get("domain", "unknown"))
        
        # Extract action type
        action_type = recommendation.get("action_type", recommendation.get("action", "adjust_priority"))
        
        # Validate action type
        if action_type not in self._valid_action_types:
            logger.warning(f"Unknown action type: {action_type}, defaulting to adjust_priority")
            action_type = "adjust_priority"
        
        # Extract parameters
        parameters = self._extract_parameters(recommendation)
        
        # Build intent
        intent = ExecutionIntent(
            recommendation_id=recommendation_id,
            domain=domain,
            action_type=action_type,
            parameters=parameters,
            confidence=confidence,
        )
        
        logger.info(f"Built execution intent: {intent.intent_id} for recommendation {recommendation_id}")
        
        return intent

    def _extract_parameters(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract actionable parameters from recommendation."""
        params = {}
        
        # Copy relevant fields
        if "priority" in recommendation:
            params["priority"] = recommendation["priority"]
        
        if "resource_allocation" in recommendation:
            params["resource_allocation"] = recommendation["resource_allocation"]
        
        if "target_value" in recommendation:
            params["target_value"] = recommendation["target_value"]
        
        if "threshold" in recommendation:
            params["threshold"] = recommendation["threshold"]
        
        if "adjustment" in recommendation:
            params["adjustment"] = recommendation["adjustment"]
        
        # Include risk factors if present
        if "risk_factors" in recommendation:
            params["risk_factors"] = recommendation["risk_factors"]
        
        # Include metadata
        if "metadata" in recommendation:
            params["metadata"] = recommendation["metadata"]
        
        return params

    def can_build_intent(self, recommendation: Dict[str, Any]) -> bool:
        """Check if a recommendation can be converted to an intent."""
        
        # Must have a domain
        if not recommendation.get("target_domain") and not recommendation.get("domain"):
            return False
        
        # Must have an action
        action = recommendation.get("action_type") or recommendation.get("action")
        if not action:
            return False
        
        return True

    def get_valid_action_types(self) -> set:
        """Get set of valid action types."""
        return self._valid_action_types.copy()


# Global builder instance
_builder: Optional[ExecutionIntentBuilder] = None


def get_intent_builder() -> ExecutionIntentBuilder:
    """Get the global intent builder instance."""
    global _builder
    if _builder is None:
        _builder = ExecutionIntentBuilder()
    return _builder
