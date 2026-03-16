"""Sector Intelligence Service - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    SectorLeadershipRanking,
    RotationEvent,
    SectorBreadthProfile,
    MomentumProfile,
    CapitalFlowSignal,
    SectorPolicyRecommendation,
    SectorIntelligenceReport,
)
from app.finance.sector_intelligence.relative_strength_engine import (
    get_relative_strength_engine,
    RelativeStrengthEngine,
)
from app.finance.sector_intelligence.momentum_engine import (
    get_momentum_engine,
    MomentumEngine,
)
from app.finance.sector_intelligence.sector_breadth_engine import (
    get_sector_breadth_engine,
    SectorBreadthEngine,
)
from app.finance.sector_intelligence.rotation_detector import (
    get_rotation_detector,
    RotationDetector,
)
from app.finance.sector_intelligence.capital_flow_engine import (
    get_capital_flow_engine,
    CapitalFlowEngine,
)
from app.finance.sector_intelligence.sector_ranker import (
    get_sector_ranker,
    SectorRanker,
)
from app.finance.sector_intelligence.sector_policy_mapper import (
    get_sector_policy_mapper,
    SectorPolicyMapper,
)

logger = logging.getLogger(__name__)


class SectorIntelligenceService:
    """Orchestrates the sector intelligence pipeline."""

    def __init__(self):
        # Initialize engines
        self.rs_engine = get_relative_strength_engine()
        self.momentum_engine = get_momentum_engine()
        self.breadth_engine = get_sector_breadth_engine()
        self.rotation_detector = get_rotation_detector()
        self.flow_engine = get_capital_flow_engine()
        self.ranker = get_sector_ranker()
        self.policy_mapper = get_sector_policy_mapper()
        
        # State
        self._prior_rankings: List[SectorProfile] = []
        self._market_regime: Optional[str] = None
        self._regime_risk_posture: Optional[str] = None

    def set_market_context(self, regime: str, risk_posture: str) -> None:
        """Set market regime context from BB-FIN-014."""
        self._market_regime = regime
        self._regime_risk_posture = risk_posture

    def analyze(
        self,
        prices: Optional[Dict[str, float]] = None,
        changes: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> SectorIntelligenceReport:
        """Run complete sector intelligence analysis."""
        
        # Use demo data if none provided
        if prices is None:
            prices, changes = self._generate_demo_data()
        
        # Step 1: Get sector universe and create profiles
        sector_profiles = self.rs_engine.analyze_all_sectors(prices, changes.get("1m", {}))
        
        # Step 2: Analyze momentum
        sector_profiles = self.momentum_engine.calculate_momentum_for_sectors(sector_profiles)
        momentum_profiles = {
            s.symbol: self.momentum_engine.analyze_momentum(s)
            for s in sector_profiles
        }
        
        # Step 3: Analyze breadth
        breadth_profiles = self.breadth_engine.analyze_all_breadths(sector_profiles)
        
        # Step 4: Detect rotation
        rotation = None
        if self._prior_rankings:
            rotation = self.rotation_detector.detect_rotation(
                sector_profiles,
                self._prior_rankings,
            )
        
        # Step 5: Estimate capital flows
        flow_signals = self.flow_engine.estimate_all_flows(sector_profiles)
        
        # Step 6: Create rankings
        leadership = self.ranker.create_leadership_ranking(
            sector_profiles,
            momentum_profiles,
            breadth_profiles,
            flow_signals,
        )
        
        # Step 7: Generate policy recommendations
        recommendations = self.policy_mapper.generate_recommendations(
            leadership,
            rotation,
            self._market_regime,
        )
        
        # Store current rankings for next iteration
        self._prior_rankings = sector_profiles.copy()
        
        # Generate summary
        summary = self._generate_summary(leadership, rotation, flow_signals)
        
        return SectorIntelligenceReport(
            timestamp=datetime.utcnow(),
            leadership=leadership,
            rotation=rotation,
            rotation_detected=rotation is not None,
            breadth_profiles=breadth_profiles,
            capital_flows=flow_signals,
            recommendations=recommendations,
            summary=summary,
            market_regime=self._market_regime,
            regime_risk_posture=self._regime_risk_posture,
            data_freshness={
                "prices": "live" if prices else "demo",
                "changes": "live" if changes else "demo",
            },
        )

    def get_current_rankings(self) -> SectorLeadershipRanking:
        """Get current sector rankings."""
        
        prices, changes = self._generate_demo_data()
        
        sector_profiles = self.rs_engine.analyze_all_sectors(prices, changes.get("1m", {}))
        sector_profiles = self.momentum_engine.calculate_momentum_for_sectors(sector_profiles)
        
        momentum_profiles = {
            s.symbol: self.momentum_engine.analyze_momentum(s)
            for s in sector_profiles
        }
        
        breadth_profiles = self.breadth_engine.analyze_all_breadths(sector_profiles)
        flow_signals = self.flow_engine.estimate_all_flows(sector_profiles)
        
        return self.ranker.create_leadership_ranking(
            sector_profiles,
            momentum_profiles,
            breadth_profiles,
            flow_signals,
        )

    def get_rotation_status(self) -> Optional[RotationEvent]:
        """Get current rotation status."""
        return self.rotation_detector.get_rotation_history(1)[0] if self.rotation_detector.get_rotation_history() else None

    def get_recommendations(
        self,
        market_regime: Optional[str] = None,
    ) -> List[SectorPolicyRecommendation]:
        """Get current sector recommendations."""
        
        if market_regime:
            self._market_regime = market_regime
        
        report = self.analyze()
        return report.recommendations

    def _generate_demo_data(self) -> tuple:
        """Generate demo market data."""
        
        prices = {
            "SPY": 520.0,
            "XLK": 245.0,  # Tech - strong
            "XLF": 42.0,   # Financials - moderate
            "XLE": 92.0,   # Energy - strong
            "XLV": 145.0,  # Healthcare - moderate
            "XLI": 128.0,  # Industrials - strong
            "XLP": 78.0,   # Staples - weak
            "XLY": 198.0,  # Discretionary - moderate
            "XLU": 72.0,   # Utilities - weak
            "XLB": 85.0,   # Materials - moderate
            "XLRE": 42.0,  # Real Estate - weak
            "XLC": 82.0,   # Comm Services - moderate
        }
        
        changes_1m = {
            "XLK": 4.5,   # Tech up
            "XLF": 1.2,   # Financials moderate
            "XLE": 3.8,   # Energy strong
            "XLV": 0.8,   # Healthcare flat
            "XLI": 2.5,   # Industrials up
            "XLP": -1.5,  # Staples down
            "XLY": 1.0,   # Discretionary flat
            "XLU": -2.0,  # Utilities down
            "XLB": 0.5,   # Materials flat
            "XLRE": -1.8, # Real Estate down
            "XLC": 0.3,   # Comm Services flat
        }
        
        return prices, {"1m": changes_1m}

    def _generate_summary(
        self,
        leadership: SectorLeadershipRanking,
        rotation: Optional[RotationEvent],
        flows: List[CapitalFlowSignal],
    ) -> str:
        """Generate executive summary."""
        
        # Get top 3 leaders
        leaders = leadership.composite[:3]
        leader_names = [s.name for s in leaders]
        
        # Get rotation info
        rot_text = ""
        if rotation:
            rot_text = f" Rotation detected: {rotation.description}."
        
        # Get flow summary
        inflows = [f.symbol for f in flows if f.direction.value == "inflow"]
        outflows = [f.symbol for f in flows if f.direction.value == "outflow"]
        
        flow_text = ""
        if inflows:
            flow_text += f" Inflows: {', '.join(inflows[:3])}."
        if outflows:
            flow_text += f" Outflows: {', '.join(outflows[:3])}."
        
        return (
            f"Sector leadership: {', '.join(leader_names)}. "
            f"{rot_text}{flow_text}"
        )


# Singleton
_service: Optional[SectorIntelligenceService] = None


def get_sector_intelligence_service() -> SectorIntelligenceService:
    """Get the singleton SectorIntelligenceService instance."""
    global _service
    if _service is None:
        _service = SectorIntelligenceService()
    return _service
