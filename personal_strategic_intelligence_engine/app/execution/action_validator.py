"""Action Validator for safe execution."""
from typing import Optional
from app.execution.action_types import ActionType, ACTION_RISK_LEVELS
from app.core.logging import get_logger

logger = get_logger(__name__)


class ActionValidator:
    """Validates actions before execution for safety."""
    
    # Global safety controls
    SYSTEM_EXECUTION_ENABLED = True
    
    # Financial limits
    MAX_TRADE_SIZE = 10000  # Maximum dollar amount per trade
    MAX_TRANSFER_AMOUNT = 5000  # Maximum transfer amount
    MAX_DAILY_FINANCIAL_EXPOSURE = 25000  # Maximum daily financial exposure
    
    # Action limits
    MAX_DAILY_ACTIONS = 50
    MAX_RETRY_COUNT = 3
    
    def __init__(self):
        self.daily_action_count = 0
        self.daily_financial_exposure = 0.0
    
    def validate(self, action_type: str, payload: dict) -> tuple[bool, Optional[str]]:
        """
        Validate an action before execution.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check system execution is enabled
        if not self.SYSTEM_EXECUTION_ENABLED:
            return False, "System execution is disabled"
        
        # Check daily action limit
        if self.daily_action_count >= self.MAX_DAILY_ACTIONS:
            return False, "Daily action limit exceeded"
        
        # Validate action type
        try:
            action = ActionType(action_type)
        except ValueError:
            return False, f"Unknown action type: {action_type}"
        
        # Check risk score for this action type
        risk_score = ACTION_RISK_LEVELS.get(action, 0.5)
        
        if risk_score > 0.7:
            return False, f"Action {action_type} requires manual approval (high risk)"
        
        # Validate financial limits
        if action in [ActionType.EXECUTE_TRADE, ActionType.TRANSFER_FUNDS]:
            amount = payload.get("amount", 0) or payload.get("quantity", 0) * payload.get("price", 0)
            
            if action == ActionType.EXECUTE_TRADE and amount > self.MAX_TRADE_SIZE:
                return False, f"Trade size ${amount} exceeds maximum ${self.MAX_TRADE_SIZE}"
            
            if action == ActionType.TRANSFER_FUNDS and amount > self.MAX_TRANSFER_AMOUNT:
                return False, f"Transfer amount ${amount} exceeds maximum ${self.MAX_TRANSFER_AMOUNT}"
            
            # Check daily exposure
            if self.daily_financial_exposure + amount > self.MAX_DAILY_FINANCIAL_EXPOSURE:
                return False, "Daily financial exposure limit would be exceeded"
        
        # Validate payload
        is_valid, error = self._validate_payload(action_type, payload)
        if not is_valid:
            return False, error
        
        return True, None
    
    def _validate_payload(self, action_type: str, payload: dict) -> tuple[bool, Optional[str]]:
        """Validate action-specific payload."""
        
        if action_type == ActionType.EXECUTE_TRADE:
            if not payload.get("symbol"):
                return False, "Missing required field: symbol"
            if not payload.get("quantity") or payload.get("quantity", 0) <= 0:
                return False, "Invalid quantity"
        
        elif action_type == ActionType.TRANSFER_FUNDS:
            if not payload.get("to_account"):
                return False, "Missing recipient account"
            if not payload.get("amount") or payload.get("amount", 0) <= 0:
                return False, "Invalid amount"
        
        elif action_type == ActionType.SEND_EMAIL:
            if not payload.get("to"):
                return False, "Missing recipient"
            if not payload.get("subject"):
                return False, "Missing email subject"
        
        elif action_type == ActionType.SCHEDULE_EVENT:
            if not payload.get("title"):
                return False, "Missing event title"
            if not payload.get("start_time"):
                return False, "Missing event start time"
        
        elif action_type == ActionType.CREATE_TASK:
            if not payload.get("title"):
                return False, "Missing task title"
        
        return True, None
    
    def get_risk_score(self, action_type: str, payload: dict) -> float:
        """Calculate risk score for an action."""
        base_risk = ACTION_RISK_LEVELS.get(ActionType(action_type), 0.5)
        
        # Add modifiers based on payload
        amount = payload.get("amount", 0) or payload.get("quantity", 0) * payload.get("price", 0)
        
        if amount > 5000:
            base_risk += 0.2
        elif amount > 1000:
            base_risk += 0.1
        
        return min(1.0, base_risk)
    
    def record_action_execution(self, action_type: str, amount: float = 0) -> None:
        """Record an action execution for tracking."""
        self.daily_action_count += 1
        
        # Track financial exposure
        if amount > 0:
            self.daily_daily_financial_exposure += amount
    
    def reset_daily_counters(self) -> None:
        """Reset daily counters (should be called at midnight)."""
        self.daily_action_count = 0
        self.daily_financial_exposure = 0.0


# Global validator instance
_validator: Optional[ActionValidator] = None


def get_validator() -> ActionValidator:
    """Get global validator instance."""
    global _validator
    if _validator is None:
        _validator = ActionValidator()
    return _validator
