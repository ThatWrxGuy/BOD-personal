"""Lab Orchestrator.

Coordinates the full research cycle.
"""

from typing import List, Dict, Optional

from app.intelligence.autonomous_strategy_lab.lab_models import (
    StrategyVariant, VariantStatus, ExperimentRun, ExperimentStatus
)
from app.intelligence.autonomous_strategy_lab.template_registry import get_registry
from app.intelligence.autonomous_strategy_lab.variant_generator import create_generator
from app.intelligence.autonomous_strategy_lab.constraint_engine import create_engine as create_constraint_engine
from app.intelligence.autonomous_strategy_lab.experiment_planner import create_planner
from app.intelligence.autonomous_strategy_lab.replay_test_engine import create_engine as create_replay_engine
from app.intelligence.autonomous_strategy_lab.result_aggregator import create_aggregator
from app.intelligence.autonomous_strategy_lab.promotion_engine import create_engine as create_promotion_engine
from app.intelligence.autonomous_strategy_lab.retirement_engine import create_engine as create_retirement_engine
from app.intelligence.autonomous_strategy_lab.research_registry import get_registry as get_research_registry


class LabOrchestrator:
    """Coordinates the full research cycle."""
    
    def __init__(self):
        self.template_registry = get_registry()
        self.variant_generator = create_generator()
        self.constraint_engine = create_constraint_engine()
        self.experiment_planner = create_planner()
        self.replay_engine = create_replay_engine()
        self.result_aggregator = create_aggregator()
        self.promotion_engine = create_promotion_engine()
        self.retirement_engine = create_retirement_engine()
        self.research_registry = get_research_registry()
    
    def run_research_cycle(
        self,
        template_id: str,
        num_variants: int = 10,
    ) -> Dict:
        """Run complete research cycle."""
        
        # 1. Generate variants
        variants = self.variant_generator.generate_variants(template_id, num_variants)
        
        # 2. Apply constraints
        valid_variants = []
        for variant in variants:
            if self.constraint_engine.is_valid(variant):
                variant.status = VariantStatus.QUEUED
                valid_variants.append(variant)
                self.research_registry.register_variant(variant)
        
        # 3. Plan experiment
        variant_ids = [v.id for v in valid_variants]
        experiment = self.experiment_planner.plan_experiment(
            variant_ids=variant_ids,
            regime_scope=["trend_morning", "midday", "power_hour"],
        )
        experiment.status = ExperimentStatus.RUNNING
        self.research_registry.register_experiment(experiment)
        
        # 4. Run tests (simulated)
        results = self.replay_engine.run_tests(experiment, [])
        
        # 5. Evaluate results
        promotion_results = []
        for variant in valid_variants:
            perf = results.get(variant.id)
            if perf:
                decision = self.promotion_engine.evaluate_promotion(variant, perf)
                self.research_registry.record_promotion(decision)
                promotion_results.append(decision)
                
                # Update variant status
                if decision.decision.value == "promoted":
                    variant.status = VariantStatus.PROMOTED
                elif decision.decision.value == "rejected":
                    variant.status = VariantStatus.REJECTED
        
        experiment.status = ExperimentStatus.COMPLETED
        
        # 6. Generate report
        template = self.template_registry.get(template_id)
        report = self.result_aggregator.generate_research_report(
            template_name=template.name if template else template_id,
            results=results,
        )
        
        return {
            "experiment_id": experiment.id,
            "variants_generated": len(variants),
            "variants_valid": len(valid_variants),
            "promotions": [d.to_dict() for d in promotion_results],
            "report": report,
        }
    
    def get_research_summary(self) -> Dict:
        """Get research summary."""
        
        return {
            "registry": self.research_registry.get_summary(),
            "pending_promotions": len(self.promotion_engine.get_pending_decisions()),
        }


def create_orchestrator() -> LabOrchestrator:
    """Create lab orchestrator."""
    return LabOrchestrator()
