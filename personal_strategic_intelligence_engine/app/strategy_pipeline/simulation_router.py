"""Simulation Router - determines which simulation engines should be executed."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.strategy_pipeline.proposal_models import (
    RiskLevel,
    SimulationResult,
    StrategyProposal,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class SimulationType(str, Enum):
    """Types of simulations available."""
    HISTORICAL_BACKTEST = "historical_backtest"
    MONTE_CARLO = "monte_carlo"
    STRESS_TESTING = "stress_testing"
    CAPITAL_IMPACT = "capital_impact"


class SimulationRouter:
    """
    The Simulation Router determines which simulation engines should be executed
    to evaluate a proposal.
    
    Simulation types include:
    - Historical Backtest: Strategy performance analysis
    - Monte Carlo: Probabilistic outcomes
    - Stress Testing: Adverse condition modeling
    - Capital Impact: Portfolio allocation effects
    """
    
    def __init__(self):
        self.simulation_history: Dict[str, Dict[str, Any]] = {}
    
    async def run_simulations(
        self,
        proposal: StrategyProposal,
        simulation_types: Optional[List[SimulationType]] = None,
    ) -> Dict[str, SimulationResult]:
        """
        Run simulations for a proposal.
        
        Args:
            proposal: The strategy proposal to simulate
            simulation_types: List of simulation types to run (defaults to all)
            
        Returns:
            Dictionary mapping simulation type to results
        """
        logger.info(f"Running simulations for proposal: {proposal.id}")
        
        if simulation_types is None:
            simulation_types = [
                SimulationType.HISTORICAL_BACKTEST,
                SimulationType.MONTE_CARLO,
                SimulationType.STRESS_TESTING,
                SimulationType.CAPITAL_IMPACT,
            ]
        
        results = {}
        
        for sim_type in simulation_types:
            logger.debug(f"Running {sim_type} simulation")
            result = await self._run_simulation(proposal, sim_type)
            results[sim_type.value] = result
        
        # Log simulation results
        self._log_simulation_results(proposal.id, results)
        
        return results
    
    async def _run_simulation(
        self,
        proposal: StrategyProposal,
        sim_type: SimulationType,
    ) -> SimulationResult:
        """
        Run a specific type of simulation.
        
        This is a placeholder implementation. In production, this would
        invoke actual simulation engines.
        """
        if sim_type == SimulationType.HISTORICAL_BACKTEST:
            return await self._historical_backtest(proposal)
        elif sim_type == SimulationType.MONTE_CARLO:
            return await self._monte_carlo(proposal)
        elif sim_type == SimulationType.STRESS_TESTING:
            return await self._stress_testing(proposal)
        elif sim_type == SimulationType.CAPITAL_IMPACT:
            return await self._capital_impact(proposal)
        else:
            return SimulationResult(
                simulation_type=sim_type.value,
                risk_metrics={},
                scenario_results={},
            )
    
    async def _historical_backtest(
        self,
        proposal: StrategyProposal,
    ) -> SimulationResult:
        """Historical Backtest: Strategy performance analysis."""
        # Simulate historical performance analysis
        expected_return = 0.12  # 12% expected return
        max_drawdown = 0.04  # 4% max drawdown
        
        # Adjust based on risk level
        if proposal.risk_level == RiskLevel.HIGH:
            expected_return = 0.18
            max_drawdown = 0.08
        elif proposal.risk_level == RiskLevel.LOW:
            expected_return = 0.06
            max_drawdown = 0.02
        
        return SimulationResult(
            simulation_type=SimulationType.HISTORICAL_BACKTEST.value,
            expected_return=expected_return,
            max_drawdown=max_drawdown,
            win_probability=0.61,
            risk_metrics={
                "sharpe_ratio": 1.5,
                "volatility": 0.12,
                "sortino_ratio": 1.8,
            },
            scenario_results={
                "bull_case": expected_return * 1.5,
                "bear_case": expected_return * 0.5,
                "base_case": expected_return,
            },
        )
    
    async def _monte_carlo(
        self,
        proposal: StrategyProposal,
    ) -> SimulationResult:
        """Monte Carlo: Probabilistic outcomes."""
        # Simulate probabilistic analysis
        win_probability = 0.65
        
        # Adjust based on confidence
        win_probability = min(win_probability * proposal.confidence_score * 2, 0.95)
        
        return SimulationResult(
            simulation_type=SimulationType.MONTE_CARLO.value,
            win_probability=win_probability,
            risk_metrics={
                "percentile_5": -0.08,
                "percentile_25": -0.02,
                "percentile_50": 0.08,
                "percentile_75": 0.15,
                "percentile_95": 0.25,
            },
            scenario_results={
                "simulations_run": 10000,
                "success_rate": win_probability,
            },
        )
    
    async def _stress_testing(
        self,
        proposal: StrategyProposal,
    ) -> SimulationResult:
        """Stress Testing: Adverse condition modeling."""
        # Calculate stress impact based on risk level
        stress_impact = {
            RiskLevel.LOW: 0.05,
            RiskLevel.MEDIUM: 0.10,
            RiskLevel.HIGH: 0.20,
            RiskLevel.CRITICAL: 0.35,
        }.get(proposal.risk_level, 0.15)
        
        return SimulationResult(
            simulation_type=SimulationType.STRESS_TESTING.value,
            expected_return=-stress_impact * 0.5,
            max_drawdown=stress_impact,
            risk_metrics={
                "market_crash_impact": -stress_impact,
                "liquidity_crisis_impact": -stress_impact * 0.7,
                "correlation_breakdown_impact": -stress_impact * 0.8,
            },
            scenario_results={
                "scenarios_tested": 5,
                "failures_in_stress": 1,
            },
        )
    
    async def _capital_impact(
        self,
        proposal: StrategyProposal,
    ) -> SimulationResult:
        """Capital Impact: Portfolio allocation effects."""
        # Analyze capital requirements
        proposed_action = proposal.proposed_action
        capital_required = proposed_action.get("amount", 100000)  # Default to 100k
        
        # Calculate allocation percentage
        total_portfolio = 1000000  # Assumed 1M portfolio
        allocation_percentage = (capital_required / total_portfolio) * 100
        
        return SimulationResult(
            simulation_type=SimulationType.CAPITAL_IMPACT.value,
            risk_metrics={
                "capital_required": capital_required,
                "allocation_percentage": allocation_percentage,
                "remaining_capacity": 100 - allocation_percentage,
            },
            scenario_results={
                "full_allocation_impact": allocation_percentage / 100,
                "partial_allocation_impact": (allocation_percentage / 100) * 0.5,
            },
        )
    
    def _log_simulation_results(
        self,
        proposal_id: str,
        results: Dict[str, SimulationResult],
    ) -> None:
        """Log simulation results for auditing."""
        session_id = str(uuid.uuid4())
        self.simulation_history[session_id] = {
            "proposal_id": proposal_id,
            "timestamp": datetime.utcnow(),
            "results": {
                k: {
                    "expected_return": v.expected_return,
                    "max_drawdown": v.max_drawdown,
                    "win_probability": v.win_probability,
                    "risk_metrics": v.risk_metrics,
                }
                for k, v in results.items()
            },
        }
        
        logger.info(f"Simulation session {session_id} completed for proposal {proposal_id}")
    
    def get_simulation_results(
        self,
        proposal_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get simulation results for a proposal."""
        for session in self.simulation_history.values():
            if session["proposal_id"] == proposal_id:
                return session.get("results")
        return None
    
    def get_aggregated_metrics(
        self,
        simulation_results: Dict[str, SimulationResult],
    ) -> Dict[str, Any]:
        """
        Aggregate metrics from multiple simulations.
        
        Args:
            simulation_results: Dictionary of simulation results
            
        Returns:
            Aggregated metrics dictionary
        """
        aggregated = {
            "expected_return": None,
            "max_drawdown": None,
            "win_probability": None,
            "overall_risk_score": 0.0,
        }
        
        returns = []
        drawdowns = []
        probabilities = []
        
        for result in simulation_results.values():
            if result.expected_return is not None:
                returns.append(result.expected_return)
            if result.max_drawdown is not None:
                drawdowns.append(result.max_drawdown)
            if result.win_probability is not None:
                probabilities.append(result.win_probability)
        
        if returns:
            aggregated["expected_return"] = sum(returns) / len(returns)
        if drawdowns:
            aggregated["max_drawdown"] = max(drawdowns)
        if probabilities:
            aggregated["win_probability"] = sum(probabilities) / len(probabilities)
        
        # Calculate overall risk score
        if returns and drawdowns:
            aggregated["overall_risk_score"] = abs(aggregated["expected_return"] or 0) + (aggregated["max_drawdown"] or 0)
        
        return aggregated


# Singleton instance
_simulation_router: Optional[SimulationRouter] = None


def get_simulation_router() -> SimulationRouter:
    """Get the global simulation router instance."""
    global _simulation_router
    if _simulation_router is None:
        _simulation_router = SimulationRouter()
    return _simulation_router
