"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.config_validation import validate_and_raise
from app.core.config_check import get_readiness_report
from app.core.logging import setup_logging, get_logger
from app.api import profile, board, decisions, reviews, health, signals, governance, intelligence, simulation, execution, debate, learning, kernel
from app.db.init_db import init_db, seed_agents

# Setup logging
setup_logging()
logger = get_logger(__name__)


def validate_configuration() -> None:
    """Validate configuration at startup."""
    try:
        validate_and_raise()
        logger.info("Configuration validation passed")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        # In development, continue anyway with warnings
        settings = get_settings()
        if settings.app_env == "production":
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Validate configuration
    validate_configuration()
    
    # Log readiness report
    report = get_readiness_report()
    logger.info(f"System readiness: {report['overall']['status']}")
    
    # Initialize database
    try:
        await init_db()
        await seed_agents()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    
    yield
    
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Personal Strategic Intelligence Engine - A multi-agent strategic board system",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(profile.router)
    app.include_router(board.router)
    app.include_router(decisions.router)
    app.include_router(reviews.router)
    app.include_router(signals.router)
    app.include_router(governance.router)
    app.include_router(intelligence.router)
    app.include_router(simulation.router)
    app.include_router(execution.router)
    app.include_router(debate.router)
    app.include_router(learning.router)
    app.include_router(kernel.router)

    return app


# Create app instance
app = create_app()
