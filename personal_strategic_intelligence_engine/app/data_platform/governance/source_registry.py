"""Source Registry - Canonical source management for the data platform.

The Source Registry records all data sources available to agents,
including metadata for access control, trust classification, and governance.
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.data_platform.models import SourceRecord, SourceType, TrustTier

logger = logging.getLogger(__name__)


class SourceRegistry:
    """Manages data source registration and lookup.
    
    The source registry provides:
    - Source registration and updates
    - Source lookup by various filters
    - Trust tier management
    - Access tag management
    """
    
    def __init__(self):
        """Initialize the source registry."""
        self._sources: Dict[str, SourceRecord] = {}
        self._initialize_default_sources()
    
    def _initialize_default_sources(self):
        """Initialize with default platform sources."""
        default_sources = [
            # Internal structured sources
            SourceRecord(
                source_id="internal_strategy",
                source_name="Strategic Plans Database",
                domain="strategy",
                source_type=SourceType.RELATIONAL,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain", "executive", "planning"],
            ),
            SourceRecord(
                source_id="internal_finance",
                source_name="Financial Records Database",
                domain="finance",
                source_type=SourceType.RELATIONAL,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain", "executive"],
            ),
            SourceRecord(
                source_id="internal_health",
                source_name="Health Metrics Database",
                domain="health",
                source_type=SourceType.RELATIONAL,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain"],
            ),
            SourceRecord(
                source_id="internal_operations",
                source_name="Operations Database",
                domain="operations",
                source_type=SourceType.RELATIONAL,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain", "executive"],
            ),
            SourceRecord(
                source_id="internal_risk",
                source_name="Risk Register",
                domain="risk",
                source_type=SourceType.RELATIONAL,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain", "executive", "governance"],
            ),
            # Knowledge base
            SourceRecord(
                source_id="knowledge_graph",
                source_name="Personal Knowledge Graph",
                domain="general",
                source_type=SourceType.VECTOR,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain", "executive", "intelligence"],
            ),
            SourceRecord(
                source_id="strategic_doctrine",
                source_name="Strategic Doctrine Library",
                domain="strategy",
                source_type=SourceType.DOCUMENT,
                license="internal",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain", "executive", "governance"],
            ),
            # External sources (examples)
            SourceRecord(
                source_id="finance_yahoo",
                source_name="Yahoo Finance",
                domain="finance",
                source_type=SourceType.WEB,
                license="public",
                trust_tier=TrustTier.MEDIUM,
                agent_access_tags=["domain"],
            ),
            SourceRecord(
                source_id="health_nih",
                source_name="NIH Health Data",
                domain="health",
                source_type=SourceType.WEB,
                license="public",
                trust_tier=TrustTier.HIGH,
                agent_access_tags=["domain"],
            ),
        ]
        
        for source in default_sources:
            self._sources[source.source_id] = source
    
    async def register_source(self, source: SourceRecord) -> SourceRecord:
        """Register a new source or update existing."""
        source.updated_at = datetime.utcnow()
        self._sources[source.source_id] = source
        logger.info(f"Registered source: {source.source_id}")
        return source
    
    async def get_source(self, source_id: str) -> Optional[SourceRecord]:
        """Get a source by ID."""
        return self._sources.get(source_id)
    
    async def list_sources(
        self,
        domain: Optional[str] = None,
        source_type: Optional[SourceType] = None,
        trust_tier: Optional[TrustTier] = None,
        enabled_only: bool = True,
    ) -> List[SourceRecord]:
        """List sources with optional filters."""
        results = []
        
        for source in self._sources.values():
            if enabled_only and not source.enabled:
                continue
            if domain and source.domain != domain:
                continue
            if source_type and source.source_type != source_type:
                continue
            if trust_tier and source.trust_tier != trust_tier:
                continue
            results.append(source)
        
        return results
    
    async def get_sources_for_agent(
        self,
        agent_type: str,
        agent_domain: Optional[str] = None,
        trust_tiers: Optional[List[TrustTier]] = None,
    ) -> List[SourceRecord]:
        """Get sources accessible to a specific agent type."""
        if trust_tiers is None:
            trust_tiers = [TrustTier.HIGH, TrustTier.MEDIUM]
        
        results = []
        for source in self._sources.values():
            if not source.enabled:
                continue
            if source.trust_tier not in trust_tiers:
                continue
            if agent_type not in source.agent_access_tags and "*" not in source.agent_access_tags:
                continue
            if agent_domain and source.domain != agent_domain and source.domain != "general":
                continue
            results.append(source)
        
        return results
    
    async def enable_source(self, source_id: str) -> bool:
        """Enable a source."""
        if source_id in self._sources:
            self._sources[source_id].enabled = True
            self._sources[source_id].updated_at = datetime.utcnow()
            return True
        return False
    
    async def disable_source(self, source_id: str) -> bool:
        """Disable a source."""
        if source_id in self._sources:
            self._sources[source_id].enabled = False
            self._sources[source_id].updated_at = datetime.utcnow()
            return True
        return False
    
    async def update_source_tags(self, source_id: str, tags: List[str]) -> bool:
        """Update agent access tags for a source."""
        if source_id in self._sources:
            self._sources[source_id].agent_access_tags = tags
            self._sources[source_id].updated_at = datetime.utcnow()
            return True
        return False


# Singleton instance
_registry: Optional[SourceRegistry] = None


def get_source_registry() -> SourceRegistry:
    """Get the source registry singleton."""
    global _registry
    if _registry is None:
        _registry = SourceRegistry()
    return _registry


def reset_source_registry():
    """Reset the source registry (for testing)."""
    global _registry
    _registry = None
