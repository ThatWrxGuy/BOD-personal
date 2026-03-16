"""OpenHands AI Agent API client.

This module provides integration with the OpenHands Cloud API for 
advanced agentic AI operations.
"""
import json
from typing import Any, Optional

import aiohttp

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenHandsClient:
    """Client for OpenHands Cloud API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenHands client."""
        settings = get_settings()
        self.api_key = api_key or settings.openhands_api_key
        self.base_url = "https://api.openhands.ai/v1"
        
        if not self.api_key:
            logger.warning("OpenHands API key not configured.")

    async def create_session(
        self,
        agent_id: str = "default",
        instructions: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new agent session."""
        if not self.api_key:
            return {"error": "OpenHands API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "agent_id": agent_id,
            "instructions": instructions or "You are a helpful AI assistant.",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/sessions",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenHands API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"OpenHands connection error: {e}")
            return {"error": str(e)}

    async def send_message(
        self,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Send a message to an existing session."""
        if not self.api_key:
            return {"error": "OpenHands API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "message": message,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/sessions/{session_id}/messages",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenHands API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"OpenHands connection error: {e}")
            return {"error": str(e)}

    async def run_task(
        self,
        task: str,
        agent_id: str = "general-purpose",
    ) -> dict[str, Any]:
        """Run a single task using OpenHands agent.
        
        This is a convenience method that creates a session,
        runs the task, and returns the result.
        """
        if not self.api_key:
            return {"error": "OpenHands API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "agent_id": agent_id,
            "task": task,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/run",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenHands API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"OpenHands connection error: {e}")
            return {"error": str(e)}

    async def get_agent_capabilities(self) -> dict[str, Any]:
        """Get available OpenHands agent capabilities."""
        if not self.api_key:
            return {"error": "OpenHands API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/agents",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenHands API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"OpenHands connection error: {e}")
            return {"error": str(e)}


def get_openhands_client() -> OpenHandsClient:
    """Get an OpenHands client instance."""
    return OpenHandsClient()
