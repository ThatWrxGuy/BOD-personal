"""Hypothesis Engine.

Converts patterns into testable trading hypotheses.
"""

from typing import List, Dict, Optional
import uuid

from app.intelligence.alpha_engine.alpha_models import AlphaCandidate, AlphaStatus


class HypothesisEngine:
    """Converts patterns into testable hypotheses."""
    
    def __init__(self):
        self.hypotheses_generated = []
    
    def generate_hypothesis(
        self,
        pattern_id: str,
        pattern_description: str,
        signal_sequence: List[str],
        domain: str = "finance",
    ) -> AlphaCandidate:
        """Generate a testable hypothesis from a pattern."""
        
        # Convert pattern to hypothesis
        hypothesis_text = self._pattern_to_hypothesis(pattern_description, signal_sequence)
        
        # Create alpha candidate
        candidate = AlphaCandidate.create(
            name=f"Alpha-{pattern_id[:8]}",
            domain=domain,
            hypothesis=hypothesis_text,
            signal_dependencies=signal_sequence,
            regime_requirements=self._extract_regime_requirements(signal_sequence),
        )
        
        candidate.status = AlphaStatus.DISCOVERED
        self.hypotheses_generated.append(candidate)
        
        return candidate
    
    def _pattern_to_hypothesis(
        self,
        description: str,
        signal_sequence: List[str],
    ) -> str:
        """Convert pattern to hypothesis text."""
        
        # Map signal types to readable descriptions
        signal_map = {
            "vwap_reclaim_signal": "SPY reclaims VWAP",
            "gamma_acceleration_event": "gamma acceleration occurs",
            "liquidity_sweep": "liquidity sweep detected",
            "volatility_regime_shift": "volatility regime shifts",
            "spy_delta_velocity_event": "delta velocity accelerates",
            "opening_range_breakout": "opening range breaks out",
        }
        
        components = []
        for sig in signal_sequence:
            components.append(signal_map.get(sig, sig))
        
        if len(components) >= 2:
            return f"When {' then '.join(components[:-1])}, then {components[-1]} produces favorable outcomes."
        
        return f"Signal sequence {signal_sequence} produces favorable outcomes."
    
    def _extract_regime_requirements(
        self,
        signal_sequence: List[str],
    ) -> Dict:
        """Extract regime requirements from signals."""
        
        requirements = {}
        
        # Infer requirements based on signal types
        if any("vwap" in s.lower() for s in signal_sequence):
            requirements["vwap_state"] = "reclaimed"
        
        if any("gamma" in s.lower() for s in signal_sequence):
            requirements["gamma_level"] = "> 0.05"
        
        if any("iv" in s.lower() or "volatility" in s.lower() for s in signal_sequence):
            requirements["iv_regime"] = "normal"
        
        return requirements
    
    def generate_spy_options_hypotheses(self) -> List[AlphaCandidate]:
        """Generate standard SPY options hypotheses."""
        
        hypotheses = [
            AlphaCandidate.create(
                name="VWAP-Reclaim-Call-Continuation",
                domain="finance",
                hypothesis="When SPY reclaims VWAP after downside sweep and nearby call gamma increases, 1-step OTM calls outperform ATM calls over 5-10 minutes.",
                signal_dependencies=["vwap_reclaim_signal", "gamma_acceleration_event"],
                regime_requirements={"vwap_state": "reclaimed", "gamma_level": "> 0.05"},
            ),
            AlphaCandidate.create(
                name="Liquidity-Sweep-Reversal",
                domain="finance",
                hypothesis="When SPY sweeps liquidity to downside and immediately reverses, short-dated puts capture the reversal.",
                signal_dependencies=["liquidity_sweep", "vwap_reclaim_signal"],
                regime_requirements={"market_type": "reversal"},
            ),
            AlphaCandidate.create(
                name="Opening-Range-Breakout",
                domain="finance",
                hypothesis="SPY opening range breakout with high volume leads to sustained momentum in breakout direction.",
                signal_dependencies=["opening_range_breakout", "relative_volume"],
                regime_requirements={"time": "market_open", "volume": "high"},
            ),
            AlphaCandidate.create(
                name="Gamma-Acceleration-Momentum",
                domain="finance",
                hypothesis="Gamma acceleration after directional move predicts continued momentum for 5-15 minutes.",
                signal_dependencies=["gamma_acceleration_event", "spy_delta_velocity_event"],
                regime_requirements={"momentum": "strong"},
            ),
            AlphaCandidate.create(
                name="IV-Crush-Recovery",
                domain="finance",
                hypothesis="Post-event IV crush followed by recovery in underlying creates long volatility opportunity.",
                signal_dependencies=["volatility_regime_shift"],
                regime_requirements={"iv_regime": "crush", "event_type": "earnings"},
            ),
        ]
        
        for h in hypotheses:
            h.status = AlphaStatus.DISCOVERED
            self.hypotheses_generated.append(h)
        
        return hypotheses
    
    def get_pending_hypotheses(self) -> List[AlphaCandidate]:
        """Get hypotheses awaiting validation."""
        
        return [
            h for h in self.hypotheses_generated
            if h.status in [AlphaStatus.DISCOVERED, AlphaStatus.UNDER_TEST]
        ]


def create_engine() -> HypothesisEngine:
    """Create hypothesis engine."""
    return HypothesisEngine()
