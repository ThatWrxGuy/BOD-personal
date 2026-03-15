"""Action types and constants for execution layer."""
from enum import Enum


class ActionType(str, Enum):
    """Supported action types for execution."""
    
    # Financial Actions
    EXECUTE_TRADE = "EXECUTE_TRADE"
    REBALANCE_PORTFOLIO = "REBALANCE_PORTFOLIO"
    TRANSFER_FUNDS = "TRANSFER_FUNDS"
    PAY_BILL = "PAY_BILL"
    
    # Operational Actions
    CREATE_TASK = "CREATE_TASK"
    SCHEDULE_EVENT = "SCHEDULE_EVENT"
    SEND_EMAIL = "SEND_EMAIL"
    START_PROJECT = "START_PROJECT"
    
    # Strategic Actions
    ACTIVATE_STRATEGY = "ACTIVATE_STRATEGY"
    START_RESEARCH_JOB = "START_RESEARCH_JOB"
    RUN_SIMULATION_BATCH = "RUN_SIMULATION_BATCH"
    DEPLOY_MODEL = "DEPLOY_MODEL"


class ActionCategory(str, Enum):
    """Categories of actions."""
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"
    STRATEGIC = "STRATEGIC"


class ExecutionStatus(str, Enum):
    """Status of execution."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApprovalType(str, Enum):
    """Type of approval required."""
    AUTO_APPROVED = "AUTO_APPROVED"
    MANUAL_APPROVAL_REQUIRED = "MANUAL_APPROVAL_REQUIRED"
    MULTI_AGENT_APPROVAL = "MULTI_AGENT_APPROVAL"


# Action categories mapping
ACTION_CATEGORIES = {
    ActionType.EXECUTE_TRADE: ActionCategory.FINANCIAL,
    ActionType.REBALANCE_PORTFOLIO: ActionCategory.FINANCIAL,
    ActionType.TRANSFER_FUNDS: ActionCategory.FINANCIAL,
    ActionType.PAY_BILL: ActionCategory.FINANCIAL,
    ActionType.CREATE_TASK: ActionCategory.OPERATIONAL,
    ActionType.SCHEDULE_EVENT: ActionCategory.OPERATIONAL,
    ActionType.SEND_EMAIL: ActionCategory.OPERATIONAL,
    ActionType.START_PROJECT: ActionCategory.OPERATIONAL,
    ActionType.ACTIVATE_STRATEGY: ActionCategory.STRATEGIC,
    ActionType.START_RESEARCH_JOB: ActionCategory.STRATEGIC,
    ActionType.RUN_SIMULATION_BATCH: ActionCategory.STRATEGIC,
    ActionType.DEPLOY_MODEL: ActionCategory.STRATEGIC,
}

# Risk levels by action type
ACTION_RISK_LEVELS = {
    ActionType.EXECUTE_TRADE: 0.7,
    ActionType.REBALANCE_PORTFOLIO: 0.6,
    ActionType.TRANSFER_FUNDS: 0.8,
    ActionType.PAY_BILL: 0.3,
    ActionType.CREATE_TASK: 0.1,
    ActionType.SCHEDULE_EVENT: 0.1,
    ActionType.SEND_EMAIL: 0.2,
    ActionType.START_PROJECT: 0.4,
    ActionType.ACTIVATE_STRATEGY: 0.5,
    ActionType.START_RESEARCH_JOB: 0.2,
    ActionType.RUN_SIMULATION_BATCH: 0.1,
    ActionType.DEPLOY_MODEL: 0.3,
}
