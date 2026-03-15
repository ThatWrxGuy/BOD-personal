"""Options Intelligence Service.

Service interface for options intelligence system.
"""

from typing import Dict, List
from datetime import datetime


class OptionsIntelligenceService:
    """Main service for options intelligence."""
    
    def __init__(self):
        self.initialized = True
    
    def get_strategies(self) -> List[Dict]:
        """Get available options strategies."""
        from app.finance.options_intelligence.knowledge_base.options_theory_models import OPTIONS_STRATEGIES
        return [s.to_dict() for s in OPTIONS_STRATEGIES]
    
    def get_principles(self) -> List[Dict]:
        """Get strategy principles."""
        from app.finance.options_intelligence.knowledge_base.options_theory_models import STRATEGY_PRINCIPLES
        return [p.to_dict() for p in STRATEGY_PRINCIPLES]
    
    def analyze_volatility(self, symbol: str) -> Dict:
        """Analyze volatility for symbol."""
        from app.finance.options_intelligence.knowledge_base.volatility_models import VolatilityAnalyzer
        analyzer = VolatilityAnalyzer()
        
        # Mock data
        regime = analyzer.detect_regime(18.5, 45, 40, 15.2)
        
        return {
            "symbol": symbol,
            "regime": regime.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_greek_exposure(self, positions: List[Dict]) -> Dict:
        """Calculate Greek exposure for positions."""
        from app.finance.options_intelligence.knowledge_base.greeks_models import GreeksCalculator
        calc = GreeksCalculator()
        exposure = calc.analyze_exposure(positions)
        return exposure.to_dict()


def create_service() -> OptionsIntelligenceService:
    return OptionsIntelligenceService()
