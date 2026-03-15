"""Contradiction detection engine."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.meta_cognition.meta_types import (
    OriginEngine,
    ContradictionSeverity,
)
from app.meta_cognition.meta_models import ContradictionRecord


class ContradictionDetector:
    """Detects conflicting signals between intelligence engines.
    
    Contradictions can occur between:
    - forecast vs simulation
    - forecast vs Monte Carlo
    - simulation vs Monte Carlo
    - synthesizer vs doctrine
    """
    
    # Severity thresholds for different conflict types
    SEVERITY_THRESHOLDS = {
        "critical_conflict": 0.8,  # Opposite recommendations
        "high_conflict": 0.6,       # Significant disagreement
        "medium_conflict": 0.4,    # Minor disagreement
        "low_conflict": 0.2,       # Slight variance
    }
    
    def __init__(self):
        self._contradiction_history: List[ContradictionRecord] = []
    
    def detect_contradictions(
        self,
        engine_a_data: Dict[str, Any],
        engine_b_data: Dict[str, Any],
        engine_a: OriginEngine,
        engine_b: OriginEngine,
    ) -> List[ContradictionRecord]:
        """Detect contradictions between two engine outputs.
        
        Args:
            engine_a_data: Output data from first engine
            engine_b_data: Output data from second engine
            engine_a: Origin of first engine data
            engine_b: Origin of second engine data
            
        Returns:
            List of detected contradictions
        """
        contradictions = []
        
        # Determine which comparison to make
        if (engine_a == OriginEngine.FORECAST and engine_b == OriginEngine.SIMULATION) or \
           (engine_a == OriginEngine.SIMULATION and engine_b == OriginEngine.FORECAST):
            contradictions = self._compare_forecast_simulation(
                engine_a_data, engine_b_data, engine_a, engine_b
            )
        elif (engine_a == OriginEngine.FORECAST and engine_b == OriginEngine.MONTE_CARLO) or \
             (engine_a == OriginEngine.MONTE_CARLO and engine_b == OriginEngine.FORECAST):
            contradictions = self._compare_forecast_monte_carlo(
                engine_a_data, engine_b_data, engine_a, engine_b
            )
        elif (engine_a == OriginEngine.SIMULATION and engine_b == OriginEngine.MONTE_CARLO) or \
             (engine_a == OriginEngine.MONTE_CARLO and engine_b == OriginEngine.SIMULATION):
            contradictions = self._compare_simulation_monte_carlo(
                engine_a_data, engine_b_data, engine_a, engine_b
            )
        elif engine_a == OriginEngine.SYNTHESIZER or engine_b == OriginEngine.SYNTHESIZER:
            contradictions = self._compare_with_synthesizer(
                engine_a_data, engine_b_data, engine_a, engine_b
            )
        
        # Add to history
        self._contradiction_history.extend(contradictions)
        
        return contradictions
    
    def detect_all_contradictions(
        self,
        all_engines_data: Dict[OriginEngine, Dict[str, Any]],
    ) -> List[ContradictionRecord]:
        """Detect contradictions across all engines.
        
        Args:
            all_engines_data: Dictionary mapping engine to their output data
            
        Returns:
            List of all detected contradictions
        """
        all_contradictions = []
        engines = list(all_engines_data.keys())
        
        # Compare each pair of engines
        for i, engine_a in enumerate(engines):
            for engine_b in engines[i+1:]:
                contradictions = self.detect_contradictions(
                    all_engines_data[engine_a],
                    all_engines_data[engine_b],
                    engine_a,
                    engine_b
                )
                all_contradictions.extend(contradictions)
        
        return all_contradictions
    
    def _compare_forecast_simulation(
        self,
        forecast_data: Dict[str, Any],
        simulation_data: Dict[str, Any],
        engine_a: OriginEngine,
        engine_b: OriginEngine,
    ) -> List[ContradictionRecord]:
        """Compare forecast and simulation outputs."""
        contradictions = []
        
        # Get recommendations
        forecast_rec = forecast_data.get("recommendation", "neutral")
        simulation_rec = simulation_data.get("recommendation", "neutral")
        
        # Check for conflict in direction
        conflict = self._calculate_direction_conflict(forecast_rec, simulation_rec)
        
        if conflict > self.SEVERITY_THRESHOLDS["medium_conflict"]:
            severity = self._conflict_to_severity(conflict)
            contradictions.append(self._create_contradiction(
                engine_a, engine_b,
                f"Forecast recommends {forecast_rec}, Simulation recommends {simulation_rec}",
                severity,
                {
                    "forecast_recommendation": forecast_rec,
                    "simulation_recommendation": simulation_rec,
                    "conflict_score": conflict,
                }
            ))
        
        # Check for confidence disagreement
        forecast_conf = forecast_data.get("confidence", 0.5)
        sim_conf = simulation_data.get("confidence", 0.5)
        
        if abs(forecast_conf - sim_conf) > 0.4:
            contradictions.append(self._create_contradiction(
                engine_a, engine_b,
                f"Confidence disagreement: Forecast={forecast_conf}, Simulation={sim_conf}",
                ContradictionSeverity.MEDIUM,
                {
                    "forecast_confidence": forecast_conf,
                    "simulation_confidence": sim_conf,
                }
            ))
        
        return contradictions
    
    def _compare_forecast_monte_carlo(
        self,
        forecast_data: Dict[str, Any],
        monte_carlo_data: Dict[str, Any],
        engine_a: OriginEngine,
        engine_b: OriginEngine,
    ) -> List[ContradictionRecord]:
        """Compare forecast and Monte Carlo outputs."""
        contradictions = []
        
        # Get risk assessment
        forecast_risk = forecast_data.get("risk_assessment", 0.5)
        mc_risk = monte_carlo_data.get("expected_max_drawdown", 0.5)
        
        # High MC drawdown vs low forecast risk is a contradiction
        if mc_risk > 0.5 and forecast_risk < 0.3:
            contradictions.append(self._create_contradiction(
                engine_a, engine_b,
                f"Monte Carlo shows high risk ({mc_risk:.1%}), Forecast shows low risk ({forecast_risk:.1%})",
                ContradictionSeverity.HIGH,
                {
                    "forecast_risk": forecast_risk,
                    "monte_carlo_drawdown": mc_risk,
                }
            ))
        
        # Check outcome expectation
        forecast_outcome = forecast_data.get("expected_outcome", 0.5)
        mc_outcome = monte_carlo_data.get("expected_return", 0.5)
        
        # Opposite direction expectations
        if (forecast_outcome > 0.6 and mc_outcome < 0.3) or \
           (forecast_outcome < 0.3 and mc_outcome > 0.6):
            contradictions.append(self._create_contradiction(
                engine_a, engine_b,
                f"Outcome expectation conflict: Forecast={forecast_outcome:.1%}, Monte Carlo={mc_outcome:.1%}",
                ContradictionSeverity.HIGH,
                {
                    "forecast_outcome": forecast_outcome,
                    "monte_carlo_return": mc_outcome,
                }
            ))
        
        return contradictions
    
    def _compare_simulation_monte_carlo(
        self,
        simulation_data: Dict[str, Any],
        monte_carlo_data: Dict[str, Any],
        engine_a: OriginEngine,
        engine_b: OriginEngine,
    ) -> List[ContradictionRecord]:
        """Compare simulation and Monte Carlo outputs."""
        contradictions = []
        
        # Get success rates
        sim_success = simulation_data.get("success_rate", 0.5)
        mc_success = monte_carlo_data.get("success_rate", 0.5)
        
        # Significant disagreement in success rate
        if abs(sim_success - mc_success) > 0.3:
            severity = ContradictionSeverity.HIGH if abs(sim_success - mc_success) > 0.5 else ContradictionSeverity.MEDIUM
            contradictions.append(self._create_contradiction(
                engine_a, engine_b,
                f"Success rate conflict: Simulation={sim_success:.1%}, Monte Carlo={mc_success:.1%}",
                severity,
                {
                    "simulation_success_rate": sim_success,
                    "monte_carlo_success_rate": mc_success,
                }
            ))
        
        return contradictions
    
    def _compare_with_synthesizer(
        self,
        synthesizer_data: Dict[str, Any],
        other_data: Dict[str, Any],
        engine_a: OriginEngine,
        engine_b: OriginEngine,
    ) -> List[ContradictionRecord]:
        """Compare synthesizer output with other engines."""
        # For now, just check if synthesizer recommendation aligns with other engine
        contradictions = []
        
        synth_rec = synthesizer_data.get("recommendation", "neutral")
        other_rec = other_data.get("recommendation", "neutral")
        
        conflict = self._calculate_direction_conflict(synth_rec, other_rec)
        
        if conflict > self.SEVERITY_THRESHOLDS["high_conflict"]:
            contradictions.append(self._create_contradiction(
                engine_a, engine_b,
                f"Synthesizer conflicts with {engine_b.value}: {synth_rec} vs {other_rec}",
                ContradictionSeverity.MEDIUM,
                {
                    "synthesizer_recommendation": synth_rec,
                    "other_recommendation": other_rec,
                }
            ))
        
        return contradictions
    
    def _calculate_direction_conflict(
        self,
        recommendation_a: str,
        recommendation_b: str,
    ) -> float:
        """Calculate conflict score between two recommendations."""
        direction_map = {
            "aggressive": 1.0,
            "growth": 0.75,
            "expansion": 0.75,
            "positive": 0.5,
            "neutral": 0.25,
            "maintain": 0.25,
            "cautious": 0.25,
            "negative": 0.0,
            "contraction": 0.0,
            "defensive": 0.0,
            "conservative": 0.1,
        }
        
        # Get numeric values
        val_a = direction_map.get(recommendation_a.lower(), 0.25)
        val_b = direction_map.get(recommendation_b.lower(), 0.25)
        
        # Calculate conflict (difference in direction)
        return abs(val_a - val_b)
    
    def _conflict_to_severity(self, conflict: float) -> ContradictionSeverity:
        """Convert conflict score to severity."""
        if conflict >= self.SEVERITY_THRESHOLDS["critical_conflict"]:
            return ContradictionSeverity.CRITICAL
        elif conflict >= self.SEVERITY_THRESHOLDS["high_conflict"]:
            return ContradictionSeverity.HIGH
        elif conflict >= self.SEVERITY_THRESHOLDS["medium_conflict"]:
            return ContradictionSeverity.MEDIUM
        else:
            return ContradictionSeverity.LOW
    
    def _create_contradiction(
        self,
        engine_a: OriginEngine,
        engine_b: OriginEngine,
        description: str,
        severity: ContradictionSeverity,
        evidence: Dict[str, Any],
    ) -> ContradictionRecord:
        """Create a contradiction record."""
        return ContradictionRecord(
            contradiction_id=f"contra_{uuid.uuid4().hex[:12]}",
            engine_a=engine_a,
            engine_b=engine_b,
            conflicting_signal=description,
            severity=severity,
            resolution_status="unresolved",
            detected_at=datetime.utcnow(),
            description=description,
            evidence=evidence,
        )
    
    def get_contradiction_severity_summary(
        self,
        contradictions: List[ContradictionRecord],
    ) -> Dict[str, int]:
        """Get summary of contradictions by severity."""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        
        for c in contradictions:
            summary[c.severity.value] += 1
        
        return summary
    
    def has_critical_contradictions(
        self,
        contradictions: List[ContradictionRecord],
    ) -> bool:
        """Check if there are any critical contradictions."""
        return any(c.severity == ContradictionSeverity.CRITICAL for c in contradictions)
    
    def get_contradiction_history(
        self,
        limit: int = 100,
    ) -> List[ContradictionRecord]:
        """Get contradiction history."""
        return self._contradiction_history[-limit:]
