"""Strategy Evaluator.

Evaluates simulated strategies using quantitative metrics.
"""

from typing import List, Dict

from app.intelligence.strategy_simulation.simulation_models import (
    SimulationResult,
    SimulationMetrics,
)


class StrategyEvaluator:
    """Evaluates strategy simulation results."""
    
    def __init__(self):
        self.min_trade_count = 20
        self.min_expectancy = 0.1
        self.min_sharpe = 0.5
        self.max_drawdown_threshold = 50
    
    def evaluate(self, result: SimulationResult) -> Dict:
        """Evaluate a simulation result."""
        
        metrics = result.metrics
        
        # Calculate overall score
        score = self._calculate_score(metrics)
        
        # Determine if strategy passes
        passes = self._passes_evaluation(metrics)
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(metrics)
        weaknesses = self._identify_weaknesses(metrics)
        
        return {
            "simulation_id": result.simulation_id,
            "strategy_id": result.strategy_config.strategy_id,
            "score": score,
            "passes": passes,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "metrics": metrics.to_dict(),
        }
    
    def _calculate_score(self, metrics: SimulationMetrics) -> float:
        """Calculate overall strategy score."""
        
        score = 0
        
        # Expectancy (30%)
        if metrics.expectancy > 0:
            score += min(30, metrics.expectancy * 30)
        
        # Win rate (20%)
        score += metrics.win_rate * 0.2
        
        # Sharpe ratio (20%)
        score += min(20, metrics.sharpe_ratio * 10)
        
        # Profit factor (15%)
        if metrics.profit_factor > 1:
            score += min(15, metrics.profit_factor * 5)
        
        # Drawdown penalty
        if metrics.max_drawdown > self.max_drawdown_threshold:
            score -= 10
        
        return max(0, min(100, score))
    
    def _passes_evaluation(self, metrics: SimulationMetrics) -> bool:
        """Check if strategy passes evaluation criteria."""
        
        if metrics.total_trades < self.min_trade_count:
            return False
        
        if metrics.expectancy < self.min_expectancy:
            return False
        
        if metrics.sharpe_ratio < self.min_sharpe:
            return False
        
        if metrics.max_drawdown > self.max_drawdown_threshold * 2:
            return False
        
        return True
    
    def _identify_strengths(self, metrics: SimulationMetrics) -> List[str]:
        """Identify strategy strengths."""
        
        strengths = []
        
        if metrics.expectancy > 1.0:
            strengths.append("High expectancy")
        
        if metrics.win_rate > 60:
            strengths.append("Strong win rate")
        
        if metrics.sharpe_ratio > 1.5:
            strengths.append("Excellent risk-adjusted returns")
        
        if metrics.profit_factor > 2.0:
            strengths.append("Strong profit factor")
        
        if metrics.max_drawdown < 20:
            strengths.append("Low drawdown")
        
        return strengths
    
    def _identify_weaknesses(self, metrics: SimulationMetrics) -> List[str]:
        """Identify strategy weaknesses."""
        
        weaknesses = []
        
        if metrics.expectancy < 0.5:
            weaknesses.append("Low expectancy")
        
        if metrics.win_rate < 45:
            weaknesses.append("Poor win rate")
        
        if metrics.sharpe_ratio < 0.5:
            weaknesses.append("Poor risk-adjusted returns")
        
        if metrics.profit_factor < 1.5:
            weaknesses.append("Weak profit factor")
        
        if metrics.max_drawdown > 40:
            weaknesses.append("High drawdown risk")
        
        return weaknesses
    
    def rank_strategies(self, results: List[SimulationResult]) -> List[Dict]:
        """Rank strategies by score."""
        
        ranked = []
        
        for result in results:
            evaluation = self.evaluate(result)
            ranked.append(evaluation)
        
        # Sort by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked


def create_evaluator() -> StrategyEvaluator:
    """Create a new strategy evaluator."""
    return StrategyEvaluator()
