"""OpenHands Autonomous Development Gateway.

This module enables Busy Bee to improve its own codebase through the OpenHands API.
It supports code refactoring, bug fixing, feature implementation, and architecture analysis.
"""
import json
from typing import Any, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenHandsEngine:
    """OpenHands-powered autonomous development engine."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenHands development engine."""
        settings = get_settings()
        self.api_key = api_key or settings.openhands_api_key
        self.base_url = "https://api.openhands.ai/v1"
        
        if not self.api_key:
            logger.warning("OpenHands API key not configured. Development capabilities limited.")

    async def analyze_issue(self, issue: str) -> dict[str, Any]:
        """Analyze a problem and propose a solution.
        
        Args:
            issue: Description of the problem
            
        Returns:
            Analysis with proposed approach
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenHands API key not configured",
                "analysis": "Analysis unavailable",
            }
        
        try:
            from app.services import get_openhands_client
            client = get_openhands_client()
            
            result = await client.run_task(
                task=f"Analyze this issue and propose a solution: {issue}",
                agent_id="code-analysis",
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                }
            
            return {
                "success": True,
                "analysis": result.get("result", ""),
                "task_id": result.get("task_id"),
            }
        except Exception as e:
            logger.error(f"OpenHands issue analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def propose_code_change(
        self,
        file_path: str,
        description: str,
        current_code: Optional[str] = None
    ) -> dict[str, Any]:
        """Propose a code change for a specific file.
        
        Args:
            file_path: Path to the file to modify
            description: Description of the desired change
            current_code: Current code (optional if file exists)
            
        Returns:
            Proposed code changes
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenHands API key not configured",
                "proposal": {},
            }
        
        task = f"""
Modify the file at: {file_path}

Description of change: {description}
"""
        
        if current_code:
            task += f"\n\nCurrent code:\n```\n{current_code}\n```"
        
        try:
            from app.services import get_openhands_client
            client = get_openhands_client()
            
            result = await client.run_task(
                task=task,
                agent_id="code-generation",
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                }
            
            return {
                "success": True,
                "proposal": result.get("result", ""),
                "file_path": file_path,
            }
        except Exception as e:
            logger.error(f"OpenHands code proposal error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def generate_patch(
        self,
        directive: str,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate a code patch based on a directive.
        
        Args:
            directive: The change directive
            context: Relevant context for the patch
            
        Returns:
            Generated patch
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenHands API key not configured",
                "patch": "",
            }
        
        context_str = json.dumps(context, indent=2)
        
        task = f"""
Generate a code patch for the following directive:

{directive}

Context:
{context_str}

Provide the complete modified code or patch.
"""
        
        try:
            from app.services import get_openhands_client
            client = get_openhands_client()
            
            result = await client.run_task(
                task=task,
                agent_id="code-generation",
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                }
            
            return {
                "success": True,
                "patch": result.get("result", ""),
                "directive": directive,
            }
        except Exception as e:
            logger.error(f"OpenHands patch generation error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def implement_feature(
        self,
        spec: str,
        existing_code: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Implement a new feature based on specification.
        
        Args:
            spec: Feature specification
            existing_code: Existing relevant code files
            
        Returns:
            Implementation code
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenHands API key not configured",
                "implementation": {},
            }
        
        task = f"""
Implement a new feature based on this specification:

{spec}
"""
        
        if existing_code:
            task += "\n\nExisting code references:\n"
            for path, code in existing_code.items():
                task += f"\n\nFile: {path}\n```\n{code}\n```"
        
        try:
            from app.services import get_openhands_client
            client = get_openhands_client()
            
            result = await client.run_task(
                task=task,
                agent_id="general-purpose",
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                }
            
            return {
                "success": True,
                "implementation": result.get("result", ""),
                "spec": spec,
            }
        except Exception as e:
            logger.error(f"OpenHands feature implementation error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def analyze_architecture(self, codebase_path: str) -> dict[str, Any]:
        """Analyze the system architecture.
        
        Args:
            codebase_path: Path to the codebase
            
        Returns:
            Architecture analysis and recommendations
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenHands API key not configured",
                "analysis": {},
            }
        
        task = f"""
Analyze the architecture of the codebase at: {codebase_path}

Provide:
1. Overall architecture overview
2. Key components and their responsibilities
3. Potential improvements
4. Design patterns identified
"""
        
        try:
            from app.services import get_openhands_client
            client = get_openhands_client()
            
            result = await client.run_task(
                task=task,
                agent_id="code-analysis",
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                }
            
            return {
                "success": True,
                "analysis": result.get("result", ""),
                "codebase_path": codebase_path,
            }
        except Exception as e:
            logger.error(f"OpenHands architecture analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def fix_bug(self, bug_description: str, related_files: list[str]) -> dict[str, Any]:
        """Fix a bug in the codebase.
        
        Args:
            bug_description: Description of the bug
            related_files: List of relevant file paths
            
        Returns:
            Bug fix proposal
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenHands API key not configured",
                "fix": {},
            }
        
        files_str = "\n".join([f"- {f}" for f in related_files])
        
        task = f"""
Fix the following bug:

Bug: {bug_description}

Related files:
{files_str}

Analyze the issue and provide the fix.
"""
        
        try:
            from app.services import get_openhands_client
            client = get_openhands_client()
            
            result = await client.run_task(
                task=task,
                agent_id="code-bugfix",
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                }
            
            return {
                "success": True,
                "fix": result.get("result", ""),
                "bug_description": bug_description,
            }
        except Exception as e:
            logger.error(f"OpenHands bug fix error: {e}")
            return {
                "success": False,
                "error": str(e),
            }


# Global instance
_development_engine: Optional[OpenHandsEngine] = None


def get_openhands_engine() -> OpenHandsEngine:
    """Get the OpenHands development engine instance."""
    global _development_engine
    
    if _development_engine is None:
        _development_engine = OpenHandsEngine()
    
    return _development_engine
