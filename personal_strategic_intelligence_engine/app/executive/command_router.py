"""Command router - routes executive commands to appropriate subsystems."""
from typing import Dict, Any, Optional

from app.executive.command_types import ExecutiveCommand, CommandCategory
from app.core.logging import get_logger

logger = get_logger(__name__)


class CommandRouter:
    """Routes executive commands to correct subsystems."""
    
    def __init__(self):
        self.handlers = {
            CommandCategory.STRATEGIC: self._handle_strategic,
            CommandCategory.GOAL: self._handle_goal,
            CommandCategory.RISK: self._handle_risk,
            CommandCategory.FINANCIAL: self._handle_financial,
            CommandCategory.AUTONOMY: self._handle_autonomy,
            CommandCategory.HABIT: self._handle_habit,
            CommandCategory.SYSTEM: self._handle_system,
        }
    
    async def route(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Route command to appropriate handler."""
        
        handler = self.handlers.get(command.category)
        
        if not handler:
            return {"error": f"No handler for category: {command.category}"}
        
        return await handler(command)
    
    async def _handle_strategic(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle strategic commands."""
        
        if command.command_type == "recalculate_strategy":
            return {"status": "triggered", "action": "recalculate_strategy"}
        
        return {"status": "unknown_command", "type": command.command_type}
    
    async def _handle_goal(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle goal commands."""
        
        if command.command_type == "create_goal":
            return {"status": "created", "target": command.target}
        elif command.command_type == "archive_goal":
            return {"status": "archived", "target": command.target}
        elif command.command_type == "promote_priority":
            return {"status": "promoted", "target": command.target}
        elif command.command_type == "demote_priority":
            return {"status": "demoted", "target": command.target}
        
        return {"status": "unknown_command", "type": command.command_type}
    
    async def _handle_risk(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle risk commands."""
        
        return {"status": "acknowledged", "type": command.command_type}
    
    async def _handle_financial(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle financial commands."""
        
        return {"status": "acknowledged", "type": command.command_type}
    
    async def _handle_autonomy(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle autonomy commands."""
        
        return {"status": "acknowledged", "type": command.command_type}
    
    async def _handle_habit(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle habit commands."""
        
        return {"status": "acknowledged", "type": command.command_type}
    
    async def _handle_system(self, command: ExecutiveCommand) -> Dict[str, Any]:
        """Handle system commands."""
        
        return {"status": "acknowledged", "type": command.command_type}


async def get_command_router() -> CommandRouter:
    """Get command router instance."""
    return CommandRouter()
