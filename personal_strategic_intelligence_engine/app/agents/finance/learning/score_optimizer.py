"""Score Optimizer.

Generates advisory optimization proposals for improving signal scoring.
"""

from datetime import datetime
from typing import List, Dict, Optional
import uuid

from app.agents.finance.learning.learning_models import (
    ScoreOptimizationProposal,
    FeaturePerformanceReport,
    ConfidenceCalibrationReport,
    SuppressionEffectivenessReport,
    RegimePerformanceReport,
    TimingPerformanceReport,
)


class ScoreOptimizer:
    """Generates optimization proposals for tactical scoring."""
    
    def __init__(self):
        self.proposals: List[ScoreOptimizationProposal] = []
    
    def generate_proposals(
        self,
        feature_report: Optional[FeaturePerformanceReport],
        calibration_report: Optional[ConfidenceCalibrationReport],
        suppression_report: Optional[SuppressionEffectivenessReport],
        regime_report: Optional[RegimePerformanceReport],
        timing_report: Optional[TimingPerformanceReport],
    ) -> List[ScoreOptimizationProposal]:
        """Generate optimization proposals based on analysis reports."""
        
        proposals = []
        
        # Feature weight proposals
        if feature_report:
            proposals.extend(self._generate_feature_proposals(feature_report))
        
        # Confidence calibration proposals
        if calibration_report:
            proposals.extend(self._generate_calibration_proposals(calibration_report))
        
        # Suppression threshold proposals
        if suppression_report:
            proposals.extend(self._generate_suppression_proposals(suppression_report))
        
        # Regime modifier proposals
        if regime_report:
            proposals.extend(self._generate_regime_proposals(regime_report))
        
        # Timing modifier proposals
        if timing_report:
            proposals.extend(self._generate_timing_proposals(timing_report))
        
        self.proposals = proposals
        return proposals
    
    def _generate_feature_proposals(
        self,
        report: FeaturePerformanceReport,
    ) -> List[ScoreOptimizationProposal]:
        """Generate feature weight proposals."""
        proposals = []
        
        # Boost strong predictors
        for feature in report.top_positive_predictors[:3]:
            proposals.append(ScoreOptimizationProposal(
                proposal_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                proposal_type="feature_weight_boost",
                target_feature=feature.feature_name,
                current_weight=1.0,
                proposed_weight=1.0 + (feature.predictive_power * 0.2),
                expected_improvement=feature.predictive_power * 5,
                confidence=feature.predictive_power * 0.8,
                rationale=f"Feature {feature.feature_name} shows strong predictive power ({feature.predictive_power:.2f})",
                requires_approval=True,
            ))
        
        # Consider reducing weak predictors
        for feature_name in report.low_value_features[:2]:
            proposals.append(ScoreOptimizationProposal(
                proposal_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                proposal_type="feature_weight_reduction",
                target_feature=feature_name,
                current_weight=1.0,
                proposed_weight=0.7,
                expected_improvement=2.0,
                confidence=0.6,
                rationale=f"Feature {feature_name} shows low predictive power",
                requires_approval=True,
            ))
        
        return proposals
    
    def _generate_calibration_proposals(
        self,
        report: ConfidenceCalibrationReport,
    ) -> List[ScoreOptimizationProposal]:
        """Generate confidence calibration proposals."""
        proposals = []
        
        for bucket_name, adjustment in report.recommended_adjustments.items():
            if abs(adjustment) > 5:  # Only significant adjustments
                proposals.append(ScoreOptimizationProposal(
                    proposal_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    proposal_type="confidence_calibration",
                    target_feature=f"confidence_bucket_{bucket_name}",
                    current_weight=None,
                    proposed_weight=adjustment,
                    expected_improvement=abs(adjustment) * 0.5,
                    confidence=0.7,
                    rationale=f"Confidence bucket {bucket_name} shows {adjustment:.1f}% over/under-confidence",
                    requires_approval=True,
                ))
        
        return proposals
    
    def _generate_suppression_proposals(
        self,
        report: SuppressionEffectivenessReport,
    ) -> List[ScoreOptimizationProposal]:
        """Generate suppression threshold proposals."""
        proposals = []
        
        for category in report.harmful_suppressions:
            proposals.append(ScoreOptimizationProposal(
                proposal_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                proposal_type="suppression_threshold_relax",
                target_feature=f"suppression_{category}",
                current_weight=1.0,
                proposed_weight=0.5,
                expected_improvement=5.0,
                confidence=0.6,
                rationale=f"Suppression {category} is blocking potentially profitable trades",
                requires_approval=True,
            ))
        
        for category in report.over_restricted_categories:
            proposals.append(ScoreOptimizationProposal(
                proposal_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                proposal_type="suppression_threshold_tighten",
                target_feature=f"suppression_{category}",
                current_weight=1.0,
                proposed_weight=1.2,
                expected_improvement=3.0,
                confidence=0.5,
                rationale=f"Suppression {category} has high false suppression rate",
                requires_approval=True,
            ))
        
        return proposals
    
    def _generate_regime_proposals(
        self,
        report: RegimePerformanceReport,
    ) -> List[ScoreOptimizationProposal]:
        """Generate regime modifier proposals."""
        proposals = []
        
        for regime, modifier in report.regime_confidence_modifiers.items():
            if abs(modifier) > 5:  # Only significant modifiers
                proposals.append(ScoreOptimizationProposal(
                    proposal_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    proposal_type="regime_confidence_modifier",
                    target_feature=f"regime_{regime}",
                    current_weight=0.0,
                    proposed_weight=modifier,
                    expected_improvement=abs(modifier) * 0.3,
                    confidence=0.7,
                    rationale=f"Regime {regime} shows {'strong' if modifier > 0 else 'weak'} performance",
                    requires_approval=True,
                ))
        
        return proposals
    
    def _generate_timing_proposals(
        self,
        report: TimingPerformanceReport,
    ) -> List[ScoreOptimizationProposal]:
        """Generate timing modifier proposals."""
        proposals = []
        
        for perf in report.timing_decisions:
            if perf.signal_count >= 5 and perf.expectancy > 5:
                proposals.append(ScoreOptimizationProposal(
                    proposal_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    proposal_type="timing_weight_adjustment",
                    target_feature=f"timing_{perf.timing_decision.value}",
                    current_weight=1.0,
                    proposed_weight=1.0 + (perf.expectancy / 100),
                    expected_improvement=perf.expectancy * 0.3,
                    confidence=0.6,
                    rationale=f"Timing decision {perf.timing_decision.value} shows positive expectancy ({perf.expectancy:.2f})",
                    requires_approval=True,
                ))
            elif perf.signal_count >= 5 and perf.expectancy < -10:
                proposals.append(ScoreOptimizationProposal(
                    proposal_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    proposal_type="timing_weight_adjustment",
                    target_feature=f"timing_{perf.timing_decision.value}",
                    current_weight=1.0,
                    proposed_weight=0.7,
                    expected_improvement=5.0,
                    confidence=0.6,
                    rationale=f"Timing decision {perf.timing_decision.value} shows negative expectancy ({perf.expectancy:.2f})",
                    requires_approval=True,
                ))
        
        return proposals
    
    def get_pending_proposals(self) -> List[ScoreOptimizationProposal]:
        """Get all pending proposals."""
        return [p for p in self.proposals if p.status == "pending"]
    
    def approve_proposal(self, proposal_id: str) -> bool:
        """Approve a proposal (requires governance)."""
        for proposal in self.proposals:
            if proposal.proposal_id == proposal_id:
                proposal.status = "approved"
                return True
        return False
    
    def reject_proposal(self, proposal_id: str) -> bool:
        """Reject a proposal."""
        for proposal in self.proposals:
            if proposal.proposal_id == proposal_id:
                proposal.status = "rejected"
                return True
        return False


def create_optimizer() -> ScoreOptimizer:
    """Create a new score optimizer."""
    return ScoreOptimizer()
