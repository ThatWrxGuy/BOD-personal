"""Lab Service.

Main service interface for the Autonomous Strategy Lab.
"""

from typing import List, Dict, Optional

from app.intelligence.autonomous_strategy_lab.lab_orchestrator import create_orchestrator
from app.intelligence.autonomous_strategy_lab.template_registry import get_registry


class LabService:
    """Main service for the Autonomous Strategy Lab."""
    
    def __init__(self):
        self.orchestrator = create_orchestrator()
        self.template_registry = get_registry()
    
    def run_research(self, template_id: str, num_variants: int = 10) -> Dict:
        """Run research on a template."""
        return self.orchestrator.run_research_cycle(template_id, num_variants)
    
    def get_templates(self) -> List[Dict]:
        """Get all templates."""
        return [t.to_dict() for t in self.template_registry.list_all()]
    
    def get_variants(self, status: Optional[str] = None) -> List[Dict]:
        """Get variants."""
        variants = self.orchestrator.research_registry.list_variants()
        if status:
            from app.intelligence.autonomous_strategy_lab.lab_models import VariantStatus
            variants = [v for v in variants if v.status.value == status]
        return [v.to_dict() for v in variants]
    
    def get_summary(self) -> Dict:
        """Get lab summary."""
        return self.orchestrator.get_research_summary()


def create_service() -> LabService:
    """Create lab service."""
    return LabService()
