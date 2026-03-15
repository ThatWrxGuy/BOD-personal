"""Execution Engine - orchestrates all operational actions.

This module provides the main Execution Engine that orchestrates operational
actions based on approved strategy proposals from the Strategy Pipeline.
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_engine.execution_types import ExecutionStatus
from app.execution_engine.execution_models import (
    ActionType,
    ApprovalLevel,
    ExecutionRequest,
    ActionExecutionResult,
    SafetyValidationResult,
)
from app.execution_engine.action_router import ActionRouter, get_action_router
from app.execution_engine.safety_validator import SafetyValidator, get_safety_validator
from app.execution_engine.execution_logger import ExecutionLogger, get_execution_logger
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutionEngine:
    """
    The Execution Engine orchestrates all operational actions.
    
    Responsibilities:
    - Validate execution requests
    - Route requests to appropriate handlers
    - Track execution outcomes
    - Emit execution signals
    
    The engine ensures all actions are:
    - authorized (must come from approved proposals)
    - validated (safety checks pass)
    - logged (complete audit trail)
    - reversible where possible
    """
    
    def __init__(
        self,
        action_router: Optional[ActionRouter] = None,
        safety_validator: Optional[SafetyValidator] = None,
        execution_logger: Optional[ExecutionLogger] = None,
    ):
        self.action_router = action_router or get_action_router()
        self.safety_validator = safety_validator or get_safety_validator()
        self.execution_logger = execution_logger or get_execution_logger()
        
        # In-memory storage for execution requests
        self._executions: Dict[str, ExecutionRequest] = {}
    
    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ActionExecutionResult:
        """
        Execute an approved action.
        
        Args:
            request: The execution request
            
        Returns:
            Execution result
        """
        start_time = time.time()
        
        logger.info(f"Starting execution: {request.id} - {request.action_type}")
        
        # Step 1: Validate execution request
        validation_result = await self.safety_validator.validate(request)
        
        if not validation_result.is_valid:
            logger.error(f"Execution validation failed: {validation_result.errors}")
            request.status = ExecutionStatus.REJECTED
            
            return ActionExecutionResult(
                execution_id=request.id,
                status=ExecutionStatus.FAILED,
                action_taken="validation",
                result_data={},
                success=False,
                error="Validation failed: " + "; ".join(validation_result.errors),
                error_details={"validation_errors": validation_result.errors},
            )
        
        # Update status to validated
        request.status = ExecutionStatus.VALIDATED
        request.validated_at = datetime.utcnow()
        self._executions[request.id] = request
        
        # Step 2: Check approval status
        if request.approved_by == "pending":
            logger.warning(f"Execution {request.id} not approved, rejecting")
            request.status = ExecutionStatus.REJECTED
            
            return ActionExecutionResult(
                execution_id=request.id,
                status=ExecutionStatus.REJECTED,
                action_taken="approval_check",
                result_data={},
                success=False,
                error="Execution not approved",
            )
        
        # Update status to approved
        request.status = ExecutionStatus.APPROVED
        request.approved_at = datetime.utcnow()
        
        # Step 3: Route to appropriate handler
        action_key = request.action_type.value if hasattr(request.action_type, 'value') else request.action_type
        logger.info(f"Routing execution {request.id} to handler for {action_key}")
        
        try:
            handler = self.action_router.get_handler(request.action_type)
            
            if handler is None:
                raise ValueError(f"No handler found for action type: {request.action_type}")
            
            # Execute the action
            request.status = ExecutionStatus.EXECUTING
            request.executed_at = datetime.utcnow()
            
            result = await handler.execute(request)
            
            # Update request with results
            request.status = ExecutionStatus.COMPLETED
            request.result = result.result_data
            request.completed_at = datetime.utcnow()
            
            execution_time = (time.time() - start_time) * 1000  # ms
            request.execution_duration_ms = execution_time
            
            logger.info(f"Execution {request.id} completed successfully in {execution_time:.2f}ms")
            
            # Log the execution
            await self.execution_logger.log_execution(request, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Execution {request.id} failed: {str(e)}")
            
            request.status = ExecutionStatus.FAILED
            request.error_message = str(e)
            request.completed_at = datetime.utcnow()
            
            execution_time = (time.time() - start_time) * 1000
            request.execution_duration_ms = execution_time
            
            # Log the failure
            await self.execution_logger.log_failure(request, str(e))
            
            return ActionExecutionResult(
                execution_id=request.id,
                status=ExecutionStatus.FAILED,
                action_taken="error",
                result_data={},
                success=False,
                error=str(e),
            )
    
    async def create_execution_request(
        self,
        proposal_id: str,
        action_type: ActionType,
        parameters: Dict[str, Any],
        risk_level: str = "medium",
        governance_decision_id: Optional[str] = None,
        approved_by: str = "governance",
    ) -> ExecutionRequest:
        """
        Create an execution request from an approved proposal.
        
        Args:
            proposal_id: ID of the approved proposal
            action_type: Type of action to execute
            parameters: Action parameters
            risk_level: Risk level of the action
            governance_decision_id: ID of the governance decision
            approved_by: Who approved this execution
            
        Returns:
            Created execution request
        """
        # Determine approval level based on risk
        approval_level = ApprovalLevel.MANUAL
        if risk_level == "low":
            approval_level = ApprovalLevel.AUTOMATIC
        elif risk_level == "critical":
            approval_level = ApprovalLevel.CEO
        
        request = ExecutionRequest(
            proposal_id=proposal_id,
            action_type=action_type,
            parameters=parameters,
            risk_level=risk_level,
            approved_by=approved_by,
            approval_level=approval_level,
            governance_decision_id=governance_decision_id,
        )
        
        self._executions[request.id] = request
        
        logger.info(f"Created execution request: {request.id} for proposal {proposal_id}")
        
        return request
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRequest]:
        """Get an execution request by ID."""
        return self._executions.get(execution_id)
    
    def get_executions_by_proposal(self, proposal_id: str) -> List[ExecutionRequest]:
        """Get all executions for a proposal."""
        return [
            e for e in self._executions.values()
            if e.proposal_id == proposal_id
        ]
    
    def get_executions_by_status(
        self,
        status: ExecutionStatus,
    ) -> List[ExecutionRequest]:
        """Get all executions with a specific status."""
        return [
            e for e in self._executions.values()
            if e.status == status
        ]
    
    def get_pending_executions(self) -> List[ExecutionRequest]:
        """Get all pending executions."""
        return self.get_executions_by_status(ExecutionStatus.PENDING)
    
    def get_active_executions(self) -> List[ExecutionRequest]:
        """Get all active (executing) executions."""
        return self.get_executions_by_status(ExecutionStatus.EXECUTING)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an execution if not yet executed."""
        request = self._executions.get(execution_id)
        
        if request is None:
            return False
        
        if request.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            logger.warning(f"Cannot cancel execution {execution_id} in status: {request.status}")
            return False
        
        request.status = ExecutionStatus.CANCELLED
        logger.info(f"Cancelled execution: {execution_id}")
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        executions = list(self._executions.values())
        
        if not executions:
            return {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "pending": 0,
                "executing": 0,
            }
        
        total = len(executions)
        completed = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)
        pending = sum(1 for e in executions if e.status == ExecutionStatus.PENDING)
        executing = sum(1 for e in executions if e.status == ExecutionStatus.EXECUTING)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "executing": executing,
            "success_rate": completed / total if total > 0 else 0,
        }


# Singleton instance
_execution_engine: Optional[ExecutionEngine] = None


def get_execution_engine() -> ExecutionEngine:
    """Get the global execution engine instance."""
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine


def reset_execution_engine() -> None:
    """Reset the execution engine (for testing)."""
    global _execution_engine
    _execution_engine = None
