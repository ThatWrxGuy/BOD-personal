"""Doctrine registry for managing policy rules."""
import logging
from typing import Dict, List, Optional

from app.doctrine.doctrine_models import PolicyRule, PolicyRuleType
from app.doctrine.doctrine_rules import DoctrineRule, create_default_rules

logger = logging.getLogger(__name__)


class DoctrineRegistry:
    """Central registry of doctrine rules."""

    def __init__(self):
        self._rules: Dict[str, DoctrineRule] = {}
        self._rules_by_type: Dict[PolicyRuleType, List[str]] = {}
        
        # Initialize with default rules
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Initialize with default rules."""
        for rule in create_default_rules():
            self.register_rule(rule)

    def register_rule(self, rule: DoctrineRule) -> bool:
        """Register a doctrine rule."""
        try:
            self._rules[rule.rule_id] = rule
            
            # Index by type
            if rule.rule_type not in self._rules_by_type:
                self._rules_by_type[rule.rule_type] = []
            if rule.rule_id not in self._rules_by_type[rule.rule_type]:
                self._rules_by_type[rule.rule_type].append(rule.rule_id)
            
            logger.info(f"Registered doctrine rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register rule {rule.rule_id}: {e}")
            return False

    def get_rule(self, rule_id: str) -> Optional[DoctrineRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_rules_by_type(self, rule_type: PolicyRuleType) -> List[DoctrineRule]:
        """Get all rules of a specific type."""
        rule_ids = self._rules_by_type.get(rule_type, [])
        return [self._rules[rid] for rid in rule_ids if rid in self._rules]

    def get_all_rules(self) -> List[DoctrineRule]:
        """Get all registered rules."""
        return list(self._rules.values())

    def get_enabled_rules(self) -> List[DoctrineRule]:
        """Get all enabled rules."""
        return [r for r in self._rules.values() if r.is_enabled()]

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        rule = self._rules.get(rule_id)
        if rule:
            rule.rule.enabled = True
            logger.info(f"Enabled rule: {rule_id}")
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        rule = self._rules.get(rule_id)
        if rule:
            rule.rule.enabled = False
            logger.info(f"Disabled rule: {rule_id}")
            return True
        return False

    def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """Update rule configuration."""
        rule = self._rules.get(rule_id)
        if not rule:
            return False
        
        if "weight" in updates:
            rule.rule.weight = updates["weight"]
        if "threshold" in updates:
            rule.rule.threshold = updates["threshold"]
        if "enabled" in updates:
            rule.rule.enabled = updates["enabled"]
        
        logger.info(f"Updated rule: {rule_id}")
        return True

    def get_statistics(self) -> Dict:
        """Get registry statistics."""
        enabled = len(self.get_enabled_rules())
        disabled = len(self._rules) - enabled
        
        by_type = {}
        for rtype, rule_ids in self._rules_by_type.items():
            by_type[rtype.value] = len(rule_ids)
        
        return {
            "total_rules": len(self._rules),
            "enabled_rules": enabled,
            "disabled_rules": disabled,
            "rules_by_type": by_type,
        }


# Global registry instance
_registry: Optional[DoctrineRegistry] = None


def get_doctrine_registry() -> DoctrineRegistry:
    """Get the global doctrine registry instance."""
    global _registry
    if _registry is None:
        _registry = DoctrineRegistry()
    return _registry
