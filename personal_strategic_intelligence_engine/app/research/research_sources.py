"""Research sources for external data gathering."""
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from app.security.secret_manager import get_secret_manager
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseResearchSource:
    """Base class for research sources."""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = False
    
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Query the source."""
        raise NotImplementedError
    
    async def is_available(self) -> bool:
        """Check if source is available."""
        return self.enabled


class FinancialDataSource(BaseResearchSource):
    """Financial data research source."""
    
    def __init__(self):
        super().__init__("financial_data")
        self._check_availability()
    
    def _check_availability(self):
        """Check if financial data sources are available."""
        secret_manager = get_secret_manager()
        has_alpha_vantage = secret_manager.has_secret("ALPHAVANTAGE_API_KEY")
        has_polygon = secret_manager.has_secret("POLYGON_API_KEY")
        
        self.enabled = has_alpha_vantage or has_polygon
    
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Query financial data."""
        
        if not self.enabled:
            return {
                "success": False,
                "error": "No financial API keys configured",
                "data": [],
            }
        
        # In a real implementation, this would call financial APIs
        # For now, return mock data
        return {
            "success": True,
            "query": query,
            "data": [
                {
                    "type": "market_overview",
                    "summary": "Market conditions analysis for: " + query,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "source": self.name,
        }


class EconomicDataSource(BaseResearchSource):
    """Economic data research source."""
    
    def __init__(self):
        super().__init__("economic_data")
        self._check_availability()
    
    def _check_availability(self):
        """Check if economic data sources are available."""
        secret_manager = get_secret_manager()
        has_fred = secret_manager.has_secret("FRED_API_KEY")
        
        self.enabled = has_fred
    
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Query economic data."""
        
        if not self.enabled:
            return {
                "success": False,
                "error": "No economic API keys configured",
                "data": [],
            }
        
        return {
            "success": True,
            "query": query,
            "data": [
                {
                    "type": "economic_indicator",
                    "summary": "Economic analysis for: " + query,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "source": self.name,
        }


class KnowledgeBaseSource(BaseResearchSource):
    """Internal knowledge base research source."""
    
    def __init__(self):
        super().__init__("knowledge_base")
        self.enabled = True
    
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Query internal knowledge base."""
        
        return {
            "success": True,
            "query": query,
            "data": [
                {
                    "type": "internal_knowledge",
                    "summary": f"Internal knowledge analysis for: {query}",
                    "sources": ["knowledge_graph", "strategic_plans", "past_decisions"],
                }
            ],
            "source": self.name,
        }


class LLMSummarizationSource(BaseResearchSource):
    """LLM-powered research source."""
    
    def __init__(self):
        super().__init__("llm_summarization")
        self._check_availability()
    
    def _check_availability(self):
        """Check if LLM is available."""
        secret_manager = get_secret_manager()
        has_openai = secret_manager.has_secret("OPENAI_API_KEY")
        has_anthropic = secret_manager.has_secret("ANTHROPIC_API_KEY")
        
        self.enabled = has_openai or has_anthropic
    
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Query LLM for analysis."""
        
        if not self.enabled:
            return {
                "success": False,
                "error": "No LLM API keys configured",
                "data": [],
            }
        
        # In a real implementation, this would call an LLM
        return {
            "success": True,
            "query": query,
            "data": [
                {
                    "type": "llm_analysis",
                    "summary": f"AI-generated analysis for: {query}",
                    "confidence": 0.75,
                    "considerations": [
                        "Multiple factors should be evaluated",
                        "Long-term implications considered",
                        "Risk factors identified",
                    ],
                }
            ],
            "source": self.name,
        }


class ResearchSourceManager:
    """Manages research sources."""
    
    def __init__(self):
        self.sources: Dict[str, BaseResearchSource] = {
            "financial": FinancialDataSource(),
            "economic": EconomicDataSource(),
            "knowledge_base": KnowledgeBaseSource(),
            "llm": LLMSummarizationSource(),
        }
    
    def get_available_sources(self) -> List[str]:
        """Get list of available sources."""
        return [name for name, source in self.sources.items() if source.enabled]
    
    async def query_all(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Query multiple sources."""
        
        if source_types is None:
            source_types = self.get_available_sources()
        
        results = []
        
        for source_name in source_types:
            source = self.sources.get(source_name)
            if source and source.enabled:
                try:
                    result = await source.query(query)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error querying source {source_name}: {e}")
                    results.append({
                        "success": False,
                        "source": source_name,
                        "error": str(e),
                    })
        
        return results
    
    async def query_with_timeout(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        timeout_seconds: int = 30,
    ) -> List[Dict[str, Any]]:
        """Query sources with timeout."""
        
        try:
            results = await asyncio.wait_for(
                self.query_all(query, source_types),
                timeout=timeout_seconds,
            )
            return results
        except asyncio.TimeoutError:
            logger.warning(f"Research query timed out after {timeout_seconds}s")
            return [{
                "success": False,
                "error": "Query timeout",
                "data": [],
            }]


# Global source manager
_source_manager: Optional[ResearchSourceManager] = None


def get_source_manager() -> ResearchSourceManager:
    """Get research source manager."""
    global _source_manager
    
    if _source_manager is None:
        _source_manager = ResearchSourceManager()
    
    return _source_manager
