"""Monte Carlo Simulation Engine - BB-FIN-020

Simulates strategy robustness with randomized trade sequences.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging
import uuid
import random
import statistics

from app.finance.strategy_lab.strategy_models import (
    BacktestResult,
    MonteCarloSimulation,
)

logger = logging.getLogger(__name__)


class MonteCarloEngine:
    """Monte Carlo simulation for strategy robustness testing."""
    
    def __init__(self):
        self._default_simulations = 1000
    
    def run_simulation(
        self,
        backtest_result: BacktestResult,
        num_simulations: Optional[int] = None,
    ) -> MonteCarloSimulation:
        """Run Monte Carlo simulation on backtest results."""
        
        if num_simulations is None:
            num_simulations = self._default_simulations
        
        trades = backtest_result.trades
        if not trades:
            logger.warning("No trades in backtest result, returning empty simulation")
            return self._empty_simulation(backtest_result, num_simulations)
        
        # Extract trade returns as percentages
        trade_returns = [t.pnl_percent / 100.0 for t in trades if t.pnl_percent != 0]
        
        if not trade_returns:
            logger.warning("No valid trade returns, returning empty simulation")
            return self._empty_simulation(backtest_result, num_simulations)
        
        num_trades = len(trade_returns)
        
        # Run simulations
        simulation_results = []
        
        for _ in range(num_simulations):
            # Resample with replacement
            sampled_returns = [random.choice(trade_returns) for _ in range(num_trades)]
            
            # Calculate cumulative return
            cumulative = 1.0
            for ret in sampled_returns:
                cumulative *= (1 + ret)
            
            simulation_results.append({
                "return": cumulative - 1.0,
                "drawdown": self._calculate_max_drawdown(sampled_returns),
                "win_rate": sum(1 for r in sampled_returns if r > 0) / len(sampled_returns),
            })
        
        # Extract metrics
        returns = [r["return"] for r in simulation_results]
        drawdowns = [abs(r["drawdown"]) for r in simulation_results]
        win_rates = [r["win_rate"] for r in simulation_results]
        
        # Sort for percentiles
        sorted_returns = sorted(returns)
        
        simulation_id = f"mc_{backtest_result.strategy_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        result = MonteCarloSimulation(
            simulation_id=simulation_id,
            strategy_id=backtest_result.strategy_id,
            num_simulations=num_simulations,
            num_trades_per_sim=num_trades,
            start_date=backtest_result.start_date,
            end_date=backtest_result.end_date,
            mean_return=statistics.mean(returns),
            median_return=statistics.median(returns),
            std_deviation=statistics.stdev(returns) if len(returns) > 1 else 0,
            percentile_5=self._percentile(sorted_returns, 5),
            percentile_10=self._percentile(sorted_returns, 10),
            percentile_25=self._percentile(sorted_returns, 25),
            percentile_75=self._percentile(sorted_returns, 75),
            percentile_90=self._percentile(sorted_returns, 90),
            percentile_95=self._percentile(sorted_returns, 95),
            avg_max_drawdown=statistics.mean(drawdowns),
            median_max_drawdown=statistics.median(drawdowns),
            worst_drawdown=min(drawdowns),
            prob_ruin=self._calculate_prob_ruin(returns),
            avg_win_rate=statistics.mean(win_rates),
        )
        
        logger.info(
            f"Monte Carlo simulation {simulation_id}: "
            f"mean={result.mean_return:.2%}, "
            f"prob_ruin={result.prob_ruin:.2%}"
        )
        
        return result
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns."""
        cumulative = 1.0
        peak = 1.0
        max_dd = 0.0
        
        for ret in returns:
            cumulative *= (1 + ret)
            if cumulative > peak:
                peak = cumulative
            dd = (peak - cumulative) / peak
            if dd > max_dd:
                max_dd = dd
        
        return -max_dd
    
    def _calculate_prob_ruin(self, returns: List[float]) -> float:
        """Calculate probability of ruin (losing >50% of initial capital)."""
        if not returns:
            return 0.0
        
        ruined = sum(1 for r in returns if r < -0.5)
        return ruined / len(returns)
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        weight = index - lower
        
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def _empty_simulation(
        self,
        backtest_result: BacktestResult,
        num_simulations: int,
    ) -> MonteCarloSimulation:
        """Return empty simulation result."""
        
        return MonteCarloSimulation(
            simulation_id=f"mc_{backtest_result.strategy_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            strategy_id=backtest_result.strategy_id,
            num_simulations=num_simulations,
            num_trades_per_sim=0,
            start_date=backtest_result.start_date,
            end_date=backtest_result.end_date,
        )
    
    def assess_robustness(
        self,
        simulation: MonteCarloSimulation,
    ) -> Dict[str, any]:
        """Assess strategy robustness from Monte Carlo results."""
        
        assessment = {
            "is_robust": False,
            "stability_score": 0.0,
            "risk_score": 0.0,
            "recommendations": [],
        }
        
        # Calculate stability score (based on return distribution)
        if simulation.std_deviation > 0:
            cv = abs(simulation.mean_return / simulation.std_deviation)  # Coefficient of variation
            stability = min(1.0, cv)
        else:
            stability = 0.0
        
        # Calculate risk score (based on drawdown and ruin probability)
        risk_factors = []
        if simulation.prob_ruin > 0.1:
            risk_factors.append("high_prob_ruin")
        if simulation.percentile_5 < -0.30:
            risk_factors.append("severe_downside")
        if simulation.std_deviation > 0.5:
            risk_factors.append("high_volatility")
        
        risk_score = len(risk_factors) / 3.0  # Normalize to 0-1
        
        # Overall robustness
        is_robust = (
            simulation.prob_ruin < 0.1 and
            simulation.percentile_10 > -0.20 and
            stability > 0.5
        )
        
        assessment["is_robust"] = is_robust
        assessment["stability_score"] = stability
        assessment["risk_score"] = risk_score
        assessment["risk_factors"] = risk_factors
        
        # Recommendations
        if simulation.prob_ruin > 0.1:
            assessment["recommendations"].append(
                "Reduce position size to lower ruin probability"
            )
        if simulation.percentile_5 < -0.30:
            assessment["recommendations"].append(
                "Implement tighter stop losses to reduce downside"
            )
        if stability < 0.5:
            assessment["recommendations"].append(
                "Strategy may be overfitted - consider simplifying rules"
            )
        if is_robust:
            assessment["recommendations"].append(
                "Strategy demonstrates good robustness characteristics"
            )
        
        return assessment


# Global instance
_monte_carlo_engine: Optional[MonteCarloEngine] = None


def get_monte_carlo_engine() -> MonteCarloEngine:
    """Get the Monte Carlo engine."""
    global _monte_carlo_engine
    
    if _monte_carlo_engine is None:
        _monte_carlo_engine = MonteCarloEngine()
    
    return _monte_carlo_engine
