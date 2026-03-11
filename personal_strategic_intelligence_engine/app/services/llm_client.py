"""LLM Client abstraction layer.

This module provides a clean abstraction for LLM interactions.
The agent logic calls this service, not provider SDKs directly.
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClientBase(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a completion from messages."""
        pass

    @abstractmethod
    async def complete_with_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate a JSON completion from messages."""
        pass


class OpenAIClient(LLMClientBase):
    """OpenAI LLM client implementation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the OpenAI client."""
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.default_model
        
        if not self.api_key:
            logger.warning("OpenAI API key not configured. Using mock responses.")

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a completion from messages using OpenAI."""
        if not self.api_key:
            return self._mock_complete(messages)
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._mock_complete(messages)

    async def complete_with_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate a JSON completion from messages using OpenAI."""
        if not self.api_key:
            return self._mock_json_complete(messages)
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            # Add JSON instruction to messages
            json_messages = messages + [
                {"role": "user", "content": "Respond with valid JSON only, no markdown."}
            ]
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=json_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._mock_json_complete(messages)

    def _mock_complete(self, messages: list[dict[str, str]]) -> str:
        """Generate a mock completion for testing."""
        last_message = messages[-1]["content"] if messages else ""
        return f"Based on my analysis of: {last_message[:100]}... I recommend a balanced approach considering all factors."

    def _mock_json_complete(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Generate a mock JSON completion for testing."""
        return {
            "summary_judgment": "Consider a balanced approach",
            "main_recommendation": "Proceed with moderate risk",
            "supporting_reasons": ["Reason 1", "Reason 2"],
            "main_risks": ["Risk 1"],
            "tradeoffs": ["Tradeoff 1"],
            "confidence_score": 7.0,
        }


class AnthropicClient(LLMClientBase):
    """Anthropic Claude LLM client implementation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the Anthropic client."""
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or "claude-3-opus-20240229"
        
        if not self.api_key:
            logger.warning("Anthropic API key not configured. Using mock responses.")

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a completion from messages using Anthropic."""
        if not self.api_key:
            return self._mock_complete(messages)
        
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            
            # Convert messages format
            system = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
            anthropic_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in messages if m["role"] != "system"
            ]
            
            response = await client.messages.create(
                model=self.model,
                system=system,
                messages=anthropic_messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._mock_complete(messages)

    async def complete_with_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate a JSON completion from messages using Anthropic."""
        if not self.api_key:
            return self._mock_json_complete(messages)
        
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            
            # Add JSON instruction to last message
            system = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
            anthropic_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in messages if m["role"] != "system"
            ]
            
            # Add JSON instruction
            if anthropic_messages:
                anthropic_messages[-1]["content"] += "\n\nRespond with valid JSON only."
            
            response = await client.messages.create(
                model=self.model,
                system=system,
                messages=anthropic_messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
            content = response.content[0].text
            return json.loads(content)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._mock_json_complete(messages)

    def _mock_complete(self, messages: list[dict[str, str]]) -> str:
        """Generate a mock completion for testing."""
        last_message = messages[-1]["content"] if messages else ""
        return f"Based on my analysis of: {last_message[:100]}... I recommend a balanced approach considering all factors."

    def _mock_json_complete(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Generate a mock JSON completion for testing."""
        return {
            "summary_judgment": "Consider a balanced approach",
            "main_recommendation": "Proceed with moderate risk",
            "supporting_reasons": ["Reason 1", "Reason 2"],
            "main_risks": ["Risk 1"],
            "tradeoffs": ["Tradeoff 1"],
            "confidence_score": 7.0,
        }


class MockLLMClient(LLMClientBase):
    """Mock LLM client for testing without API calls."""

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a mock completion."""
        last_message = messages[-1]["content"] if messages else ""
        return f"Mock response for: {last_message[:100]}..."

    async def complete_with_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate a mock JSON completion."""
        return {
            "summary_judgment": "Mock recommendation",
            "main_recommendation": "Proceed with caution",
            "supporting_reasons": ["Mock reason 1", "Mock reason 2"],
            "main_risks": ["Mock risk 1"],
            "tradeoffs": ["Mock tradeoff 1"],
            "confidence_score": 5.0,
        }


def get_llm_client() -> LLMClientBase:
    """Get the configured LLM client based on settings."""
    settings = get_settings()
    
    if settings.llm_provider == "openai":
        return OpenAIClient()
    elif settings.llm_provider == "anthropic":
        return AnthropicClient()
    else:
        return MockLLMClient()


async def get_llm_client_async() -> LLMClientBase:
    """Get the configured LLM client (async version)."""
    return get_llm_client()
