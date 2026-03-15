"""Safety Validator - validates execution safety rules before action.

The safety validator ensures all execution requests meet safety requirements
before they can be executed.
"""
from typing import Any, Dict, List

from app.execution_engine.execution_models import (
    ActionType,
    ApprovalLevel,
    ExecutionRequest,
    SafetyValidationResult,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class SafetyValidator:
    """
    Validates execution safety rules before action.
    
    Validation checks include:
    - governance approval verification
    - risk limit enforcement
    - capital availability
    - duplicate execution prevention
    
    Requests failing validation must be rejected.
    """
    
    # Risk thresholds
    MAX_RISK_SCORES = {
        "low": 0.3,
        "medium": 0.6,
        "high": 0.8,
        "critical": 1.0,
    }
    
    # Capital limits (in dollars)
    MAX_TRADE_AMOUNT = 100000
    MAX_DAILY_TRADES = 10
    
    def __init__(self):
        self._executed_proposals: set = set()
        self._daily_trade_count: int = 0
    
    async def validate(self, request: ExecutionRequest) -> SafetyValidationResult:
        """
        Validate an execution request.
        
        Args:
            request: The execution request to validate
            
        Returns:
            Validation result with errors and warnings
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # Check 1: Proposal governance approval
        if not self._validate_approval(request):
            errors.append("Execution not approved by governance")
        
        # Check 2: Risk level validation
        risk_errors, risk_warnings = self._validate_risk_level(request)
        errors.extend(risk_errors)
        warnings.extend(risk_warnings)
        
        # Check 3: Duplicate execution prevention
        if self._is_duplicate(request):
            errors.append("Duplicate execution: this proposal has already been executed")
        
        # Check 4: Action-specific validation
        action_errors, action_warnings = self._validate_action(request)
        errors.extend(action_errors)
        warnings.extend(action_warnings)
        
        # Check 5: Parameter validation
        param_errors, param_warnings = self._validate_parameters(request)
        errors.extend(param_errors)
        warnings.extend(param_warnings)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Execution validation passed for: {request.id}")
        else:
            logger.warning(f"Execution validation failed for: {request.id} - {errors}")
        
        return SafetyValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_approval(self, request: ExecutionRequest) -> bool:
        """Validate that the execution has governance approval."""
        # Check if approved
        if request.approved_by in ["pending", "rejected"]:
            return False
        
        # Check approval level requirements
        if request.risk_level == "critical":
            return request.approval_level == ApprovalLevel.CEO
        elif request.risk_level == "high":
            return request.approval_level in [ApprovalLevel.GOVERNANCE, ApprovalLevel.CEO]
        
        return True
    
    def _validate_risk_level(
        self,
        request: ExecutionRequest,
    ) -> tuple[List[str], List[str]]:
        """Validate risk level constraints."""
        errors: List[str] = []
        warnings: List[str] = []
        
        max_score = self.MAX_RISK_SCORES.get(request.risk_level, 0.6)
        
        # For critical risk, always require explicit approval
        if request.risk_level == "critical":
            if request.approval_level != ApprovalLevel.CEO:
                errors.append("Critical risk executions require CEO approval")
        
        # Warn on high risk
        if request.risk_level == "high":
            warnings.append("High risk execution - ensure mitigation measures are in place")
        
        return errors, warnings
    
    def _is_duplicate(self, request: ExecutionRequest) -> bool:
        """Check if this is a duplicate execution."""
        if request.proposal_id in self._executed_proposals:
            logger.warning(f"Duplicate execution detected for proposal: {request.proposal_id}")
            return True
        return False
    
    def _validate_action(
        self,
        request: ExecutionRequest,
    ) -> tuple[List[str], List[str]]:
        """Validate action-specific constraints."""
        errors: List[str] = []
        warnings: List[str] = []
        
        action_type = request.action_type
        
        # Validate trade execution
        if action_type == ActionType.TRADE_EXECUTION:
            params = request.parameters
            
            # Check for required parameters
            if "symbol" not in params:
                errors.append("Trade execution requires 'symbol' parameter")
            if "quantity" not in params:
                errors.append("Trade execution requires 'quantity' parameter")
            
            # Check trade amount
            quantity = params.get("quantity", 0)
            price = params.get("price", 0)
            total_value = quantity * price
            
            if total_value > self.MAX_TRADE_AMOUNT:
                errors.append(f"Trade value ${total_value} exceeds maximum ${self.MAX_TRADE_AMOUNT}")
            
            # Check daily trade limit
            if self._daily_trade_count >= self.MAX_DAILY_TRADES:
                errors.append("Daily trade limit reached")
        
        # Validate portfolio adjustment
        elif action_type == ActionType.PORTFOLIO_ADJUSTMENT:
            params = request.parameters
            
            if "target_allocation" not in params:
                errors.append("Portfolio adjustment requires 'target_allocation' parameter")
            
            # Validate allocation sums to 100%
            allocation = params.get("target_allocation", {})
            total = sum(allocation.values())
            if total > 0 and abs(total - 1.0) > 0.01:
                warnings.append("Allocation does not sum to 100%")
        
        return errors, warnings
    
    def _validate_parameters(
        self,
        request: ExecutionRequest,
    ) -> tuple[List[str], List[str]]:
        """Validate request parameters."""
        errors: List[str] = []
        warnings: List[str] = []
        
        # Check required fields
        if not request.proposal_id:
            errors.append("Execution request must have a proposal_id")
        
        if not request.action_type:
            errors.append("Execution request must have an action_type")
        
        # Validate parameters structure
        if not isinstance(request.parameters, dict):
            errors.append("Parameters must be a dictionary")
        
        return errors, warnings
    
    def mark_executed(self, proposal_id: str) -> None:
        """Mark a proposal as executed to prevent duplicates."""
        self._executed_proposals.add(proposal_id)
        self._daily_trade_count += 1
    
    def reset_daily_counters(self) -> None:
        """Reset daily counters (for testing or end of day)."""
        self._daily_trade_count = 0
        self._executed_proposals.clear()
    
    def get_risk_score(self, action_type: str, parameters: Dict[str, Any]) -> float:
        """Calculate risk score for an action."""
        base_score = 0.5
        
        # Adjust based on action type
        if action_type == ActionType.TRADE_EXECUTION:
            base_score = 0.6
        elif action_type == ActionType.PORTFOLIO_ADJUSTMENT:
            base_score = 0.5
        elif action_type == ActionType.ALERT_NOTIFICATION:
            base_score = 0.2
        elif action_type == ActionType.SYSTEM_ACTION:
            base_score = 0.3
        
        # Adjust based on parameters
        amount = parameters.get("quantity", 0) * parameters.get("price", 0)
        if amount > 50000:
            base_score += 0.2
        elif amount > 10000:
            base_score += 0.1
        
        return min(base_score, 1.0)


# Singleton instance
_safety_validator: SafetyValidator = None


def get_safety_validator() -> SafetyValidator:
    """Get the global safety validator instance."""
    global _safety_validator
    if _safety_validator is None:
        _safety_validator = SafetyValidator()
    return _safety_validator
