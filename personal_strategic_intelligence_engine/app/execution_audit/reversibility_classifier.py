"""Reversibility classifier - classifies action reversibility."""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.execution_audit.outcome_models import (
    ReversibilityClassification,
    ReversibilityLevel,
)

logger = logging.getLogger(__name__)


class ReversibilityClassifier:
    """Classifies action reversibility."""

    # Default reversibility rules
    DEFAULT_RULES = {
        # Fully reversible actions
        "adjust_priority": ReversibilityLevel.FULLY_REVERSIBLE,
        "adjust_threshold": ReversibilityLevel.FULLY_REVERSIBLE,
        "update_parameter": ReversibilityLevel.FULLY_REVERSIBLE,
        "generate_insight": ReversibilityLevel.FULLY_REVERSIBLE,
        "create_reminder": ReversibilityLevel.FULLY_REVERSIBLE,
        
        # Partially reversible
        "allocate_resource": ReversibilityLevel.PARTIALLY_REVERSIBLE,
        
        # Irreversible (default)
    }

    def __init__(self):
        self._custom_rules: Dict[str, ReversibilityLevel] = {}

    def classify(
        self,
        action_type: str,
        domain: str = "",
    ) -> ReversibilityClassification:
        """
        Classify reversibility of an action.
        
        Args:
            action_type: Type of action
            domain: Domain of action
            
        Returns:
            ReversibilityClassification
        """
        # Check custom rules first
        if action_type in self._custom_rules:
            level = self._custom_rules[action_type]
            return self._create_classification(action_type, domain, level)
        
        # Check default rules
        if action_type in self.DEFAULT_RULES:
            level = self.DEFAULT_RULES[action_type]
            return self._create_classification(action_type, domain, level)
        
        # Default to unknown
        return self._create_classification(
            action_type,
            domain,
            ReversibilityLevel.UNKNOWN,
            ["No reversibility data available for this action type"],
        )

    def set_rule(self, action_type: str, level: ReversibilityLevel):
        """Set a custom reversibility rule."""
        self._custom_rules[action_type] = level
        logger.info(f"Set reversibility rule: {action_type} -> {level.value}")

    def get_rule(self, action_type: str) -> Optional[ReversibilityLevel]:
        """Get reversibility level for an action type."""
        if action_type in self._custom_rules:
            return self._custom_rules[action_type]
        if action_type in self.DEFAULT_RULES:
            return self.DEFAULT_RULES[action_type]
        return None

    def _create_classification(
        self,
        action_type: str,
        domain: str,
        level: ReversibilityLevel,
        conditions: Optional[List[str]] = None,
    ) -> ReversibilityClassification:
        """Create a reversibility classification."""
        
        conditions = conditions or self._get_default_conditions(action_type, level)
        
        return ReversibilityClassification(
            action_type=action_type,
            domain=domain,
            reversibility=level,
            reversible_conditions=conditions,
            recovery_time_estimate=self._estimate_recovery_time(level),
        )

    def _get_default_conditions(
        self,
        action_type: str,
        level: ReversibilityLevel,
    ) -> List[str]:
        """Get default conditions for reversibility."""
        
        if level == ReversibilityLevel.FULLY_REVERSIBLE:
            return [
                f"Action '{action_type}' can be easily reversed",
                "State can be restored to previous values",
                "No permanent data changes",
            ]
        elif level == ReversibilityLevel.PARTIALLY_REVERSIBLE:
            return [
                f"Action '{action_type}' may be partially reversible",
                "Some state changes may require manual intervention",
                "Consider backup before execution",
            ]
        elif level == ReversibilityLevel.IRREVERSIBLE:
            return [
                f"Action '{action_type}' is irreversible",
                "Cannot restore previous state automatically",
                "Requires explicit manual recovery",
            ]
        else:
            return [
                "Reversibility unknown - requires manual review",
            ]

    def _estimate_recovery_time(self, level: ReversibilityLevel) -> Optional[str]:
        """Estimate recovery time based on reversibility level."""
        
        if level == ReversibilityLevel.FULLY_REVERSIBLE:
            return "minutes"
        elif level == ReversibilityLevel.PARTIALLY_REVERSIBLE:
            return "hours"
        elif level == ReversibilityLevel.IRREVERSIBLE:
            return "manual"
        else:
            return None


# Global classifier instance
_classifier: Optional["ReversibilityClassifier"] = None


def get_reversibility_classifier() -> ReversibilityClassifier:
    """Get the global reversibility classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = ReversibilityClassifier()
    return _classifier
