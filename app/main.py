"""
BB-APP-001 Phase 3: FastAPI Backend

Core application setup and API routes.
Following BB-APP-001 Section 3.3 Backend Application API requirements.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import Settings


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    # Startup
    print("Starting Busy Bee API...")
    
    # Initialize services
    # TODO: Initialize database connection
    # TODO: Initialize service layer
    
    yield
    
    # Shutdown
    print("Shutting down Busy Bee API...")
    # TODO: Close database connection


# Create FastAPI app
app = FastAPI(
    title="Busy Bee API",
    description="Personal Life Operating System - API",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
    }


# API Router imports
from app.api import auth, users, signals, domains, recommendations, briefs, actions, memory, reviews, settings as settings_router


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["Signals"])
app.include_router(domains.router, prefix="/api/v1/domains", tags=["Domains"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(briefs.router, prefix="/api/v1/briefs", tags=["Briefs"])
app.include_router(actions.router, prefix="/api/v1/actions", tags=["Actions"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])


__all__ = ["app", "settings"]
