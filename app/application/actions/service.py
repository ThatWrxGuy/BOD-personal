"""
BB-APP-002: Actions Service

Per BB-APP-002 Section 8.5 - Actions Integration.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.read_models import (
    ActionDetailReadModel,
    ActionSummaryReadModel,
    ActionOrigin,
    ActionStatus,
)
from app.commands import (
    UpdateActionStatusCommand,
    CompleteActionCommand,
    AttachActionOutcomeCommand,
    ActionCommandHandler,
)


class ActionsService:
    """Service for actions."""
    
    # Mock action store
    _actions = {
        "action-1": {
            "id": "action-1",
            "title": "Complete weekly review",
            "description": "Conduct weekly review of progress and plan ahead",
            "domain": "Review",
            "status": ActionStatus.PROPOSED,
            "due_date": datetime.now(),
            "estimated_minutes": 30,
            "created_at": datetime.now() - timedelta(days=1),
            "updated_at": datetime.now() - timedelta(days=1),
            "completed_at": None,
            "origin": {
                "recommendation_id": None,
                "brief_id": "brief-001",
                "domain": "Review"
            },
            "outcome_notes": "",
            "effectiveness_score": None,
        },
        "action-2": {
            "id": "action-2",
            "title": "Update career goals",
            "description": "Review and update career objectives for the quarter",
            "domain": "Career",
            "status": ActionStatus.PROPOSED,
            "due_date": datetime.now() + timedelta(days=1),
            "estimated_minutes": 45,
            "created_at": datetime.now() - timedelta(days=2),
            "updated_at": datetime.now() - timedelta(days=2),
            "completed_at": None,
            "origin": {
                "recommendation_id": "rec-4",
                "brief_id": "brief-001",
                "domain": "Career"
            },
            "outcome_notes": "",
            "effectiveness_score": None,
        },
        "action-3": {
            "id": "action-3",
            "title": "Review Q1 budget",
            "description": "Analyze Q1 spending and adjust budget as needed",
            "domain": "Finance",
            "status": ActionStatus.PROPOSED,
            "due_date": datetime.now() + timedelta(days=3),
            "estimated_minutes": 60,
            "created_at": datetime.now() - timedelta(days=3),
            "updated_at": datetime.now() - timedelta(days=3),
            "completed_at": None,
            "origin": {
                "recommendation_id": None,
                "brief_id": "brief-001",
                "domain": "Finance"
            },
            "outcome_notes": "",
            "effectiveness_score": None,
        },
        "action-4": {
            "id": "action-4",
            "title": "Implement sleep schedule",
            "description": "Set consistent bedtimes and wake times for better recovery",
            "domain": "Health",
            "status": ActionStatus.IN_PROGRESS,
            "due_date": datetime.now() + timedelta(days=7),
            "estimated_minutes": 15,
            "created_at": datetime.now() - timedelta(days=5),
            "updated_at": datetime.now() - timedelta(hours=12),
            "completed_at": None,
            "origin": {
                "recommendation_id": "rec-3",
                "brief_id": "brief-001",
                "domain": "Health"
            },
            "outcome_notes": "Started tracking sleep times",
            "effectiveness_score": None,
        },
    }
    
    async def list_actions(
        self,
        user_id: str,
        domain: Optional[str] = None,
        status: Optional[ActionStatus] = None,
        limit: int = 50
    ) -> List[ActionSummaryReadModel]:
        """List actions with optional filters."""
        results = []
        
        for action in self._actions.values():
            # Apply filters
            if domain and action["domain"].lower() != domain.lower():
                continue
            if status and action["status"] != status:
                continue
            
            results.append(ActionSummaryReadModel(
                id=action["id"],
                title=action["title"],
                domain=action["domain"],
                status=action["status"],
                due_date=action.get("due_date"),
                priority=3 if action["status"] == ActionStatus.PROPOSED else 2
            ))
        
        return results[:limit]
    
    async def get_action(
        self,
        action_id: str,
        user_id: str
    ) -> Optional[ActionDetailReadModel]:
        """Get detailed action."""
        action = self._actions.get(action_id)
        if not action:
            return None
        
        origin = ActionOrigin(
            recommendation_id=action["origin"].get("recommendation_id"),
            brief_id=action["origin"].get("brief_id"),
            domain=action["origin"].get("domain")
        )
        
        return ActionDetailReadModel(
            id=action["id"],
            title=action["title"],
            description=action["description"],
            domain=action["domain"],
            status=action["status"],
            due_date=action.get("due_date"),
            estimated_minutes=action.get("estimated_minutes", 30),
            created_at=action["created_at"],
            updated_at=action["updated_at"],
            completed_at=action.get("completed_at"),
            origin=origin,
            outcome_notes=action.get("outcome_notes", ""),
            effectiveness_score=action.get("effectiveness_score"),
        )
    
    async def update_status(
        self,
        action_id: str,
        user_id: str,
        new_status: ActionStatus,
        notes: str = ""
    ) -> bool:
        """Update action status."""
        handler = ActionCommandHandler()
        command = UpdateActionStatusCommand(
            action_id=action_id,
            user_id=user_id,
            new_status=new_status,
            notes=notes
        )
        result = handler.handle_update_status(command)
        
        if result.success and action_id in self._actions:
            self._actions[action_id]["status"] = new_status
            self._actions[action_id]["updated_at"] = datetime.now()
        
        return result.success
    
    async def complete_action(
        self,
        action_id: str,
        user_id: str,
        outcome_notes: str = "",
        effectiveness_score: Optional[float] = None
    ) -> bool:
        """Complete an action."""
        handler = ActionCommandHandler()
        command = CompleteActionCommand(
            action_id=action_id,
            user_id=user_id,
            outcome_notes=outcome_notes,
            effectiveness_score=effectiveness_score
        )
        result = handler.handle_complete(command)
        
        if result.success and action_id in self._actions:
            self._actions[action_id]["status"] = ActionStatus.COMPLETED
            self._actions[action_id]["updated_at"] = datetime.now()
            self._actions[action_id]["completed_at"] = datetime.now()
            self._actions[action_id]["outcome_notes"] = outcome_notes
            self._actions[action_id]["effectiveness_score"] = effectiveness_score
        
        return result.success
    
    async def attach_outcome(
        self,
        action_id: str,
        user_id: str,
        outcome_notes: str,
        effectiveness_score: Optional[float] = None
    ) -> bool:
        """Attach outcome notes to an action."""
        handler = ActionCommandHandler()
        command = AttachActionOutcomeCommand(
            action_id=action_id,
            user_id=user_id,
            outcome_notes=outcome_notes,
            effectiveness_score=effectiveness_score
        )
        result = handler.handle_attach_outcome(command)
        
        if result.success and action_id in self._actions:
            self._actions[action_id]["outcome_notes"] = outcome_notes
            self._actions[action_id]["effectiveness_score"] = effectiveness_score
            self._actions[action_id]["updated_at"] = datetime.now()
        
        return result.success
    
    async def create_action(
        self,
        user_id: str,
        title: str,
        description: str = "",
        domain: str = "",
        due_date: Optional[datetime] = None,
        estimated_minutes: int = 30,
        recommendation_id: Optional[str] = None,
        brief_id: Optional[str] = None
    ) -> str:
        """Create a new action."""
        import uuid
        action_id = str(uuid.uuid4())
        
        self._actions[action_id] = {
            "id": action_id,
            "title": title,
            "description": description,
            "domain": domain or "General",
            "status": ActionStatus.PROPOSED,
            "due_date": due_date,
            "estimated_minutes": estimated_minutes,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "completed_at": None,
            "origin": {
                "recommendation_id": recommendation_id,
                "brief_id": brief_id,
                "domain": domain
            },
            "outcome_notes": "",
            "effectiveness_score": None,
        }
        
        return action_id


# Singleton instance
actions_service = ActionsService()
