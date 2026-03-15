"""Signal Outcome Analyzer.

Analyzes historical signal outcomes to identify patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    SignalDirection,
    MarketRegime,
)


class SignalOutcomeAnalyzer:
    """Analyzes signal outcomes for patterns."""
    
    def __init__(self):
        self.records: List[SignalOutcomeRecord] = []
    
    def add_record(self, record: SignalOutcomeRecord) -> None:
        """Add a signal outcome record."""
        self.records.append(record)
    
    def get_records(self) -> List[SignalOutcomeRecord]:
        """Get all records."""
        return self.records
    
    def get_resolved_records(self) -> List[SignalOutcomeRecord]:
        """Get records with resolved outcomes."""
        return [r for r in self.records if r.outcome != SignalOutcome.PENDING]
    
    def analyze_win_rate_by_direction(self) -> Dict[SignalDirection, float]:
        """Calculate win rate by signal direction."""
        resolved = self.get_resolved_records()
        by_direction = defaultdict(lambda: {"wins": 0, "total": 0})
        
        for record in resolved:
            direction = record.direction
            by_direction[direction]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                by_direction[direction]["wins"] += 1
        
        return {
            direction: (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            for direction, stats in by_direction.items()
        }
    
    def analyze_win_rate_by_confidence_bucket(self, bucket_size: int = 10) -> Dict[int, float]:
        """Calculate win rate by confidence bucket."""
        resolved = self.get_resolved_records()
        buckets = defaultdict(lambda: {"wins": 0, "total": 0})
        
        for record in resolved:
            bucket = int(record.confidence_score / bucket_size) * bucket_size
            buckets[bucket]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                buckets[bucket]["wins"] += 1
        
        return {
            bucket: (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            for bucket, stats in buckets.items()
        }
    
    def analyze_score_distribution(self) -> Dict[str, float]:
        """Analyze score distribution vs outcome."""
        resolved = self.get_resolved_records()
        
        wins = [r.signal_score for r in resolved if r.outcome == SignalOutcome.WIN]
        losses = [r.signal_score for r in resolved if r.outcome == SignalOutcome.LOSS]
        
        return {
            "avg_score_wins": sum(wins) / len(wins) if wins else 0,
            "avg_score_losses": sum(losses) / len(losses) if losses else 0,
            "score_separation": (sum(wins) / len(wins) if wins else 0) - (sum(losses) / len(losses) if losses else 0),
        }
    
    def analyze_profit_loss_distribution(self) -> Dict[str, float]:
        """Analyze P&L distribution."""
        resolved = self.get_resolved_records()
        with_pnl = [r for r in resolved if r.profit_loss is not None]
        
        if not with_pnl:
            return {
                "total_pnl": 0,
                "avg_pnl": 0,
                "max_win": 0,
                "max_loss": 0,
                "win_to_loss_ratio": 0,
            }
        
        pnls = [r.profit_loss for r in with_pnl]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        return {
            "total_pnl": sum(pnls),
            "avg_pnl": sum(pnls) / len(pnls),
            "max_win": max(wins) if wins else 0,
            "max_loss": min(losses) if losses else 0,
            "avg_win": sum(wins) / len(wins) if wins else 0,
            "avg_loss": sum(losses) / len(losses) if losses else 0,
            "win_to_loss_ratio": abs(sum(wins) / len(wins) / (sum(losses) / len(losses))) if losses and wins else 0,
        }
    
    def calculate_false_positive_rate(self, threshold: float = 60) -> float:
        """Calculate false positive rate (high score but loss)."""
        resolved = self.get_resolved_records()
        high_score = [r for r in resolved if r.signal_score >= threshold]
        
        if not high_score:
            return 0.0
        
        false_positives = [r for r in high_score if r.outcome == SignalOutcome.LOSS]
        return len(false_positives) / len(high_score) * 100
    
    def calculate_false_negative_rate(self, threshold: float = 40) -> float:
        """Calculate false negative rate (low score but win)."""
        resolved = self.get_resolved_records()
        low_score = [r for r in resolved if r.signal_score <= threshold]
        
        if not low_score:
            return 0.0
        
        false_negatives = [r for r in low_score if r.outcome == SignalOutcome.WIN]
        return len(false_negatives) / len(low_score) * 100
    
    def identify_top_performers(self, min_signals: int = 5) -> List[Dict]:
        """Identify top performing signal archetypes."""
        resolved = self.get_resolved_records()
        
        # Group by strike range
        by_strike = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0})
        for record in resolved:
            strike_bucket = int(record.strike / 5) * 5
            by_strike[strike_bucket]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                by_strike[strike_bucket]["wins"] += 1
            if record.profit_loss:
                by_strike[strike_bucket]["pnl"] += record.profit_loss
        
        # Calculate metrics
        performers = []
        for strike, stats in by_strike.items():
            if stats["total"] >= min_signals:
                win_rate = stats["wins"] / stats["total"] * 100
                performers.append({
                    "strike_range": f"{strike}-{strike+5}",
                    "signal_count": stats["total"],
                    "win_rate": win_rate,
                    "total_pnl": stats["pnl"],
                })
        
        # Sort by win rate
        performers.sort(key=lambda x: x["win_rate"], reverse=True)
        return performers[:10]
    
    def identify_poor_performers(self, min_signals: int = 5) -> List[Dict]:
        """Identify worst performing signal archetypes."""
        resolved = self.get_resolved_records()
        
        by_strike = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0})
        for record in resolved:
            strike_bucket = int(record.strike / 5) * 5
            by_strike[strike_bucket]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                by_strike[strike_bucket]["wins"] += 1
            if record.profit_loss:
                by_strike[strike_bucket]["pnl"] += record.profit_loss
        
        performers = []
        for strike, stats in by_strike.items():
            if stats["total"] >= min_signals:
                win_rate = stats["wins"] / stats["total"] * 100
                performers.append({
                    "strike_range": f"{strike}-{strike+5}",
                    "signal_count": stats["total"],
                    "win_rate": win_rate,
                    "total_pnl": stats["pnl"],
                })
        
        performers.sort(key=lambda x: x["win_rate"])
        return performers[:10]
    
    def identify_failure_patterns(self) -> Dict[str, any]:
        """Identify recurring failure patterns."""
        resolved = self.get_resolved_records()
        losses = [r for r in resolved if r.outcome == SignalOutcome.LOSS]
        
        if not losses:
            return {"patterns": [], "count": 0}
        
        # Analyze common characteristics of losses
        by_regime = defaultdict(int)
        by_timing = defaultdict(int)
        by_vwap = defaultdict(int)
        
        for loss in losses:
            by_regime[loss.regime.value] += 1
            by_timing[loss.timing_decision.value] += 1
            by_vwap[loss.vwap_state] += 1
        
        return {
            "patterns": [
                {"type": "regime", "value": max(by_regime, key=by_regime.get), "count": max(by_regime.values())},
                {"type": "timing", "value": max(by_timing, key=by_timing.get), "count": max(by_timing.values())},
                {"type": "vwap", "value": max(by_vwap, key=by_vwap.get), "count": max(by_vwap.values())},
            ],
            "total_losses": len(losses),
        }
    
    def generate_summary(self) -> Dict[str, any]:
        """Generate comprehensive outcome summary."""
        resolved = self.get_resolved_records()
        
        if not resolved:
            return {
                "total_signals": len(self.records),
                "resolved_signals": 0,
                "message": "No resolved outcomes yet",
            }
        
        wins = len([r for r in resolved if r.outcome == SignalOutcome.WIN])
        losses = len([r for r in resolved if r.outcome == SignalOutcome.LOSS])
        
        return {
            "total_signals": len(self.records),
            "resolved_signals": len(resolved),
            "win_count": wins,
            "loss_count": losses,
            "win_rate": wins / len(resolved) * 100 if resolved else 0,
            "by_direction": self.analyze_win_rate_by_direction(),
            "score_distribution": self.analyze_score_distribution(),
            "pnl_distribution": self.analyze_profit_loss_distribution(),
            "false_positive_rate": self.calculate_false_positive_rate(),
            "false_negative_rate": self.calculate_false_negative_rate(),
            "top_performers": self.identify_top_performers(),
            "poor_performers": self.identify_poor_performers(),
            "failure_patterns": self.identify_failure_patterns(),
        }


def create_analyzer() -> SignalOutcomeAnalyzer:
    """Create a new signal outcome analyzer."""
    return SignalOutcomeAnalyzer()
