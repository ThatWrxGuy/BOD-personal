"""Approval burden analyzer for estimating operational cost of manual review.

Analyzes approval-required intents and estimates operator burden.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    ApprovalBurdenSnapshot,
    MonitoringWindow,
    ShadowCycleRecord,
)


class ApprovalBurdenAnalyzer:
    """Analyzer for approval burden estimation."""
    
    def __init__(self):
        """Initialize approval burden analyzer."""
        self.approval_history: List[Dict[str, Any]] = []
        self.domain_burden: Dict[str, int] = {}
    
    def record_approval_metrics(
        self,
        cycle: ShadowCycleRecord,
    ) -> None:
        """Record approval metrics from a cycle."""
        self.approval_history.append({
            "cycle_number": cycle.cycle_number,
            "approval_required": cycle.approval_required_count,
            "execution_intents": cycle.execution_intents_generated,
            "current_tier": cycle.current_tier,
            "timestamp": datetime.utcnow(),
        })
        
        # Keep bounded
        if len(self.approval_history) > 1000:
            self.approval_history = self.approval_history[-500:]
    
    def get_snapshot(self, window: MonitoringWindow) -> ApprovalBurdenSnapshot:
        """Get approval burden snapshot for a window."""
        window_sizes = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        size = window_sizes.get(window, 24)
        history = self.approval_history[-size:]
        
        if not history:
            return ApprovalBurdenSnapshot(window=window)
        
        # Calculate totals
        total_approval_required = sum(h["approval_required"] for h in history)
        
        # Count by tier
        manual_only = sum(1 for h in history if h.get("current_tier") == "tier_0_manual_only")
        fast_path = sum(1 for h in history if h.get("current_tier") == "tier_1_manual_fast_path")
        
        # Calculate rates
        total_cycles = len(history)
        auto_rate = (total_cycles - manual_only) / max(1, total_cycles)
        manual_rate = manual_only / max(1, total_cycles)
        
        # Estimate daily reviews (assuming 1 review takes 5 minutes)
        avg_approvals_per_cycle = total_approval_required / max(1, total_cycles)
        estimated_daily_reviews = avg_approvals_per_cycle * 24  # 24 cycles per day
        
        # Determine burden level
        if estimated_daily_reviews > 50:
            burden_level = "critical"
        elif estimated_daily_reviews > 20:
            burden_level = "high"
        elif estimated_daily_reviews > 10:
            burden_level = "moderate"
        elif estimated_daily_reviews > 3:
            burden_level = "low"
        else:
            burden_level = "minimal"
        
        return ApprovalBurdenSnapshot(
            timestamp=datetime.utcnow(),
            window=window,
            total_approval_required=total_approval_required,
            fast_path_approvals=fast_path,
            manual_only_approvals=manual_only,
            approval_distribution={
                "auto_approved": auto_rate,
                "manual_review": manual_rate,
            },
            domain_burden=self.domain_burden,
            auto_approval_rate=auto_rate,
            manual_review_rate=manual_rate,
            estimated_daily_reviews=int(estimated_daily_reviews),
            burden_level=burden_level,
        )
    
    def get_domain_burden(self) -> Dict[str, int]:
        """Get burden by domain."""
        return self.domain_burden.copy()
    
    def estimate_efficiency(self) -> float:
        """Estimate operator efficiency (0-1)."""
        if not self.approval_history:
            return 1.0
        
        recent = self.approval_history[-100:]
        
        # Higher efficiency = more auto-approved, less manual
        manual_count = sum(1 for h in recent if h.get("current_tier") == "tier_0_manual_only")
        auto_count = len(recent) - manual_count
        
        return auto_count / max(1, len(recent))
    
    def reset(self) -> None:
        """Reset analyzer state."""
        self.approval_history = []
        self.domain_burden = {}


def create_approval_burden_analyzer() -> ApprovalBurdenAnalyzer:
    """Factory function to create an approval burden analyzer."""
    return ApprovalBurdenAnalyzer()
