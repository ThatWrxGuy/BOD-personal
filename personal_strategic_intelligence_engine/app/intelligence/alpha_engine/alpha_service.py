"""Alpha Service.

Main service interface for the Alpha Engine.
"""

from typing import List, Dict, Optional

from app.intelligence.alpha_engine.alpha_models import (
    AlphaCandidate, AlphaStatus, StrategyRanking, DegradationAlert
)
from app.intelligence.alpha_engine.alpha_registry import get_registry
from app.intelligence.alpha_engine.pattern_mining_engine import PatternMiningEngine
from app.intelligence.alpha_engine.hypothesis_engine import HypothesisEngine
from app.intelligence.alpha_engine.regime_segmenter import RegimeSegmenter
from app.intelligence.alpha_engine.feature_scoring_engine import FeatureScoringEngine
from app.intelligence.alpha_engine.edge_validator import EdgeValidator
from app.intelligence.alpha_engine.strategy_ranker import StrategyRanker
from app.intelligence.alpha_engine.degradation_monitor import DegradationMonitor


class AlphaService:
    """Main service for the Alpha Engine."""
    
    def __init__(self):
        self.registry = get_registry()
        self.pattern_miner = PatternMiningEngine()
        self.hypothesis_engine = HypothesisEngine()
        self.regime_segmenter = RegimeSegmenter()
        self.feature_scorer = FeatureScoringEngine()
        self.validator = EdgeValidator()
        self.ranker = StrategyRanker()
        self.monitor = DegradationMonitor()
    
    def discover_patterns(self, signals: List[Dict], outcomes: List[Dict]) -> List:
        """Discover patterns from signal history."""
        return self.pattern_miner.mine_patterns(signals, outcomes)
    
    def generate_hypotheses(self) -> List[AlphaCandidate]:
        """Generate hypotheses from patterns."""
        return self.hypothesis_engine.generate_spy_options_hypotheses()
    
    def validate_alpha(self, alpha_id: str, test_results: Dict) -> Dict:
        """Validate an alpha candidate."""
        alpha = self.registry.get(alpha_id)
        if not alpha:
            return {"error": "Alpha not found"}
        
        # Run validation
        from app.intelligence.alpha_engine.alpha_models import AlphaTestResult
        test = AlphaTestResult(**test_results)
        result = self.validator.validate_alpha(alpha, test)
        
        # Update status
        if result.status.value == "validated":
            self.registry.update_status(alpha_id, AlphaStatus.VALIDATED)
        
        return result.to_dict()
    
    def rank_strategies(self, current_regime: str) -> List[StrategyRanking]:
        """Rank strategies by current opportunity."""
        candidates = self.registry.list_by_status(AlphaStatus.VALIDATED)
        
        # Get recent performance (mock)
        recent_perf = {}
        
        return self.ranker.rank_strategies(candidates, current_regime, recent_perf)
    
    def check_degradation(self, alpha_id: str, recent_trades: List[Dict]) -> Optional[DegradationAlert]:
        """Check for strategy degradation."""
        alpha = self.registry.get(alpha_id)
        if not alpha:
            return None
        
        return self.monitor.check_degradation(alpha, recent_trades)
    
    def get_alphas(self, status: Optional[str] = None) -> List[Dict]:
        """Get alphas, optionally filtered by status."""
        if status:
            alphas = self.registry.list_by_status(AlphaStatus(status))
        else:
            alphas = self.registry.list_all()
        
        return [a.to_dict() for a in alphas]
    
    def get_summary(self) -> Dict:
        """Get alpha engine summary."""
        
        registry_summary = self.registry.get_summary()
        
        return {
            "total_alphas": registry_summary["total_alphas"],
            "by_status": registry_summary["by_status"],
            "patterns_discovered": len(self.pattern_miner.patterns_discovered),
            "hypotheses_pending": len(self.hypothesis_engine.get_pending_hypotheses()),
            "active_alerts": len(self.monitor.get_active_alerts()),
        }


def create_service() -> AlphaService:
    """Create alpha service."""
    return AlphaService()
