"""Intelligence Router.

This module routes tasks to the appropriate external intelligence service
based on the task type. It determines whether to use OpenAI for reasoning,
OpenHands for system improvement, or GitHub for repository operations.

All tasks pass through the governance layer before execution.
"""
from enum import Enum
from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskType(Enum):
    """Types of tasks that can be routed."""
    REASONING = "reasoning"
    DEVELOPMENT = "development"
    REPOSITORY = "repository"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    UNKNOWN = "unknown"


class IntelligenceRouter:
    """Routes tasks to appropriate external intelligence services."""

    def __init__(self):
        """Initialize the intelligence router."""
        self._openai_engine = None
        self._openhands_engine = None
        self._github_engine = None
        self._governor = None
        self._execution_gate = None
        self._audit_log = None

    @property
    def openai_engine(self):
        """Lazy load OpenAI engine."""
        if self._openai_engine is None:
            from app.infrastructure.external_intelligence.openai_gateway import (
                get_openai_reasoning_engine,
            )
            self._openai_engine = get_openai_reasoning_engine()
        return self._openai_engine

    @property
    def openhands_engine(self):
        """Lazy load OpenHands engine."""
        if self._openhands_engine is None:
            from app.infrastructure.external_intelligence.openhands_gateway import (
                get_openhands_engine,
            )
            self._openhands_engine = get_openhands_engine()
        return self._openhands_engine

    @property
    def github_engine(self):
        """Lazy load GitHub engine."""
        if self._github_engine is None:
            from app.infrastructure.external_intelligence.github_gateway import (
                get_github_engine,
            )
            self._github_engine = get_github_engine()
        return self._github_engine

    @property
    def governor(self):
        """Lazy load governance governor."""
        if self._governor is None:
            from app.infrastructure.governance import get_governor
            self._governor = get_governor()
        return self._governor

    @property
    def execution_gate(self):
        """Lazy load execution gate."""
        if self._execution_gate is None:
            from app.infrastructure.governance import get_execution_gate
            self._execution_gate = get_execution_gate()
        return self._execution_gate

    @property
    def audit_log(self):
        """Lazy load audit log."""
        if self._audit_log is None:
            from app.infrastructure.governance import get_audit_log
            self._audit_log = get_audit_log()
        return self._audit_log

    def classify_task(self, task: str) -> TaskType:
        """Classify a task to determine its type.
        
        Args:
            task: Description of the task
            
        Returns:
            The type of task
        """
        task_lower = task.lower()
        
        # Reasoning keywords
        reasoning_keywords = [
            "analyze", "reasoning", "strategy", "recommend",
            "evaluate", "assess", "compare", "decide",
            "what is", "how to", "why", "should i",
            "best", "optimal", "recommendation", "insight",
        ]
        
        # Development keywords
        development_keywords = [
            "implement", "fix", "refactor", "code", "bug",
            "feature", "patch", "modify", "update", "change",
            "improve", "optimize", "write", "create file",
        ]
        
        # Repository keywords
        repository_keywords = [
            "repo", "repository", "github", "issue", "pr",
            "pull request", "commit", "branch", "version",
            "release", "merge", "codebase",
        ]
        
        # Research keywords
        research_keywords = [
            "research", "find", "search", "lookup",
            "information", "data", "query", "investigate",
        ]
        
        # Check for matches
        if any(kw in task_lower for kw in reasoning_keywords):
            if any(kw in task_lower for kw in development_keywords):
                return TaskType.DEVELOPMENT
            return TaskType.REASONING
        
        if any(kw in task_lower for kw in development_keywords):
            return TaskType.DEVELOPMENT
        
        if any(kw in task_lower for kw in repository_keywords):
            return TaskType.REPOSITORY
        
        if any(kw in task_lower for kw in research_keywords):
            return TaskType.RESEARCH
        
        return TaskType.UNKNOWN

    async def route(self, task: str, **kwargs) -> dict[str, Any]:
        """Route a task to the appropriate service through governance.
        
        Args:
            task: Description of the task
            **kwargs: Additional arguments for the specific handler
            
        Returns:
            Result from the appropriate service
        """
        task_type = self.classify_task(task)
        
        logger.info(f"Routing task to {task_type.value}: {task[:50]}...")
        
        # Map task type to action type for governance
        action_type_map = {
            TaskType.REASONING: "reasoning",
            TaskType.DEVELOPMENT: "code_generation",
            TaskType.REPOSITORY: "repository_write" if kwargs.get("write") else "repository_read",
            TaskType.RESEARCH: "reasoning",
            TaskType.UNKNOWN: "reasoning",
        }
        
        # Check governance approval
        action_type = action_type_map.get(task_type, "reasoning")
        approval = self.governor.approve_reasoning({"task": task, "type": action_type})
        
        # Log the governance check
        self.audit_log.log_governance_check(
            action_type=action_type,
            required_level=approval.get("required_level", "unknown"),
            approved=approval.get("approved", False),
            reason=approval.get("reason", ""),
        )
        
        if not approval.get("approved"):
            return {
                "service": "governance",
                "task_type": task_type.value,
                "status": "blocked",
                "reason": approval.get("reason", "Governance check failed"),
                "required_level": approval.get("required_level"),
            }
        
        # Route to appropriate handler
        if task_type == TaskType.REASONING:
            return await self._handle_reasoning(task, **kwargs)
        
        elif task_type == TaskType.DEVELOPMENT:
            return await self._handle_development(task, **kwargs)
        
        elif task_type == TaskType.REPOSITORY:
            return await self._handle_repository(task, **kwargs)
        
        elif task_type == TaskType.RESEARCH:
            return await self._handle_research(task, **kwargs)
        
        else:
            return await self._handle_default(task, **kwargs)

    async def _handle_reasoning(self, task: str, **kwargs) -> dict[str, Any]:
        """Handle reasoning tasks via OpenAI."""
        context = kwargs.get("context")
        
        result = await self.openai_engine.analyze(task, context)
        
        return {
            "service": "openai",
            "task_type": "reasoning",
            "result": result,
        }

    async def _handle_development(self, task: str, **kwargs) -> dict[str, Any]:
        """Handle development tasks via OpenHands."""
        action = kwargs.get("action", "analyze")
        
        if action == "implement":
            spec = kwargs.get("spec", task)
            existing_code = kwargs.get("existing_code")
            result = await self.openhands_engine.implement_feature(spec, existing_code)
        
        elif action == "fix":
            bug_description = kwargs.get("bug_description", task)
            related_files = kwargs.get("related_files", [])
            result = await self.openhands_engine.fix_bug(bug_description, related_files)
        
        elif action == "analyze":
            result = await self.openhands_engine.analyze_issue(task)
        
        else:
            result = await self.openhands_engine.analyze_issue(task)
        
        return {
            "service": "openhands",
            "task_type": "development",
            "action": action,
            "result": result,
        }

    async def _handle_repository(self, task: str, **kwargs) -> dict[str, Any]:
        """Handle repository tasks via GitHub."""
        owner = kwargs.get("owner")
        repo = kwargs.get("repo")
        
        if not owner or not repo:
            return {
                "service": "github",
                "task_type": "repository",
                "success": False,
                "error": "owner and repo are required",
            }
        
        action = kwargs.get("action", "analyze")
        
        if action == "analyze":
            result = await self.github_engine.analyze_repo(owner, repo)
        
        elif action == "create_issue":
            title = kwargs.get("title", task)
            body = kwargs.get("body", "")
            labels = kwargs.get("labels", [])
            result = await self.github_engine.create_issue(owner, repo, title, body, labels)
        
        elif action == "create_pr":
            title = kwargs.get("title", task)
            body = kwargs.get("body", "")
            head = kwargs.get("head")
            base = kwargs.get("base", "main")
            result = await self.github_engine.create_pull_request(
                owner, repo, title, body, head, base
            )
        
        elif action == "list_issues":
            state = kwargs.get("state", "open")
            result = await self.github_engine.list_issues(owner, repo, state)
        
        else:
            result = await self.github_engine.analyze_repo(owner, repo)
        
        return {
            "service": "github",
            "task_type": "repository",
            "action": action,
            "result": result,
        }

    async def _handle_research(self, task: str, **kwargs) -> dict[str, Any]:
        """Handle research tasks - can use multiple services."""
        # Use OpenAI for research synthesis
        result = await self.openai_engine.analyze(task)
        
        return {
            "service": "openai",
            "task_type": "research",
            "result": result,
        }

    async def _handle_default(self, task: str, **kwargs) -> dict[str, Any]:
        """Handle unknown tasks with a default approach."""
        # Default to OpenAI reasoning
        result = await self.openai_engine.analyze(task)
        
        return {
            "service": "openai",
            "task_type": "unknown",
            "result": result,
        }

    def get_available_services(self) -> dict[str, bool]:
        """Get information about available services.
        
        Returns:
            Dictionary of service availability
        """
        # Check if services have valid credentials
        settings = self._get_settings()
        
        services = {
            "openai": bool(settings.openai_api_key) if hasattr(settings, 'openai_api_key') else False,
            "openhands": bool(settings.openhands_api_key) if hasattr(settings, 'openhands_api_key') else False,
            "github": bool(self.github_engine.token),
        }
        
        return services

    def get_governance_status(self) -> dict[str, Any]:
        """Get governance status for all services.
        
        Returns:
            Governance status information
        """
        return {
            "governor": self.governor.get_governance_status(),
            "execution_gate": self.execution_gate.get_status(),
            "audit_log": self.audit_log.get_statistics(),
        }

    def get_status(self) -> dict[str, Any]:
        """Get overall intelligence layer status.
        
        Returns:
            Complete status of the intelligence layer
        """
        return {
            "services": self.get_available_services(),
            "governance": self.get_governance_status(),
        }

    def _get_settings(self):
        """Get application settings."""
        from app.core.config import get_settings
        return get_settings()


# Global instance
_router: Optional[IntelligenceRouter] = None


def get_intelligence_router() -> IntelligenceRouter:
    """Get the intelligence router instance."""
    global _router
    
    if _router is None:
        _router = IntelligenceRouter()
    
    return _router


async def route_task(task: str, **kwargs) -> dict[str, Any]:
    """Convenience function to route a task.
    
    Args:
        task: Description of the task
        **kwargs: Additional arguments
        
    Returns:
        Result from the appropriate service
    """
    router = get_intelligence_router()
    return await router.route(task, **kwargs)
