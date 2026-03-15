"""Template Registry.

Stores canonical strategy families.
"""

from typing import Dict, List, Optional

from app.intelligence.autonomous_strategy_lab.lab_models import StrategyTemplate, DEFAULT_TEMPLATES


class TemplateRegistry:
    """Registry of strategy templates."""
    
    def __init__(self):
        self.templates: Dict[str, StrategyTemplate] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Load default templates."""
        for template in DEFAULT_TEMPLATES:
            self.templates[template.id] = template
    
    def register(self, template: StrategyTemplate) -> None:
        """Register a new template."""
        self.templates[template.id] = template
    
    def get(self, template_id: str) -> Optional[StrategyTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def list_all(self) -> List[StrategyTemplate]:
        """List all templates."""
        return list(self.templates.values())
    
    def list_by_domain(self, domain: str) -> List[StrategyTemplate]:
        """List templates by domain."""
        return [t for t in self.templates.values() if t.domain == domain]
    
    def get_parameter_space(self, template_id: str) -> Dict:
        """Get parameter space for template."""
        template = self.get(template_id)
        return template.parameter_space if template else {}


# Global registry
_registry = None

def get_registry() -> TemplateRegistry:
    """Get global template registry."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry
