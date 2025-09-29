"""
FastAPI Application Configuration

This module contains the main FastAPI application configuration,
including middleware, CORS, database initialization, and API routing.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import init_db, close_db
from app.api.v1 import auth, users, accounting, billing, nas, reports, system, radius, user_groups, radius_management


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Starting up daloRADIUS API...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down daloRADIUS API...")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Modern daloRADIUS API - RADIUS management system",
        version=settings.VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Include routers
    setup_routes(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """
    Configure application middleware
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware (security)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Add custom middleware for logging, rate limiting, etc.
    # This would be implemented in app/api/middleware.py


def setup_routes(app: FastAPI) -> None:
    """
    Configure application routes
    """
    # API v1 routes
    app.include_router(
        auth.router,
        prefix=settings.API_V1_STR + "/auth",
        tags=["authentication"]
    )
    
    app.include_router(
        users.router,
        prefix=settings.API_V1_STR + "/users",
        tags=["users"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        accounting.router,
        prefix=settings.API_V1_STR + "/accounting",
        tags=["accounting"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        billing.router,
        prefix=settings.API_V1_STR + "/billing",
        tags=["billing"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        nas.router,
        prefix=settings.API_V1_STR + "/nas",
        tags=["nas"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        reports.router,
        prefix=settings.API_V1_STR + "/reports",
        tags=["reports"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        system.router,
        prefix=settings.API_V1_STR + "/system",
        tags=["system"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        radius.router,
        prefix=settings.API_V1_STR + "/radius",
        tags=["radius"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        user_groups.router,
        prefix=settings.API_V1_STR + "/user-groups",
        tags=["user-groups"],
        dependencies=[Depends(security)]
    )
    
    app.include_router(
        radius_management.router,
        prefix=settings.API_V1_STR + "/radius-management",
        tags=["radius-management"],
        dependencies=[Depends(security)]
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "daloRADIUS Modern API",
            "version": settings.VERSION,
            "docs_url": "/docs" if settings.DEBUG else None
        }


# Create the application instance
app = create_application()