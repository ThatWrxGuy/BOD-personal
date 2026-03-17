"""
BB-APP-002: Command Handlers

Command patterns for state-changing operations.
Per BB-APP-002 Section 10 - Command Architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

from app.read_models import (
    CommandResult,
    RecommendationStatus,
    ActionStatus,
)


# ============== Command Base ==============

class Command(ABC):
    """Base command class."""
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate command inputs."""
        pass


# ============== Recommendation Commands ==============

@dataclass
class ApproveRecommendationCommand:
    """Approve a recommendation."""
    recommendation_id: str
    user_id: str
    notes: str = ""
    
    def validate(self) -> bool:
        return bool(self.recommendation_id and self.user_id)
    
    def execute(self) -> CommandResult:
        """Execute approval."""
        # In production, this would update the database
        # For now, return success
        return CommandResult(
            success=True,
            message="Recommendation approved successfully",
            entity_id=self.recommendation_id,
            refresh_hint="recommendations"
        )


@dataclass
class RejectRecommendationCommand:
    """Reject a recommendation."""
    recommendation_id: str
    user_id: str
    reason: str = ""
    
    def validate(self) -> bool:
        return bool(self.recommendation_id and self.user_id)
    
    def execute(self) -> CommandResult:
        """Execute rejection."""
        return CommandResult(
            success=True,
            message="Recommendation rejected",
            entity_id=self.recommendation_id,
            refresh_hint="recommendations"
        )


@dataclass
class DeferRecommendationCommand:
    """Defer a recommendation."""
    recommendation_id: str
    user_id: str
    defer_until: datetime | None = None
    reason: str = ""
    
    def validate(self) -> bool:
        return bool(self.recommendation_id and self.user_id)
    
    def execute(self) -> CommandResult:
        """Execute deferral."""
        return CommandResult(
            success=True,
            message="Recommendation deferred",
            entity_id=self.recommendation_id,
            refresh_hint="recommendations"
        )


# ============== Action Commands ==============

@dataclass
class CreateActionFromRecommendationCommand:
    """Create an action from a recommendation."""
    recommendation_id: str
    user_id: str
    title: str
    description: str = ""
    domain: str = ""
    due_date: datetime | None = None
    estimated_minutes: int = 30
    
    def validate(self) -> bool:
        return bool(self.recommendation_id and self.user_id and self.title)
    
    def execute(self) -> CommandResult:
        """Execute action creation."""
        action_id = str(uuid.uuid4())
        return CommandResult(
            success=True,
            message="Action created from recommendation",
            entity_id=action_id,
            refresh_hint="actions"
        )


@dataclass
class UpdateActionStatusCommand:
    """Update action status."""
    action_id: str
    user_id: str
    new_status: ActionStatus
    notes: str = ""
    
    def validate(self) -> bool:
        return bool(self.action_id and self.user_id and self.new_status)
    
    def execute(self) -> CommandResult:
        """Execute status update."""
        return CommandResult(
            success=True,
            message=f"Action status updated to {self.new_status.value}",
            entity_id=self.action_id,
            refresh_hint="actions"
        )


@dataclass
class CompleteActionCommand:
    """Complete an action."""
    action_id: str
    user_id: str
    outcome_notes: str = ""
    effectiveness_score: float | None = None
    
    def validate(self) -> bool:
        return bool(self.action_id and self.user_id)
    
    def execute(self) -> CommandResult:
        """Execute completion."""
        return CommandResult(
            success=True,
            message="Action completed",
            entity_id=self.action_id,
            refresh_hint="actions"
        )


@dataclass
class AttachActionOutcomeCommand:
    """Attach outcome notes to an action."""
    action_id: str
    user_id: str
    outcome_notes: str
    effectiveness_score: float | None = None
    
    def validate(self) -> bool:
        return bool(self.action_id and self.user_id and self.outcome_notes)
    
    def execute(self) -> CommandResult:
        """Execute outcome attachment."""
        return CommandResult(
            success=True,
            message="Outcome attached to action",
            entity_id=self.action_id,
            refresh_hint="actions"
        )


# ============== Settings Commands ==============

@dataclass
class UpdateUserPreferencesCommand:
    """Update user preferences."""
    user_id: str
    default_horizon: str | None = None
    operating_style: str | None = None
    notification_preference: str | None = None
    theme: str | None = None
    
    def validate(self) -> bool:
        return bool(self.user_id)
    
    def execute(self) -> CommandResult:
        """Execute preference update."""
        return CommandResult(
            success=True,
            message="Preferences updated",
            entity_id=self.user_id,
            refresh_hint="settings"
        )


# ============== Command Handlers ==============

class RecommendationCommandHandler:
    """Handler for recommendation commands."""
    
    def handle_approve(self, command: ApproveRecommendationCommand) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()
    
    def handle_reject(self, command: RejectRecommendationCommand) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()
    
    def handle_defer(self, command: DeferRecommendationCommand) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()


class ActionCommandHandler:
    """Handler for action commands."""
    
    def handle_create_from_recommendation(
        self, command: CreateActionFromRecommendationCommand
    ) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()
    
    def handle_update_status(self, command: UpdateActionStatusCommand) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()
    
    def handle_complete(self, command: CompleteActionCommand) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()
    
    def handle_attach_outcome(self, command: AttachActionOutcomeCommand) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()


class SettingsCommandHandler:
    """Handler for settings commands."""
    
    def handle_update_preferences(
        self, command: UpdateUserPreferencesCommand
    ) -> CommandResult:
        if not command.validate():
            return CommandResult(
                success=False,
                message="Invalid command inputs",
                error_code="VALIDATION_ERROR"
            )
        return command.execute()


# ============== Exports ==============

__all__ = [
    "Command",
    "ApproveRecommendationCommand",
    "RejectRecommendationCommand",
    "DeferRecommendationCommand",
    "CreateActionFromRecommendationCommand",
    "UpdateActionStatusCommand",
    "CompleteActionCommand",
    "AttachActionOutcomeCommand",
    "UpdateUserPreferencesCommand",
    "RecommendationCommandHandler",
    "ActionCommandHandler",
    "SettingsCommandHandler",
]
