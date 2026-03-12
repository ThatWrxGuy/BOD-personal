"""Drift Detector - Detects plan drift in active executions."""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.intelligence.planning.execution_models import ExecutionProgram, ExecutionTask
from app.intelligence.planning.replanning_models import (
    PlanDriftSignal,
    DriftType,
    TriggerSeverity,
)


class DriftDetector:
    """Detects drift in active execution programs."""
    
    def __init__(self):
        self.drift_signals: Dict[str, List[PlanDriftSignal]] = {}
    
    def detect_drift(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
        current_state: Dict,
    ) -> List[PlanDriftSignal]:
        """Detect drift in execution."""
        
        signals = []
        
        # Check schedule drift
        signals.extend(self._detect_schedule_drift(program, tasks))
        
        # Check performance drift
        signals.extend(self._detect_performance_drift(program, tasks))
        
        # Check risk drift
        signals.extend(self._detect_risk_drift(current_state))
        
        # Check for opportunities
        signals.extend(self._detect_opportunity_shift(current_state))
        
        # Store signals
        self.drift_signals[program.id] = signals
        
        return signals
    
    def _detect_schedule_drift(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
    ) -> List[PlanDriftSignal]:
        """Detect schedule-related drift."""
        
        signals = []
        
        # Calculate expected progress based on time
        now = datetime.utcnow()
        days_active = (now - program.created_at).days
        
        if days_active < 1:
            return signals
        
        expected_progress = min(100, days_active * 10)  # Assume 10% per day
        actual_progress = program.progress_percent
        
        drift_percent = expected_progress - actual_progress
        
        if drift_percent > 20:
            severity = TriggerSeverity.CRITICAL if drift_percent > 40 else TriggerSeverity.HIGH
            
            signal = PlanDriftSignal(
                id=str(uuid.uuid4())[:8],
                execution_program_id=program.id,
                plan_id=program.plan_id,
                drift_type=DriftType.SCHEDULE_DRIFT,
                severity=severity,
                description=f"Progress {actual_progress:.0f}% vs expected {expected_progress:.0f}%",
                expected_value=expected_progress,
                actual_value=actual_progress,
                deviation_percent=drift_percent,
            )
            signals.append(signal)
        
        # Check for overdue tasks
        overdue_count = sum(1 for t in tasks if t.status.value == "pending" and t.due_at and now > t.due_at)
        
        if overdue_count > 0:
            severity = TriggerSeverity.HIGH if overdue_count > 2 else TriggerSeverity.MEDIUM
            
            signal = PlanDriftSignal(
                id=str(uuid.uuid4())[:8],
                execution_program_id=program.id,
                plan_id=program.plan_id,
                drift_type=DriftType.SCHEDULE_DRIFT,
                severity=severity,
                description=f"{overdue_count} tasks overdue",
                impacted_tasks=[t.id for t in tasks if t.status.value == "pending"],
            )
            signals.append(signal)
        
        return signals
    
    def _detect_performance_drift(
        self,
        program: ExecutionProgram,
        tasks: List[ExecutionTask],
    ) -> List[PlanDriftSignal]:
        """Detect performance drift."""
        
        signals = []
        
        # Check blocked tasks
        blocked = [t for t in tasks if t.status.value == "blocked"]
        
        if len(blocked) >= 2:
            severity = TriggerSeverity.CRITICAL if len(blocked) >= 3 else TriggerSeverity.HIGH
            
            signal = PlanDriftSignal(
                id=str(uuid.uuid4())[:8],
                execution_program_id=program.id,
                plan_id=program.plan_id,
                drift_type=DriftType.PERFORMANCE_DRIFT,
                severity=severity,
                description=f"{len(blocked)} tasks are blocked",
                impacted_tasks=[t.id for t in blocked],
            )
            signals.append(signal)
        
        # Check failed tasks
        failed = [t for t in tasks if t.status.value == "failed"]
        
        if failed:
            severity = TriggerSeverity.CRITICAL if len(failed) > 1 else TriggerSeverity.HIGH
            
            signal = PlanDriftSignal(
                id=str(uuid.uuid4())[:8],
                execution_program_id=program.id,
                plan_id=program.plan_id,
                drift_type=DriftType.PERFORMANCE_DRIFT,
                severity=severity,
                description=f"{len(failed)} tasks have failed",
                impacted_tasks=[t.id for t in failed],
            )
            signals.append(signal)
        
        return signals
    
    def _detect_risk_drift(
        self,
        current_state: Dict,
    ) -> List[PlanDriftSignal]:
        """Detect risk-related drift."""
        
        signals = []
        
        # Check for risk spikes
        risk_level = current_state.get("overall_risk", 5.0)
        
        if risk_level > 8.0:
            severity = TriggerSeverity.CRITICAL if risk_level > 9.0 else TriggerSeverity.HIGH
            
            signal = PlanDriftSignal(
                id=str(uuid.uuid4())[:8],
                execution_program_id=current_state.get("program_id", ""),
                plan_id="",
                drift_type=DriftType.RISK_DRIFT,
                severity=severity,
                description=f"Risk level elevated to {risk_level}/10",
                expected_value=5.0,
                actual_value=risk_level,
            )
            signals.append(signal)
        
        # Check domain-specific risks
        domain_risks = current_state.get("domain_risks", {})
        
        for domain, risk in domain_risks.items():
            if risk > 7.0:
                signal = PlanDriftSignal(
                    id=str(uuid.uuid4())[:8],
                    execution_program_id=current_state.get("program_id", ""),
                    plan_id="",
                    drift_type=DriftType.RISK_DRIFT,
                    severity=TriggerSeverity.HIGH,
                    description=f"Domain {domain} risk elevated to {risk}/10",
                )
                signals.append(signal)
        
        return signals
    
    def _detect_opportunity_shift(
        self,
        current_state: Dict,
    ) -> List[PlanDriftSignal]:
        """Detect new opportunities."""
        
        signals = []
        
        opportunities = current_state.get("opportunities", [])
        
        if opportunities:
            signal = PlanDriftSignal(
                id=str(uuid.uuid4())[:8],
                execution_program_id=current_state.get("program_id", ""),
                plan_id="",
                drift_type=DriftType.OPPORTUNITY_SHIFT,
                severity=TriggerSeverity.MEDIUM,
                description=f"New opportunity: {opportunities[0]}",
            )
            signals.append(signal)
        
        return signals
    
    def get_signals(
        self,
        program_id: str,
    ) -> List[PlanDriftSignal]:
        """Get drift signals for a program."""
        
        return self.drift_signals.get(program_id, [])
    
    def get_drift_summary(
        self,
        program_id: str,
    ) -> Dict:
        """Get summary of drift."""
        
        signals = self.get_signals(program_id)
        
        if not signals:
            return {
                "total": 0,
                "health": "healthy",
            }
        
        critical = sum(1 for s in signals if s.severity == TriggerSeverity.CRITICAL)
        high = sum(1 for s in signals if s.severity == TriggerSeverity.HIGH)
        
        health = "healthy"
        if critical > 0:
            health = "critical"
        elif high > 0:
            health = "degraded"
        elif len(signals) > 0:
            health = "concerning"
        
        return {
            "total": len(signals),
            "critical": critical,
            "high": high,
            "health": health,
        }


_detector: Optional[DriftDetector] = None


def get_drift_detector() -> DriftDetector:
    """Get the global drift detector."""
    global _detector
    if _detector is None:
        _detector = DriftDetector()
    return _detector
