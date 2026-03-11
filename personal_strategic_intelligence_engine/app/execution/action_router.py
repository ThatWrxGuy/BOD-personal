"""Action Router for routing actions to appropriate connectors."""
from typing import Any, Optional

from app.execution.action_types import ActionType
from app.core.logging import get_logger

logger = get_logger(__name__)


class ActionRouter:
    """Routes actions to appropriate connectors."""
    
    # Connector registry
    _connectors: dict[str, Any] = {}
    
    # Action type to connector mapping
    ACTION_CONNECTORS = {
        ActionType.EXECUTE_TRADE: "financial",
        ActionType.REBALANCE_PORTFOLIO: "financial",
        ActionType.TRANSFER_FUNDS: "financial",
        ActionType.PAY_BILL: "financial",
        ActionType.CREATE_TASK: "task",
        ActionType.SCHEDULE_EVENT: "calendar",
        ActionType.SEND_EMAIL: "email",
        ActionType.START_PROJECT: "task",
        ActionType.ACTIVATE_STRATEGY: "strategic",
        ActionType.START_RESEARCH_JOB: "strategic",
        ActionType.RUN_SIMULATION_BATCH: "strategic",
        ActionType.DEPLOY_MODEL: "strategic",
    }
    
    @classmethod
    def register_connector(cls, name: str, connector: Any) -> None:
        """Register a connector."""
        cls._connectors[name] = connector
        logger.info(f"Registered connector: {name}")
    
    @classmethod
    def get_connector(cls, name: str) -> Optional[Any]:
        """Get a connector by name."""
        return cls._connectors.get(name)
    
    @classmethod
    def route_action(cls, action_type: str, payload: dict) -> tuple[Optional[str], Any]:
        """Route an action to the appropriate connector."""
        try:
            action = ActionType(action_type)
        except ValueError:
            logger.error(f"Unknown action type: {action_type}")
            return None, None
        
        connector_name = cls.ACTION_CONNECTORS.get(action)
        
        if not connector_name:
            logger.error(f"No connector found for action type: {action_type}")
            return None, None
        
        connector = cls._connectors.get(connector_name)
        
        if not connector:
            logger.warning(f"Connector not registered: {connector_name}")
            return connector_name, MockConnector(connector_name)
        
        return connector_name, connector
    
    @classmethod
    def execute_action(cls, action_type: str, payload: dict) -> dict:
        """Execute an action by routing to the appropriate connector."""
        connector_name, connector = cls.route_action(action_type, payload)
        
        if not connector:
            return {
                "success": False,
                "error": f"No connector available for action: {action_type}",
            }
        
        try:
            result = connector.execute(action_type, payload)
            return {
                "success": True,
                "connector": connector_name,
                "result": result,
            }
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            return {
                "success": False,
                "error": str(e),
            }


class MockConnector:
    """Mock connector for development."""
    
    def __init__(self, name: str):
        self.name = name
    
    def connect(self) -> bool:
        return True
    
    def validate(self) -> bool:
        return True
    
    def execute(self, action_type: str, payload: dict) -> dict:
        """Execute a mock action."""
        logger.info(f"Mock executing {action_type} with payload: {payload}")
        return {
            "status": "success",
            "mock": True,
            "action": action_type,
            "timestamp": str(payload),
        }


def get_router() -> ActionRouter:
    """Get the action router."""
    return ActionRouter()
