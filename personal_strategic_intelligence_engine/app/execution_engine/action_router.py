"""Action Router - routes execution requests to appropriate handlers.

The Action Router determines which handler should process an execution request
based on the action type.
"""
from typing import Any, Dict, Optional

from app.execution_engine.execution_models import ActionType, ExecutionRequest
from app.execution_engine.execution_handlers import (
    BaseExecutionHandler,
    TradeExecutionHandler,
    PortfolioAdjustmentHandler,
    NotificationHandler,
    SystemActionHandler,
    ResearchHandler,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ActionRouter:
    """
    Routes execution requests to the correct handler.
    
    Supported action categories:
    - TRADE_EXECUTION: Execute market trades
    - PORTFOLIO_ADJUSTMENT: Adjust asset allocations
    - ALERT_NOTIFICATION: Send alerts to user
    - SYSTEM_ACTION: Trigger internal automation
    - REBALANCING: Portfolio rebalancing
    - HEDGING: Hedging operations
    - RESEARCH: Research tasks
    - ANALYSIS: Analysis tasks
    """
    
    def __init__(self):
        self._handlers: Dict[str, BaseExecutionHandler] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default handlers for all action types."""
        self.register_handler(ActionType.TRADE_EXECUTION, TradeExecutionHandler())
        self.register_handler(ActionType.PORTFOLIO_ADJUSTMENT, PortfolioAdjustmentHandler())
        self.register_handler(ActionType.ALERT_NOTIFICATION, NotificationHandler())
        self.register_handler(ActionType.SYSTEM_ACTION, SystemActionHandler())
        self.register_handler(ActionType.REBALANCING, PortfolioAdjustmentHandler())
        self.register_handler(ActionType.HEDGING, PortfolioAdjustmentHandler())
        self.register_handler(ActionType.RESEARCH, ResearchHandler())
        self.register_handler(ActionType.ANALYSIS, ResearchHandler())
    
    def register_handler(
        self,
        action_type: ActionType,
        handler: BaseExecutionHandler,
    ) -> None:
        """Register a handler for an action type."""
        self._handlers[action_type.value] = handler
        logger.debug(f"Registered handler for action type: {action_type.value}")
    
    def get_handler(self, action_type: ActionType) -> Optional[BaseExecutionHandler]:
        """Get the handler for an action type."""
        # Handle both Enum and string values
        action_key = action_type.value if hasattr(action_type, 'value') else action_type
        handler = self._handlers.get(action_key)
        
        if handler is None:
            action_key = action_type.value if hasattr(action_type, 'value') else action_type
            logger.warning(f"No handler found for action type: {action_key}")
        
        return handler
    
    def get_handler_by_string(self, action_type: str) -> Optional[BaseExecutionHandler]:
        """Get handler by string action type."""
        try:
            action_enum = ActionType(action_type)
            return self.get_handler(action_enum)
        except ValueError:
            logger.warning(f"Unknown action type: {action_type}")
            return None
    
    def list_supported_actions(self) -> list[str]:
        """List all supported action types."""
        return list(self._handlers.keys())


# Singleton instance
_action_router: Optional[ActionRouter] = None


def get_action_router() -> ActionRouter:
    """Get the global action router instance."""
    global _action_router
    if _action_router is None:
        _action_router = ActionRouter()
    return _action_router
