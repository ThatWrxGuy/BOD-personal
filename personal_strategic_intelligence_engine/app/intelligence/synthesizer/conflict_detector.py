"""Conflict Detector - Detects contradictions between predictive engines."""
import uuid
from typing import List, Dict, Any, Optional, Tuple

from app.intelligence.synthesizer.insight_models import (
    IntelligenceConflict,
    PredictionSnapshot,
    RiskSeverity,
)


class ConflictDetector:
    """Detects conflicts between predictive engine outputs."""
    
    def __init__(self):
        self.conflict_threshold = 0.3  # Performance difference to trigger conflict
    
    def check_forecast_simulation_conflict(
        self,
        forecast: PredictionSnapshot,
        simulation: PredictionSnapshot,
    ) -> List[IntelligenceConflict]:
        """Check for conflicts between forecast and simulation predictions."""
        
        conflicts = []
        
        # Compare domain predictions
        for domain in set(forecast.domain_predictions.keys()) | set(simulation.domain_predictions.keys()):
            forecast_val = forecast.domain_predictions.get(domain, 5.0)
            sim_val = simulation.domain_predictions.get(domain, 5.0)
            
            diff = abs(forecast_val - sim_val)
            
            if diff > self.conflict_threshold * 10:
                conflict = IntelligenceConflict(
                    id=str(uuid.uuid4())[:8],
                    conflict_type="domain_prediction_mismatch",
                    description=f"Domain {domain} predictions differ significantly",
                    source_a="forecast",
                    source_b="simulation",
                    prediction_a=f"{forecast_val:.1f}/10",
                    prediction_b=f"{sim_val:.1f}/10",
                    severity=RiskSeverity.MEDIUM,
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def check_forecast_monte_carlo_conflict(
        self,
        forecast: PredictionSnapshot,
        monte_carlo: PredictionSnapshot,
    ) -> List[IntelligenceConflict]:
        """Check for conflicts between forecast and Monte Carlo."""
        
        conflicts = []
        
        # Monte Carlo shows variance, forecast shows single point
        # Check if forecast prediction is within MC distribution
        
        for domain in forecast.domain_predictions.keys():
            forecast_val = forecast.domain_predictions.get(domain, 5.0)
            
            # Get MC distribution stats if available
            mc_stats = monte_carlo.raw_data.get("domain_stats", {}).get(domain, {})
            
            if mc_stats:
                mc_mean = mc_stats.get("mean", forecast_val)
                mc_std = mc_stats.get("std", 0)
                
                # If forecast is far from MC mean (more than 2 std)
                if abs(forecast_val - mc_mean) > 2 * mc_std and mc_std > 0:
                    conflict = IntelligenceConflict(
                        id=str(uuid.uuid4())[:8],
                        conflict_type="forecast_mc_mismatch",
                        description=f"Forecast for {domain} outside Monte Carlo distribution",
                        source_a="forecast",
                        source_b="monte_carlo",
                        prediction_a=f"{forecast_val:.1f}/10",
                        prediction_b=f"mean={mc_mean:.1f}, std={mc_std:.1f}",
                        severity=RiskSeverity.HIGH,
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def check_simulation_monte_carlo_conflict(
        self,
        simulation: PredictionSnapshot,
        monte_carlo: PredictionSnapshot,
    ) -> List[IntelligenceConflict]:
        """Check for conflicts between simulation and Monte Carlo."""
        
        conflicts = []
        
        # Compare strategy rankings
        sim_rankings = simulation.strategy_rankings
        mc_resilience = monte_carlo.raw_data.get("resilience", {})
        
        if sim_rankings and mc_resilience:
            # Check if best strategy in simulation is also resilient in MC
            best_sim = max(sim_rankings.items(), key=lambda x: x[1])
            
            if best_sim[0] in mc_resilience:
                mc_resilience_score = mc_resilience[best_sim[0]]
                
                if mc_resilience_score < 0.5:
                    conflict = IntelligenceConflict(
                        id=str(uuid.uuid4())[:8],
                        conflict_type="strategy_resilience_mismatch",
                        description=f"Best simulation strategy {best_sim[0]} has low MC resilience",
                        source_a="simulation",
                        source_b="monte_carlo",
                        prediction_a=f"score={best_sim[1]:.2f}",
                        prediction_b=f"resilience={mc_resilience_score:.2f}",
                        severity=RiskSeverity.HIGH,
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def check_all_conflicts(
        self,
        forecast: Optional[PredictionSnapshot] = None,
        simulation: Optional[PredictionSnapshot] = None,
        monte_carlo: Optional[PredictionSnapshot] = None,
    ) -> List[IntelligenceConflict]:
        """Check for all possible conflicts between engines."""
        
        all_conflicts = []
        
        if forecast and simulation:
            all_conflicts.extend(
                self.check_forecast_simulation_conflict(forecast, simulation)
            )
        
        if forecast and monte_carlo:
            all_conflicts.extend(
                self.check_forecast_monte_carlo_conflict(forecast, monte_carlo)
            )
        
        if simulation and monte_carlo:
            all_conflicts.extend(
                self.check_simulation_monte_carlo_conflict(simulation, monte_carlo)
            )
        
        return all_conflicts
    
    def adjust_confidence_for_conflict(
        self,
        insight_confidence: float,
        conflicts: List[IntelligenceConflict],
    ) -> float:
        """Adjust insight confidence based on detected conflicts."""
        
        if not conflicts:
            return insight_confidence
        
        # Reduce confidence based on number and severity of conflicts
        reduction = 0.0
        
        for conflict in conflicts:
            if conflict.severity == RiskSeverity.CRITICAL:
                reduction += 0.2
            elif conflict.severity == RiskSeverity.HIGH:
                reduction += 0.15
            elif conflict.severity == RiskSeverity.MEDIUM:
                reduction += 0.1
            else:
                reduction += 0.05
        
        # Cap reduction at 50%
        reduction = min(reduction, 0.5)
        
        return max(0.1, insight_confidence - reduction)


_conflict_detector: Optional[ConflictDetector] = None


def get_conflict_detector() -> ConflictDetector:
    """Get the global conflict detector."""
    global _conflict_detector
    if _conflict_detector is None:
        _conflict_detector = ConflictDetector()
    return _conflict_detector
