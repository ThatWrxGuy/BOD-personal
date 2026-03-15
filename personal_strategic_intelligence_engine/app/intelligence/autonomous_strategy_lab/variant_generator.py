"""Variant Generator.

Generates new strategy variants from templates.
"""

from typing import List, Dict, Optional
import uuid
import random

from app.intelligence.autonomous_strategy_lab.lab_models import StrategyVariant, VariantStatus
from app.intelligence.autonomous_strategy_lab.template_registry import get_registry
from app.intelligence.autonomous_strategy_lab.strategy_genome import create_genome


class VariantGenerator:
    """Generates variants from templates."""
    
    def __init__(self):
        self.template_registry = get_registry()
    
    def generate_variants(
        self,
        template_id: str,
        num_variants: int = 10,
        method: str = "parameter_variation",
    ) -> List[StrategyVariant]:
        """Generate variants from template."""
        
        template = self.template_registry.get(template_id)
        if not template:
            return []
        
        variants = []
        
        for i in range(num_variants):
            if method == "parameter_variation":
                params = self._parameter_variation(template)
            elif method == "rule_mutation":
                params = self._rule_mutation(template)
            elif method == "hybrid":
                params = self._hybrid_composition(template)
            else:
                params = self._parameter_variation(template)
            
            variant = StrategyVariant(
                id=str(uuid.uuid4()),
                template_id=template_id,
                parent_variant_id=None,
                parameters=params,
                generated_by=method,
                creation_reason=f"Generated via {method}",
                status=VariantStatus.DRAFT,
            )
            
            variants.append(variant)
        
        return variants
    
    def _parameter_variation(self, template) -> Dict:
        """Generate parameter variations."""
        
        params = {}
        param_space = template.parameter_space
        
        for param_name, values in param_space.items():
            params[param_name] = random.choice(values)
        
        return params
    
    def _rule_mutation(self, template) -> Dict:
        """Generate rule mutations."""
        
        params = self._parameter_variation(template)
        
        # Add rule mutations
        if "confirmation_bars" not in params:
            params["confirmation_bars"] = random.choice([1, 2])
        
        if random.random() > 0.5:
            params["strike_selection"] = random.choice(["atm", "1step_otm", "2step_otm"])
        
        return params
    
    def _hybrid_composition(self, template) -> Dict:
        """Generate hybrid variants."""
        
        params = self._parameter_variation(template)
        
        # Add hybrid components
        params["hybrid_entry"] = random.choice(["vwap_reclaim", "liquidity_sweep"])
        params["hybrid_confirmation"] = random.choice(["gamma_rising", "volume_surge", "bar_confirmation"])
        
        return params
    
    def generate_parameter_sweep(
        self,
        template_id: str,
        param_name: str,
    ) -> List[StrategyVariant]:
        """Generate parameter sweep variants."""
        
        template = self.template_registry.get(template_id)
        if not template:
            return []
        
        param_values = template.parameter_space.get(param_name, [])
        
        variants = []
        for value in param_values:
            params = self._parameter_variation(template)
            params[param_name] = value
            
            variant = StrategyVariant(
                id=str(uuid.uuid4()),
                template_id=template_id,
                parent_variant_id=None,
                parameters=params,
                generated_by="parameter_sweep",
                creation_reason=f"Sweep {param_name}={value}",
                status=VariantStatus.DRAFT,
            )
            
            variants.append(variant)
        
        return variants


def create_generator() -> VariantGenerator:
    """Create variant generator."""
    return VariantGenerator()
