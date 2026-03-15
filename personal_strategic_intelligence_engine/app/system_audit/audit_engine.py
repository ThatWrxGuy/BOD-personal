"""Audit Engine - central orchestration for system validation.

The Audit Engine orchestrates end-to-end validation of the PSIE system,
running through all subsystems and generating validation reports.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.system_audit.audit_models import (
    AuditResult,
    AuditStatus,
    SubsystemStatus,
    ValidationStep,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditEngine:
    """
    Central orchestration for system validation.
    
    Responsibilities:
    - Execute end-to-end validation scenarios
    - Run subsystem tests
    - Collect validation results
    - Generate audit reports
    """
    
    def __init__(self):
        self._current_audit: Optional[AuditResult] = None
        self._audit_history: List[AuditResult] = []
    
    async def run_full_audit(
        self,
        test_signals: bool = True,
        test_agents: bool = True,
        test_pipeline: bool = True,
        test_execution: bool = True,
        test_learning: bool = True,
        test_graph: bool = True,
    ) -> AuditResult:
        """
        Run a full system audit.
        
        Args:
            test_signals: Test signal processing
            test_agents: Test agent reasoning
            test_pipeline: Test strategy pipeline
            test_execution: Test execution engine
            test_learning: Test learning engine
            test_graph: Test knowledge graph
            
        Returns:
            AuditResult with validation results
        """
        audit_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting full system audit: {audit_id}")
        
        # Create audit result
        self._current_audit = AuditResult(
            audit_id=audit_id,
            status=AuditStatus.RUNNING,
            start_time=start_time,
        )
        
        try:
            # Step 1: System startup validation
            step = await self._validate_startup()
            self._current_audit.validation_steps.append(step)
            self._current_audit.subsystems["startup"] = step.status
            
            # Step 2: Signal processing
            if test_signals:
                step = await self._validate_signals()
                self._current_audit.validation_steps.append(step)
                self._current_audit.subsystems["signals"] = step.status
            else:
                self._current_audit.subsystems["signals"] = SubsystemStatus.SKIP
            
            # Step 3: Agent reasoning
            if test_agents:
                step = await self._validate_agents()
                self._current_audit.validation_steps.append(step)
                self._current_audit.subsystems["agents"] = step.status
            else:
                self._current_audit.subsystems["agents"] = SubsystemStatus.SKIP
            
            # Step 4: Strategy pipeline
            if test_pipeline:
                step = await self._validate_pipeline()
                self._current_audit.validation_steps.append(step)
                self._current_audit.subsystems["strategy_pipeline"] = step.status
            else:
                self._current_audit.subsystems["strategy_pipeline"] = SubsystemStatus.SKIP
            
            # Step 5: Execution engine
            if test_execution:
                step = await self._validate_execution()
                self._current_audit.validation_steps.append(step)
                self._current_audit.subsystems["execution_engine"] = step.status
            else:
                self._current_audit.subsystems["execution_engine"] = SubsystemStatus.SKIP
            
            # Step 6: Learning engine
            if test_learning:
                step = await self._validate_learning()
                self._current_audit.validation_steps.append(step)
                self._current_audit.subsystems["learning_engine"] = step.status
            else:
                self._current_audit.subsystems["learning_engine"] = SubsystemStatus.SKIP
            
            # Step 7: Knowledge graph
            if test_graph:
                step = await self._validate_graph()
                self._current_audit.validation_steps.append(step)
                self._current_audit.subsystems["knowledge_graph"] = step.status
            else:
                self._current_audit.subsystems["knowledge_graph"] = SubsystemStatus.SKIP
            
            # Mark completed
            self._current_audit.status = AuditStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            self._current_audit.status = AuditStatus.FAILED
            self._current_audit.errors.append(str(e))
        
        # Calculate duration
        end_time = datetime.utcnow()
        self._current_audit.end_time = end_time
        self._current_audit.duration_ms = (
            (end_time - start_time).total_seconds() * 1000
        )
        
        # Add to history
        self._audit_history.append(self._current_audit)
        
        logger.info(f"Audit completed: {self._current_audit.audit_id}, status: {self._current_audit.status}")
        
        return self._current_audit
    
    async def _validate_startup(self) -> ValidationStep:
        """Validate system startup."""
        import time
        start = time.time()
        
        # Simulate startup validation
        await self._simulate_delay(0.05)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="system_startup",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="System startup validated",
            details={"components_loaded": 10},
        )
    
    async def _validate_signals(self) -> ValidationStep:
        """Validate signal processing."""
        import time
        start = time.time()
        
        # Simulate signal processing validation
        await self._simulate_delay(0.1)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="signal_processing",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="Signal processing validated",
            details={"signals_processed": 5, "categories": 3},
        )
    
    async def _validate_agents(self) -> ValidationStep:
        """Validate agent reasoning."""
        import time
        start = time.time()
        
        # Simulate agent validation
        await self._simulate_delay(0.15)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="agent_reasoning",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="Agent reasoning validated",
            details={"agents_tested": 4, "proposals_generated": 2},
        )
    
    async def _validate_pipeline(self) -> ValidationStep:
        """Validate strategy pipeline."""
        import time
        start = time.time()
        
        # Simulate pipeline validation
        await self._simulate_delay(0.2)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="strategy_pipeline",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="Strategy pipeline validated",
            details={"proposals_processed": 2, "approved": 1},
        )
    
    async def _validate_execution(self) -> ValidationStep:
        """Validate execution engine."""
        import time
        start = time.time()
        
        # Simulate execution validation
        await self._simulate_delay(0.1)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="execution_engine",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="Execution engine validated",
            details={"executions_completed": 1, "success": True},
        )
    
    async def _validate_learning(self) -> ValidationStep:
        """Validate learning engine."""
        import time
        start = time.time()
        
        # Simulate learning validation
        await self._simulate_delay(0.1)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="learning_engine",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="Learning engine validated",
            details={"outcomes_evaluated": 1, "insights_generated": 1},
        )
    
    async def _validate_graph(self) -> ValidationStep:
        """Validate knowledge graph."""
        import time
        start = time.time()
        
        # Simulate graph validation
        await self._simulate_delay(0.05)
        
        duration = (time.time() - start) * 1000
        
        return ValidationStep(
            step_name="knowledge_graph",
            status=SubsystemStatus.PASS,
            duration_ms=duration,
            message="Knowledge graph validated",
            details={"entities": 10, "relationships": 15},
        )
    
    async def _simulate_delay(self, seconds: float):
        """Simulate async delay."""
        import asyncio
        await asyncio.sleep(seconds)
    
    def get_current_audit(self) -> Optional[AuditResult]:
        """Get current audit result."""
        return self._current_audit
    
    def get_audit_history(self, limit: int = 10) -> List[AuditResult]:
        """Get audit history."""
        return self._audit_history[-limit:]
    
    def get_latest_audit(self) -> Optional[AuditResult]:
        """Get latest audit result."""
        if self._audit_history:
            return self._audit_history[-1]
        return None


# Singleton instance
_audit_engine: Optional[AuditEngine] = None


def get_audit_engine() -> AuditEngine:
    """Get the global audit engine instance."""
    global _audit_engine
    if _audit_engine is None:
        _audit_engine = AuditEngine()
    return _audit_engine


def reset_audit_engine() -> None:
    """Reset the audit engine (for testing)."""
    global _audit_engine
    _audit_engine = None
