"""Strategy Genome.

Represents strategies as composable genes.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Gene:
    """Individual strategy gene."""
    category: str
    name: str
    value: Any
    description: str


@dataclass
class StrategyGenome:
    """Complete genome for a strategy variant."""
    genome_id: str
    template_id: str
    genes: Dict[str, Gene] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "genome_id": self.genome_id,
            "template_id": self.template_id,
            "genes": {
                k: {"category": v.category, "name": v.name, "value": v.value, "description": v.description}
                for k, v in self.genes.items()
            },
            "created_at": self.created_at.isoformat(),
        }
    
    def get_gene(self, category: str) -> Optional[Gene]:
        """Get gene by category."""
        return self.genes.get(category)
    
    def set_gene(self, category: str, name: str, value: Any, description: str = "") -> None:
        """Set gene value."""
        self.genes[category] = Gene(
            category=category,
            name=name,
            value=value,
            description=description,
        )


# Gene categories
ENTRY_CONDITION = "entry_condition"
CONFIRMATION_CONDITION = "confirmation_condition"
REGIME_FILTER = "regime_filter"
TIME_FILTER = "time_filter"
STRIKE_SELECTION = "strike_selection"
EXIT_RULE = "exit_rule"
STOP_RULE = "stop_rule"
POSITION_SIZING = "position_sizing"
HOLD_WINDOW = "hold_window"


# Gene definitions
class GeneLibrary:
    """Library of available genes."""
    
    ENTRY_GENES = {
        "vwap_reclaim": {"name": "VWAP Reclaim", "description": "Enter on VWAP reclaim after downside sweep"},
        "liquidity_sweep": {"name": "Liquidity Sweep", "description": "Enter on liquidity sweep detection"},
        "opening_range_breakout": {"name": "Opening Range Breakout", "description": "Enter on opening range breakout"},
        "gamma_acceleration": {"name": "Gamma Acceleration", "description": "Enter on gamma acceleration"},
        "momentum_breakout": {"name": "Momentum Breakout", "description": "Enter on momentum confirmation"},
    }
    
    CONFIRMATION_GENES = {
        "gamma_rising": {"name": "Gamma Rising", "description": "Confirm with rising gamma"},
        "volume_surge": {"name": "Volume Surge", "description": "Confirm with volume surge"},
        "bar_confirmation": {"name": "Bar Confirmation", "description": "Confirm with N bars"},
        "none": {"name": "No Confirmation", "description": "No confirmation required"},
    }
    
    REGIME_FILTER_GENES = {
        "trend_morning": {"name": "Trend Morning", "description": "Only trade in morning trend"},
        "trend_day": {"name": "Trend Day", "description": "Only trade in trend days"},
        "any": {"name": "Any Regime", "description": "No regime filter"},
    }
    
    TIME_FILTER_GENES = {
        "market_open": {"name": "Market Open", "description": "Only during market open"},
        "power_hour": {"name": "Power Hour", "description": "Only during power hour"},
        "any_time": {"name": "Any Time", "description": "No time filter"},
    }
    
    STRIKE_SELECTION_GENES = {
        "atm": {"name": "ATM", "description": "At-the-money strike"},
        "1step_otm": {"name": "1-Step OTM", "description": "One step out-of-the-money"},
        "2step_otm": {"name": "2-Step OTM", "description": "Two steps out-of-the-money"},
        "delta_target": {"name": "Delta Target", "description": "Select by delta target"},
    }
    
    EXIT_RULE_GENES = {
        "fixed_time": {"name": "Fixed Time", "description": "Exit after fixed time"},
        "failure_candle": {"name": "Failure Candle", "description": "Exit on failure candle"},
        "trailing_stop": {"name": "Trailing Stop", "description": "Trailing stop exit"},
        "profit_target": {"name": "Profit Target", "description": "Exit at profit target"},
    }
    
    STOP_RULE_GENES = {
        "fixed_stop": {"name": "Fixed Stop", "description": "Fixed stop loss"},
        "vwap_stop": {"name": "VWAP Stop", "description": "Stop at VWAP breach"},
        "time_stop": {"name": "Time Stop", "description": "Stop if no movement"},
    }
    
    POSITION_SIZING_GENES = {
        "fixed_size": {"name": "Fixed Size", "description": "Fixed contract count"},
        "risk_based": {"name": "Risk Based", "description": "Size by risk percentage"},
        "volatility_based": {"name": "Volatility Based", "description": "Size by volatility"},
    }
    
    HOLD_WINDOW_GENES = {
        "5min": {"name": "5 Minutes", "description": "Hold for 5 minutes"},
        "8min": {"name": "8 Minutes", "description": "Hold for 8 minutes"},
        "10min": {"name": "10 Minutes", "description": "Hold for 10 minutes"},
        "15min": {"name": "15 Minutes", "description": "Hold for 15 minutes"},
    }


def create_genome(template_id: str, parameters: Dict[str, Any]) -> StrategyGenome:
    """Create a genome from parameters."""
    import uuid
    
    genome = StrategyGenome(
        genome_id=str(uuid.uuid4()),
        template_id=template_id,
    )
    
    # Map parameters to genes
    if "entry_condition" in parameters:
        gene_info = GeneLibrary.ENTRY_GENES.get(parameters["entry_condition"], {})
        genome.set_gene(ENTRY_CONDITION, parameters["entry_condition"], parameters["entry_condition"], gene_info.get("description", ""))
    
    if "confirmation" in parameters:
        genome.set_gene(CONFIRMATION_CONDITION, parameters["confirmation"], parameters["confirmation"], "")
    
    if "regime_filter" in parameters:
        genome.set_gene(REGIME_FILTER, parameters["regime_filter"], parameters["regime_filter"], "")
    
    if "time_filter" in parameters:
        genome.set_gene(TIME_FILTER, parameters["time_filter"], parameters["time_filter"], "")
    
    if "strike_selection" in parameters:
        genome.set_gene(STRIKE_SELECTION, parameters["strike_selection"], parameters["strike_selection"], "")
    
    if "exit_rule" in parameters:
        genome.set_gene(EXIT_RULE, parameters["exit_rule"], parameters["exit_rule"], "")
    
    if "stop_rule" in parameters:
        genome.set_gene(STOP_RULE, parameters["stop_rule"], parameters["stop_rule"], "")
    
    if "position_sizing" in parameters:
        genome.set_gene(POSITION_SIZING, parameters["position_sizing"], parameters["position_sizing"], "")
    
    if "hold_window" in parameters:
        genome.set_gene(HOLD_WINDOW, parameters["hold_window"], parameters["hold_window"], "")
    
    return genome
