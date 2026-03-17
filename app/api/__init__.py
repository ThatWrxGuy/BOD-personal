"""BB-APP-001: API Routes Package."""

from app.api import (
    auth,
    users,
    signals,
    domains,
    recommendations,
    briefs,
    actions,
    memory,
    reviews,
    settings as settings_router,
)

__all__ = [
    "auth",
    "users",
    "signals",
    "domains",
    "recommendations",
    "briefs",
    "actions",
    "memory",
    "reviews",
    "settings_router",
]
