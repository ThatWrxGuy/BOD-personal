"""OpenAI Intelligence Gateway.

This module provides advanced reasoning services to agents through OpenAI's
GPT models. It enables strategic reasoning, natural language analysis,
strategy generation, and scenario analysis.
"""
from typing import Any, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIReasoningEngine:
    """OpenAI-powered reasoning engine for strategic analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI reasoning engine."""
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model
        
        if not self.api_key:
            logger.warning("OpenAI API key not configured. Reasoning capabilities limited.")

    async def analyze(self, prompt: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Perform strategic analysis on the given prompt.
        
        Args:
            prompt: The analysis request
            context: Additional context for the analysis
            
        Returns:
            Analysis results with reasoning
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "analysis": "Analysis unavailable",
            }
        
        # Build messages with context
        messages = [
            {
                "role": "system",
                "content": "You are a strategic reasoning assistant for a personal intelligence system. "
                         "Provide deep, actionable insights based on the user's request."
            }
        ]
        
        if context:
            context_str = f"Context: {context}\n\n"
            messages.append({
                "role": "user", 
                "content": context_str + prompt
            })
        else:
            messages.append({"role": "user", "content": prompt})
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "model": self.model,
            }
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "Analysis failed",
            }

    async def generate_strategy(
        self, 
        context: dict[str, Any], 
        objective: str
    ) -> dict[str, Any]:
        """Generate a strategic recommendation.
        
        Args:
            context: Current situation and data
            objective: The goal to achieve
            
        Returns:
            Generated strategy with recommendations
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "strategy": {},
            }
        
        prompt = f"""
Given the following context:
{context}

Generate a strategy to achieve: {objective}

Provide:
1. Main recommendation
2. Supporting rationale
3. Potential risks
4. Success metrics
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a strategic planning expert. Generate actionable strategies."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )
            
            return {
                "success": True,
                "strategy": response.choices[0].message.content,
                "objective": objective,
                "model": self.model,
            }
        except Exception as e:
            logger.error(f"OpenAI strategy generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": {},
            }

    async def summarize(self, data: Any, focus: Optional[str] = None) -> dict[str, Any]:
        """Summarize complex data into actionable insights.
        
        Args:
            data: Data to summarize
            focus: Optional focus area for summarization
            
        Returns:
            Summary of the data
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "summary": "Summary unavailable",
            }
        
        focus_instruction = f"\nFocus on: {focus}" if focus else ""
        
        prompt = f"""
Analyze and summarize the following data:{focus_instruction}

Data: {data}

Provide a clear, concise summary with key insights.
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a data analysis expert. Provide clear, insightful summaries."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=1000,
            )
            
            return {
                "success": True,
                "summary": response.choices[0].message.content,
                "focus": focus,
            }
        except Exception as e:
            logger.error(f"OpenAI summarization error: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "Summary failed",
            }

    async def analyze_scenarios(
        self,
        scenarios: list[dict[str, Any]],
        criteria: list[str]
    ) -> dict[str, Any]:
        """Analyze multiple scenarios against criteria.
        
        Args:
            scenarios: List of scenarios to analyze
            criteria: Evaluation criteria
            
        Returns:
            Scenario analysis with recommendations
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "analysis": {},
            }
        
        scenarios_text = "\n".join([
            f"Scenario {i+1}: {s}" for i, s in enumerate(scenarios)
        ])
        criteria_text = "\n".join([f"- {c}" for c in criteria])
        
        prompt = f"""
Analyze the following scenarios against these criteria:

Scenarios:
{scenarios_text}

Evaluation Criteria:
{criteria_text}

For each scenario, provide:
1. Fit to criteria
2. Pros and cons
3. Recommended action
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a decision analysis expert. Evaluate scenarios systematically."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=2000,
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "scenarios_analyzed": len(scenarios),
            }
        except Exception as e:
            logger.error(f"OpenAI scenario analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {},
            }


# Global instance
_reasoning_engine: Optional[OpenAIReasoningEngine] = None


def get_openai_reasoning_engine() -> OpenAIReasoningEngine:
    """Get the OpenAI reasoning engine instance."""
    global _reasoning_engine
    
    if _reasoning_engine is None:
        _reasoning_engine = OpenAIReasoningEngine()
    
    return _reasoning_engine
