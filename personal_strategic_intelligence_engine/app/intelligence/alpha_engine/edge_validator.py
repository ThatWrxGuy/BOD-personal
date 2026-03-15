"""Edge Validator.

Evaluates whether a strategy represents a credible edge.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from app.intelligence.alpha_engine.alpha_models import (
    AlphaCandidate, AlphaTestResult, EdgeValidation, ValidationStatus
)


class EdgeValidator:
    """Evaluates strategy edges."""
    
    def __init__(self):
        self.min_sample_size = 30
        self.min_confidence = 0.6
    
    def validate_alpha(
        self,
        candidate: AlphaCandidate,
        test_results: AlphaTestResult,
    ) -> EdgeValidation:
        """Validate an alpha candidate."""
        
        # Check sample size
        if test_results.sample_size < self.min_sample_size:
            return EdgeValidation(
                status=ValidationStatus.UNDER_REVIEW,
                confidence_score=test_results.sample_size / self.min_sample_size,
                risk_profile="unknown",
                recommended_use="Collect more data before deployment",
                metrics=self._get_metrics(test_results),
            )
        
        # Check expectancy
        if test_results.expectancy <= 0:
            return EdgeValidation(
                status=ValidationStatus.REJECTED,
                confidence_score=0.9,
                risk_profile="negative",
                recommended_use="Do not use - negative expectancy",
                metrics=self._get_metrics(test_results),
            )
        
        # Check stability
        if test_results.stability_score < 0.5:
            return EdgeValidation(
                status=ValidationStatus.UNDER_REVIEW,
                confidence_score=test_results.stability_score,
                risk_profile="unstable",
                recommended_use="Monitor closely - low stability",
                metrics=self._get_metrics(test_results),
            )
        
        # Calculate confidence
        confidence = self._calculate_confidence(test_results)
        
        # Determine risk profile
        risk_profile = self._assess_risk(test_results)
        
        # Determine recommended use
        recommended_use = self._get_recommendation(test_results, confidence)
        
        # Validate if all checks pass
        if confidence >= self.min_confidence and test_results.stability_score >= 0.6:
            status = ValidationStatus.VALIDATED
        else:
            status = ValidationStatus.UNDER_REVIEW
        
        return EdgeValidation(
            status=status,
            confidence_score=confidence,
            risk_profile=risk_profile,
            recommended_use=recommended_use,
            metrics=self._get_metrics(test_results),
        )
    
    def _calculate_confidence(self, results: AlphaTestResult) -> float:
        """Calculate overall confidence score."""
        
        # Weight factors
        sample_factor = min(1.0, results.sample_size / 100)
        win_rate_factor = results.win_rate / 100
        expectancy_factor = min(1.0, results.expectancy / 50)
        stability_factor = results.stability_score
        
        # Weighted average
        confidence = (
            0.2 * sample_factor +
            0.2 * win_rate_factor +
            0.3 * expectancy_factor +
            0.3 * stability_factor
        )
        
        return min(0.95, confidence)
    
    def _assess_risk(self, results: AlphaTestResult) -> str:
        """Assess risk profile."""
        
        if abs(results.drawdown) > 20:
            return "high"
        elif abs(results.drawdown) > 10:
            return "moderate"
        else:
            return "low"
    
    def _get_recommendation(self, results: AlphaTestResult, confidence: float) -> str:
        """Get usage recommendation."""
        
        if confidence >= 0.8 and results.expectancy > 20:
            return "Recommended for deployment"
        elif confidence >= 0.6:
            return "Use with caution"
        else:
            return "Collect more data"
    
    def _get_metrics(self, results: AlphaTestResult) -> Dict:
        """Get validation metrics."""
        
        return {
            "sample_size": results.sample_size,
            "win_rate": results.win_rate,
            "expectancy": results.expectancy,
            "drawdown": results.drawdown,
            "sharpe_like": results.sharpe_like_score,
            "stability": results.stability_score,
        }
    
    def run_validation(
        self,
        candidate: AlphaCandidate,
        historical_trades: List[Dict],
    ) -> EdgeValidation:
        """Run full validation on candidate."""
        
        # Calculate test results from historical trades
        test_results = self._calculate_test_results(historical_trades)
        
        # Validate
        return self.validate_alpha(candidate, test_results)
    
    def _calculate_test_results(self, trades: List[Dict]) -> AlphaTestResult:
        """Calculate test results from trades."""
        
        if not trades:
            return AlphaTestResult(
                sample_size=0,
                win_rate=0,
                expectancy=0,
                drawdown=0,
                sharpe_like_score=0,
                stability_score=0,
            )
        
        pnls = [t.get("pnl", 0) for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        expectancy = sum(pnls) / len(pnls) if pnls else 0
        
        # Calculate drawdown
        cumulative = 0
        max_dd = 0
        for pnl in pnls:
            cumulative += pnl
            if cumulative < max_dd:
                max_dd = cumulative
        drawdown = max_dd
        
        # Calculate Sharpe-like
        if len(pnls) > 1:
            avg = sum(pnls) / len(pnls)
            std = (sum((p - avg) ** 2 for p in pnls) / len(pnls)) ** 0.5
            sharpe = (avg / std * (252 ** 0.5)) if std > 0 else 0
        else:
            sharpe = 0
        
        # Stability based on rolling performance
        stability = 0.7  # Placeholder
        
        return AlphaTestResult(
            sample_size=len(trades),
            win_rate=win_rate,
            expectancy=expectancy,
            drawdown=drawdown,
            sharpe_like_score=sharpe,
            stability_score=stability,
        )


def create_validator() -> EdgeValidator:
    """Create edge validator."""
    return EdgeValidator()
