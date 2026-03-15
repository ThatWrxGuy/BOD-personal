"""Trajectory Simulator.

Simulates forward trajectories using current state and trends.
"""
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.strategic_foresight.foresight_models import (
    Domain,
    ForecastHorizon,
    FutureTrajectory,
    RiskType,
    OpportunityType,
    ScenarioType,
    StrategicRiskProjection,
    StrategicOpportunityProjection,
    ScenarioProjection,
    ForecastProbability,
    StrategicForecastReport,
    LIVE_EXECUTION_ENABLED,
    FORESIGHT_MODE,
)


class TrajectorySimulator:
    """Simulates forward trajectories."""
    
    # Signal trend thresholds
    TREND_THRESHOLD = 0.3
    
    def __init__(self):
        self._current_trajectories: List[FutureTrajectory] = []
    
    def simulate_trajectories(
        self,
        current_signals: Dict[str, float],
        horizon: ForecastHorizon,
    ) -> List[FutureTrajectory]:
        """Simulate forward trajectories for signals."""
        
        trajectories = []
        
        # Create trajectories for each individual signal
        for signal_name, signal_value in current_signals.items():
            trajectory = self._simulate_signal_trajectory(
                signal_name=signal_name,
                signal_value=signal_value,
                horizon=horizon,
            )
            trajectories.append(trajectory)
        
        self._current_trajectories = trajectories
        return trajectories
    
    def _simulate_signal_trajectory(
        self,
        signal_name: str,
        signal_value: float,
        horizon: ForecastHorizon,
    ) -> FutureTrajectory:
        """Simulate trajectory for a single signal."""
        
        # Determine domain from signal
        domain = self._get_domain_from_signal(signal_name)
        
        # Calculate days from horizon
        days = self._horizon_to_days(horizon)
        
        # Calculate trend based on signal direction (negative signals increase risk)
        trend = self._calculate_trend(signal_value, horizon)
        
        # Project future value
        projected_value = self._project_value(
            current_value=signal_value,
            trend=trend,
            days=days,
        )
        
        # Determine trend direction
        if signal_value > 0.3:
            trend_direction = "increasing"  # Positive signal increasing = good
        elif signal_value < -0.3:
            trend_direction = "increasing"  # Negative signal becoming more negative = risk
        else:
            trend_direction = "stable"
        
        # Create deterministic ID
        context_hash = hashlib.sha256(
            f"{signal_name}:{signal_value:.2f}|{horizon.value}".encode()
        ).hexdigest()
        
        return FutureTrajectory(
            trajectory_id=f"traj_{context_hash[:8]}",
            domain=domain,
            horizon=horizon,
            start_value=signal_value,
            projected_value=projected_value,
            trend=trend_direction,
            contributing_signals={signal_name: signal_value},
            projected_date=datetime.utcnow() + timedelta(days=days),
            confidence=0.7,
        )
    
    def _get_domain_from_signal(self, signal_name: str) -> Domain:
        """Get domain from signal name."""
        
        signal_lower = signal_name.lower()
        
        if "energy" in signal_lower or "sleep" in signal_lower or "stress" in signal_lower or "burnout" in signal_lower:
            return Domain.HEALTH
        elif "liquidity" in signal_lower or "spending" in signal_lower or "savings" in signal_lower or "income" in signal_lower:
            return Domain.FINANCE
        elif "backlog" in signal_lower or "completion" in signal_lower or "progress" in signal_lower or "productivity" in signal_lower:
            return Domain.PRODUCTIVITY
        elif "meeting" in signal_lower or "schedule" in signal_lower or "calendar" in signal_lower:
            return Domain.SCHEDULE
        else:
            return Domain.RISK
    
    def _horizon_to_days(self, horizon: ForecastHorizon) -> int:
        """Convert horizon to days."""
        
        mapping = {
            ForecastHorizon.DAYS_7: 7,
            ForecastHorizon.DAYS_30: 30,
            ForecastHorizon.DAYS_90: 90,
            ForecastHorizon.DAYS_365: 365,
        }
        
        return mapping.get(horizon, 30)
    
    def _calculate_trend(
        self,
        signal_value: float,
        horizon: ForecastHorizon,
    ) -> float:
        """Calculate signal trend deterministically."""
        
        # Calculate based on absolute value
        avg = abs(signal_value)
        
        # Scale by horizon (longer horizon = more potential change)
        horizon_factor = self._horizon_to_days(horizon) / 30.0
        
        # Create deterministic trend based on signal values
        trend = avg * horizon_factor * 0.1
        
        return trend
    
    def _project_value(
        self,
        current_value: float,
        trend: float,
        days: int,
    ) -> float:
        """Project future value with bounded change."""
        
        # Apply trend over time (with diminishing returns)
        change = trend * (days / 30.0)
        
        # Bound change to reasonable range
        change = max(-0.5, min(0.5, change))
        
        projected = current_value + change
        
        # Bound to -1 to 1 range
        return max(-1.0, min(1.0, projected))
    
    def _hash_signals(
        self,
        signals: Dict[str, float],
        domain: Domain,
        horizon: ForecastHorizon,
    ) -> str:
        """Create deterministic hash from signals."""
        
        parts = [domain.value, horizon.value]
        
        for key in sorted(signals.keys()):
            parts.append(f"{key}:{signals[key]:.2f}")
        
        context_str = "|".join(parts)
        
        return hashlib.sha256(context_str.encode()).hexdigest()
    
    def get_current_trajectories(self) -> List[FutureTrajectory]:
        """Get current simulated trajectories."""
        return self._current_trajectories


class RiskProjectionEngine:
    """Identifies emerging strategic risks."""
    
    def __init__(self):
        self._current_risks: List[StrategicRiskProjection] = []
    
    def project_risks(
        self,
        trajectories: List[FutureTrajectory],
    ) -> List[StrategicRiskProjection]:
        """Project risks based on trajectories."""
        
        risks = []
        
        # Map domains to risk types
        domain_risks = {
            Domain.HEALTH: RiskType.BURNOUT,
            Domain.FINANCE: RiskType.FINANCIAL_STRESS,
            Domain.PRODUCTIVITY: RiskType.PRODUCTIVITY_COLLAPSE,
            Domain.SCHEDULE: RiskType.SCHEDULE_OVERLOAD,
        }
        
        # Analyze each trajectory
        for trajectory in trajectories:
            if trajectory.trend == "increasing":
                # Risk increases
                risk_type = domain_risks.get(trajectory.domain, RiskType.BURNOUT)
                
                risk = StrategicRiskProjection(
                    risk_id=f"risk_{trajectory.domain.value}_{trajectory.horizon.value}",
                    risk_type=risk_type,
                    domain=trajectory.domain,
                    probability=self._calculate_risk_probability(trajectory),
                    horizon=trajectory.horizon,
                    projected_days=self._horizon_to_days(trajectory.horizon),
                    contributing_signals=trajectory.contributing_signals,
                    severity=self._calculate_severity(trajectory),
                    confidence=trajectory.confidence,
                    preventive_recommendations=self._get_preventive_recommendations(risk_type),
                )
                risks.append(risk)
        
        self._current_risks = risks
        return risks
    
    def _calculate_risk_probability(self, trajectory: FutureTrajectory) -> float:
        """Calculate risk probability from trajectory."""
        
        # Probability increases with projected value
        prob = abs(trajectory.projected_value) * 0.8
        
        return min(0.95, prob)
    
    def _calculate_severity(self, trajectory: FutureTrajectory) -> str:
        """Calculate risk severity."""
        
        value = abs(trajectory.projected_value)
        
        if value >= 0.8:
            return "critical"
        elif value >= 0.6:
            return "high"
        elif value >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _horizon_to_days(self, horizon: ForecastHorizon) -> int:
        """Convert horizon to days."""
        
        mapping = {
            ForecastHorizon.DAYS_7: 7,
            ForecastHorizon.DAYS_30: 30,
            ForecastHorizon.DAYS_90: 90,
            ForecastHorizon.DAYS_365: 365,
        }
        
        return mapping.get(horizon, 30)
    
    def _get_preventive_recommendations(self, risk_type: RiskType) -> List[str]:
        """Get preventive recommendations for risk type."""
        
        recommendations = {
            RiskType.BURNOUT: [
                "Schedule recovery time",
                "Reduce meeting density",
                "Prioritize sleep improvements",
            ],
            RiskType.FINANCIAL_STRESS: [
                "Increase savings rate",
                "Reduce discretionary spending",
                "Review budget allocation",
            ],
            RiskType.PRODUCTIVITY_COLLAPSE: [
                "Reduce task backlog",
                "Focus on completion",
                "Delegate or defer tasks",
            ],
            RiskType.SCHEDULE_OVERLOAD: [
                "Reduce commitments",
                "Block focus time",
                "Decline non-essential meetings",
            ],
            RiskType.LIQUIDITY_SHORTAGE: [
                "Accelerate receivables",
                "Delay large expenses",
                "Build cash reserve",
            ],
        }
        
        return recommendations.get(risk_type, ["Review priorities"])
    
    def get_current_risks(self) -> List[StrategicRiskProjection]:
        """Get current projected risks."""
        return self._current_risks


class OpportunityProjectionEngine:
    """Identifies emerging strategic opportunities."""
    
    def __init__(self):
        self._current_opportunities: List[StrategicOpportunityProjection] = []
    
    def project_opportunities(
        self,
        trajectories: List[FutureTrajectory],
    ) -> List[StrategicOpportunityProjection]:
        """Project opportunities based on trajectories."""
        
        opportunities = []
        
        # Map domains to opportunity types
        domain_opportunities = {
            Domain.HEALTH: OpportunityType.HEALTH_RECOVERY,
            Domain.FINANCE: OpportunityType.FINANCIAL_SURPLUS,
            Domain.PRODUCTIVITY: OpportunityType.HIGH_PRODUCTIVITY,
            Domain.SCHEDULE: OpportunityType.SCHEDULE_RECOVERY,
        }
        
        # Analyze each trajectory
        for trajectory in trajectories:
            if trajectory.trend == "decreasing":
                # Opportunity increases (e.g., lower stress)
                opp_type = domain_opportunities.get(trajectory.domain, OpportunityType.HIGH_PRODUCTIVITY)
                
                opportunity = StrategicOpportunityProjection(
                    opportunity_id=f"opp_{trajectory.domain.value}_{trajectory.horizon.value}",
                    opportunity_type=opp_type,
                    domain=trajectory.domain,
                    probability=self._calculate_opportunity_probability(trajectory),
                    horizon=trajectory.horizon,
                    projected_days=self._horizon_to_days(trajectory.horizon),
                    supporting_signals=trajectory.contributing_signals,
                    potential_value=abs(trajectory.projected_value),
                    confidence=trajectory.confidence,
                    capitalizing_recommendations=self._get_capitalizing_recommendations(opp_type),
                )
                opportunities.append(opportunity)
        
        self._current_opportunities = opportunities
        return opportunities
    
    def _calculate_opportunity_probability(self, trajectory: FutureTrajectory) -> float:
        """Calculate opportunity probability from trajectory."""
        
        # Probability based on projected positive change
        prob = abs(trajectory.projected_value) * 0.7
        
        return min(0.85, prob)
    
    def _horizon_to_days(self, horizon: ForecastHorizon) -> int:
        """Convert horizon to days."""
        
        mapping = {
            ForecastHorizon.DAYS_7: 7,
            ForecastHorizon.DAYS_30: 30,
            ForecastHorizon.DAYS_90: 90,
            ForecastHorizon.DAYS_365: 365,
        }
        
        return mapping.get(horizon, 30)
    
    def _get_capitalizing_recommendations(self, opp_type: OpportunityType) -> List[str]:
        """Get recommendations to capitalize on opportunity."""
        
        recommendations = {
            OpportunityType.HEALTH_RECOVERY: [
                "Maintain health routines",
                "Build on energy gains",
            ],
            OpportunityType.FINANCIAL_SURPLUS: [
                "Accelerate investments",
                "Build emergency fund",
            ],
            OpportunityType.HIGH_PRODUCTIVITY: [
                "Tackle challenging projects",
                "Make significant progress on goals",
            ],
            OpportunityType.SCHEDULE_RECOVERY: [
                "Take on additional commitments",
                "Schedule important meetings",
            ],
        }
        
        return recommendations.get(opp_type, ["Leverage opportunity"])
    
    def get_current_opportunities(self) -> List[StrategicOpportunityProjection]:
        """Get current projected opportunities."""
        return self._current_opportunities


class ScenarioGenerator:
    """Creates alternative future scenarios."""
    
    def generate_scenarios(
        self,
        current_signals: Dict[str, float],
        horizons: List[ForecastHorizon],
    ) -> List[ScenarioProjection]:
        """Generate alternative scenarios."""
        
        scenarios = []
        
        # Generate for each horizon
        for horizon in horizons:
            scenario = self._generate_baseline_scenario(
                current_signals, horizon
            )
            scenarios.append(scenario)
            
            scenario = self._generate_escalation_scenario(
                current_signals, horizon
            )
            scenarios.append(scenario)
            
            scenario = self._generate_recovery_scenario(
                current_signals, horizon
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _generate_baseline_scenario(
        self,
        signals: Dict[str, float],
        horizon: ForecastHorizon,
    ) -> ScenarioProjection:
        """Generate baseline continuation scenario."""
        
        context_hash = hashlib.sha256(
            f"baseline|{horizon.value}".encode()
        ).hexdigest()[:8]
        
        return ScenarioProjection(
            scenario_id=f"scenario_baseline_{context_hash}",
            scenario_type=ScenarioType.BASELINE,
            description="Current trends continue unchanged",
            domains=[self._infer_domain(s) for s in list(signals.keys())[:3]],
            horizon=horizon,
            projected_changes={k: v * 0.1 for k, v in list(signals.items())[:3]},
            probability=0.5,
            confidence=0.7,
        )
    
    def _generate_escalation_scenario(
        self,
        signals: Dict[str, float],
        horizon: ForecastHorizon,
    ) -> ScenarioProjection:
        """Generate escalation scenario."""
        
        context_hash = hashlib.sha256(
            f"escalation|{horizon.value}".encode()
        ).hexdigest()[:8]
        
        return ScenarioProjection(
            scenario_id=f"scenario_escalation_{context_hash}",
            scenario_type=ScenarioType.ESCALATION,
            description="Current negative trends intensify",
            domains=[self._infer_domain(s) for s in list(signals.keys())[:3]],
            horizon=horizon,
            projected_changes={k: v * 0.3 for k, v in list(signals.items())[:3]},
            probability=0.2,
            confidence=0.5,
        )
    
    def _generate_recovery_scenario(
        self,
        signals: Dict[str, float],
        horizon: ForecastHorizon,
    ) -> ScenarioProjection:
        """Generate recovery scenario."""
        
        context_hash = hashlib.sha256(
            f"recovery|{horizon.value}".encode()
        ).hexdigest()[:8]
        
        return ScenarioProjection(
            scenario_id=f"scenario_recovery_{context_hash}",
            scenario_type=ScenarioType.RECOVERY,
            description="Conditions improve significantly",
            domains=[self._infer_domain(s) for s in list(signals.keys())[:3]],
            horizon=horizon,
            projected_changes={k: -v * 0.3 for k, v in list(signals.items())[:3]},
            probability=0.3,
            confidence=0.6,
        )
    
    def _infer_domain(self, signal: str) -> Domain:
        """Infer domain from signal name."""
        
        signal_lower = signal.lower()
        
        if "energy" in signal_lower or "sleep" in signal_lower or "stress" in signal_lower:
            return Domain.HEALTH
        elif "finance" in signal_lower or "spending" in signal_lower or "liquidity" in signal_lower:
            return Domain.FINANCE
        elif "productivity" in signal_lower or "backlog" in signal_lower or "completion" in signal_lower:
            return Domain.PRODUCTIVITY
        elif "schedule" in signal_lower or "meeting" in signal_lower or "calendar" in signal_lower:
            return Domain.SCHEDULE
        else:
            return Domain.RISK


class ForecastProbabilityEngine:
    """Computes forecast probabilities."""
    
    def calculate_probabilities(
        self,
        risks: List[StrategicRiskProjection],
        opportunities: List[StrategicOpportunityProjection],
    ) -> List[ForecastProbability]:
        """Calculate probability estimates."""
        
        probabilities = []
        
        # Add risk probabilities
        for risk in risks:
            prob = ForecastProbability(
                outcome=f"risk_{risk.risk_type.value}",
                domain=risk.domain,
                probability=risk.probability,
                horizon=risk.horizon,
                confidence_lower=risk.probability - 0.1,
                confidence_upper=risk.probability + 0.1,
                confidence=risk.confidence,
                evidence_count=len(risk.contributing_signals),
            )
            probabilities.append(prob)
        
        # Add opportunity probabilities
        for opp in opportunities:
            prob = ForecastProbability(
                outcome=f"opportunity_{opp.opportunity_type.value}",
                domain=opp.domain,
                probability=opp.probability,
                horizon=opp.horizon,
                confidence_lower=opp.probability - 0.15,
                confidence_upper=opp.probability + 0.15,
                confidence=opp.confidence,
                evidence_count=len(opp.supporting_signals),
            )
            probabilities.append(prob)
        
        return probabilities


class ForesightController:
    """Central orchestration for foresight engine."""
    
    def __init__(self):
        self._simulator = TrajectorySimulator()
        self._risk_engine = RiskProjectionEngine()
        self._opp_engine = OpportunityProjectionEngine()
        self._scenario_gen = ScenarioGenerator()
        self._prob_engine = ForecastProbabilityEngine()
    
    def generate_strategic_forecast(
        self,
        signal_context: Dict[str, float],
    ) -> StrategicForecastReport:
        """Generate complete strategic forecast."""
        
        # Define horizons to evaluate
        horizons = [
            ForecastHorizon.DAYS_7,
            ForecastHorizon.DAYS_30,
            ForecastHorizon.DAYS_90,
        ]
        
        # Simulate trajectories for each horizon
        all_trajectories = []
        
        for horizon in horizons:
            trajectories = self._simulator.simulate_trajectories(
                signal_context, horizon
            )
            all_trajectories.extend(trajectories)
        
        # Project risks
        risks = self._risk_engine.project_risks(all_trajectories)
        
        # Project opportunities
        opportunities = self._opp_engine.project_opportunities(all_trajectories)
        
        # Generate scenarios
        scenarios = self._scenario_gen.generate_scenarios(
            signal_context, horizons
        )
        
        # Calculate probabilities
        probabilities = self._prob_engine.calculate_probabilities(risks, opportunities)
        
        # Count high priority items
        high_risks = sum(1 for r in risks if r.severity in ["high", "critical"])
        high_opps = sum(1 for o in opportunities if o.potential_value > 0.5)
        
        # Create report ID
        context_hash = hashlib.sha256(
            f"{signal_context}".encode()
        ).hexdigest()[:12]
        
        return StrategicForecastReport(
            report_id=f"forecast_{context_hash}",
            generated_at=datetime.utcnow(),
            current_signals=signal_context,
            trajectories=all_trajectories,
            risks=risks,
            opportunities=opportunities,
            scenarios=scenarios,
            probabilities=probabilities,
            high_priority_risks=high_risks,
            high_value_opportunities=high_opps,
            forecast_horizons=horizons,
        )


# Global controller
_foresight_controller: Optional[ForesightController] = None


def get_foresight_controller() -> ForesightController:
    """Get the global foresight controller."""
    global _foresight_controller
    if _foresight_controller is None:
        _foresight_controller = ForesightController()
    return _foresight_controller
