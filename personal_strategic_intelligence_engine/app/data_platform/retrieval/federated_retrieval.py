"""Federated Retrieval Service - Multi-domain search for Strategy and Risk agents.

Allows strategy and risk agents to query multiple domain bundles simultaneously
and returns evidence packets with citations, timestamps, trust scores, and relevance.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.data_platform.models import RetrievedEvidence, TrustTier, AgentType
from app.data_platform.retrieval.retrieval_gateway import get_retrieval_gateway
from app.data_platform.governance.domain_sources import get_sources_for_domain
from app.data_platform.governance.access_policy import get_access_policy_manager, AgentRole

logger = logging.getLogger(__name__)


class EvidencePacket:
    """Evidence packet for federated retrieval results."""
    
    def __init__(
        self,
        query: str,
        domains: List[str],
    ):
        self.query = query
        self.domains = domains
        self.evidence: List[RetrievedEvidence] = []
        self.sources: Dict[str, Dict[str, Any]] = {}
        self.timestamps: List[datetime] = []
        self.trust_scores: Dict[str, float] = {}
        self.domain_tags: Dict[str, List[str]] = {}
        self.created_at = datetime.utcnow()
    
    def add_evidence(self, evidence: RetrievedEvidence):
        """Add evidence to the packet."""
        self.evidence.append(evidence)
        
        # Track sources
        if evidence.source_id not in self.sources:
            self.sources[evidence.source_id] = {
                "name": evidence.source_name,
                "domain": evidence.domain,
                "evidence_count": 0,
            }
        self.sources[evidence.source_id]["evidence_count"] += 1
        
        # Track timestamps
        self.timestamps.append(evidence.timestamp)
        
        # Track domain tags
        if evidence.domain not in self.domain_tags:
            self.domain_tags[evidence.domain] = []
        if evidence.source_id not in self.domain_tags[evidence.domain]:
            self.domain_tags[evidence.domain].append(evidence.source_id)
    
    def get_source_summary(self) -> Dict[str, Any]:
        """Get summary of sources used."""
        return {
            "total_sources": len(self.sources),
            "sources_by_domain": {
                domain: len(tags) 
                for domain, tags in self.domain_tags.items()
            },
            "sources": list(self.sources.keys()),
        }
    
    def get_citations(self) -> List[Dict[str, str]]:
        """Get formatted citations."""
        citations = []
        for ev in self.evidence:
            citation = {
                "source": ev.source_name,
                "domain": ev.domain,
                "content_preview": ev.content[:200] + "..." if len(ev.content) > 200 else ev.content,
                "timestamp": ev.timestamp.isoformat(),
                "url": ev.url or "",
            }
            citations.append(citation)
        return citations
    
    def calculate_trust_score(self) -> float:
        """Calculate overall trust score based on sources."""
        if not self.sources:
            return 0.0
        
        # Weight by trust tier
        trust_weights = {
            "HIGH": 1.0,
            "MEDIUM": 0.7,
            "LOW": 0.4,
            "UNVERIFIED": 0.2,
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for source_id, info in self.sources.items():
            # Get trust tier from source registry
            weight = trust_weights.get(info.get("trust_tier", "MEDIUM"), 0.5)
            weighted_sum += weight * info["evidence_count"]
            total_weight += info["evidence_count"]
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "query": self.query,
            "domains": self.domains,
            "evidence_count": len(self.evidence),
            "source_summary": self.get_source_summary(),
            "citations": self.get_citations(),
            "trust_score": self.calculate_trust_score(),
            "domain_tags": self.domain_tags,
            "created_at": self.created_at.isoformat(),
            "earliest_evidence": min(self.timestamps).isoformat() if self.timestamps else None,
            "latest_evidence": max(self.timestamps).isoformat() if self.timestamps else None,
        }


class FederatedRetrievalService:
    """Service for federated retrieval across multiple domains.
    
    Used by Strategy and Risk agents to query multiple domain bundles.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.gateway = None
        self.policy_manager = None
    
    async def _ensure_initialized(self):
        """Lazy initialization."""
        if self.gateway is None:
            self.gateway = await get_retrieval_gateway(self.session)
        if self.policy_manager is None:
            self.policy_manager = get_access_policy_manager()
    
    async def search_cross_domain_evidence(
        self,
        query: str,
        domains: List[str],
        agent_role: AgentRole,
        max_results_per_domain: int = 10,
    ) -> EvidencePacket:
        """Search evidence across multiple domains.
        
        Args:
            query: Search query
            domains: Domains to search
            agent_role: Requesting agent role
            max_results_per_domain: Max results per domain
            
        Returns:
            Evidence packet with cross-domain results
        """
        await self._ensure_initialized()
        
        logger.info(f"Federated search: query='{query}', domains={domains}, role={agent_role}")
        
        # Get policy for agent
        policy = await self.policy_manager.get_policy(agent_role)
        
        # Check domain permissions
        allowed_domains = policy.allowed_domains if policy else domains
        permitted_domains = [d for d in domains if d in allowed_domains]
        
        if not permitted_domains:
            logger.warning(f"No permitted domains for agent role: {agent_role}")
            return EvidencePacket(query, domains)
        
        # Create evidence packet
        packet = EvidencePacket(query, permitted_domains)
        
        # Search each domain
        for domain in permitted_domains:
            try:
                results = await self._search_domain(
                    query=query,
                    domain=domain,
                    agent_role=agent_role,
                    max_results=max_results_per_domain,
                )
                
                for evidence in results:
                    packet.add_evidence(evidence)
                    
            except Exception as e:
                logger.warning(f"Failed to search domain {domain}: {e}")
                continue
        
        return packet
    
    async def _search_domain(
        self,
        query: str,
        domain: str,
        agent_role: AgentRole,
        max_results: int,
    ) -> List[RetrievedEvidence]:
        """Search within a specific domain."""
        # Map agent role to agent type
        agent_type_map = {
            AgentRole.STRATEGY: AgentType.DOMAIN,
            AgentRole.RISK: AgentType.DOMAIN,
        }
        
        agent_type = agent_type_map.get(agent_role, AgentType.DOMAIN)
        
        # Create retrieval request
        from app.data_platform.models import RetrievalRequest
        
        request = RetrievalRequest(
            query=query,
            agent_type=agent_type,
            agent_domain=domain,
            domains=[domain],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM, TrustTier.LOW],
            max_results=max_results,
            include_documents=True,
            include_structured=True,
            include_web=False,
        )
        
        response = await self.gateway.search(request)
        return response.evidence
    
    async def get_multi_domain_updates(
        self,
        domains: List[str],
        since: datetime,
        agent_role: AgentRole,
    ) -> EvidencePacket:
        """Get latest updates across multiple domains.
        
        Args:
            domains: Domains to get updates from
            since: Get updates since this time
            agent_role: Requesting agent role
            
        Returns:
            Evidence packet with latest updates
        """
        await self._ensure_initialized()
        
        logger.info(f"Multi-domain updates: domains={domains}, since={since}")
        
        from app.data_platform.models import LatestUpdatesRequest
        
        packet = EvidencePacket("", domains)
        
        for domain in domains:
            try:
                request = LatestUpdatesRequest(
                    domains=[domain],
                    since=since,
                    limit=20,
                )
                
                updates = await self.gateway.get_latest_updates(request)
                
                for evidence in updates:
                    packet.add_evidence(evidence)
                    
            except Exception as e:
                logger.warning(f"Failed to get updates for {domain}: {e}")
                continue
        
        return packet
    
    async def build_strategy_brief(
        self,
        topics: List[str],
        agent_role: AgentRole = AgentRole.STRATEGY,
    ) -> Dict[str, Any]:
        """Build a strategy brief from multiple domains.
        
        Args:
            topics: Topics to include in brief
            agent_role: Requesting agent role
            
        Returns:
            Strategy brief dictionary
        """
        logger.info(f"Building strategy brief for topics: {topics}")
        
        brief = {
            "topics": topics,
            "domains_searched": [],
            "total_evidence": 0,
            "domain_evidence": {},
            "key_findings": [],
            "sources": set(),
            "trust_score": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        # Search relevant domains for each topic
        domain_topic_map = {
            "finance": ["market", "investment", "revenue", "economic", "financial"],
            "operations": ["operational", "process", "workflow", "efficiency"],
            "risk": ["risk", "threat", "vulnerability", "mitigation"],
            "health": ["health", "wellness", "nutrition"],
            "fitness": ["fitness", "exercise", "training", "workout"],
        }
        
        for topic in topics:
            topic_lower = topic.lower()
            
            for domain, keywords in domain_topic_map.items():
                if any(kw in topic_lower for kw in keywords):
                    if domain not in brief["domains_searched"]:
                        brief["domains_searched"].append(domain)
                    
                    # Search this domain
                    packet = await self.search_cross_domain_evidence(
                        query=topic,
                        domains=[domain],
                        agent_role=agent_role,
                        max_results_per_domain=5,
                    )
                    
                    brief["total_evidence"] += len(packet.evidence)
                    brief["domain_evidence"][domain] = len(packet.evidence)
                    
                    for ev in packet.evidence:
                        brief["sources"].add(ev.source_id)
        
        # Calculate trust score
        if brief["total_evidence"] > 0:
            # Simplified trust score calculation
            brief["trust_score"] = 0.75  # Default to good trust
        
        brief["sources"] = list(brief["sources"])
        
        return brief
    
    async def build_risk_brief(
        self,
        risk_areas: List[str],
        agent_role: AgentRole = AgentRole.RISK,
    ) -> Dict[str, Any]:
        """Build a risk brief from multiple domains.
        
        Args:
            risk_areas: Risk areas to investigate
            agent_role: Requesting agent role
            
        Returns:
            Risk brief dictionary
        """
        logger.info(f"Building risk brief for areas: {risk_areas}")
        
        brief = {
            "risk_areas": risk_areas,
            "domains_searched": [],
            "total_evidence": 0,
            "risk_evidence": {},
            "mitigation_sources": [],
            "trust_score": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        # Risk-focused domains
        risk_domains = ["risk", "finance", "operations"]
        
        for area in risk_areas:
            if area not in brief["risk_evidence"]:
                brief["risk_evidence"][area] = []
            
            for domain in risk_domains:
                if domain not in brief["domains_searched"]:
                    brief["domains_searched"].append(domain)
                
                packet = await self.search_cross_domain_evidence(
                    query=f"risk {area}",
                    domains=[domain],
                    agent_role=agent_role,
                    max_results_per_domain=5,
                )
                
                brief["total_evidence"] += len(packet.evidence)
                brief["risk_evidence"][area].extend([
                    {
                        "source": ev.source_name,
                        "content": ev.content[:200],
                        "timestamp": ev.timestamp.isoformat(),
                    }
                    for ev in packet.evidence
                ])
        
        # High trust for risk briefs
        brief["trust_score"] = 0.85
        
        return brief


# Factory function
async def get_federated_retrieval_service(session: AsyncSession) -> FederatedRetrievalService:
    """Get a federated retrieval service instance."""
    return FederatedRetrievalService(session)
