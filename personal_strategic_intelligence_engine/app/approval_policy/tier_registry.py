"""Tier registry - stores action tier assignments."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    ApprovalPolicyRule,
    DEFAULT_TIERS,
)

logger = logging.getLogger(__name__)


class TierRegistry:
    """Registry of action tier assignments."""

    def __init__(self):
        self._rules: Dict[str, ApprovalPolicyRule] = {}  # (action_type, domain) -> rule

    def register(
        self,
        action_type: str,
        domain: str,
        tier: ApprovalTierLevel,
        justification: str = "",
        factors: Optional[List[str]] = None,
    ) -> ApprovalPolicyRule:
        """
        Register a tier assignment.
        
        Args:
            action_type: Type of action
            domain: Domain
            tier: Assigned tier
            justification: Justification for assignment
            factors: Factors considered
            
        Returns:
            Created ApprovalPolicyRule
        """
        key = self._make_key(action_type, domain)
        
        rule = ApprovalPolicyRule(
            action_type=action_type,
            domain=domain,
            tier=tier,
            justification=justification,
            factors=factors or [],
        )
        
        self._rules[key] = rule
        
        logger.info(f"Registered tier {tier.value} for {action_type}:{domain}")
        
        return rule

    def get(self, action_type: str, domain: str = "") -> Optional[ApprovalPolicyRule]:
        """Get tier assignment for an action."""
        key = self._make_key(action_type, domain)
        return self._rules.get(key)

    def list_all(self) -> List[ApprovalPolicyRule]:
        """List all registered rules."""
        return list(self._rules.values())

    def list_by_tier(self, tier: ApprovalTierLevel) -> List[ApprovalPolicyRule]:
        """List all rules for a specific tier."""
        return [r for r in self._rules.values() if r.tier == tier]

    def unregister(self, action_type: str, domain: str = "") -> bool:
        """Unregister a tier assignment."""
        key = self._make_key(action_type, domain)
        
        if key in self._rules:
            del self._rules[key]
            logger.info(f"Unregistered tier for {action_type}:{domain}")
            return True
        
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        tier_counts = {}
        
        for rule in self._rules.values():
            tier = rule.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        return {
            "total_rules": len(self._rules),
            "by_tier": tier_counts,
        }

    def _make_key(self, action_type: str, domain: str) -> str:
        """Create key for action/domain pair."""
        return f"{action_type}:{domain}"


# Global registry instance
_registry: Optional["TierRegistry"] = None


def get_tier_registry() -> TierRegistry:
    """Get the global tier registry instance."""
    global _registry
    if _registry is None:
        _registry = TierRegistry()
    return _registry
