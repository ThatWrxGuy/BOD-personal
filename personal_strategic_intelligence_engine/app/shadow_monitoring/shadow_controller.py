"""Shadow controller for central orchestration of shadow monitoring.

Coordinates all monitoring components and enforces shadow-only behavior.
"""
import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import ApprovalTierLevel
from app.governance_simulation.scenario_generator import ScenarioGenerator
from app.governance_simulation.simulation_models import ScenarioType
from app.shadow_monitoring.approval_burden_analyzer import ApprovalBurdenAnalyzer, create_approval_burden_analyzer
from app.shadow_monitoring.anomaly_detector import AnomalyDetector, create_anomaly_detector
from app.shadow_monitoring.confidence_drift_detector import ConfidenceDriftDetector, create_confidence_drift_detector
from app.shadow_monitoring.cycle_monitor import CycleMonitor, create_cycle_monitor
from app.shadow_monitoring.governance_load_monitor import GovernanceLoadMonitor, create_governance_load_monitor
from app.shadow_monitoring.monitoring_models import (
    MonitoringStatus,
    MonitoringWindow,
    ShadowCycleRecord,
)
from app.shadow_monitoring.monitoring_reporter import MonitoringReporter, create_monitoring_reporter
from app.shadow_monitoring.monitoring_store import MonitoringStore, create_monitoring_store
from app.shadow_monitoring.recommendation_monitor import RecommendationMonitor, create_recommendation_monitor
from app.shadow_monitoring.signal_reliability_monitor import SignalReliabilityMonitor, create_signal_reliability_monitor


class ShadowController:
    """Central controller for shadow monitoring operation."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize shadow controller."""
        # Initialize all monitors
        self.cycle_monitor = create_cycle_monitor()
        self.recommendation_monitor = create_recommendation_monitor()
        self.confidence_drift_detector = create_confidence_drift_detector()
        self.governance_load_monitor = create_governance_load_monitor()
        self.signal_reliability_monitor = create_signal_reliability_monitor()
        self.approval_burden_analyzer = create_approval_burden_analyzer()
        self.anomaly_detector = create_anomaly_detector()
        self.monitoring_reporter = create_monitoring_reporter()
        self.monitoring_store = create_monitoring_store(storage_path)
        
        # Status
        self.status = MonitoringStatus.STOPPED
        self.cycle_interval_seconds = 60  # Default: 1 minute cycles
        
        # Safety - ensure shadow mode
        self._shadow_mode = True
    
    async def start(self, interval_seconds: int = 60) -> None:
        """Start shadow monitoring."""
        self.cycle_interval_seconds = interval_seconds
        self.status = MonitoringStatus.RUNNING
        await self.cycle_monitor.start_monitoring()
    
    async def stop(self) -> None:
        """Stop shadow monitoring."""
        self.status = MonitoringStatus.STOPPED
        await self.cycle_monitor.stop_monitoring()
    
    async def run_cycle(self) -> ShadowCycleRecord:
        """Run a single shadow monitoring cycle."""
        if self.status != MonitoringStatus.RUNNING:
            raise RuntimeError("Shadow monitoring not running")
        
        start_time = time.time()
        
        # Generate synthetic signals (shadow mode - no real inputs)
        generator = ScenarioGenerator(random_seed=int(datetime.utcnow().timestamp()))
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        signals = generator.generate_signals(scenario, cycle_number=self.cycle_monitor.get_cycle_count() + 1)
        
        # Simulate governance processing
        cycle_data = await self._simulate_governance_cycle(signals)
        
        # Record cycle
        record = await self.cycle_monitor.record_cycle(cycle_data)
        
        # Update all monitors
        await self._update_monitors(record, cycle_data)
        
        # Store record
        self.monitoring_store.store_cycle(record)
        
        # Check for anomalies
        cycles = self.cycle_monitor.get_recent_cycles(20)
        anomalies = self.anomaly_detector.detect_anomalies(cycles)
        
        for anomaly in anomalies:
            self.monitoring_store.store_anomaly(anomaly)
        
        return record
    
    async def _simulate_governance_cycle(
        self,
        signals: List[Any],
    ) -> Dict[str, Any]:
        """Simulate a governance cycle in shadow mode."""
        # Simulate state
        state = {
            "domains": {
                d: {"performance": random.uniform(0.3, 0.8), "risk": random.uniform(0.1, 0.5)}
                for d in ["finance", "health", "operations", "strategy"]
            }
        }
        
        # Simulate recommendations
        recommendations = []
        for domain in state["domains"]:
            if random.random() < 0.3:  # 30% chance per domain
                recommendations.append({
                    "recommendation_id": f"rec_{datetime.utcnow().timestamp()}_{domain}",
                    "domain": domain,
                    "action_type": "improve_performance",
                    "priority": random.uniform(0.3, 0.9),
                })
        
        # Simulate execution intents (advisory only)
        execution_intents = []
        for rec in recommendations:
            if random.random() < 0.5:
                execution_intents.append({
                    "intent_id": f"intent_{datetime.utcnow().timestamp()}_{rec['domain']}",
                    "recommendation_id": rec["recommendation_id"],
                    "domain": rec["domain"],
                    "requires_approval": True,
                })
        
        # Simulate doctrine assessment
        alignment_score = random.uniform(-0.3, 0.8)
        confidence = random.uniform(0.4, 0.8)
        
        doctrine_flags = []
        if random.random() < 0.1:
            doctrine_flags.append("high_risk_domain")
        
        # Simulate tier
        tiers = [
            ApprovalTierLevel.TIER_0_MANUAL_ONLY,
            ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
        ]
        current_tier = random.choice(tiers)
        
        # Build cycle data
        cycle_data = {
            "duration_ms": (time.time() - start_time) * 1000,
            "signals_processed": len(signals),
            "signals_by_domain": {s.domain: 1 for s in signals},
            "recommendations_generated": len(recommendations),
            "recommendations_by_domain": {},
            "recommendations_by_urgency": {},
            "execution_intents_generated": len(execution_intents),
            "approval_required_count": sum(1 for i in execution_intents if i.get("requires_approval")),
            "doctrine_flags": doctrine_flags,
            "doctrine_conflicts": random.randint(0, 2),
            "alignment_score": alignment_score,
            "alignment_level": "aligned" if alignment_score > 0.3 else "neutral",
            "risk_flags": [],
            "risk_level": "low",
            "confidence_score": confidence,
            "confidence_delta": random.uniform(-0.05, 0.05),
            "current_tier": current_tier.value,
            "governance_load_score": len(recommendations) / 10.0,
            "pending_approvals": len(execution_intents),
            "state_snapshot": state,
        }
        
        # Aggregate recommendation data
        for rec in recommendations:
            domain = rec.get("domain", "unknown")
            priority = rec.get("priority", 0.5)
            
            cycle_data["recommendations_by_domain"][domain] = \
                cycle_data["recommendations_by_domain"].get(domain, 0) + 1
            
            urgency = "high" if priority > 0.7 else "normal"
            cycle_data["recommendations_by_urgency"][urgency] = \
                cycle_data["recommendations_by_urgency"].get(urgency, 0) + 1
        
        return cycle_data
    
    async def _update_monitors(
        self,
        record: ShadowCycleRecord,
        cycle_data: Dict[str, Any],
    ) -> None:
        """Update all monitors with cycle data."""
        # Update recommendation monitor
        recommendations = [
            {"recommendation_id": f"rec_{i}", "domain": d, "priority": p}
            for i, (d, p) in enumerate([
                (d, random.uniform(0.3, 0.9))
                for d in cycle_data.get("recommendations_by_domain", {}).keys()
            ])
        ]
        self.recommendation_monitor.record_recommendations(
            recommendations,
            record.cycle_number
        )
        
        # Update confidence drift detector
        self.confidence_drift_detector.record_confidence(
            record.confidence_score,
            record.cycle_number
        )
        
        # Update governance load monitor
        self.governance_load_monitor.record_cycle(record)
        
        # Update signal reliability monitor
        signals = [
            {"source": s.domain, "is_stale": False, "is_malformed": False}
            for s in []  # Would use real signals in production
        ]
        self.signal_reliability_monitor.record_signals(
            signals,
            record.cycle_number
        )
        
        # Update approval burden analyzer
        self.approval_burden_analyzer.record_approval_metrics(record)
    
    async def run_continuous(
        self,
        duration_minutes: Optional[int] = None,
        max_cycles: Optional[int] = None,
    ) -> None:
        """Run shadow monitoring continuously.
        
        Args:
            duration_minutes: How long to run (None = infinite)
            max_cycles: Maximum number of cycles (None = infinite)
        """
        await self.start()
        
        cycles_run = 0
        
        try:
            while True:
                # Check limits
                if duration_minutes and cycles_run >= duration_minutes:
                    break
                if max_cycles and cycles_run >= max_cycles:
                    break
                
                # Run cycle
                await self.run_cycle()
                cycles_run += 1
                
                # Wait for next cycle
                await asyncio.sleep(self.cycle_interval_seconds)
                
        finally:
            await self.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "status": self.status.value,
            "total_cycles": self.cycle_monitor.get_cycle_count(),
            "recent_cycles": len(self.cycle_monitor.get_recent_cycles(10)),
        }
    
    def get_recent_cycles(self, count: int = 10) -> List[ShadowCycleRecord]:
        """Get recent cycles."""
        return self.cycle_monitor.get_recent_cycles(count)
    
    def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get recommendation summary."""
        cycles = self.cycle_monitor.get_recent_cycles(100)
        return self.recommendation_monitor.get_summary(cycles).model_dump()
    
    def get_confidence_drift(self) -> Dict[str, Any]:
        """Get confidence drift information."""
        events = self.confidence_drift_detector.get_drift_events()
        stats = self.confidence_drift_detector.get_confidence_statistics(MonitoringWindow.ONE_DAY)
        
        return {
            "events": [e.model_dump() for e in events[-10:]],
            "statistics": stats,
        }
    
    def get_governance_load(self) -> Dict[str, Any]:
        """Get governance load information."""
        snapshot = self.governance_load_monitor.get_snapshot(MonitoringWindow.ONE_DAY)
        overload = self.governance_load_monitor.detect_overload()
        
        return {
            "snapshot": snapshot.model_dump(),
            "overload": overload,
        }
    
    def get_signal_reliability(self) -> Dict[str, Any]:
        """Get signal reliability information."""
        snapshot = self.signal_reliability_monitor.get_snapshot(MonitoringWindow.ONE_DAY)
        degradation = self.signal_reliability_monitor.detect_degradation()
        
        return {
            "snapshot": snapshot.model_dump(),
            "degradation": degradation,
        }
    
    def get_anomalies(self) -> List[Dict[str, Any]]:
        """Get detected anomalies."""
        anomalies = self.anomaly_detector.get_anomalies()
        return [a.model_dump() for a in anomalies]
    
    def generate_report(self, window: MonitoringWindow = MonitoringWindow.ONE_DAY) -> Dict[str, Any]:
        """Generate a monitoring report."""
        cycles = self.cycle_monitor.get_cycles_in_window(window)
        anomalies = self.anomaly_detector.get_anomalies()
        drift_events = self.confidence_drift_detector.get_drift_events()
        
        report = self.monitoring_reporter.generate_report(
            window=window,
            cycles=cycles,
            anomalies=anomalies,
            confidence_drift_events=drift_events,
        )
        
        # Store report
        self.monitoring_store.store_report(report)
        
        return report.model_dump()
    
    def generate_readiness_report(
        self,
        window: MonitoringWindow = MonitoringWindow.ONE_DAY,
        simulation_stability: float = 0.8,
    ) -> Dict[str, Any]:
        """Generate a readiness report."""
        cycles = self.cycle_monitor.get_cycles_in_window(window)
        
        # Get all snapshots
        recommendation_summary = self.recommendation_monitor.get_summary(cycles)
        governance_load = self.governance_load_monitor.get_snapshot(window)
        approval_burden = self.approval_burden_analyzer.get_snapshot(window)
        signal_reliability = self.signal_reliability_monitor.get_snapshot(window)
        
        assessment = self.monitoring_reporter.generate_readiness_assessment(
            window=window,
            cycles=cycles,
            recommendation_summary=recommendation_summary,
            governance_load=governance_load,
            approval_burden=approval_burden,
            signal_reliability=signal_reliability,
            simulation_stability=simulation_stability,
        )
        
        # Store assessment
        self.monitoring_store.store_assessment(assessment)
        
        return assessment.model_dump()


def create_shadow_controller(storage_path: Optional[str] = None) -> ShadowController:
    """Factory function to create a shadow controller."""
    return ShadowController(storage_path=storage_path)
