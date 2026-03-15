"""Shadow Monitoring Tests.

Tests for the Shadow Monitoring & Long-Horizon Observation Layer.
"""
import pytest
from datetime import datetime, timedelta

from app.shadow_monitoring import (
    SHADOW_MODE,
    LIVE_EXECUTION_ENABLED,
    AUTO_EXECUTION_ENABLED,
    EXECUTION_MODE,
    create_shadow_controller,
    create_cycle_monitor,
    create_recommendation_monitor,
    create_confidence_drift_detector,
    create_governance_load_monitor,
    create_signal_reliability_monitor,
    create_approval_burden_analyzer,
    create_anomaly_detector,
    create_monitoring_reporter,
    MonitoringWindow,
    MonitoringStatus,
    SeverityLevel,
    AnomalyType,
)


class TestShadowMonitoringSafety:
    """Test that shadow monitoring enforces safety constraints."""
    
    def test_shadow_mode_enabled(self):
        """Test that SHADOW_MODE is always True."""
        assert SHADOW_MODE is True
    
    def test_live_execution_disabled(self):
        """Test that LIVE_EXECUTION_ENABLED is always False."""
        assert LIVE_EXECUTION_ENABLED is False
    
    def test_auto_execution_disabled(self):
        """Test that AUTO_EXECUTION_ENABLED is always False."""
        assert AUTO_EXECUTION_ENABLED is False
    
    def test_execution_mode_disabled(self):
        """Test that EXECUTION_MODE is disabled."""
        assert EXECUTION_MODE == "disabled"


class TestCycleMonitor:
    """Test cycle monitoring functionality."""
    
    def test_create_cycle_monitor(self):
        """Test creating a cycle monitor."""
        monitor = create_cycle_monitor()
        assert monitor is not None
        assert monitor.get_status() == MonitoringStatus.STOPPED
    
    def test_record_cycle(self):
        """Test recording a cycle."""
        import asyncio
        monitor = create_cycle_monitor()
        
        cycle_data = {
            "cycle_id": "test_1",
            "signals_processed": 10,
            "recommendations_generated": 3,
            "execution_intents_generated": 2,
            "confidence_score": 0.7,
            "governance_load_score": 0.3,
        }
        
        asyncio.run(monitor.start_monitoring())
        record = asyncio.run(monitor.record_cycle(cycle_data))
        
        assert record is not None
        assert record.signals_processed == 10
        assert record.recommendations_generated == 3
    
    def test_get_recent_cycles(self):
        """Test getting recent cycles."""
        monitor = create_cycle_monitor()
        
        # Add some cycles
        for i in range(5):
            cycle_data = {"cycle_id": f"test_{i}", "signals_processed": i}
            asyncio.run(monitor.record_cycle(cycle_data))
        
        recent = monitor.get_recent_cycles(3)
        assert len(recent) == 3


class TestRecommendationMonitor:
    """Test recommendation monitoring functionality."""
    
    def test_create_recommendation_monitor(self):
        """Test creating a recommendation monitor."""
        monitor = create_recommendation_monitor()
        assert monitor is not None
    
    def test_record_recommendations(self):
        """Test recording recommendations."""
        monitor = create_recommendation_monitor()
        
        recommendations = [
            {"recommendation_id": "rec_1", "domain": "finance", "priority": 0.8},
            {"recommendation_id": "rec_2", "domain": "health", "priority": 0.5},
        ]
        
        monitor.record_recommendations(recommendations, 1)
        
        summary = monitor.get_summary([])
        assert summary.total_recommendations == 2


class TestConfidenceDriftDetector:
    """Test confidence drift detection."""
    
    def test_create_detector(self):
        """Test creating a detector."""
        detector = create_confidence_drift_detector()
        assert detector is not None
    
    def test_record_confidence(self):
        """Test recording confidence values."""
        detector = create_confidence_drift_detector()
        
        detector.record_confidence(0.7, 1)
        detector.record_confidence(0.6, 2)
        
        stats = detector.get_confidence_statistics(MonitoringWindow.ONE_DAY)
        assert "avg" in stats


class TestGovernanceLoadMonitor:
    """Test governance load monitoring."""
    
    def test_create_monitor(self):
        """Test creating a monitor."""
        monitor = create_governance_load_monitor()
        assert monitor is not None
    
    def test_record_cycle(self):
        """Test recording cycle load."""
        from app.shadow_monitoring.monitoring_models import ShadowCycleRecord
        
        monitor = create_governance_load_monitor()
        
        cycle = ShadowCycleRecord(
            cycle_id="test_1",
            cycle_number=1,
            governance_load_score=0.5,
            doctrine_flags=["flag1"],
            risk_flags=["risk1"],
        )
        
        monitor.record_cycle(cycle)
        
        snapshot = monitor.get_snapshot(MonitoringWindow.ONE_DAY)
        assert snapshot.avg_governance_load == 0.5


class TestAnomalyDetector:
    """Test anomaly detection."""
    
    def test_create_detector(self):
        """Test creating a detector."""
        detector = create_anomaly_detector()
        assert detector is not None
    
    def test_detect_anomalies(self):
        """Test detecting anomalies."""
        from app.shadow_monitoring.monitoring_models import ShadowCycleRecord
        
        detector = create_anomaly_detector()
        
        # Create cycles with high recommendations (spike)
        cycles = []
        for i in range(15):
            cycle = ShadowCycleRecord(
                cycle_id=f"test_{i}",
                cycle_number=i,
                recommendations_generated=50 if i > 10 else 5,  # Spike
                confidence_score=0.5,
                governance_load_score=0.3,
                doctrine_conflicts=0,
            )
            cycles.append(cycle)
        
        anomalies = detector.detect_anomalies(cycles)
        assert len(anomalies) > 0


class TestMonitoringReporter:
    """Test monitoring reporting."""
    
    def test_create_reporter(self):
        """Test creating a reporter."""
        reporter = create_monitoring_reporter()
        assert reporter is not None
    
    def test_generate_report(self):
        """Test generating a report."""
        from app.shadow_monitoring.monitoring_models import (
            ShadowCycleRecord,
            MonitoringAnomaly,
            ConfidenceDriftEvent,
        )
        
        reporter = create_monitoring_reporter()
        
        cycles = [
            ShadowCycleRecord(
                cycle_id="test_1",
                cycle_number=1,
                signals_processed=10,
                recommendations_generated=3,
                execution_intents_generated=2,
                confidence_score=0.7,
            )
        ]
        
        anomalies = []
        drift_events = []
        
        report = reporter.generate_report(
            window=MonitoringWindow.ONE_DAY,
            cycles=cycles,
            anomalies=anomalies,
            confidence_drift_events=drift_events,
        )
        
        assert report.total_cycles == 1


class TestShadowController:
    """Test shadow controller."""
    
    def test_create_controller(self):
        """Test creating a controller."""
        controller = create_shadow_controller()
        assert controller is not None
    
    def test_get_status(self):
        """Test getting controller status."""
        controller = create_shadow_controller()
        status = controller.get_status()
        
        assert "status" in status
        assert status["status"] == "stopped"
    
    def test_generate_report(self):
        """Test generating monitoring report."""
        controller = create_shadow_controller()
        report = controller.generate_report(MonitoringWindow.ONE_DAY)
        
        assert "total_cycles" in report


class TestShadowMonitoringIntegration:
    """Integration tests for shadow monitoring."""
    
    @pytest.mark.asyncio
    async def test_shadow_cycle_execution(self):
        """Test running a shadow monitoring cycle."""
        controller = create_shadow_controller()
        
        await controller.start()
        
        # Run a cycle
        record = await controller.run_cycle()
        
        assert record is not None
        assert record.cycle_number == 1
        
        # Verify no real execution happened
        assert LIVE_EXECUTION_ENABLED is False
    
    def test_monitoring_end_to_end(self):
        """Test complete monitoring flow."""
        controller = create_shadow_controller()
        
        # Run async operations
        import asyncio
        
        async def run_test():
            await controller.start()
            await controller.run_cycle()
            await controller.run_cycle()
            await controller.stop()
        
        asyncio.run(run_test())
        
        # Check status
        status = controller.get_status()
        assert status["total_cycles"] == 2
