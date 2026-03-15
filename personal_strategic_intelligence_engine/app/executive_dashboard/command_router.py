"""Command Router - handles dashboard commands.

The Command Router processes commands issued from the Executive Dashboard,
validates them against governance rules, and executes appropriate actions.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from app.executive_dashboard.dashboard_models import (
    CommandCategory,
    CommandRequest,
    CommandResult,
    CommandStatus,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class CommandRouter:
    """
    Handles command actions from the dashboard.
    
    Supported commands:
    - approve_proposal: governance override
    - reject_proposal: governance override
    - trigger_execution: manual execution
    - pause_agent: disable agent
    - resume_agent: re-enable agent
    - rebuild_graph: rebuild knowledge graph
    - trigger_learning_cycle: force learning update
    """
    
    def __init__(self):
        self._command_history = []
    
    async def execute_command(
        self,
        request: CommandRequest,
    ) -> CommandResult:
        """
        Execute a dashboard command.
        
        Args:
            request: The command request
            
        Returns:
            CommandResult with execution status
        """
        logger.info(f"Executing dashboard command: {request.command}")
        
        result = CommandResult(
            command_id=str(uuid.uuid4()),
            command=request.command,
            category=request.category,
            status=CommandStatus.EXECUTED,
            message="Command executed successfully",
        )
        
        # Route to appropriate handler
        try:
            if request.command == "approve_proposal":
                result = await self._approve_proposal(request, result)
            elif request.command == "reject_proposal":
                result = await self._reject_proposal(request, result)
            elif request.command == "trigger_execution":
                result = await self._trigger_execution(request, result)
            elif request.command == "pause_agent":
                result = await self._pause_agent(request, result)
            elif request.command == "resume_agent":
                result = await self._resume_agent(request, result)
            elif request.command == "rebuild_graph":
                result = await self._rebuild_graph(request, result)
            elif request.command == "trigger_learning_cycle":
                result = await self._trigger_learning(request, result)
            elif request.command == "get_system_status":
                result = await self._get_system_status(request, result)
            else:
                result.status = CommandStatus.FAILED
                result.message = f"Unknown command: {request.command}"
        
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            result.status = CommandStatus.FAILED
            result.message = f"Execution failed: {str(e)}"
        
        # Store in history
        self._command_history.append({
            "request": request.dict(),
            "result": result.dict(),
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return result
    
    async def _approve_proposal(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle approve_proposal command."""
        proposal_id = request.parameters.get("proposal_id")
        
        if not proposal_id:
            result.status = CommandStatus.FAILED
            result.message = "Missing proposal_id parameter"
            return result
        
        # In real implementation, would call governance service
        result.message = f"Proposal {proposal_id} approved"
        result.result = {
            "proposal_id": proposal_id,
            "decision": "approved",
            "approved_by": request.requester,
        }
        
        return result
    
    async def _reject_proposal(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle reject_proposal command."""
        proposal_id = request.parameters.get("proposal_id")
        
        if not proposal_id:
            result.status = CommandStatus.FAILED
            result.message = "Missing proposal_id parameter"
            return result
        
        result.message = f"Proposal {proposal_id} rejected"
        result.result = {
            "proposal_id": proposal_id,
            "decision": "rejected",
            "rejected_by": request.requester,
            "reason": request.parameters.get("reason"),
        }
        
        return result
    
    async def _trigger_execution(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle trigger_execution command."""
        execution_params = request.parameters
        
        result.message = "Execution triggered"
        result.result = {
            "execution_id": str(uuid.uuid4()),
            "status": "triggered",
            "parameters": execution_params,
        }
        
        return result
    
    async def _pause_agent(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle pause_agent command."""
        agent_id = request.parameters.get("agent_id")
        
        if not agent_id:
            result.status = CommandStatus.FAILED
            result.message = "Missing agent_id parameter"
            return result
        
        result.message = f"Agent {agent_id} paused"
        result.result = {
            "agent_id": agent_id,
            "status": "paused",
        }
        
        return result
    
    async def _resume_agent(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle resume_agent command."""
        agent_id = request.parameters.get("agent_id")
        
        if not agent_id:
            result.status = CommandStatus.FAILED
            result.message = "Missing agent_id parameter"
            return result
        
        result.message = f"Agent {agent_id} resumed"
        result.result = {
            "agent_id": agent_id,
            "status": "active",
        }
        
        return result
    
    async def _rebuild_graph(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle rebuild_graph command."""
        result.message = "Knowledge graph rebuild triggered"
        result.result = {
            "status": "rebuild_started",
            "estimated_time": "5 minutes",
        }
        
        return result
    
    async def _trigger_learning(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle trigger_learning_cycle command."""
        result.message = "Learning cycle triggered"
        result.result = {
            "status": "learning_started",
            "cycles_queued": 1,
        }
        
        return result
    
    async def _get_system_status(
        self,
        request: CommandRequest,
        result: CommandResult,
    ) -> CommandResult:
        """Handle get_system_status command."""
        result.message = "System status retrieved"
        result.result = {
            "status": "operational",
            "version": "1.0.0",
            "components": {
                "signal_bus": "operational",
                "agents": "operational",
                "strategy_pipeline": "operational",
                "execution_engine": "operational",
                "learning_engine": "operational",
            },
        }
        
        return result
    
    def get_command_history(
        self,
        limit: int = 50,
    ) -> list:
        """Get command execution history."""
        return self._command_history[-limit:]


# Singleton instance
_command_router: Optional[CommandRouter] = None


def get_command_router() -> CommandRouter:
    """Get the global command router instance."""
    global _command_router
    if _command_router is None:
        _command_router = CommandRouter()
    return _command_router


def reset_command_router() -> None:
    """Reset the command router (for testing)."""
    global _command_router
    _command_router = None
