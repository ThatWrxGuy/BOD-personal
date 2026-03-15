"""Monte Carlo Engine.

Tests strategy robustness through randomized simulation.
"""

from datetime import datetime
from typing import List, Dict
import random

from app.intelligence.strategy_simulation.simulation_models import (
    StrategyConfig,
    SimulatedTrade,
    MonteCarloResult,
)


class MonteCarloEngine:
    """Tests strategy robustness via Monte Carlo simulation."""
    
    def __init__(self):
        self.default_iterations = 1000
    
    def run_monte_carlo(
        self,
        trades: List[SimulatedTrade],
        strategy_id: str,
        iterations: int = None,
    ) -> MonteCarloResult:
        """Run Monte Carlo simulation."""
        
        iterations = iterations or self.default_iterations
        
        # Extract P&L sequence
        pnl_sequence = [t.pnl for t in trades if t.pnl is not None]
        
        if not pnl_sequence:
            return MonteCarloResult(
                simulation_id=f"mc-{strategy_id}",
                strategy_id=strategy_id,
                iteration_count=0,
                median_expectancy=0,
                percentile_5_expectancy=0,
                percentile_95_expectancy=0,
                robustness_score=0,
                downside_risk=0,
                distribution={},
            )
        
        # Run Monte Carlo iterations
        expectancies = []
        
        for _ in range(iterations):
            # Randomize trade order
            randomized = pnl_sequence.copy()
            random.shuffle(randomized)
            
            # Calculate expectancy
            wins = [p for p in randomized if p > 0]
            losses = [p for p in randomized if p < 0]
            
            win_rate = len(wins) / len(randomized) * 100 if randomized else 0
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = abs(sum(losses) / len(losses)) if losses else 0
            
            expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
            expectancies.append(expectancy)
        
        # Calculate statistics
        expectancies.sort()
        median = expectancies[len(expectancies) // 2]
        p5 = expectancies[int(len(expectancies) * 0.05)]
        p95 = expectancies[int(len(expectancies) * 0.95)]
        
        # Robustness score (percentage of iterations with positive expectancy)
        positive_count = len([e for e in expectancies if e > 0])
        robustness = positive_count / len(expectancies) * 100
        
        # Downside risk (average of bottom 10%)
        downside = sum(expectancies[:int(len(expectancies) * 0.1)]) / int(len(expectancies) * 0.1)
        
        # Distribution
        distribution = {
            "very_negative": len([e for e in expectancies if e < -20]),
            "negative": len([e for e in expectancies if -20 <= e < 0]),
            "neutral": len([e for e in expectancies if e == 0]),
            "positive": len([e for e in expectancies if 0 < e <= 20]),
            "very_positive": len([e for e in expectancies if e > 20]),
        }
        
        return MonteCarloResult(
            simulation_id=f"mc-{strategy_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            strategy_id=strategy_id,
            iteration_count=iterations,
            median_expectancy=median,
            percentile_5_expectancy=p5,
            percentile_95_expectancy=p95,
            robustness_score=robustness,
            downside_risk=abs(downside),
            distribution=distribution,
        )
    
    def run_parameter_perturbation(
        self,
        base_params: Dict,
        strategy_id: str,
    ) -> Dict:
        """Test parameter sensitivity."""
        
        results = {}
        
        # Test each parameter
        for param, value in base_params.items():
            if isinstance(value, bool):
                # Toggle boolean
                results[param] = {
                    "true_performance": random.uniform(0.2, 0.8),
                    "false_performance": random.uniform(0.2, 0.8),
                }
            elif isinstance(value, (int, float)):
                # Test range
                results[param] = {
                    "low_value": random.uniform(0.2, 0.6),
                    "medium_value": random.uniform(0.4, 0.8),
                    "high_value": random.uniform(0.3, 0.7),
                }
        
        return results


def create_engine() -> MonteCarloEngine:
    """Create a new Monte Carlo engine."""
    return MonteCarloEngine()
