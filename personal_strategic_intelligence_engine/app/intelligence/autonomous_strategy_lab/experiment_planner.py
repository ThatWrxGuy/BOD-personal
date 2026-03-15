"""Experiment Planner.

Schedules and structures research experiments.
"""

from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta

from app.intelligence.autonomous_strategy_lab.lab_models import ExperimentRun, ExperimentStatus


class ExperimentPlanner:
    """Plans research experiments."""
    
    def __init__(self):
        self.experiments = []
    
    def plan_experiment(
        self,
        variant_ids: List[str],
        regime_scope: List[str],
        experiment_type: str = "broad_exploration",
    ) -> ExperimentRun:
        """Plan a new experiment."""
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Determine sample requirements
        sample_size = len(variant_ids) * 50  # Rough estimate
        
        experiment = ExperimentRun(
            id=str(uuid.uuid4()),
            variant_ids=variant_ids,
            regime_scope=regime_scope,
            date_range={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            test_method=experiment_type,
            sample_size=sample_size,
            status=ExperimentStatus.PLANNED,
        )
        
        self.experiments.append(experiment)
        return experiment
    
    def plan_parameter_sweep(
        self,
        template_id: str,
        param_name: str,
        param_values: List,
        regime_scope: List[str],
    ) -> ExperimentRun:
        """Plan a parameter sweep experiment."""
        
        # Generate variant IDs (would come from variant generator)
        variant_ids = [f"variant-{v}" for v in param_values]
        
        return self.plan_experiment(
            variant_ids=variant_ids,
            regime_scope=regime_scope,
            experiment_type="parameter_sweep",
        )
    
    def plan_comparison(
        self,
        variant_a_id: str,
        variant_b_id: str,
        regime_scope: List[str],
    ) -> ExperimentRun:
        """Plan a head-to-head comparison."""
        
        return self.plan_experiment(
            variant_ids=[variant_a_id, variant_b_id],
            regime_scope=regime_scope,
            experiment_type="head_to_head",
        )
    
    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRun]:
        """Get experiment by ID."""
        
        for exp in self.experiments:
            if exp.id == experiment_id:
                return exp
        return None
    
    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[ExperimentRun]:
        """List experiments."""
        
        if status:
            return [e for e in self.experiments if e.status == status]
        return self.experiments


def create_planner() -> ExperimentPlanner:
    """Create experiment planner."""
    return ExperimentPlanner()
