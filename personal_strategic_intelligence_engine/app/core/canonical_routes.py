"""PSIE Canonical Route Map & Deprecation Layer.

This module defines the canonical route ownership and provides deprecation
handling for legacy routes per V47-006.

Canonical Architecture:
- Executive Layer: /dashboard, /outputs, /kernel, /autonomy
- Observation Layer: /signals, /detection, /intelligence-bus
- Intelligence Layer: /intelligence, /research, /optimization, /simulation
- Strategy Layer: /strategies, /debate, /strategy-lab
- Planning Layer: /planning
- Governance Layer: /governance, /decisions, /reviews, /board
- Execution Layer: /execution, /orchestration
- Learning Layer: /learning
- Knowledge Layer: /knowledge
- Platform Layer: /auth, /admin, /users, /profile, /security, /observability, /health

Finance Domain:
- /finance, /finance/intelligence, /finance/simulation, /finance/governance, /finance-ops
- /options-agent, /options-intelligence
"""
from typing import Any, Dict, List, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

# Canonical route ownership map
CANONICAL_ROUTES: Dict[str, Dict[str, Any]] = {
    # Executive Layer
    "/dashboard": {
        "layer": "Executive",
        "owner": "Executive Dashboard",
        "description": "CEO command interface, system overview, approval workflows",
        "tier": 1,  # Public
    },
    "/outputs": {
        "layer": "Executive", 
        "owner": "System Outputs",
        "description": "Intelligence output reports",
        "tier": 1,
    },
    "/kernel": {
        "layer": "Executive",
        "owner": "Kernel",
        "description": "System core, mode management, cycle execution",
        "tier": 2,  # Internal
    },
    "/autonomy": {
        "layer": "Executive",
        "owner": "Autonomy Engine",
        "description": "Autonomous cycle management",
        "tier": 2,
    },
    
    # Observation Layer
    "/signals": {
        "layer": "Observation",
        "owner": "Signal Bus",
        "description": "Signal ingestion and classification",
        "tier": 2,
    },
    "/detection": {
        "layer": "Observation",
        "owner": "Detection Engine",
        "description": "Opportunity and risk detection",
        "tier": 2,
    },
    "/intelligence-bus": {
        "layer": "Observation",
        "owner": "Intelligence Bus",
        "description": "Event routing and distribution",
        "tier": 2,
    },
    
    # Intelligence Layer
    "/intelligence": {
        "layer": "Intelligence",
        "owner": "Intelligence Engine",
        "description": "Forecasting, trends, risk analysis",
        "tier": 1,
    },
    "/research": {
        "layer": "Intelligence",
        "owner": "Research Engine",
        "description": "Research reports and analysis",
        "tier": 1,
    },
    "/optimization": {
        "layer": "Intelligence",
        "owner": "Optimization Engine",
        "description": "Domain optimization",
        "tier": 2,
    },
    "/simulation": {
        "layer": "Intelligence",
        "owner": "Simulation Engine",
        "description": "Scenario simulation",
        "tier": 2,
    },
    
    # Strategy Layer
    "/strategies": {
        "layer": "Strategy",
        "owner": "Strategy Pipeline",
        "description": "Production strategy lifecycle",
        "tier": 1,
    },
    "/debate": {
        "layer": "Strategy",
        "owner": "Debate Engine",
        "description": "Multi-agent strategy debate",
        "tier": 1,
    },
    "/strategy-lab": {
        "layer": "Strategy",
        "owner": "Strategy Lab",
        "description": "Experimental strategy research",
        "tier": 2,
    },
    
    # Planning Layer
    "/planning": {
        "layer": "Planning",
        "owner": "Planning Engine",
        "description": "Long-term plans and action sequencing",
        "tier": 1,
    },
    
    # Governance Layer
    "/governance": {
        "layer": "Governance",
        "owner": "Governance Service",
        "description": "Policy enforcement, goals, plans",
        "tier": 1,
    },
    "/decisions": {
        "layer": "Governance",
        "owner": "Decision Journal",
        "description": "Decision records and audit trail",
        "tier": 1,
    },
    "/reviews": {
        "layer": "Governance",
        "owner": "Review Engine",
        "description": "Strategic review cycles",
        "tier": 1,
    },
    "/board": {
        "layer": "Governance",
        "owner": "Board Service",
        "description": "Board meeting management",
        "tier": 1,
    },
    
    # Execution Layer
    "/execution": {
        "layer": "Execution",
        "owner": "Execution Controller",
        "description": "Public execution interface",
        "tier": 1,
    },
    "/execution-engine": {
        "layer": "Execution",
        "owner": "Execution Engine",
        "description": "Internal execution service (legacy compatibility)",
        "tier": 2,
        "deprecated": True,
        "canonical": "/execution",
    },
    "/orchestration": {
        "layer": "Execution",
        "owner": "Orchestration Engine",
        "description": "Workflow automation",
        "tier": 2,
    },
    
    # Learning Layer
    "/learning": {
        "layer": "Learning",
        "owner": "Learning Engine",
        "description": "Adaptive system memory, pattern discovery",
        "tier": 1,
    },
    
    # Knowledge Layer
    "/knowledge": {
        "layer": "Knowledge",
        "owner": "Knowledge Graph",
        "description": "Entity graph and relationships",
        "tier": 1,
    },
    
    # Platform Layer
    "/auth": {
        "layer": "Platform",
        "owner": "Auth Service",
        "description": "Authentication",
        "tier": 3,  # Infrastructure
    },
    "/admin": {
        "layer": "Platform",
        "owner": "Admin Service",
        "description": "System administration",
        "tier": 3,
    },
    "/users": {
        "layer": "Platform",
        "owner": "User Service",
        "description": "User management",
        "tier": 3,
    },
    "/profile": {
        "layer": "Platform",
        "owner": "Profile Service",
        "description": "User profiles",
        "tier": 3,
    },
    "/security": {
        "layer": "Platform",
        "owner": "Security Service",
        "description": "Security and permissions",
        "tier": 3,
    },
    "/observability": {
        "layer": "Platform",
        "owner": "Observability Service",
        "description": "Monitoring and metrics",
        "tier": 3,
    },
    "/health": {
        "layer": "Platform",
        "owner": "Health Service",
        "description": "Health checks",
        "tier": 3,
    },
    
    # Audit (Legacy)
    "/audit": {
        "layer": "Platform",
        "owner": "Audit Service",
        "description": "Legacy audit endpoints (use /observability)",
        "tier": 3,
        "deprecated": True,
        "canonical": "/observability",
    },
    
    # Finance Domain
    "/finance": {
        "layer": "Finance",
        "owner": "Finance Core",
        "description": "Personal financial state",
        "tier": 1,
    },
    "/finance/intelligence": {
        "layer": "Finance",
        "owner": "Finance Intelligence",
        "description": "Financial analysis and signals",
        "tier": 1,
    },
    "/finance/simulation": {
        "layer": "Finance",
        "owner": "Finance Simulation",
        "description": "Financial scenario modeling",
        "tier": 2,
    },
    "/finance/governance": {
        "layer": "Finance",
        "owner": "Finance Governance",
        "description": "Financial decisions and audit",
        "tier": 1,
    },
    "/finance-ops": {
        "layer": "Finance",
        "owner": "Finance Operations",
        "description": "Bills, expenses, subscriptions",
        "tier": 1,
    },
    "/options-agent": {
        "layer": "Finance",
        "owner": "Options Agent",
        "description": "Options trading signals",
        "tier": 1,
    },
    "/options-intelligence": {
        "layer": "Finance",
        "owner": "Options Intelligence",
        "description": "Options market analysis",
        "tier": 1,
    },
}

# Legacy route mappings (old -> new)
LEGACY_ROUTE_MAPPINGS: Dict[str, str] = {
    "/execution-engine": "/execution",
    "/audit": "/observability",
}


def get_route_info(prefix: str) -> Optional[Dict[str, Any]]:
    """Get canonical route information."""
    return CANONICAL_ROUTES.get(prefix)


def is_route_deprecated(prefix: str) -> bool:
    """Check if a route prefix is deprecated."""
    route_info = CANONICAL_ROUTES.get(prefix, {})
    return route_info.get("deprecated", False)


def get_canonical_route(prefix: str) -> Optional[str]:
    """Get the canonical route for a deprecated prefix."""
    route_info = CANONICAL_ROUTES.get(prefix, {})
    return route_info.get("canonical")


def get_layer_routes(layer: str) -> List[Dict[str, Any]]:
    """Get all routes for an architectural layer."""
    return [
        {"prefix": prefix, **info}
        for prefix, info in CANONICAL_ROUTES.items()
        if info.get("layer") == layer
    ]


def get_tier_routes(tier: int) -> List[Dict[str, Any]]:
    """Get all routes for a specific tier."""
    return [
        {"prefix": prefix, **info}
        for prefix, info in CANONICAL_ROUTES.items()
        if info.get("tier") == tier
    ]


def get_deprecated_routes() -> List[Dict[str, Any]]:
    """Get all deprecated routes."""
    return [
        {"prefix": prefix, **info}
        for prefix, info in CANONICAL_ROUTES.items()
        if info.get("deprecated", False)
    ]


def create_deprecation_headers(prefix: str) -> Dict[str, str]:
    """Create deprecation headers for a legacy route."""
    canonical = get_canonical_route(prefix)
    return {
        "X-PSIE-Deprecated": "true",
        "X-PSIE-Canonical": canonical or "",
    }
