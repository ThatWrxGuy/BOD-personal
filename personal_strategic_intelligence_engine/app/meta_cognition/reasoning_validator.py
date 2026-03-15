"""Reasoning validation engine."""
from typing import List, Dict, Any, Optional
from app.meta_cognition.meta_types import ReasoningQuality, OriginEngine
from app.meta_cognition.meta_models import ReasoningValidationResult


class ReasoningValidator:
    """Validates the quality and completeness of reasoning.
    
    Checks include:
    - missing supporting signals
    - insufficient data sources
    - outdated state inputs
    - contradictory evidence ignored
    """
    
    # Minimum requirements for each reasoning quality tier
    MINIMUM_SIGNALS = {
        ReasoningQuality.COMPREHENSIVE: 3,
        ReasoningQuality.ADEQUATE: 2,
        ReasoningQuality.PARTIAL: 1,
        ReasoningQuality.INSUFFICIENT: 0,
    }
    
    # Minimum required engines
    MINIMUM_ENGINES = 2
    
    def __init__(self):
        self._required_engines = [
            OriginEngine.FORECAST,
            OriginEngine.SIMULATION,
        ]
    
    def validate_reasoning(
        self,
        supporting_signals: List[Dict[str, Any]],
        engines_consulted: List[OriginEngine],
        context: Dict[str, Any],
    ) -> ReasoningValidationResult:
        """Validate reasoning completeness.
        
        Args:
            supporting_signals: Signals supporting the decision
            engines_consulted: List of engines that provided input
            context: Additional context about the decision
            
        Returns:
            Validation result with quality assessment
        """
        issues = []
        missing_signals = []
        score = 1.0
        
        # Check for supporting signals
        if len(supporting_signals) < self.MINIMUM_SIGNALS[ReasoningQuality.ADEQUATE]:
            missing = self.MINIMUM_SIGNALS[ReasoningQuality.ADEQUATE] - len(supporting_signals)
            missing_signals.append(f"Need {missing} more supporting signals")
            issues.append("Insufficient supporting signals")
            score -= 0.3
        
        # Check for engine diversity
        if len(engines_consulted) < self.MINIMUM_ENGINES:
            issues.append(f"Only {len(engines_consulted)} engine(s) consulted, need at least {self.MINIMUM_ENGINES}")
            score -= 0.2
        
        # Check for data freshness
        if context:
            freshness_issue = self._check_data_freshness(context)
            if freshness_issue:
                issues.append(freshness_issue)
                score -= 0.1
        
        # Check for evidence quality
        signal_quality = self._assess_signal_quality(supporting_signals)
        if signal_quality < 0.5:
            issues.append("Low quality supporting signals")
            score -= 0.2
        
        # Check for contradictory evidence
        contradiction_issue = self._check_contradictory_evidence(supporting_signals)
        if contradiction_issue:
            issues.append(contradiction_issue)
            score -= 0.1
        
        # Determine quality tier
        score = max(0.0, min(1.0, score))
        quality = self._score_to_quality(score)
        
        # Determine if valid
        is_valid = quality in [ReasoningQuality.ADEQUATE, ReasoningQuality.COMPREHENSIVE]
        
        return ReasoningValidationResult(
            is_valid=is_valid,
            quality=quality,
            issues=issues,
            missing_signals=missing_signals,
            score=score,
        )
    
    def _check_data_freshness(self, context: Dict[str, Any]) -> Optional[str]:
        """Check if data is fresh enough."""
        import datetime
        
        # Check for timestamp in context
        if "last_update" in context:
            try:
                last_update = datetime.datetime.fromisoformat(context["last_update"])
                age = datetime.datetime.utcnow() - last_update
                
                # If data is older than 1 hour
                if age > datetime.timedelta(hours=1):
                    return f"Data is {age.total_seconds()/3600:.1f} hours old"
            except:
                pass
        
        # Check for explicit freshness indicator
        if context.get("is_stale", False):
            return "Data is marked as stale"
        
        return None
    
    def _assess_signal_quality(self, signals: List[Dict[str, Any]]) -> float:
        """Assess quality of supporting signals."""
        if not signals:
            return 0.0
        
        quality_scores = []
        
        for signal in signals:
            score = 0.5  # Base score
            
            # Has source
            if signal.get("source"):
                score += 0.15
            
            # Has confidence
            if "confidence" in signal:
                score += 0.15
            
            # Has timestamp
            if "timestamp" in signal:
                score += 0.1
            
            # Has supporting data
            if signal.get("data"):
                score += 0.1
            
            quality_scores.append(min(1.0, score))
        
        return sum(quality_scores) / len(quality_scores)
    
    def _check_contradictory_evidence(
        self,
        signals: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Check for contradictory evidence in signals."""
        if len(signals) < 2:
            return None
        
        # Get directions
        directions = set()
        for signal in signals:
            direction = signal.get("direction", "neutral").lower()
            if direction != "neutral":
                directions.add(direction)
        
        # If we have both positive and negative, flag it
        if len(directions) > 1:
            return "Contradictory evidence in supporting signals"
        
        return None
    
    def _score_to_quality(self, score: float) -> ReasoningQuality:
        """Convert score to quality tier."""
        if score >= 0.8:
            return ReasoningQuality.COMPREHENSIVE
        elif score >= 0.6:
            return ReasoningQuality.ADEQUATE
        elif score >= 0.4:
            return ReasoningQuality.PARTIAL
        else:
            return ReasoningQuality.INSUFFICIENT
    
    def set_required_engines(self, engines: List[OriginEngine]):
        """Set required engines for validation."""
        self._required_engines = engines
    
    def get_minimum_signals_for_quality(self, quality: ReasoningQuality) -> int:
        """Get minimum signals required for a quality tier."""
        return self.MINIMUM_SIGNALS.get(quality, 0)
