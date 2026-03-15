"""Policy store - persistent storage for policy decisions."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import (
    ApprovalPolicyRule,
    PolicyTransitionEvent,
)

logger = logging.getLogger(__name__)


class PolicyStore:
    """Stores policy decisions and tier assignments."""

    def __init__(self):
        self._rules: Dict[str, ApprovalPolicyRule] = {}
        self._transitions: List[PolicyTransitionEvent] = []

    # Rule storage
    def store_rule(self, rule: ApprovalPolicyRule) -> bool:
        """Store a policy rule."""
        try:
            key = f"{rule.action_type}:{rule.domain}"
            self._rules[key] = rule
            logger.info(f"Stored policy rule for {rule.action_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to store rule: {e}")
            return False

    def get_rule(self, action_type: str, domain: str = "") -> Optional[ApprovalPolicyRule]:
        """Get a policy rule."""
        key = f"{action_type}:{domain}"
        return self._rules.get(key)

    def get_all_rules(self) -> List[ApprovalPolicyRule]:
        """Get all policy rules."""
        return list(self._rules.values())

    # Transition storage
    def store_transition(self, event: PolicyTransitionEvent) -> bool:
        """Store a transition event."""
        try:
            self._transitions.append(event)
            logger.info(f"Stored transition event: {event.event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store transition: {e}")
            return False

    def get_transitions(
        self,
        action_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[PolicyTransitionEvent]:
        """Get transition events."""
        events = self._transitions
        
        if action_type:
            events = [e for e in events if e.action_type == action_type]
        
        return events[-limit:]

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_rules": len(self._rules),
            "total_transitions": len(self._transitions),
        }

    def clear(self):
        """Clear all stored data."""
        self._rules.clear()
        self._transitions.clear()


# Global store instance
_store: Optional["PolicyStore"] = None


def get_policy_store() -> PolicyStore:
    """Get the global policy store instance."""
    global _store
    if _store is None:
        _store = PolicyStore()
    return _store
