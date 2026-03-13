"""Cross-Signal Balancer.

Balances signals across domains to prevent low-value signals from overpowering high-impact ones.
"""
from typing import Any, Dict, List

from app.signal_calibration.calibration_models import CrossSignalBalanceResult


class CrossSignalBalancer:
    """Balances signals across different domains."""
    
    # Domain importance weights (relative strategic impact)
    DOMAIN_IMPORTANCE = {
        "finance": 1.0,        # Highest - money matters most
        "health": 0.95,       # Critical - health is foundational
        "tasks": 0.7,         # High - productivity affects outcomes
        "calendar": 0.5,       # Medium - schedule affects execution
    }
    
    # Maximum ratio between highest and lowest domain weights
    MAX_RATIO = 5.0
    
    def __init__(self, custom_weights: Dict[str, float] = None):
        self.domain_importance = {**self.DOMAIN_IMPORTANCE}
        if custom_weights:
            self.domain_importance.update(custom_weights)
    
    def balance_signal(
        self,
        signal_id: str,
        domain: str,
        base_weight: float,
        all_signals: List[Dict[str, Any]],
    ) -> CrossSignalBalanceResult:
        """Balance a signal against other domain signals."""
        
        # Get domain importance
        domain_weight = self.domain_importance.get(domain, 0.5)
        
        # Calculate balance score
        # Higher importance domains get higher balance
        balance_score = base_weight * domain_weight
        
        # Check proportionality vs highest impact
        max_importance = max(self.domain_importance.values())
        vs_highest = domain_weight / max_importance if max_importance > 0 else 0
        
        # Determine if proportional
        proportional = vs_highest >= 0.3  # At least 30% of max
        
        # Build rationale
        if proportional:
            reason = f"Domain '{domain}' has appropriate weight ({domain_weight:.2f})"
        else:
            reason = f"Domain '{domain}' weighted down due to lower strategic impact"
        
        return CrossSignalBalanceResult(
            signal_id=signal_id,
            domain=domain,
            domain_weight=domain_weight,
            balance_score=balance_score,
            vs_highest_impact=vs_highest,
            proportional_to_severity=proportional,
            reason=reason,
        )
    
    def balance_batch(
        self,
        signals: List[Dict[str, Any]],
    ) -> Dict[str, CrossSignalBalanceResult]:
        """Balance multiple signals."""
        results = {}
        
        for signal in signals:
            result = self.balance_signal(
                signal_id=signal.get("signal_id", ""),
                domain=signal.get("domain", "default"),
                base_weight=signal.get("weight", 1.0),
                all_signals=signals,
            )
            results[result.signal_id] = result
        
        return results
    
    def get_domain_distribution(
        self,
        signals: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """Get distribution of signals by domain."""
        distribution = {}
        
        for signal in signals:
            domain = signal.get("domain", "unknown")
            distribution[domain] = distribution.get(domain, 0) + 1
        
        return distribution
    
    def get_weighted_domain_scores(
        self,
        signals: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Get weighted scores by domain."""
        domain_scores = {}
        
        for signal in signals:
            domain = signal.get("domain", "unknown")
            weight = signal.get("weight", 1.0)
            domain_importance = self.domain_importance.get(domain, 0.5)
            
            weighted_score = weight * domain_importance
            domain_scores[domain] = domain_scores.get(domain, 0.0) + weighted_score
        
        return domain_scores


# Global balancer instance
_cross_signal_balancer: CrossSignalBalancer = None


def get_cross_signal_balancer() -> CrossSignalBalancer:
    """Get the global cross-signal balancer instance."""
    global _cross_signal_balancer
    if _cross_signal_balancer is None:
        _cross_signal_balancer = CrossSignalBalancer()
    return _cross_signal_balancer
