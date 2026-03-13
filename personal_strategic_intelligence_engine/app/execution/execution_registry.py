"""Execution registry - tracks available execution handlers."""
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ExecutionRegistry:
    """Registry of available execution handlers."""

    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        action_type: str,
        handler: Callable,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register an execution handler.
        
        Args:
            action_type: Type of action the handler processes
            handler: Callable that executes the action
            metadata: Optional metadata about the handler
            
        Returns:
            True if registered successfully
        """
        if action_type in self._handlers:
            logger.warning(f"Overwriting existing handler for {action_type}")
        
        self._handlers[action_type] = handler
        self._metadata[action_type] = metadata or {}
        
        logger.info(f"Registered execution handler: {action_type}")
        return True

    def get_handler(self, action_type: str) -> Optional[Callable]:
        """Get a handler by action type."""
        return self._handlers.get(action_type)

    def list_handlers(self) -> list:
        """List all registered action types."""
        return list(self._handlers.keys())

    def is_registered(self, action_type: str) -> bool:
        """Check if an action type has a handler."""
        return action_type in self._handlers

    def unregister(self, action_type: str) -> bool:
        """Unregister an execution handler."""
        if action_type in self._handlers:
            del self._handlers[action_type]
            if action_type in self._metadata:
                del self._metadata[action_type]
            logger.info(f"Unregistered handler: {action_type}")
            return True
        return False

    def get_metadata(self, action_type: str) -> Dict[str, Any]:
        """Get metadata for an action type."""
        return self._metadata.get(action_type, {})

    def clear(self):
        """Clear all registered handlers."""
        self._handlers.clear()
        self._metadata.clear()


# Global registry instance
_registry: Optional["ExecutionRegistry"] = None


def get_execution_registry() -> ExecutionRegistry:
    """Get the global execution registry instance."""
    global _registry
    if _registry is None:
        _registry = ExecutionRegistry()
    return _registry
