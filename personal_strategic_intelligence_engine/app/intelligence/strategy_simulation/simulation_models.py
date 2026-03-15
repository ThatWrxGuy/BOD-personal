"""Simulation Models for Strategy Simulation Subsystem.

Models representing strategy configurations, simulation results, and discovery outputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StrategyType(str, Enum):
    MOMENTUM = "momentum"
    REVERSAL = "reversal"
    BREAKOUT = "breakout"
    RANGE = "range"
    HYBRID = "hybrid"


@dataclass
class StrategyConfig:
    """Configuration for a tactical strategy."""
    strategy_id: str
    strategy_name: str
    strategy_type: StrategyType
    parameters: Dict[str, Any]
    hypothesis: str
    created_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "strategy_type": self.strategy_type.value,
            "parameters": self.parameters,
            "hypothesis": self.hypothesis,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SimulatedTrade:
    """A single simulated trade."""
    trade_id: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    direction: str
    pnl: Optional[float]
    pnl_pct: Optional[float]
    max_favorable_excursion: float
    max_adverse_excursion: float
    holding_period_minutes: int
    regime: str
    day_type: str
    vwap_state: str
    
    def to_dict(self) -> dict:
        return {
            "trade_id": self.trade_id,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "direction": self.direction,
            "pnl": self.pnl,
            "pnl_pct": self.pnl_pct,
            "max_favorable_excursion": self.max_favorable_excursion,
            "max_adverse_excursion": self.max_adverse_excursion,
            "holding_period_minutes": self.holding_period_minutes,
            "regime": self.regime,
            "day_type": self.day_type,
            "vwap_state": self.vwap_state,
        }


@dataclass
class SimulationMetrics:
    """Quantitative metrics for a strategy simulation."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    expectancy: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    avg_holding_period: float
    volatility: float
    volatility_adjusted_return: float
    
    def to_dict(self) -> dict:
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
            "expectancy": self.expectancy,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_pct": self.max_drawdown_pct,
            "avg_holding_period": self.avg_holding_period,
            "volatility": self.volatility,
            "volatility_adjusted_return": self.volatility_adjusted_return,
        }


@dataclass
class RegimeBreakdown:
    """Performance breakdown by regime."""
    regime: str
    trade_count: int
    win_rate: float
    expectancy: float
    avg_pnl: float
    
    def to_dict(self) -> dict:
        return {
            "regime": self.regime,
            "trade_count": self.trade_count,
            "win_rate": self.win_rate,
            "expectancy": self.expectancy,
            "avg_pnl": self.avg_pnl,
        }


@dataclass
class SimulationResult:
    """Complete result of a strategy simulation."""
    simulation_id: str
    strategy_config: StrategyConfig
    status: SimulationStatus
    start_time: datetime
    end_time: Optional[datetime]
    metrics: SimulationMetrics
    trades: List[SimulatedTrade]
    regime_breakdown: List[RegimeBreakdown]
    day_type_breakdown: List[RegimeBreakdown]
    vwap_breakdown: List[RegimeBreakdown]
    
    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "strategy_config": self.strategy_config.to_dict(),
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": self.metrics.to_dict(),
            "regime_breakdown": [r.to_dict() for r in self.regime_breakdown],
            "day_type_breakdown": [r.to_dict() for r in self.day_type_breakdown],
            "vwap_breakdown": [r.to_dict() for r in self.vwap_breakdown],
        }


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result."""
    simulation_id: str
    strategy_id: str
    iteration_count: int
    median_expectancy: float
    percentile_5_expectancy: float
    percentile_95_expectancy: float
    robustness_score: float
    downside_risk: float
    distribution: Dict[str, float]
    
    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "strategy_id": self.strategy_id,
            "iteration_count": self.iteration_count,
            "median_expectancy": self.median_expectancy,
            "percentile_5_expectancy": self.percentile_5_expectancy,
            "percentile_95_expectancy": self.percentile_95_expectancy,
            "robustness_score": self.robustness_score,
            "downside_risk": self.downside_risk,
            "distribution": self.distribution,
        }


@dataclass
class StrategyComparison:
    """Comparison between two strategies."""
    comparison_id: str
    baseline_strategy: StrategyConfig
    candidate_strategy: StrategyConfig
    baseline_metrics: SimulationMetrics
    candidate_metrics: SimulationMetrics
    expectancy_improvement: float
    sharpe_improvement: float
    drawdown_improvement: float
    winner: str
    recommendation: str
    
    def to_dict(self) -> dict:
        return {
            "comparison_id": self.comparison_id,
            "baseline_strategy": self.baseline_strategy.to_dict(),
            "candidate_strategy": self.candidate_strategy.to_dict(),
            "baseline_metrics": self.baseline_metrics.to_dict(),
            "candidate_metrics": self.candidate_metrics.to_dict(),
            "expectancy_improvement": self.expectancy_improvement,
            "sharpe_improvement": self.sharpe_improvement,
            "drawdown_improvement": self.drawdown_improvement,
            "winner": self.winner,
            "recommendation": self.recommendation,
        }


@dataclass
class StrategyDiscovery:
    """Discovered strategy pattern from simulation."""
    discovery_id: str
    pattern_name: str
    description: str
    conditions: Dict[str, Any]
    sample_size: int
    statistical_significance: float
    win_rate: float
    expectancy: float
    confidence: float
    discovered_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "discovery_id": self.discovery_id,
            "pattern_name": self.pattern_name,
            "description": self.description,
            "conditions": self.conditions,
            "sample_size": self.sample_size,
            "statistical_significance": self.statistical_significance,
            "win_rate": self.win_rate,
            "expectancy": self.expectancy,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at.isoformat(),
        }


@dataclass
class OptimizationProposal:
    """Strategy optimization proposal from simulation."""
    proposal_id: str
    strategy_id: str
    optimization_type: str
    target_parameter: str
    current_value: Any
    proposed_value: Any
    expected_improvement: float
    confidence: float
    rationale: str
    created_at: datetime
    status: str = "pending"
    
    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "strategy_id": self.strategy_id,
            "optimization_type": self.optimization_type,
            "target_parameter": self.target_parameter,
            "current_value": str(self.current_value),
            "proposed_value": str(self.proposed_value),
            "expected_improvement": self.expected_improvement,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


@dataclass
class SimulationSnapshot:
    """Complete simulation snapshot."""
    timestamp: datetime
    simulations: List[SimulationResult]
    comparisons: List[StrategyComparison]
    discoveries: List[StrategyDiscovery]
    proposals: List[OptimizationProposal]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "simulations": [s.to_dict() for s in self.simulations],
            "comparisons": [c.to_dict() for c in self.comparisons],
            "discoveries": [d.to_dict() for d in self.discoveries],
            "proposals": [p.to_dict() for p in self.proposals],
        }
