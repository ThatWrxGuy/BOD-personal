"""Execution Engine for executing approved actions."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.execution_record import ExecutionRecord, ExecutionHistory
from app.execution.action_types import ActionType, ExecutionStatus
from app.execution.action_validator import get_validator
from app.execution.action_router import get_router
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutionEngine:
    """Central controller for executing approved decisions."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.validator = get_validator()
        self.router = get_router()
    
    async def create_execution(
        self,
        action_type: str,
        payload: dict,
        decision_id: Optional[uuid.UUID] = None,
        approval_type: str = "MANUAL_APPROVAL_REQUIRED",
    ) -> ExecutionRecord:
        """Create a new execution record."""
        
        # Get risk score
        risk_score = self.validator.get_risk_score(action_type, payload)
        
        # Create execution record
        execution = ExecutionRecord(
            decision_id=decision_id,
            action_type=action_type,
            status=ExecutionStatus.PENDING,
            approval_type=approval_type,
            payload=payload,
            risk_score=risk_score,
            max_retries=3,
        )
        
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        
        logger.info(f"Created execution record: {execution.id}")
        
        return execution
    
    async def validate_execution(self, execution_id: uuid.UUID) -> tuple[bool, Optional[str]]:
        """Validate an execution before approval."""
        
        execution = await self.session.get(ExecutionRecord, execution_id)
        if not execution:
            return False, "Execution not found"
        
        # Validate action
        is_valid, error = self.validator.validate(
            execution.action_type,
            execution.payload or {},
        )
        
        if is_valid:
            execution.validated = True
            execution.validation_message = "Validated successfully"
        else:
            execution.validation_message = error
        
        await self.session.commit()
        
        return is_valid, error
    
    async def approve_execution(self, execution_id: uuid.UUID) -> ExecutionRecord:
        """Approve an execution for running."""
        
        execution = await self.session.get(ExecutionRecord, execution_id)
        if not execution:
            raise ValueError("Execution not found")
        
        if execution.status != ExecutionStatus.PENDING:
            raise ValueError(f"Cannot approve execution in status: {execution.status}")
        
        # Check if auto-approved
        if execution.approval_type == "AUTO_APPROVED":
            execution.status = ExecutionStatus.APPROVED
        else:
            # Require manual approval for higher risk
            if execution.risk_score > 0.7:
                raise ValueError("High risk actions require manual approval")
            execution.status = ExecutionStatus.APPROVED
        
        await self.session.commit()
        await self.session.refresh(execution)
        
        await self._add_history(execution, "APPROVED", "Execution approved")
        
        logger.info(f"Execution {execution_id} approved")
        
        return execution
    
    async def reject_execution(self, execution_id: uuid.UUID, reason: str) -> ExecutionRecord:
        """Reject an execution."""
        
        execution = await self.session.get(ExecutionRecord, execution_id)
        if not execution:
            raise ValueError("Execution not found")
        
        execution.status = ExecutionStatus.REJECTED
        execution.error_message = reason
        
        await self.session.commit()
        await self.session.refresh(execution)
        
        await self._add_history(execution, "REJECTED", reason)
        
        logger.info(f"Execution {execution_id} rejected: {reason}")
        
        return execution
    
    async def execute(self, execution_id: uuid.UUID) -> ExecutionRecord:
        """Execute an approved action."""
        
        execution = await self.session.get(ExecutionRecord, execution_id)
        if not execution:
            raise ValueError("Execution not found")
        
        if execution.status != ExecutionStatus.APPROVED:
            raise ValueError(f"Cannot execute execution in status: {execution.status}")
        
        # Update status to executing
        execution.status = ExecutionStatus.EXECUTING
        execution.execution_start = datetime.utcnow()
        
        await self.session.commit()
        
        await self._add_history(execution, "EXECUTING", "Execution started")
        
        logger.info(f"Executing action: {execution.action_type}")
        
        try:
            # Route and execute the action
            result = self.router.execute_action(
                execution.action_type,
                execution.payload or {},
            )
            
            if result.get("success"):
                execution.status = ExecutionStatus.COMPLETED
                execution.result = result
                execution.execution_end = datetime.utcnow()
                
                if execution.execution_start:
                    execution.execution_duration = (
                        execution.execution_end - execution.execution_start
                    ).total_seconds()
                
                await self._add_history(execution, "COMPLETED", "Execution completed successfully")
                
                logger.info(f"Execution {execution_id} completed successfully")
            else:
                raise Exception(result.get("error", "Unknown error"))
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.execution_end = datetime.utcnow()
            
            if execution.execution_start:
                execution.execution_duration = (
                    execution.execution_end - execution.execution_start
                ).total_seconds()
            
            # Check for retry
            if execution.retry_count < execution.max_retries:
                execution.status = ExecutionStatus.PENDING
                execution.retry_count += 1
                logger.warning(f"Execution {execution_id} failed, will retry ({execution.retry_count}/{execution.max_retries})")
            else:
                await self._add_history(execution, "FAILED", str(e))
                logger.error(f"Execution {execution_id} failed after {execution.retry_count} retries")
        
        await self.session.commit()
        await self.session.refresh(execution)
        
        return execution
    
    async def get_execution(self, execution_id: uuid.UUID) -> Optional[ExecutionRecord]:
        """Get an execution record."""
        return await self.session.get(ExecutionRecord, execution_id)
    
    async def list_pending(self) -> list[ExecutionRecord]:
        """List all pending executions."""
        result = await self.session.execute(
            select(ExecutionRecord)
            .where(ExecutionRecord.status == ExecutionStatus.PENDING)
            .order_by(ExecutionRecord.created_at)
        )
        return list(result.scalars().all())
    
    async def list_executing(self) -> list[ExecutionRecord]:
        """List all executing actions."""
        result = await self.session.execute(
            select(ExecutionRecord)
            .where(ExecutionRecord.status == ExecutionStatus.EXECUTING)
        )
        return list(result.scalars().all())
    
    async def get_history(self, limit: int = 50) -> list[ExecutionHistory]:
        """Get execution history."""
        result = await self.session.execute(
            select(ExecutionHistory)
            .order_by(ExecutionHistory.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def _add_history(
        self,
        execution: ExecutionRecord,
        status: str,
        details: str,
    ) -> None:
        """Add a history entry."""
        history = ExecutionHistory(
            execution_id=execution.id,
            action_type=execution.action_type,
            status=status,
            timestamp=datetime.utcnow(),
            details={"message": details},
        )
        
        self.session.add(history)
        await self.session.commit()


async def get_execution_engine(session: AsyncSession) -> ExecutionEngine:
    """Get an execution engine instance."""
    return ExecutionEngine(session)
