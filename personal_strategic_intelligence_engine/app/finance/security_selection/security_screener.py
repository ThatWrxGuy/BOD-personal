"""Security Screener.

This module filters securities based on baseline quality criteria.
"""
from typing import Optional

from app.finance.security_selection.selection_models import (
    ScreenCriteria,
    ScreenResult,
    ScreeningResult,
    SecurityProfile,
)


class SecurityScreener:
    """Screens securities based on quality criteria."""
    
    def __init__(self, criteria: Optional[ScreenCriteria] = None):
        """Initialize the screener.
        
        Args:
            criteria: Screening criteria
        """
        self.criteria = criteria or ScreenCriteria()
        
    def screen(self, security: SecurityProfile) -> ScreenResult:
        """Screen a security against criteria.
        
        Args:
            security: Security profile to screen
            
        Returns:
            Screening result
        """
        result = ScreenResult(
            symbol=security.symbol,
            result=ScreeningResult.PASSED,
        )
        
        # Check volume
        if security.volume < self.criteria.min_volume:
            result.result = ScreeningResult.FAILED
            result.reasons_failed.append(
                f"Volume {security.volume:,} below minimum {self.criteria.min_volume:,}"
            )
        else:
            result.reasons_passed.append("Volume meets minimum")
        
        # Check average volume
        if security.avg_volume < self.criteria.min_avg_volume:
            result.result = ScreeningResult.FAILED
            result.reasons_failed.append(
                f"Avg volume {security.avg_volume:,} below minimum {self.criteria.min_avg_volume:,}"
            )
        else:
            result.reasons_passed.append("Average volume meets minimum")
        
        # Check market cap
        if security.market_cap and security.market_cap < self.criteria.min_market_cap:
            result.result = ScreeningResult.FAILED
            result.reasons_failed.append(
                f"Market cap ${security.market_cap/1e9:.1f}B below minimum ${self.criteria.min_market_cap/1e9:.1f}B"
            )
        elif security.market_cap:
            result.reasons_passed.append("Market cap adequate")
        
        # Check price
        if security.price < self.criteria.min_price:
            result.result = ScreeningResult.FAILED
            result.reasons_failed.append(
                f"Price ${security.price} below minimum ${self.criteria.min_price}"
            )
        else:
            result.reasons_passed.append("Price adequate")
        
        # Check max price
        if self.criteria.max_price and security.price > self.criteria.max_price:
            result.warnings.append(
                f"Price ${security.price} above typical threshold"
            )
        
        # Check relative strength
        if security.change_percent < self.criteria.min_relative_strength:
            result.warnings.append(
                f"Relative strength {security.change_percent:.1f}% below threshold"
            )
        
        # Check options criteria if applicable
        if security.has_options:
            if security.options_volume and security.options_volume < self.criteria.min_options_volume:
                result.warnings.append(
                    f"Options volume below threshold"
                )
            
            if security.put_call_ratio and security.put_call_ratio > self.criteria.max_put_call_ratio:
                result.warnings.append(
                    f"Put/call ratio {security.put_call_ratio:.2f} elevated"
                )
        
        # Calculate screening score
        result.score = self._calculate_screen_score(result)
        
        return result
    
    def screen_batch(
        self,
        securities: list[SecurityProfile],
    ) -> tuple[list[SecurityProfile], list[ScreenResult]]:
        """Screen multiple securities.
        
        Args:
            securities: List of security profiles
            
        Returns:
            Tuple of (passed securities, all results)
        """
        results = []
        passed = []
        
        for security in securities:
            result = self.screen(security)
            results.append(result)
            
            if result.result == ScreeningResult.PASSED:
                passed.append(security)
        
        return passed, results
    
    def filter_by_category(
        self,
        securities: list[SecurityProfile],
        category: str,
    ) -> list[SecurityProfile]:
        """Filter securities by category.
        
        Args:
            securities: List of securities
            category: Category to filter
            
        Returns:
            Filtered list
        """
        return [
            s for s in securities
            if s.category.value == category
        ]
    
    def update_criteria(self, **kwargs):
        """Update screening criteria."""
        for key, value in kwargs.items():
            if hasattr(self.criteria, key):
                setattr(self.criteria, key, value)
    
    def get_criteria_summary(self) -> dict:
        """Get criteria summary."""
        return {
            "min_volume": self.criteria.min_volume,
            "min_avg_volume": self.criteria.min_avg_volume,
            "min_market_cap": f"${self.criteria.min_market_cap/1e9:.1f}B",
            "min_price": float(self.criteria.min_price),
            "min_relative_strength": self.criteria.min_relative_strength,
        }
    
    def _calculate_screen_score(self, result: ScreenResult) -> float:
        """Calculate overall screening score."""
        if result.result == ScreeningResult.FAILED:
            return 0.0
        
        score = 100.0
        
        # Deduct for warnings
        score -= len(result.warnings) * 5
        
        return max(0.0, score)


# Global instance
_screener: Optional[SecurityScreener] = None


def get_screener() -> SecurityScreener:
    """Get the global security screener."""
    global _screener
    
    if _screener is None:
        _screener = SecurityScreener()
    
    return _screener
