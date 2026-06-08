"""Main FastAPI application entry point."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.core import (
    close_db,
    get_logger,
    init_db,
    settings,
    setup_logging,
    setup_middlewares,
)
from app.core.sentry import init_sentry
from app.services.scheduler import start_scheduler, stop_scheduler

# ─── Application Lifespan ──────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger = get_logger("app.main")

    # Startup
    logger.info(
        "Starting application",
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        mode=settings.APP_MODE.value,
        environment=settings.ENVIRONMENT,
    )

    init_sentry()

    await init_db()
    logger.info("Database initialized")

    if not os.getenv("TESTING"):
        start_scheduler()
        logger.info("Background scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down application")
    if not os.getenv("TESTING"):
        stop_scheduler()
    await close_db()
    logger.info("Database connections closed")


# ─── Application Factory ───────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Setup logging first
    setup_logging()

    # Create app with optimal settings
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API para sistema de agendamento de barbearias e salões",
        docs_url="/docs" if settings.is_debug else None,
        redoc_url="/redoc" if settings.is_debug else None,
        openapi_url="/openapi.json" if settings.is_debug else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # Setup middlewares
    setup_middlewares(app)

    # Include routers
    _include_routers(app)

    return app


def _include_routers(app: FastAPI) -> None:
    """Include all API routers."""

    from app.api.health import router as health_router

    app.include_router(health_router)

    # API v1 routes
    from app.api.v1 import router as v1_router

    app.include_router(v1_router)

    # Debug routes (only in maintenance mode)
    if settings.is_maintenance:
        try:
            from app.api.debug import router as debug_router

            app.include_router(debug_router)
        except ImportError:
            pass


# ─── Application Instance ──────────────────────────────────────────────────────


app = create_app()


# ─── CLI Entry Point ───────────────────────────────────────────────────────────


def run() -> None:
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.is_debug,
        log_level=settings.log_level_effective.lower(),
    )


if __name__ == "__main__":
    run()
