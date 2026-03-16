"""Strategy Lab Service - BB-FIN-020

Orchestrates the entire strategy research pipeline.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import uuid

from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    StrategySignal,
    BacktestResult,
    MonteCarloSimulation,
    StrategyRobustnessProfile,
    StrategyLeaderboard,
    StrategySimulationReport,
    StrategyLabStatus,
    StrategyStatus,
)
from app.finance.strategy_lab.strategy_registry import StrategyRegistry, get_strategy_registry
from app.finance.strategy_lab.strategy_discovery_engine import (
    StrategyDiscoveryEngine,
    get_strategy_discovery_engine,
)
from app.finance.strategy_lab.backtesting_engine import (
    BacktestingEngine,
    get_backtesting_engine,
)
from app.finance.strategy_lab.monte_carlo_engine import (
    MonteCarloEngine,
    get_monte_carlo_engine,
)
from app.finance.strategy_lab.regime_performance_engine import (
    RegimePerformanceEngine,
    get_regime_performance_engine,
)
from app.finance.strategy_lab.strategy_scoring_engine import (
    StrategyScoringEngine,
    get_strategy_scoring_engine,
)
from app.finance.strategy_lab.strategy_ranker import StrategyRanker, get_strategy_ranker

logger = logging.getLogger(__name__)


class StrategyLabService:
    """Orchestrates the complete strategy research and analysis pipeline."""
    
    def __init__(self):
        self.registry = get_strategy_registry()
        self.discovery = get_strategy_discovery_engine()
        self.backtester = get_backtesting_engine()
        self.monte_carlo = get_monte_carlo_engine()
        self.regime_engine = get_regime_performance_engine()
        self.scorer = get_strategy_scoring_engine()
        self.ranker = get_strategy_ranker()
        
        self._analysis_cache: Dict[str, StrategySimulationReport] = {}
        self._last_analysis: Optional[datetime] = None
    
    def get_status(self) -> StrategyLabStatus:
        """Get current status of the strategy lab."""
        
        stats = self.registry.get_stats()
        
        return StrategyLabStatus(
            is_initialized=True,
            last_analysis_time=self._last_analysis,
            total_strategies=stats["total_strategies"],
            active_strategies=stats["active_strategies"],
            backtesting_strategies=stats["testing_strategies"],
            latest_backtest=self._last_analysis,
            latest_monte_carlo=self._last_analysis,
            latest_ranking=self._last_analysis,
            regime_intelligence_available=True,
            market_replay_available=True,
            alpha_engine_available=True,
        )
    
    def discover_strategies(
        self,
        patterns: Optional[List] = None,
        from_alpha: bool = False,
    ) -> List[StrategyDefinition]:
        """Discover new strategies from patterns or alpha signals."""
        
        if from_alpha:
            discovered = self.discovery.discover_from_alpha_signals()
        else:
            discovered = self.discovery.discover_from_patterns(patterns)
        
        # Register discovered strategies
        for strategy in discovered:
            self.registry.register_strategy(strategy)
        
        logger.info(f"Discovered and registered {len(discovered)} strategies")
        return discovered
    
    def run_backtest(
        self,
        strategy_id: str,
        symbols: Optional[List[str]] = None,
    ) -> BacktestResult:
        """Run backtest for a strategy."""
        
        strategy = self.registry.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        result = self.backtester.run_backtest(strategy, symbols)
        
        # Update strategy status
        self.registry.update_strategy_status(strategy_id, StrategyStatus.BACKTESTING)
        
        logger.info(f"Backtest completed for {strategy_id}: {result.total_trades} trades")
        return result
    
    def run_monte_carlo(
        self,
        backtest_result: BacktestResult,
        num_simulations: int = 1000,
    ) -> MonteCarloSimulation:
        """Run Monte Carlo simulation on backtest results."""
        
        simulation = self.monte_carlo.run_simulation(backtest_result, num_simulations)
        
        logger.info(f"Monte Carlo simulation completed: {simulation.num_simulations} runs")
        return simulation
    
    def analyze_regime_performance(
        self,
        backtest_result: BacktestResult,
        strategy: StrategyDefinition,
    ):
        """Analyze strategy performance across market regimes."""
        
        performances = self.regime_engine.analyze_regime_performance(backtest_result, strategy)
        
        logger.info(f"Regime analysis completed for {len(performances)} regimes")
        return performances
    
    def assess_robustness(
        self,
        backtest_result: BacktestResult,
        monte_carlo: MonteCarloSimulation,
        regime_performance: List,
    ) -> StrategyRobustnessProfile:
        """Assess overall strategy robustness."""
        
        # Get robustness assessment from Monte Carlo
        mc_assessment = self.monte_carlo.assess_robustness(monte_carlo)
        
        # Determine readiness level
        if mc_assessment["is_robust"] and backtest_result.total_trades >= 30:
            readiness = "production"
        elif mc_assessment["is_robust"] or backtest_result.total_trades >= 20:
            readiness = "qualified"
        elif backtest_result.total_trades >= 10:
            readiness = "experimental"
        else:
            readiness = "not_ready"
        
        robustness = StrategyRobustnessProfile(
            strategy_id=backtest_result.strategy_id,
            monte_carlo=monte_carlo,
            regime_performance=regime_performance,
            stability_score=mc_assessment.get("stability_score", 0.0),
            consistency_score=mc_assessment.get("stability_score", 0.0),
            tail_risk_score=mc_assessment.get("risk_score", 0.0),
            overfitting_detected=False,
            actual_sample_size=backtest_result.total_trades,
            sample_adequate=backtest_result.total_trades >= 30,
            is_robust=mc_assessment.get("is_robust", False),
            readiness_level=readiness,
            recommendations=mc_assessment.get("recommendations", []),
        )
        
        return robustness
    
    def analyze_strategy(
        self,
        strategy_id: str,
        symbols: Optional[List[str]] = None,
    ) -> StrategySimulationReport:
        """Run complete analysis on a strategy."""
        
        # Get strategy
        strategy = self.registry.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        # Run backtest
        backtest = self.run_backtest(strategy_id, symbols)
        
        # Compute metrics
        metrics = self.scorer.compute_metrics(backtest)
        
        # Run Monte Carlo
        monte_carlo = self.run_monte_carlo(backtest)
        
        # Analyze regime performance
        regime_performance = self.analyze_regime_performance(backtest, strategy)
        
        # Assess robustness
        robustness = self.assess_robustness(backtest, monte_carlo, regime_performance)
        
        # Update strategy status based on robustness
        if robustness.is_robust:
            self.registry.update_strategy_status(strategy_id, StrategyStatus.ACTIVE)
        else:
            self.registry.update_strategy_status(strategy_id, StrategyStatus.TESTING)
        
        # Generate recommendation
        is_recommended = (
            robustness.is_robust and
            metrics.sharpe_ratio >= 0.5 and
            metrics.win_rate >= 0.4
        )
        
        if is_recommended:
            reason = f"Strong performance: Sharpe {metrics.sharpe_ratio:.2f}, Win Rate {metrics.win_rate:.0%}, Robust"
        elif robustness.is_robust:
            reason = f"Robust strategy but moderate performance: Sharpe {metrics.sharpe_ratio:.2f}"
        elif metrics.sharpe_ratio >= 1.0:
            reason = f"Good returns but needs more validation: {backtest.total_trades} trades"
        else:
            reason = "Requires further development"
        
        # Create report
        report = StrategySimulationReport(
            report_id=f"rpt_{strategy_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            strategy_id=strategy_id,
            strategy_name=strategy.name,
            generated_at=datetime.utcnow(),
            analysis_period_start=backtest.start_date,
            analysis_period_end=backtest.end_date,
            definition=strategy,
            backtest=backtest,
            metrics=metrics,
            monte_carlo=monte_carlo,
            regime_performance=regime_performance,
            robustness=robustness,
            is_recommended=is_recommended,
            recommendation_reason=reason,
        )
        
        # Cache and update
        self._analysis_cache[strategy_id] = report
        self._last_analysis = datetime.utcnow()
        
        logger.info(f"Strategy analysis completed for {strategy_id}: recommended={is_recommended}")
        
        return report
    
    def get_leaderboard(self) -> StrategyLeaderboard:
        """Generate strategy leaderboard."""
        
        # Get all strategies
        strategies = self.registry.get_all_strategies()
        
        # Analyze each strategy
        metrics_map = {}
        
        for strategy in strategies:
            try:
                backtest = self.backtester.run_backtest(strategy)
                metrics = self.scorer.compute_metrics(backtest)
                metrics_map[strategy.strategy_id] = metrics
            except Exception as e:
                logger.warning(f"Failed to analyze {strategy.strategy_id}: {e}")
        
        # Generate leaderboard
        leaderboard = self.ranker.rank_strategies(strategies, metrics_map)
        
        logger.info(f"Generated leaderboard with {leaderboard.total_strategies} strategies")
        
        return leaderboard
    
    def get_strategies_for_current_regime(
        self,
        regime: str,
    ) -> List[StrategyDefinition]:
        """Get strategies suitable for the current market regime."""
        
        # Would integrate with regime intelligence
        return self.registry.get_all_strategies()
    
    def get_analysis_report(self, strategy_id: str) -> Optional[StrategySimulationReport]:
        """Get cached analysis report for a strategy."""
        return self._analysis_cache.get(strategy_id)


_strategy_lab_service: Optional[StrategyLabService] = None


def get_strategy_lab_service() -> StrategyLabService:
    """Get the strategy lab service."""
    global _strategy_lab_service
    
    if _strategy_lab_service is None:
        _strategy_lab_service = StrategyLabService()
    
    return _strategy_lab_service
