"""Canonical Routes API - exposes PSIE route architecture.

This module provides API endpoints for the canonical route map
and route metadata per V47-006.
"""
from typing import Optional, List, Dict, Any

from fastapi import APIRouter

from app.core.canonical_routes import (
    CANONICAL_ROUTES,
    get_route_info,
    get_layer_routes,
    get_tier_routes,
    get_deprecated_routes,
    get_canonical_route,
)
from app.core.response_wrapper import success_response
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["canonical-routes"])


@router.get("/routes")
async def get_all_routes():
    """Get all canonical routes."""
    return success_response({
        "routes": CANONICAL_ROUTES,
        "total": len(CANONICAL_ROUTES),
    })


@router.get("/routes/layers")
async def get_routes_by_layer():
    """Get routes grouped by architectural layer."""
    layers = {}
    for prefix, info in CANONICAL_ROUTES.items():
        layer = info.get("layer", "Unknown")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append({"prefix": prefix, **info})
    
    return success_response({"layers": layers})


@router.get("/routes/tiers")
async def get_routes_by_tier():
    """Get routes grouped by tier."""
    return success_response({
        "tier_1_public": get_tier_routes(1),
        "tier_2_internal": get_tier_routes(2),
        "tier_3_infrastructure": get_tier_routes(3),
    })


@router.get("/routes/deprecated")
async def get_deprecated():
    """Get deprecated routes."""
    return success_response({"deprecated": get_deprecated_routes()})


@router.get("/routes/{prefix}")
async def get_route_info(prefix: str):
    """Get information about a specific route prefix."""
    info = get_route_info(f"/{prefix}")
    if info:
        return success_response(info)
    return success_response({
        "error": "Route prefix not found",
        "prefix": prefix,
    })


@router.get("/routes/{prefix}/canonical")
async def get_canonical(prefix: str):
    """Get canonical route for a given prefix."""
    canonical = get_canonical_route(f"/{prefix}")
    return success_response({
        "requested": f"/{prefix}",
        "canonical": canonical,
        "is_deprecated": canonical is not None,
    })


@router.get("/architecture")
async def get_architecture():
    """Get PSIE canonical architecture overview."""
    # Group by layer
    layers = {}
    tiers = {1: 0, 2: 0, 3: 0}
    
    for prefix, info in CANONICAL_ROUTES.items():
        layer = info.get("layer", "Unknown")
        tier = info.get("tier", 0)
        
        if layer not in layers:
            layers[layer] = {"routes": [], "count": 0}
        layers[layer]["routes"].append(prefix)
        layers[layer]["count"] += 1
        
        if tier in tiers:
            tiers[tier] += 1
    
    return success_response({
        "architecture": {
            "layers": layers,
            "tiers": {
                "tier_1_public": tiers[1],
                "tier_2_internal": tiers[2],
                "tier_3_infrastructure": tiers[3],
            },
        },
        "total_routes": len(CANONICAL_ROUTES),
    })


@router.get("/ui-mapping")
async def get_ui_mapping():
    """Get canonical UI panel to API mapping."""
    mapping = {
        "Executive Dashboard": {
            "apis": ["/dashboard", "/outputs"],
            "description": "CEO command interface, system overview, reports"
        },
        "Intelligence": {
            "apis": ["/signals", "/intelligence", "/detection"],
            "description": "Forecasting, trends, risk detection"
        },
        "Strategy": {
            "apis": ["/strategies", "/debate", "/strategy-lab"],
            "description": "Strategy generation and testing"
        },
        "Governance": {
            "apis": ["/governance", "/decisions", "/reviews", "/board"],
            "description": "Approvals, decisions, reviews"
        },
        "Execution": {
            "apis": ["/execution", "/orchestration"],
            "description": "Action execution, workflow automation"
        },
        "Finance": {
            "apis": ["/finance", "/finance-ops", "/options-agent"],
            "description": "Financial intelligence and operations"
        },
    }
    return success_response({"ui_mapping": mapping})
